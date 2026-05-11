#!/usr/bin/env python3
# scripts/init-iceberg.py
# Creates sample Iceberg tables and populates them with test data via Trino.
# Run this after `make up` and `make health` both succeed.
#
# Prerequisites:
#   pip install trino
#
# Usage:
#   python scripts/init-iceberg.py
#
# What it creates:
#   iceberg.raw.raw_orders           — raw ingest layer (5 rows)
#   iceberg.staging.stg_orders       — cleaned / typed staging layer
#   iceberg.mart.mart_daily_revenue  — aggregated mart layer

import trino
import time

TRINO_HOST = "localhost"
TRINO_PORT = 8080
CATALOG = "iceberg"


def connect():
    return trino.dbapi.connect(
        host=TRINO_HOST,
        port=TRINO_PORT,
        user="admin",
        catalog=CATALOG,
    )


def execute(cursor, sql, description=""):
    label = description or sql[:60]
    print(f"  {label}...")
    cursor.execute(sql)
    try:
        return cursor.fetchall()
    except Exception:
        return None


def main():
    print("Connecting to Trino...")
    conn = None
    for attempt in range(1, 11):
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            print("  Connected.\n")
            break
        except Exception as exc:
            print(f"  Attempt {attempt}/10 failed: {exc}. Retrying in 5s...")
            time.sleep(5)
    else:
        raise RuntimeError("Could not connect to Trino after 10 attempts.")

    # ------------------------------------------------------------------
    # Create schemas (one per lakehouse layer)
    # ------------------------------------------------------------------
    print("Creating schemas...")
    for schema in ["raw", "staging", "mart"]:
        execute(
            cursor,
            f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{schema} "
            f"WITH (location = 's3a://lakehouse-{schema}/warehouse/')",
            f"Schema: {schema}",
        )

    # ------------------------------------------------------------------
    # Raw layer
    # ------------------------------------------------------------------
    print("\nBuilding raw layer...")
    execute(
        cursor,
        """
        CREATE TABLE IF NOT EXISTS iceberg.raw.raw_orders (
            order_id     VARCHAR,
            customer_id  VARCHAR,
            order_date   DATE,
            amount       DOUBLE,
            status       VARCHAR,
            _ingested_at TIMESTAMP
        ) WITH (
            format   = 'PARQUET',
            location = 's3a://lakehouse-raw/warehouse/raw_orders'
        )
        """,
        "Create raw.raw_orders",
    )

    execute(
        cursor,
        """
        INSERT INTO iceberg.raw.raw_orders VALUES
        ('ORD-001', 'CUST-1', DATE '2024-01-15', 125.50, 'completed', TIMESTAMP '2024-01-15 10:00:00'),
        ('ORD-002', 'CUST-2', DATE '2024-01-16',  89.99, 'completed', TIMESTAMP '2024-01-16 11:00:00'),
        ('ORD-003', 'CUST-1', DATE '2024-01-17', 340.00, 'pending',   TIMESTAMP '2024-01-17 09:30:00'),
        ('ORD-004', 'CUST-3', DATE '2024-01-18',  55.00, 'completed', TIMESTAMP '2024-01-18 14:00:00'),
        ('ORD-005', 'CUST-2', DATE '2024-02-01', 210.75, 'completed', TIMESTAMP '2024-02-01 16:00:00')
        """,
        "Insert 5 sample rows into raw_orders",
    )

    # ------------------------------------------------------------------
    # Staging layer
    # ------------------------------------------------------------------
    print("\nBuilding staging layer...")
    execute(
        cursor,
        """
        CREATE TABLE IF NOT EXISTS iceberg.staging.stg_orders (
            order_id    VARCHAR,
            customer_id VARCHAR,
            order_date  DATE,
            amount_usd  DOUBLE,
            status      VARCHAR,
            is_complete BOOLEAN,
            _loaded_at  TIMESTAMP
        ) WITH (
            format   = 'PARQUET',
            location = 's3a://lakehouse-staging/warehouse/stg_orders'
        )
        """,
        "Create staging.stg_orders",
    )

    execute(
        cursor,
        """
        INSERT INTO iceberg.staging.stg_orders
        SELECT
            order_id,
            customer_id,
            order_date,
            amount              AS amount_usd,
            status,
            status = 'completed' AS is_complete,
            _ingested_at        AS _loaded_at
        FROM iceberg.raw.raw_orders
        """,
        "Populate stg_orders from raw_orders",
    )

    # ------------------------------------------------------------------
    # Mart layer
    # ------------------------------------------------------------------
    print("\nBuilding mart layer...")
    execute(
        cursor,
        """
        CREATE TABLE IF NOT EXISTS iceberg.mart.mart_daily_revenue (
            order_date      DATE,
            total_revenue   DOUBLE,
            order_count     BIGINT,
            avg_order_value DOUBLE
        ) WITH (
            format   = 'PARQUET',
            location = 's3a://lakehouse-mart/warehouse/mart_daily_revenue'
        )
        """,
        "Create mart.mart_daily_revenue",
    )

    execute(
        cursor,
        """
        INSERT INTO iceberg.mart.mart_daily_revenue
        SELECT
            order_date,
            SUM(amount_usd)  AS total_revenue,
            COUNT(*)         AS order_count,
            AVG(amount_usd)  AS avg_order_value
        FROM iceberg.staging.stg_orders
        WHERE is_complete = TRUE
        GROUP BY order_date
        ORDER BY order_date
        """,
        "Populate mart_daily_revenue from stg_orders",
    )

    # ------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------
    print("\nVerification (row counts):")
    tables = [
        "iceberg.raw.raw_orders",
        "iceberg.staging.stg_orders",
        "iceberg.mart.mart_daily_revenue",
    ]
    for table in tables:
        result = execute(cursor, f"SELECT COUNT(*) FROM {table}", f"Count {table}")
        count = result[0][0] if result else "?"
        print(f"  {table}: {count} rows")

    print("\nIceberg tables initialized successfully!")
    print("  Open Trino CLI with:  make trino-cli")
    print("  Then query:           SELECT * FROM iceberg.raw.raw_orders;")


if __name__ == "__main__":
    main()
