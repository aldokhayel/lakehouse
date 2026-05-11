# CLAUDE.md — Lakehouse Platform

## What is this?
A self-hosted lakehouse platform with a drag-and-drop UI. Users connect data sources, build pipelines visually, transform data with dbt, and query using plain English (Vanna.ai text-to-SQL). Everything runs in Docker Compose.

## Stack
- **Frontend:** Next.js 14+ (App Router, TypeScript, Tailwind, Zustand, React Flow, Recharts)
- **Backend:** Python 3.11+ FastAPI (async, Pydantic v2, SQLite)
- **ETL/ELT:** Apache NiFi (embedded iframe + REST API)
- **Query Engine:** Trino with Apache Iceberg tables on MinIO (S3-compatible)
- **Catalog:** Hive Metastore (backed by PostgreSQL)
- **Text-to-SQL:** Vanna.ai (v2.0) with ChromaDB vector store
- **LLM Provider:** OpenRouter (OpenAI-compatible API, model-agnostic)
- **Transforms:** dbt Core CLI (raw → staging → mart)
- **Monitoring:** Grafana + Prometheus
- **Auth:** None (MVP)
- **Deployment:** Docker Compose (local machine only)

## Repo layout
- `frontend/` — Next.js app
- `backend/` — FastAPI app
- `dbt_project/` — dbt models and config
- `infrastructure/` — Docker configs, Trino catalogs, NiFi templates, Grafana dashboards
- `scripts/` — Seed and init scripts
- `docker-compose.yml` — Full stack

## Commands
```bash
make up              # Start all services
make down            # Stop all services
make logs            # Tail all logs
make seed            # Seed Vanna.ai with schema data
make dbt-run         # Run dbt models
make trino-cli       # Open Trino CLI
```

## Environment
- Copy `.env.example` to `.env` and set `OPENROUTER_API_KEY`
- All services run locally via Docker Compose — no cloud dependency
- Typical resource needs: 16GB+ RAM recommended (Trino + NiFi are memory-hungry)

## Key conventions
- Data layers: `raw` → `staging` → `mart` (dbt-style)
- All API responses: `{ "status": "success|error", "data": {...}, "message": "..." }`
- TypeScript strict mode in frontend
- Python type hints everywhere in backend
- Every file has a top comment explaining its purpose
- Environment variables for all service URLs/ports (see `.env.example`)
- No magic numbers — use constants

## Testing
- Backend: `pytest` with async test client
- Frontend: Vitest + React Testing Library
- dbt: `dbt test` for data quality

## The full prompt
See `lakehouse-prompt.md` for the complete architecture doc, module specs, and implementation phases.
