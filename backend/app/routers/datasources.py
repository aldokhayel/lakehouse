"""CRUD endpoints for DataSource management."""

import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.datasource import DataSource
from app.schemas.datasource import DataSourceCreate, DataSourceResponse

router = APIRouter(prefix="/datasources", tags=["datasources"])


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _serialize(ds: DataSource) -> DataSourceResponse:
    """Convert ORM DataSource to Pydantic response, deserializing config JSON."""
    return DataSourceResponse(
        id=ds.id,
        name=ds.name,
        type=ds.type,
        config=json.loads(ds.config) if isinstance(ds.config, str) else ds.config,
        is_active=ds.is_active,
        created_at=ds.created_at,
    )


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_datasource(payload: DataSourceCreate, db: AsyncSession = Depends(get_db)):
    """Register a new data source connection."""
    ds = DataSource(
        id=str(uuid.uuid4()),
        name=payload.name,
        type=payload.type,
        config=json.dumps(payload.config),
        is_active=True,
        created_at=_now_iso(),
    )
    db.add(ds)
    await db.commit()
    await db.refresh(ds)
    return {"status": "success", "data": _serialize(ds), "message": "Data source created"}


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------

@router.get("")
async def list_datasources(db: AsyncSession = Depends(get_db)):
    """Return all active data sources."""
    result = await db.execute(select(DataSource).where(DataSource.is_active == True))  # noqa: E712
    datasources = result.scalars().all()
    return {
        "status": "success",
        "data": {"datasources": [_serialize(ds) for ds in datasources]},
        "message": f"{len(datasources)} data sources",
    }


# ---------------------------------------------------------------------------
# Test connection (stub)
# ---------------------------------------------------------------------------

@router.post("/{datasource_id}/test")
async def test_datasource(datasource_id: str, db: AsyncSession = Depends(get_db)):
    """Test connectivity to a data source (stub — live testing in Phase 3)."""
    ds = await db.get(DataSource, datasource_id)
    if not ds or not ds.is_active:
        raise HTTPException(status_code=404, detail="Data source not found")
    return {
        "status": "success",
        "data": {"reachable": True},
        "message": "Connection test not yet implemented",
    }


# ---------------------------------------------------------------------------
# Delete (soft)
# ---------------------------------------------------------------------------

@router.delete("/{datasource_id}", status_code=status.HTTP_200_OK)
async def delete_datasource(datasource_id: str, db: AsyncSession = Depends(get_db)):
    """Soft-delete a data source by marking it inactive."""
    ds = await db.get(DataSource, datasource_id)
    if not ds or not ds.is_active:
        raise HTTPException(status_code=404, detail="Data source not found")
    ds.is_active = False
    await db.commit()
    return {"status": "success", "data": None, "message": "Data source deactivated"}
