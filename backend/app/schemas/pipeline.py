"""Pydantic schemas for Pipeline and PipelineRun request/response models."""

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class PipelineCreate(BaseModel):
    """Payload for creating a new pipeline."""

    name: str
    description: str = ""
    definition: dict[str, Any]


class PipelineUpdate(BaseModel):
    """Payload for updating an existing pipeline (all fields optional)."""

    name: Optional[str] = None
    description: Optional[str] = None
    definition: Optional[dict[str, Any]] = None


class PipelineResponse(BaseModel):
    """API response shape for a Pipeline record."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str
    definition: dict[str, Any]
    status: str
    created_at: str
    updated_at: str


class PipelineRunResponse(BaseModel):
    """API response shape for a PipelineRun record."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    pipeline_id: str
    status: str
    logs: Optional[str]
    started_at: str
    finished_at: Optional[str]
