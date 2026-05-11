"""Synchronous Trino client service (PyTrino does not support async)."""

from typing import Any, Optional

import trino

from app.config import settings


class TrinoService:
    """Wraps the Trino dbapi connection for common query operations."""

    def _connect(self, catalog: Optional[str] = None) -> trino.dbapi.Connection:
        return trino.dbapi.connect(
            host=settings.trino_host,
            port=settings.trino_port,
            user=settings.trino_user,
            catalog=catalog or settings.trino_catalog,
        )

    def execute_query(self, sql: str, catalog: Optional[str] = None) -> dict[str, Any]:
        """Execute an arbitrary SQL statement and return columns + rows."""
        conn = self._connect(catalog)
        cursor = conn.cursor()
        cursor.execute(sql)
        columns = [desc[0] for desc in (cursor.description or [])]
        rows = cursor.fetchall()
        return {
            "columns": columns,
            "rows": [dict(zip(columns, row)) for row in rows],
            "row_count": len(rows),
        }

    def get_catalogs(self) -> list[str]:
        """Return a list of available Trino catalogs."""
        result = self.execute_query("SHOW CATALOGS", catalog="system")
        return [list(row.values())[0] for row in result["rows"]]

    def get_schemas(self, catalog: str) -> list[str]:
        """Return all schemas within a given catalog."""
        result = self.execute_query(f'SHOW SCHEMAS FROM "{catalog}"', catalog=catalog)
        return [list(row.values())[0] for row in result["rows"]]

    def get_tables(self, catalog: str, schema: str) -> list[str]:
        """Return all tables within a given catalog.schema."""
        result = self.execute_query(f'SHOW TABLES FROM "{catalog}"."{schema}"', catalog=catalog)
        return [list(row.values())[0] for row in result["rows"]]

    def is_healthy(self) -> bool:
        """Return True if Trino is reachable and responsive."""
        try:
            self.get_catalogs()
            return True
        except Exception:
            return False


trino_service = TrinoService()
