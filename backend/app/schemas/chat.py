# app/schemas/chat.py
# Pydantic schemas for natural-language chat (Vanna.ai) request/response models.

from typing import Any, Optional

from pydantic import BaseModel


class ChatAskRequest(BaseModel):
    question: str


class ChatExecuteRequest(BaseModel):
    sql: str
    message_id: Optional[str] = None  # ID from a prior /ask call to update history


class ChatAskResponse(BaseModel):
    question: str
    generated_sql: Optional[str] = None
    results: Optional[list[dict[str, Any]]] = None
    columns: Optional[list[str]] = None
    row_count: Optional[int] = None
    execution_time_ms: Optional[float] = None
    status: str
    error: Optional[str] = None


class ChatTrainRequest(BaseModel):
    question: str
    sql: str


class ChatHistoryItem(BaseModel):
    id: str
    question: str
    generated_sql: Optional[str] = None
    status: str
    created_at: str
