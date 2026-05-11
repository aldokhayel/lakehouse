"""ORM models for Pipeline and PipelineRun entities."""

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class Pipeline(Base):
    """Represents a data pipeline definition (React Flow JSON)."""

    __tablename__ = "pipelines"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    definition: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="idle")
    created_at: Mapped[str] = mapped_column(String, nullable=False, default=func.now())
    updated_at: Mapped[str] = mapped_column(String, nullable=False, default=func.now(), onupdate=func.now())

    runs: Mapped[list["PipelineRun"]] = relationship("PipelineRun", back_populates="pipeline", cascade="all, delete-orphan")


class PipelineRun(Base):
    """Represents a single execution of a Pipeline."""

    __tablename__ = "pipeline_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    pipeline_id: Mapped[str] = mapped_column(String, ForeignKey("pipelines.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    logs: Mapped[str] = mapped_column(Text, nullable=True)
    started_at: Mapped[str] = mapped_column(String, nullable=False, default=func.now())
    finished_at: Mapped[str] = mapped_column(String, nullable=True)

    pipeline: Mapped["Pipeline"] = relationship("Pipeline", back_populates="runs")
