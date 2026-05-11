"""FastAPI application entry point for the Lakehouse API."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from app.database import create_tables
from app.routers import monitoring, trino, dbt, pipelines, datasources, nifi, vanna


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup tasks before serving requests."""
    await create_tables()
    yield


app = FastAPI(
    title="Lakehouse API",
    version="0.1.0",
    description="Backend API for the Lakehouse platform.",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Prometheus metrics
# ---------------------------------------------------------------------------

Instrumentator().instrument(app).expose(app, endpoint="/api/metrics")

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(monitoring.router, prefix="/api")
app.include_router(trino.router, prefix="/api")
app.include_router(dbt.router, prefix="/api")
app.include_router(pipelines.router, prefix="/api")
app.include_router(datasources.router, prefix="/api")
app.include_router(nifi.router, prefix="/api")
app.include_router(vanna.router, prefix="/api")


# ---------------------------------------------------------------------------
# Root
# ---------------------------------------------------------------------------

@app.get("/", include_in_schema=False)
async def root():
    """Welcome message and API info."""
    return JSONResponse(
        content={
            "status": "success",
            "data": {"version": "0.1.0"},
            "message": "Lakehouse API is running. Visit /docs for the interactive API reference.",
        }
    )
