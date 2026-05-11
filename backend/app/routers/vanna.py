# app/routers/vanna.py
# Vanna.ai natural-language-to-SQL endpoints: ask (generate), execute (run), train, history.

import asyncio
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.chat_history import ChatMessage
from app.schemas.chat import (
    ChatAskRequest,
    ChatExecuteRequest,
    ChatHistoryItem,
    ChatTrainRequest,
)
from app.services.vanna_service import vanna_service

router = APIRouter(prefix="/vanna", tags=["vanna"])

loop = asyncio.get_event_loop


def _run_sync(fn):
    """Run a blocking call in a thread pool executor."""
    return asyncio.get_event_loop().run_in_executor(None, fn)


@router.get("/status")
async def status():
    """Check if Vanna + ChromaDB are ready."""
    result = await asyncio.get_event_loop().run_in_executor(
        None, vanna_service.status
    )
    return {"status": "success", "data": result, "message": "Vanna status"}


@router.post("/ask")
async def ask(req: ChatAskRequest, db: AsyncSession = Depends(get_db)):
    """Translate a natural-language question to SQL. Does NOT execute the SQL."""
    result = await asyncio.get_event_loop().run_in_executor(
        None, lambda: vanna_service.ask(req.question)
    )

    # Persist to chat history
    msg = ChatMessage(
        id=str(uuid.uuid4()),
        question=req.question,
        generated_sql=result.get("generated_sql"),
        status=result.get("status", "error"),
        created_at=datetime.utcnow().isoformat(),
    )
    db.add(msg)
    await db.commit()

    return {
        "status": result["status"],
        "data": {
            "message_id": msg.id,
            "question": req.question,
            "generated_sql": result.get("generated_sql"),
            "error": result.get("error"),
        },
        "message": "SQL generated" if result["status"] == "success" else result.get("error", "Failed"),
    }


@router.post("/execute")
async def execute(req: ChatExecuteRequest, db: AsyncSession = Depends(get_db)):
    """Execute SQL via Trino and return results as rows + columns."""
    result = await asyncio.get_event_loop().run_in_executor(
        None, lambda: vanna_service.execute(req.sql)
    )

    # Update or create a history entry for the execution
    if req.message_id:
        existing = await db.get(ChatMessage, req.message_id)
        if existing:
            existing.generated_sql = req.sql
            existing.status = result["status"]
            existing.result_summary = (
                f"{result.get('row_count', 0)} rows" if result["status"] == "success" else result.get("error")
            )
            existing.execution_time_ms = result.get("execution_time_ms")
            await db.commit()

    return {
        "status": result["status"],
        "data": {
            "columns": result.get("columns", []),
            "rows": result.get("rows", []),
            "row_count": result.get("row_count", 0),
            "execution_time_ms": result.get("execution_time_ms"),
            "error": result.get("error"),
        },
        "message": f"{result.get('row_count', 0)} rows returned" if result["status"] == "success" else result.get("error", "Execution failed"),
    }


@router.get("/history")
async def get_history(db: AsyncSession = Depends(get_db)):
    """Return the chat question/SQL history (most recent first)."""
    result = await db.execute(
        select(ChatMessage).order_by(ChatMessage.created_at.desc()).limit(100)
    )
    messages = result.scalars().all()
    items = [
        ChatHistoryItem(
            id=m.id,
            question=m.question,
            generated_sql=m.generated_sql,
            status=m.status,
            created_at=m.created_at,
        )
        for m in messages
    ]
    return {
        "status": "success",
        "data": {"history": [i.model_dump() for i in items]},
        "message": f"{len(items)} messages",
    }


@router.post("/train")
async def train(req: ChatTrainRequest):
    """Train Vanna with a confirmed question/SQL pair."""
    result = await asyncio.get_event_loop().run_in_executor(
        None, lambda: vanna_service.train_pair(req.question, req.sql)
    )
    return {"status": result["status"], "data": None, "message": result.get("message", result.get("error"))}


@router.post("/auto-train")
async def auto_train():
    """Auto-train Vanna by scraping Trino's information_schema."""
    result = await asyncio.get_event_loop().run_in_executor(
        None, vanna_service.auto_train_from_trino
    )
    return {
        "status": result["status"],
        "data": {"tables_trained": result.get("tables_trained")},
        "message": f"Trained on {result.get('tables_trained')} tables" if result["status"] == "success" else result.get("error"),
    }


@router.get("/training-data")
async def get_training_data():
    """Return stored Vanna training data from ChromaDB."""
    result = await asyncio.get_event_loop().run_in_executor(
        None, vanna_service.get_training_data
    )
    return {
        "status": result["status"],
        "data": {"items": result.get("data", []), "count": result.get("count", 0)},
        "message": result.get("error", f"{result.get('count', 0)} training items"),
    }
