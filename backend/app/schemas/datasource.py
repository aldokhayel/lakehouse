"""Pydantic schemas for DataSource request/response models."""

from typing import Any

from pydantic import BaseModel, ConfigDict


class DataSourceCreate(BaseModel):
    """Payload for creating a new data source."""

    name: str
    type: str
    config: dict[str, Any]


class DataSourceResponse(BaseModel):
    """API response shape for a DataSource record."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    type: str
    config: dict[str, Any]
    is_active: bool
    created_at: str
