# app/services/vanna_service.py
# Vanna.ai service — natural-language-to-SQL using ChromaDB vector store and OpenRouter LLM.
# Lazy-initializes on first use so the backend starts cleanly even without ChromaDB running.

import logging
import os
import time
from typing import Any

logger = logging.getLogger(__name__)

_vn = None
_init_error: str | None = None


def _build_vanna():
    global _vn, _init_error
    if _vn is not None:
        return _vn

    try:
        import chromadb
        from openai import OpenAI
        from vanna.chromadb import ChromaDB_VectorStore
        from vanna.openai.openai_chat import OpenAI_Chat

        chromadb_host = os.environ.get("CHROMADB_HOST", "chromadb")
        chromadb_port = int(os.environ.get("CHROMADB_PORT", "8500"))
        openrouter_api_key = os.environ.get("OPENROUTER_API_KEY", "") or "not-configured"
        model = os.environ.get("OPENROUTER_MODEL", "anthropic/claude-sonnet-4-20250514")

        openrouter_client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=openrouter_api_key,
        )

        # ChromaDB listens on 8000 inside the container; the port env var reflects the host mapping.
        # Use HttpClient to connect to the separate ChromaDB container.
        chroma_client = chromadb.HttpClient(host=chromadb_host, port=8000)

        class LakehouseVanna(ChromaDB_VectorStore, OpenAI_Chat):
            def __init__(self, config=None):
                ChromaDB_VectorStore.__init__(self, config=config)
                OpenAI_Chat.__init__(self, client=openrouter_client, config=config)

            def run_sql(self, sql: str):
                import pandas as pd
                import trino as trino_module

                conn = trino_module.dbapi.connect(
                    host=os.environ.get("TRINO_HOST", "trino"),
                    port=int(os.environ.get("TRINO_PORT", "8080")),
                    user="vanna",
                    catalog="iceberg",
                )
                cursor = conn.cursor()
                cursor.execute(sql)
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                return pd.DataFrame(rows, columns=columns)

        _vn = LakehouseVanna(config={"model": model, "client": chroma_client})
        _init_error = None
        logger.info("Vanna initialized with ChromaDB at %s:8000, model=%s", chromadb_host, model)
        return _vn

    except Exception as exc:
        _init_error = str(exc)
        logger.warning("Vanna init failed (ChromaDB may not be running): %s", exc)
        return None


class VannaService:
    def _get_vn(self):
        return _build_vanna()

    def status(self) -> dict:
        vn = self._get_vn()
        if vn is None:
            return {"ready": False, "error": _init_error or "Vanna not initialized"}
        return {"ready": True, "error": None}

    def ask(self, question: str) -> dict:
        """Generate SQL from a natural-language question. Does NOT execute."""
        vn = self._get_vn()
        if vn is None:
            return {
                "status": "error",
                "generated_sql": None,
                "error": "ChromaDB is not running. Start it with: docker compose --profile phase5 up -d chromadb",
            }
        try:
            sql = vn.generate_sql(question)
            return {"status": "success", "generated_sql": sql, "error": None}
        except Exception as exc:
            logger.error("Vanna generate_sql failed: %s", exc)
            return {"status": "error", "generated_sql": None, "error": str(exc)}

    def execute(self, sql: str) -> dict:
        """Execute SQL via Trino and return rows + columns."""
        vn = self._get_vn()
        if vn is None:
            return {"status": "error", "error": "ChromaDB is not running"}
        try:
            start = time.time()
            df = vn.run_sql(sql)
            elapsed_ms = (time.time() - start) * 1000

            # Convert NaN/NaT to None for JSON serialization
            rows = [
                [None if (v != v) else v for v in row]
                for row in df.values.tolist()
            ]
            return {
                "status": "success",
                "columns": list(df.columns),
                "rows": rows,
                "row_count": len(df),
                "execution_time_ms": round(elapsed_ms, 1),
                "error": None,
            }
        except Exception as exc:
            logger.error("Vanna execute failed: %s", exc)
            return {"status": "error", "error": str(exc)}

    def train_pair(self, question: str, sql: str) -> dict:
        vn = self._get_vn()
        if vn is None:
            return {"status": "error", "error": "ChromaDB is not running"}
        try:
            vn.train(question=question, sql=sql)
            return {"status": "success", "message": "Training pair added"}
        except Exception as exc:
            return {"status": "error", "error": str(exc)}

    def train_ddl(self, ddl: str) -> dict:
        vn = self._get_vn()
        if vn is None:
            return {"status": "error", "error": "ChromaDB is not running"}
        try:
            vn.train(ddl=ddl)
            return {"status": "success", "message": "DDL training added"}
        except Exception as exc:
            return {"status": "error", "error": str(exc)}

    def get_training_data(self) -> dict:
        vn = self._get_vn()
        if vn is None:
            return {"status": "error", "error": "ChromaDB is not running"}
        try:
            df = vn.get_training_data()
            if df is None or len(df) == 0:
                return {"status": "success", "data": [], "count": 0}
            records = df.to_dict(orient="records")
            return {"status": "success", "data": records, "count": len(records)}
        except Exception as exc:
            return {"status": "error", "error": str(exc)}

    def auto_train_from_trino(self) -> dict:
        """Query Trino information_schema and train Vanna on DDL."""
        vn = self._get_vn()
        if vn is None:
            return {"status": "error", "error": "ChromaDB is not running"}
        try:
            import trino as trino_module
            conn = trino_module.dbapi.connect(
                host=os.environ.get("TRINO_HOST", "trino"),
                port=int(os.environ.get("TRINO_PORT", "8080")),
                user="vanna",
                catalog="iceberg",
            )
            cursor = conn.cursor()
            cursor.execute("""
                SELECT table_schema, table_name, column_name, data_type
                FROM iceberg.information_schema.columns
                WHERE table_schema NOT IN ('information_schema')
                ORDER BY table_schema, table_name, ordinal_position
            """)
            rows = cursor.fetchall()

            # Group columns by table and build CREATE TABLE DDL
            tables: dict[tuple, list] = {}
            for schema, table, col, dtype in rows:
                key = (schema, table)
                tables.setdefault(key, []).append((col, dtype))

            trained = 0
            for (schema, table), columns in tables.items():
                col_defs = ",\n  ".join(f"{col} {dtype}" for col, dtype in columns)
                ddl = f"CREATE TABLE iceberg.{schema}.{table} (\n  {col_defs}\n);"
                vn.train(ddl=ddl)
                trained += 1

            logger.info("Auto-trained Vanna on %d tables from Trino", trained)
            return {"status": "success", "tables_trained": trained}
        except Exception as exc:
            logger.error("Auto-train failed: %s", exc)
            return {"status": "error", "error": str(exc)}


vanna_service = VannaService()
