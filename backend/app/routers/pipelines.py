"""CRUD endpoints for Pipeline and PipelineRun management."""

import json
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.pipeline import Pipeline, PipelineRun
from app.schemas.pipeline import PipelineCreate, PipelineResponse, PipelineRunResponse, PipelineUpdate

router = APIRouter(prefix="/pipelines", tags=["pipelines"])


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _serialize(pipeline: Pipeline) -> PipelineResponse:
    """Convert ORM Pipeline to Pydantic response, deserializing the JSON definition."""
    return PipelineResponse(
        id=pipeline.id,
        name=pipeline.name,
        description=pipeline.description,
        definition=json.loads(pipeline.definition) if isinstance(pipeline.definition, str) else pipeline.definition,
        status=pipeline.status,
        created_at=pipeline.created_at,
        updated_at=pipeline.updated_at,
    )


def _serialize_run(run: PipelineRun) -> PipelineRunResponse:
    return PipelineRunResponse(
        id=run.id,
        pipeline_id=run.pipeline_id,
        status=run.status,
        logs=run.logs,
        started_at=run.started_at,
        finished_at=run.finished_at,
    )


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_pipeline(payload: PipelineCreate, db: AsyncSession = Depends(get_db)):
    """Create a new pipeline definition."""
    now = _now_iso()
    pipeline = Pipeline(
        id=str(uuid.uuid4()),
        name=payload.name,
        description=payload.description,
        definition=json.dumps(payload.definition),
        status="idle",
        created_at=now,
        updated_at=now,
    )
    db.add(pipeline)
    await db.commit()
    await db.refresh(pipeline)
    return {"status": "success", "data": _serialize(pipeline), "message": "Pipeline created"}


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------

@router.get("")
async def list_pipelines(db: AsyncSession = Depends(get_db)):
    """Return all pipelines."""
    result = await db.execute(select(Pipeline))
    pipelines = result.scalars().all()
    return {
        "status": "success",
        "data": {"pipelines": [_serialize(p) for p in pipelines]},
        "message": f"{len(pipelines)} pipelines",
    }


# ---------------------------------------------------------------------------
# Get one
# ---------------------------------------------------------------------------

@router.get("/{pipeline_id}")
async def get_pipeline(pipeline_id: str, db: AsyncSession = Depends(get_db)):
    """Return a single pipeline by ID."""
    pipeline = await db.get(Pipeline, pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return {"status": "success", "data": _serialize(pipeline), "message": "Pipeline retrieved"}


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

@router.put("/{pipeline_id}")
async def update_pipeline(pipeline_id: str, payload: PipelineUpdate, db: AsyncSession = Depends(get_db)):
    """Update an existing pipeline."""
    pipeline = await db.get(Pipeline, pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    if payload.name is not None:
        pipeline.name = payload.name
    if payload.description is not None:
        pipeline.description = payload.description
    if payload.definition is not None:
        pipeline.definition = json.dumps(payload.definition)
    pipeline.updated_at = _now_iso()
    await db.commit()
    await db.refresh(pipeline)
    return {"status": "success", "data": _serialize(pipeline), "message": "Pipeline updated"}


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

@router.delete("/{pipeline_id}", status_code=status.HTTP_200_OK)
async def delete_pipeline(pipeline_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a pipeline and all its runs."""
    pipeline = await db.get(Pipeline, pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    await db.delete(pipeline)
    await db.commit()
    return {"status": "success", "data": None, "message": "Pipeline deleted"}


# ---------------------------------------------------------------------------
# Run (stub)
# ---------------------------------------------------------------------------

@router.post("/{pipeline_id}/run", status_code=status.HTTP_202_ACCEPTED)
async def run_pipeline(pipeline_id: str, db: AsyncSession = Depends(get_db)):
    """Trigger a pipeline execution (stub — orchestration wired in Phase 3)."""
    pipeline = await db.get(Pipeline, pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    now = _now_iso()
    run = PipelineRun(
        id=str(uuid.uuid4()),
        pipeline_id=pipeline_id,
        status="pending",
        logs="Pipeline execution triggered.",
        started_at=now,
        finished_at=None,
    )
    pipeline.status = "running"
    pipeline.updated_at = now
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return {
        "status": "success",
        "data": _serialize_run(run),
        "message": "Pipeline execution triggered",
    }


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------

@router.get("/{pipeline_id}/status")
async def pipeline_status(pipeline_id: str, db: AsyncSession = Depends(get_db)):
    """Return the latest run status for a pipeline."""
    pipeline = await db.get(Pipeline, pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    result = await db.execute(
        select(PipelineRun)
        .where(PipelineRun.pipeline_id == pipeline_id)
        .order_by(PipelineRun.started_at.desc())
        .limit(1)
    )
    latest_run: Optional[PipelineRun] = result.scalars().first()
    return {
        "status": "success",
        "data": {
            "pipeline_status": pipeline.status,
            "latest_run": _serialize_run(latest_run) if latest_run else None,
        },
        "message": f"Pipeline is {pipeline.status}",
    }
