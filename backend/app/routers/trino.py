"""Trino query and catalog browser endpoints."""

import asyncio
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.trino_service import trino_service

router = APIRouter(prefix="/trino", tags=["trino"])


class QueryRequest(BaseModel):
    """Payload for an ad-hoc Trino SQL query."""

    sql: str
    catalog: Optional[str] = None


@router.post("/query")
async def execute_query(req: QueryRequest):
    """Execute a SQL statement against Trino and return columns + rows."""
    try:
        result = await asyncio.get_event_loop().run_in_executor(
            None, lambda: trino_service.execute_query(req.sql, req.catalog)
        )
        return {
            "status": "success",
            "data": result,
            "message": f"{result['row_count']} rows returned",
        }
    except Exception as e:
        return {"status": "error", "data": None, "message": str(e)}


@router.get("/catalogs")
async def list_catalogs():
    """List all available Trino catalogs."""
    try:
        catalogs = await asyncio.get_event_loop().run_in_executor(None, trino_service.get_catalogs)
        return {
            "status": "success",
            "data": {"catalogs": catalogs},
            "message": f"{len(catalogs)} catalogs",
        }
    except Exception as e:
        return {"status": "error", "data": None, "message": str(e)}


@router.get("/schemas/{catalog}")
async def list_schemas(catalog: str):
    """List all schemas within a given catalog."""
    try:
        schemas = await asyncio.get_event_loop().run_in_executor(
            None, lambda: trino_service.get_schemas(catalog)
        )
        return {
            "status": "success",
            "data": {"schemas": schemas},
            "message": f"{len(schemas)} schemas",
        }
    except Exception as e:
        return {"status": "error", "data": None, "message": str(e)}


@router.get("/tables/{catalog}/{schema}")
async def list_tables(catalog: str, schema: str):
    """List all tables within a given catalog.schema."""
    try:
        tables = await asyncio.get_event_loop().run_in_executor(
            None, lambda: trino_service.get_tables(catalog, schema)
        )
        return {
            "status": "success",
            "data": {"tables": tables},
            "message": f"{len(tables)} tables",
        }
    except Exception as e:
        return {"status": "error", "data": None, "message": str(e)}
