#!/usr/bin/env python3
# scripts/seed-vanna.py
# Seeds Vanna.ai with schema DDL and sample question/SQL pairs so the AI
# can generate accurate SQL against the lakehouse's Iceberg tables.
#
# Run after ChromaDB + Trino are healthy:
#   docker compose --profile phase5 up -d chromadb
#   python scripts/seed-vanna.py

import os
import sys

# ---------------------------------------------------------------------------
# Vanna setup (same config as vanna_service.py)
# ---------------------------------------------------------------------------

try:
    import chromadb
    from openai import OpenAI
    from vanna.chromadb import ChromaDB_VectorStore
    from vanna.openai.openai_chat import OpenAI_Chat
except ImportError:
    print("ERROR: Vanna packages not installed. Run: pip install vanna chromadb openai")
    sys.exit(1)

CHROMADB_HOST = os.environ.get("CHROMADB_HOST", "localhost")
CHROMADB_PORT = int(os.environ.get("CHROMADB_PORT", "8500"))
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
MODEL = os.environ.get("OPENROUTER_MODEL", "anthropic/claude-sonnet-4-20250514")

if not OPENROUTER_API_KEY:
    print("WARNING: OPENROUTER_API_KEY not set. LLM calls will fail but DDL/Q+A training will still work.")

openrouter_client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)
chroma_client = chromadb.HttpClient(host=CHROMADB_HOST, port=8000)


class LakehouseVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, client=openrouter_client, config=config)


vn = LakehouseVanna(config={"model": MODEL, "client": chroma_client})

# ---------------------------------------------------------------------------
# 1. DDL — Iceberg table schemas
# ---------------------------------------------------------------------------

DDL_STATEMENTS = [
    """
    CREATE TABLE iceberg.raw.orders (
      order_id VARCHAR,
      customer_id VARCHAR,
      order_date DATE,
      product_id VARCHAR,
      quantity BIGINT,
      unit_price DOUBLE,
      status VARCHAR,
      region VARCHAR
    );
    """,
    """
    CREATE TABLE iceberg.staging.orders (
      order_id VARCHAR,
      customer_id VARCHAR,
      order_date DATE,
      product_id VARCHAR,
      quantity BIGINT,
      unit_price DOUBLE,
      revenue DOUBLE,
      status VARCHAR,
      region VARCHAR,
      loaded_at TIMESTAMP
    );
    """,
    """
    CREATE TABLE iceberg.mart.orders (
      order_id VARCHAR,
      customer_id VARCHAR,
      order_date DATE,
      product_id VARCHAR,
      quantity BIGINT,
      unit_price DOUBLE,
      revenue DOUBLE,
      status VARCHAR,
      region VARCHAR
    );
    """,
    """
    CREATE TABLE iceberg.mart.customer_summary (
      customer_id VARCHAR,
      total_orders BIGINT,
      total_revenue DOUBLE,
      first_order_date DATE,
      last_order_date DATE,
      avg_order_value DOUBLE
    );
    """,
]

print("Training on DDL...")
for ddl in DDL_STATEMENTS:
    vn.train(ddl=ddl.strip())
    print("  ✓", ddl.strip().split("\n")[0][:60])

# ---------------------------------------------------------------------------
# 2. Documentation — data layer descriptions
# ---------------------------------------------------------------------------

DOCS = [
    "The iceberg catalog contains three schemas: raw (raw ingested data), staging (cleaned/enriched data), and mart (business-ready aggregated data).",
    "The mart.orders table is the primary fact table. Use it for revenue, order count, and product analysis.",
    "The mart.customer_summary table provides pre-aggregated customer metrics. Use it for customer segmentation and lifetime value queries.",
    "revenue = quantity * unit_price. This column is pre-computed in staging and mart layers.",
    "Dates are stored as DATE type. Use date_trunc('month', order_date) to group by month.",
    "All monetary values are in USD. The revenue column is a DOUBLE.",
    "The status column can be: 'completed', 'pending', 'cancelled', 'refunded'.",
    "The region column contains geographic regions: 'North', 'South', 'East', 'West'.",
]

print("\nTraining on documentation...")
for doc in DOCS:
    vn.train(documentation=doc)
    print("  ✓", doc[:70])

# ---------------------------------------------------------------------------
# 3. Sample question/SQL pairs
# ---------------------------------------------------------------------------

QA_PAIRS = [
    (
        "Show total revenue by month",
        "SELECT date_trunc('month', order_date) AS month, SUM(revenue) AS total_revenue FROM iceberg.mart.orders GROUP BY 1 ORDER BY 1",
    ),
    (
        "What is the total revenue?",
        "SELECT SUM(revenue) AS total_revenue FROM iceberg.mart.orders",
    ),
    (
        "How many orders are there?",
        "SELECT COUNT(*) AS order_count FROM iceberg.mart.orders",
    ),
    (
        "Top 10 customers by revenue",
        "SELECT customer_id, SUM(revenue) AS total_revenue FROM iceberg.mart.orders GROUP BY customer_id ORDER BY total_revenue DESC LIMIT 10",
    ),
    (
        "Revenue by region",
        "SELECT region, SUM(revenue) AS total_revenue, COUNT(*) AS order_count FROM iceberg.mart.orders GROUP BY region ORDER BY total_revenue DESC",
    ),
    (
        "Show monthly order count and revenue",
        "SELECT date_trunc('month', order_date) AS month, COUNT(*) AS order_count, SUM(revenue) AS total_revenue FROM iceberg.mart.orders GROUP BY 1 ORDER BY 1",
    ),
    (
        "What is the average order value?",
        "SELECT AVG(revenue) AS avg_order_value FROM iceberg.mart.orders WHERE status = 'completed'",
    ),
    (
        "Show orders from the last 30 days",
        "SELECT * FROM iceberg.mart.orders WHERE order_date >= current_date - INTERVAL '30' DAY ORDER BY order_date DESC",
    ),
    (
        "Revenue by product",
        "SELECT product_id, SUM(revenue) AS total_revenue, SUM(quantity) AS total_quantity FROM iceberg.mart.orders GROUP BY product_id ORDER BY total_revenue DESC",
    ),
    (
        "How many completed vs cancelled orders?",
        "SELECT status, COUNT(*) AS order_count, SUM(revenue) AS total_revenue FROM iceberg.mart.orders GROUP BY status ORDER BY order_count DESC",
    ),
    (
        "Show customer lifetime value",
        "SELECT customer_id, total_orders, total_revenue, avg_order_value, first_order_date, last_order_date FROM iceberg.mart.customer_summary ORDER BY total_revenue DESC LIMIT 20",
    ),
    (
        "Daily revenue trend this year",
        "SELECT order_date, SUM(revenue) AS daily_revenue FROM iceberg.mart.orders WHERE order_date >= date_trunc('year', current_date) GROUP BY order_date ORDER BY order_date",
    ),
]

print("\nTraining on question/SQL pairs...")
for question, sql in QA_PAIRS:
    vn.train(question=question, sql=sql)
    print(f"  ✓ {question}")

print(f"\n✅ Seeding complete: {len(DDL_STATEMENTS)} DDL, {len(DOCS)} docs, {len(QA_PAIRS)} Q/A pairs")
print("   Vanna is ready. Open the Chat panel and ask questions about your data.")
