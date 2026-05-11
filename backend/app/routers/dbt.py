"""dbt CLI runner endpoints."""

import asyncio
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.dbt_service import dbt_service

router = APIRouter(prefix="/dbt", tags=["dbt"])


class DbtRunRequest(BaseModel):
    """Optional node selector for dbt run/test commands."""

    select: Optional[str] = None


@router.post("/run")
async def run_dbt(req: DbtRunRequest = DbtRunRequest()):
    """Execute `dbt run`, optionally filtered by a model selector."""
    result = await asyncio.get_event_loop().run_in_executor(
        None, lambda: dbt_service.run_models(req.select)
    )
    return {
        "status": "success" if result["success"] else "error",
        "data": result,
        "message": "dbt run completed" if result["success"] else "dbt run failed",
    }


@router.post("/test")
async def test_dbt(req: DbtRunRequest = DbtRunRequest()):
    """Execute `dbt test`, optionally filtered by a model selector."""
    result = await asyncio.get_event_loop().run_in_executor(
        None, lambda: dbt_service.run_tests(req.select)
    )
    return {
        "status": "success" if result["success"] else "error",
        "data": result,
        "message": "dbt test completed" if result["success"] else "dbt test failed",
    }


@router.get("/models")
async def list_models():
    """List all dbt models defined in the project."""
    models = await asyncio.get_event_loop().run_in_executor(None, dbt_service.list_models)
    return {
        "status": "success",
        "data": {"models": models},
        "message": f"{len(models)} models",
    }


@router.get("/run-results")
async def get_run_results():
    """Return the most recent dbt run_results.json artifact."""
    results = await asyncio.get_event_loop().run_in_executor(None, dbt_service.get_run_results)
    return {"status": "success", "data": results, "message": "Run results retrieved"}
