"""ORM model for ChatMessage history entities."""

import uuid

from sqlalchemy import Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class ChatMessage(Base):
    """Stores the history of natural-language-to-SQL interactions."""

    __tablename__ = "chat_messages"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    question: Mapped[str] = mapped_column(Text, nullable=False)
    generated_sql: Mapped[str] = mapped_column(Text, nullable=True)
    result_summary: Mapped[str] = mapped_column(Text, nullable=True)
    execution_time_ms: Mapped[float] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")  # pending / success / error
    created_at: Mapped[str] = mapped_column(String, nullable=False, default=func.now())
