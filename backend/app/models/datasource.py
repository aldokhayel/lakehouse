"""ORM model for DataSource entities."""

import uuid

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class DataSource(Base):
    """Represents an external data source connection configuration."""

    __tablename__ = "datasources"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # api / mssql / postgresql / mongodb
    config: Mapped[str] = mapped_column(Text, nullable=False, default="{}")  # JSON string
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[str] = mapped_column(String, nullable=False, default=func.now())
