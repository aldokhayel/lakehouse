# Lakehouse

A self-hosted, open-source data lakehouse platform with a drag-and-drop visual interface. Connect data sources, build ETL pipelines, run SQL transformations, query with plain English, and monitor everything — all from a single browser tab.

> **100% local.** Runs entirely on your machine via Docker Compose. No cloud dependency, no SaaS subscriptions.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Browser (Next.js 14)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────────┐   │
│  │  Pipeline    │  │  NiFi iframe │  │  AI Chat (Vanna.ai)     │   │
│  │  Canvas      │  │  (ETL/ELT)   │  │  Text → SQL → Results   │   │
│  │  (React Flow)│  │              │  │  (Bar / Line / Pie)     │   │
│  └──────┬───────┘  └──────────────┘  └────────────┬────────────┘   │
└─────────┼────────────────────────────────────────────┼──────────────┘
          │                                            │
┌─────────┼────────────────────────────────────────────┼──────────────┐
│         │         FastAPI Backend                    │              │
│  ┌──────▼──────┐ ┌──────────────┐ ┌─────────────────▼──────────┐   │
│  │ NiFi API   │ │ Trino Gateway │ │ Vanna.ai + ChromaDB        │   │
│  │ Orchestrator│ │ dbt Runner   │ │ (NL → SQL via OpenRouter)  │   │
│  └─────────────┘ └──────┬───────┘ └────────────────────────────┘   │
└─────────────────────────┼──────────────────────────────────────────┘
                          │
┌─────────────────────────▼──────────────────────────────────────────┐
│                   Data Infrastructure                               │
│   Trino ←→ Hive Metastore ←→ Apache Iceberg ←→ MinIO (S3)         │
│   PostgreSQL (catalog)         NiFi (ETL)     Grafana + Prometheus  │
└─────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
External Sources         Raw Layer          Staging Layer       Mart Layer
(API / MSSQL /    ──►   MinIO / Iceberg ──► dbt transforms ──► Business tables
 PostgreSQL /            (lakehouse-raw)    (lakehouse-staging)  (lakehouse-mart)
 MongoDB)
     ▲
  Apache NiFi
  (drag & drop ETL)
```

---

## Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | Next.js 14, TypeScript, Tailwind, React Flow, Recharts, Zustand | Visual pipeline builder + AI chat UI |
| **Backend** | FastAPI, Python 3.12, SQLAlchemy, SQLite | REST API, orchestration |
| **Query Engine** | Trino 435 | Distributed SQL over Iceberg tables |
| **Table Format** | Apache Iceberg | ACID-compliant lakehouse tables |
| **Object Storage** | MinIO | S3-compatible local storage |
| **Metastore** | Hive Metastore 4.0 + PostgreSQL | Iceberg catalog |
| **ETL** | Apache NiFi 2.x | Visual data ingestion pipelines |
| **Transformations** | dbt Core + dbt-trino | SQL models (raw → staging → mart) |
| **Text-to-SQL** | Vanna.ai 0.7 + ChromaDB + OpenRouter | Natural language → SQL |
| **Monitoring** | Prometheus + Grafana | Metrics, dashboards, alerting |
| **Deployment** | Docker Compose | Single-machine local deployment |

---

## Prerequisites

| Requirement | Version |
|---|---|
| Docker Desktop | 24+ |
| Docker Compose | v2 (bundled with Docker Desktop) |
| RAM | 8 GB minimum, **16 GB recommended** (Trino + NiFi are memory-hungry) |
| Disk | ~10 GB free (Docker images + data volumes) |

Optional (for local frontend development):

- Node.js 20+
- npm 10+

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/aldokhayel/lakehouse.git
cd lakehouse

# 2. Configure environment
cp .env.example .env
# Edit .env and set OPENROUTER_API_KEY for AI chat features

# 3. Start core infrastructure (Phase 1)
make up

# 4. Start the full stack with backend + AI + monitoring
make full-up

# 5. Install frontend dependencies and start the dev server
make frontend-install
make dev
```

### Service URLs

| Service | URL | Credentials |
|---|---|---|
| **Frontend (local dev)** | http://localhost:3001 | — |
| **Frontend (Docker)** | http://localhost:3000 | — |
| **Backend API** | http://localhost:8000 | — |
| **API Docs (Swagger)** | http://localhost:8000/docs | — |
| **Trino UI** | http://localhost:8080 | — |
| **MinIO Console** | http://localhost:9001 | minioadmin / minioadmin |
| **NiFi** | https://localhost:8443 | admin / adminadminadmin |
| **Grafana** | http://localhost:3002 | admin / admin |
| **Prometheus** | http://localhost:9090 | — |
| **ChromaDB** | http://localhost:8500 | — |

---

## Features

### Visual Pipeline Builder
Drag source nodes (API, MSSQL, PostgreSQL, MongoDB) onto the React Flow canvas, connect them to NiFi Flow and dbt Model nodes, and wire up to Iceberg Table destinations. Click **Run Pipeline** to trigger ingestion.

### AI-Powered SQL Chat
Type a question in plain English in the Chat panel:

> *"Show total revenue by month"*
> *"Top 10 customers by order count"*
> *"Average order value in the last 90 days"*

Vanna.ai generates SQL, shows it for confirmation (editable inline), executes it against Trino, and renders results as a table or interactive chart (bar, line, pie).

### NiFi ETL Integration
The NiFi UI is embedded as an iframe inside the workspace. Use the NiFi Controls panel to start/stop flows and monitor throughput without leaving the app.

### dbt Transformations
Run dbt models directly from the UI or via `make dbt-run`. Data flows through three Iceberg layers:
- `raw` — raw ingested records
- `staging` — cleaned and enriched
- `mart` — business-ready aggregates

### Live Observability
The status bar shows real-time health dots for all services (API, Trino, MinIO, VectorDB, AI). Click **📊 Metrics** to open the pre-built Grafana dashboard showing request rates, latency percentiles, and error rates.

---

## Project Structure

```
lakehouse/
├── frontend/                    # Next.js 14 application
│   └── src/
│       ├── app/                 # App Router pages and layouts
│       ├── components/
│       │   ├── canvas/          # WorkspaceCanvas (root layout)
│       │   ├── chat/            # ChatPanel, SQL block, results table/charts
│       │   ├── nifi/            # NiFi iframe embed and controls
│       │   ├── pipeline/        # React Flow editor, node types, config panel
│       │   └── shared/          # StatusBar, Toast
│       ├── hooks/               # useVannaChat, useServiceHealth, useNiFi, ...
│       ├── lib/                 # api.ts (all fetch calls), constants.ts
│       ├── stores/              # Zustand stores (workspace, pipeline, chat)
│       └── types/               # TypeScript types
│
├── backend/                     # FastAPI application
│   └── app/
│       ├── routers/             # pipelines, trino, dbt, nifi, vanna, monitoring
│       ├── services/            # trino_service, minio_service, vanna_service, ...
│       ├── models/              # SQLAlchemy ORM (pipeline, datasource, chat)
│       └── schemas/             # Pydantic request/response models
│
├── dbt_project/                 # dbt Core project
│   ├── models/
│   │   ├── staging/             # Cleaned models (stg_orders, ...)
│   │   └── mart/                # Business models (orders, customer_summary, ...)
│   └── profiles.yml             # Trino connection config
│
├── infrastructure/
│   ├── trino/                   # Dockerfile + Iceberg/PostgreSQL catalog configs
│   ├── hive-metastore/          # Dockerfile + entrypoint + metastore-site.xml
│   ├── minio/                   # Dockerfile + bucket init script
│   ├── nifi/                    # NiFi templates and config
│   ├── prometheus/              # prometheus.yml scrape config
│   └── grafana/
│       ├── provisioning/        # Auto-provisioned datasource + dashboard loader
│       └── dashboards/          # lakehouse-overview.json (pre-built dashboard)
│
├── scripts/
│   ├── init-iceberg.py          # Create raw/staging/mart schemas in Trino
│   ├── health-check.sh          # Check all Phase 1 services
│   └── seed-vanna.py            # Train Vanna.ai on schema DDL + sample Q/A pairs
│
├── docker-compose.yml           # Full stack (profiles gate phases 2–6)
├── Makefile                     # Convenience targets
└── .env.example                 # Environment variable template
```

---

## Configuration

Copy `.env.example` to `.env` and edit as needed:

```bash
cp .env.example .env
```

Key variables:

| Variable | Default | Description |
|---|---|---|
| `OPENROUTER_API_KEY` | *(required for AI chat)* | Get a free key at [openrouter.ai](https://openrouter.ai) |
| `OPENROUTER_MODEL` | `anthropic/claude-sonnet-4-20250514` | Any model on OpenRouter |
| `MINIO_ROOT_USER` | `minioadmin` | MinIO admin username |
| `MINIO_ROOT_PASSWORD` | `minioadmin` | MinIO admin password |
| `GRAFANA_PASSWORD` | `admin` | Grafana admin password |

All other values have sensible defaults for local development.

---

## Make Targets

```bash
# Phase 1 — Core infrastructure
make up               # Start MinIO, Hive Metastore, Trino, PostgreSQL
make down             # Stop all services (keeps data volumes)
make clean            # Stop all services AND delete all data volumes
make health           # Run the health-check script
make init-iceberg     # Create raw/staging/mart schemas in Trino
make trino-cli        # Open an interactive Trino SQL shell

# Phase 2 — Backend API
make backend-up       # Start backend + Phase 1 deps
make backend-logs     # Stream backend logs
make test-backend     # Run pytest suite

# Phase 3 — NiFi
make nifi-up          # Start NiFi + all deps
make nifi-logs        # Stream NiFi logs

# Phase 4 — Frontend
make dev              # Recommended: infra in Docker + Next.js locally
make frontend-up      # Run frontend in Docker too
make frontend-install # Install npm dependencies locally

# Phase 5 — AI Chat
make vanna-up         # Start ChromaDB + backend + all deps
make seed             # Seed Vanna.ai with schema DDL + sample Q/A pairs

# Phase 6 — Monitoring
make monitoring-up    # Start Prometheus + Grafana
make monitoring-logs  # Stream Prometheus + Grafana logs

# All phases
make full-up          # Start everything (phases 2, 3, 5, 6)

# dbt
make dbt-run          # Run all dbt models
make dbt-test         # Run dbt data quality tests
```

---

## Development Guide

### Running the Frontend Locally (Recommended)

The fastest dev loop keeps infrastructure in Docker and runs Next.js on the host:

```bash
make dev
```

This starts all backend services in Docker, waits for them to initialize, then launches `next dev` on http://localhost:3001 with hot-reload.

### AI Chat Setup

1. Add your OpenRouter API key to `.env`:
   ```
   OPENROUTER_API_KEY=sk-or-...
   ```

2. Start ChromaDB and the backend:
   ```bash
   make vanna-up
   ```

3. Seed Vanna with your schema:
   ```bash
   make seed
   ```

4. Open the **Chat** tab in the right panel and start asking questions.

The seed script trains Vanna on:
- Iceberg table DDL (raw, staging, mart layers)
- Data layer documentation
- 12 sample question/SQL pairs for the orders domain

### Initializing Sample Data

```bash
# Create the three Iceberg schemas
make init-iceberg

# Load sample orders data (raw → staging → mart via Trino)
python scripts/init-iceberg.py

# Run dbt transformations
make dbt-run
```

### Monitoring

After `make monitoring-up`, open:
- **Grafana**: http://localhost:3002 (admin / admin)
  - The *Lakehouse Overview* dashboard loads automatically
- **Prometheus**: http://localhost:9090

The **📊 Metrics** link in the status bar opens Grafana directly.

---

## API Reference

The FastAPI backend auto-generates interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Key endpoint groups:

| Prefix | Description |
|---|---|
| `GET /api/health` | Service health for all platform components |
| `POST /api/trino/query` | Execute SQL against Trino |
| `GET /api/trino/catalogs` | List available Trino catalogs |
| `POST /api/vanna/ask` | Generate SQL from a natural-language question |
| `POST /api/vanna/execute` | Execute a SQL query and return rows + columns |
| `POST /api/vanna/auto-train` | Train Vanna on Trino's information_schema |
| `GET /api/vanna/history` | Chat history (stored in SQLite) |
| `POST /api/pipelines` | Create a pipeline |
| `POST /api/pipelines/{id}/run` | Trigger a pipeline run |
| `GET /api/nifi/status` | NiFi connectivity status |
| `POST /api/dbt/run` | Run dbt models |
| `GET /api/metrics` | Prometheus metrics endpoint |

All responses follow the envelope format:

```json
{
  "status": "success | error | degraded",
  "data": { ... },
  "message": "Human-readable description"
}
```

---

## Architecture Decisions

**Why Trino + Iceberg instead of a traditional data warehouse?**
Trino separates compute from storage — MinIO holds the Parquet files, Iceberg manages schema evolution and ACID guarantees, and Trino executes distributed queries. This means you can scale storage and compute independently, and swap query engines without rewriting pipelines.

**Why Vanna.ai for text-to-SQL?**
Vanna uses a retrieval-augmented approach: it stores DDL and sample Q/A pairs in ChromaDB (a vector store), retrieves the most relevant context for each question, and sends it to an LLM (via OpenRouter) to generate accurate SQL. The two-step flow (generate → confirm → execute) prevents accidental destructive queries.

**Why Docker Compose profiles?**
Phase 1 (Trino, MinIO, Metastore) starts by default. Phases 2–6 are gated behind profiles (`phase2`, `phase3`, etc.) so `make up` is fast and only launches what you need. `make full-up` brings everything online.

---

## Troubleshooting

**Trino fails to start**
Check `docker compose logs trino`. Trino needs ~2 GB of heap — ensure Docker Desktop has at least 6 GB of memory assigned (Settings → Resources).

**Hive Metastore is unhealthy**
PostgreSQL must be healthy before the metastore runs `schematool -initSchema`. The entrypoint waits using `nc` (netcat). Check `docker compose logs hive-metastore`.

**AI Chat returns "ChromaDB is not running"**
Start ChromaDB with `make vanna-up`, wait for it to be healthy, then retry. Check health with:
```bash
docker inspect lakehouse-chromadb --format='{{.State.Health.Status}}'
```

**Vanna generates incorrect SQL**
Run `make seed` to load domain-specific training data, or click **Auto-train** in the Chat panel to train on your actual Trino schema. Adding more question/SQL pairs to `scripts/seed-vanna.py` improves accuracy significantly.

**MinIO metrics target is "down" in Prometheus**
MinIO's Prometheus endpoint requires bearer token authentication, which is not configured by default. For production use, generate a service account token from the MinIO Console under Identity → Service Accounts and add it to `infrastructure/prometheus/prometheus.yml`.

---

## Cost

| Item | Cost |
|---|---|
| All infrastructure (MinIO, Trino, NiFi, dbt, Grafana, etc.) | **$0** — open source |
| OpenRouter API (Vanna.ai LLM calls) | **~$0.001–$0.03 per query** — pay-per-use |
| Hosting | **$0** — runs on your local machine |

---

## License

MIT
