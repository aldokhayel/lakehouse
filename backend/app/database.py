"""Async SQLAlchemy engine and session factory for SQLite persistence."""

import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

os.makedirs(os.path.dirname(settings.sqlite_path), exist_ok=True)

DATABASE_URL = f"sqlite+aiosqlite:///{settings.sqlite_path}"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


async def create_tables() -> None:
    """Create all database tables on startup."""
    from app.models import pipeline as pipeline_models  # noqa: F401
    from app.models import datasource as datasource_models  # noqa: F401
    from app.models import chat_history as chat_models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    """FastAPI dependency that yields an async database session."""
    async with AsyncSessionLocal() as session:
        yield session
