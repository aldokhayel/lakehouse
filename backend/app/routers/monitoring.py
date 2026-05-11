"""Health-check and monitoring endpoints for all Lakehouse platform services."""

import os

import httpx
from fastapi import APIRouter

from app.services.minio_service import minio_service
from app.services.trino_service import trino_service
from app.services.vanna_service import vanna_service

router = APIRouter(tags=["monitoring"])


def _check_chromadb() -> str:
    host = os.environ.get("CHROMADB_HOST", "chromadb")
    try:
        with httpx.Client(timeout=3) as client:
            r = client.get(f"http://{host}:8000/api/v2/heartbeat")
            return "ok" if r.status_code == 200 else "error"
    except Exception:
        return "error"


@router.get("/health")
async def health():
    """Return the health status of all platform services."""
    checks = {
        "backend": "ok",
        "trino": "ok" if trino_service.is_healthy() else "error",
        "minio": "ok" if minio_service.is_healthy() else "error",
        "chromadb": _check_chromadb(),
        "vanna": "ok" if vanna_service.status()["ready"] else "degraded",
    }
    all_ok = all(v in ("ok", "degraded") for v in checks.values())
    return {
        "status": "success" if all(v == "ok" for v in checks.values()) else "degraded",
        "data": {"services": checks},
        "message": "All services healthy" if all(v == "ok" for v in checks.values()) else "Some services degraded",
    }
