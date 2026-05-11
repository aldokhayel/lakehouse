# Lakehouse — Claude Code Master Prompt

## Project Identity

**Name:** Lakehouse
**Type:** Self-hosted, open-source lakehouse platform with a drag-and-drop visual interface
**Builder:** Solo developer — monorepo, clear module boundaries, comprehensive inline docs
**Deployment Target:** Local machine (Docker Compose) — no cloud dependency

---

## Vision

Build a unified lakehouse platform where a non-technical user can:

1. **Connect** to data sources (APIs, MSSQL, PostgreSQL, MongoDB) via drag-and-drop
2. **Ingest & Transform** data using Apache NiFi (ETL/ELT) and dbt Core (SQL transformations)
3. **Query** the lakehouse by typing plain English, which Vanna.ai converts to SQL
4. **Visualize** query results as interactive charts and tables
5. **Monitor** the entire platform via Grafana dashboards

All from a single full-canvas workspace — no context switching, no CLI required for end users.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────────┐ │
│  │  React Flow   │  │  NiFi iframe │  │  Vanna Chat + Results    │ │
│  │  Pipeline     │  │  (ETL/ELT)   │  │  (Text→SQL + Charts)    │ │
│  │  Canvas       │  │              │  │                          │ │
│  └──────┬───────┘  └──────────────┘  └───────────┬───────────────┘ │
│         │                                         │                 │
├─────────┴─────────────────────────────────────────┴─────────────────┤
│                     BACKEND (FastAPI)                                │
│  ┌────────────┐ ┌────────────┐ ┌──────────┐ ┌───────────────────┐  │
│  │ NiFi API   │ │ Trino      │ │ dbt Core │ │ Vanna.ai +        │  │
│  │ Orchestrator│ │ Gateway    │ │ Runner   │ │ ChromaDB          │  │
│  └─────┬──────┘ └─────┬──────┘ └────┬─────┘ └────────┬──────────┘  │
│        │              │             │                 │              │
├────────┴──────────────┴─────────────┴─────────────────┴──────────────┤
│                     DATA PLATFORM LAYER                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ Apache   │  │ Trino    │  │ Hive         │  │ MinIO          │  │
│  │ NiFi     │  │ Engine   │  │ Metastore    │  │ (S3-compat)    │  │
│  └──────────┘  └──────────┘  └──────────────┘  └────────────────┘  │
│                                                                      │
│  Storage Format: Apache Iceberg                                      │
│  Data Layers:   raw → staging → mart                                 │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│                     OBSERVABILITY                                    │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────────┐ │
│  │ Prometheus       │  │ Grafana          │  │ SQLite            │ │
│  │ (metrics)        │  │ (dashboards)     │  │ (platform meta)   │ │
│  └──────────────────┘  └──────────────────┘  └───────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack (Locked Decisions)

| Layer               | Technology                        | Notes                                      |
|---------------------|-----------------------------------|---------------------------------------------|
| Frontend            | Next.js (React)                   | App Router, TypeScript                      |
| Drag-and-drop       | React Flow                        | Node-based pipeline builder                 |
| UI workspace        | Full canvas                       | Pipelines + NiFi + SQL Chat in one view     |
| Backend API         | Python FastAPI                    | Async, orchestrates all services            |
| ETL/ELT engine      | Apache NiFi                       | Embedded in iframe within the UI            |
| Processing engine   | Trino                             | Distributed SQL query engine                |
| Transformation      | dbt Core (CLI)                    | Raw → Staging → Mart layer convention       |
| Table format        | Apache Iceberg                    | ACID transactions, time travel, schema evo  |
| Object storage      | MinIO                             | S3-compatible, self-hosted                  |
| Metadata catalog    | Hive Metastore                    | Backed by PostgreSQL or Derby               |
| Text-to-SQL         | Vanna.ai                          | Natural language → SQL (v2.0 Agent-based) |
| LLM Provider        | OpenRouter                        | OpenAI-compatible API, model-agnostic     |
| Vector store        | ChromaDB                          | For Vanna.ai schema embeddings              |
| Platform metadata   | SQLite                            | Pipeline configs, chat history, settings    |
| Monitoring          | Grafana + Prometheus              | Metrics, dashboards, alerting               |
| Auth                | None (MVP)                        | Add Keycloak or Azure AD later              |
| Deployment          | Docker Compose (local)            | Runs entirely on developer machine          |
| Data sources        | APIs, MSSQL, PostgreSQL, MongoDB  | NiFi connectors handle ingestion            |

---

## Monorepo Structure

```
lakehouse/
├── docker-compose.yml              # Full stack orchestration
├── .env.example                    # Environment variables template (includes OPENROUTER_API_KEY)
├── Makefile                        # Common commands (make up, make down, make seed)
│
├── frontend/                       # Next.js application
│   ├── package.json
│   ├── next.config.js
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── src/
│   │   ├── app/                    # Next.js App Router
│   │   │   ├── layout.tsx          # Root layout with sidebar
│   │   │   ├── page.tsx            # Main canvas workspace
│   │   │   └── api/               # Next.js API routes (BFF proxy)
│   │   ├── components/
│   │   │   ├── canvas/             # Full workspace canvas
│   │   │   │   ├── WorkspaceCanvas.tsx
│   │   │   │   ├── PanelManager.tsx
│   │   │   │   └── ResizablePanel.tsx
│   │   │   ├── pipeline/           # React Flow pipeline builder
│   │   │   │   ├── PipelineEditor.tsx
│   │   │   │   ├── nodes/          # Custom node types
│   │   │   │   │   ├── SourceNode.tsx       # API, MSSQL, PG, Mongo
│   │   │   │   │   ├── TransformNode.tsx    # dbt model reference
│   │   │   │   │   ├── DestinationNode.tsx  # Iceberg table target
│   │   │   │   │   └── NiFiFlowNode.tsx     # NiFi processor reference
│   │   │   │   ├── edges/
│   │   │   │   └── sidebar/
│   │   │   │       └── NodePalette.tsx      # Draggable node types
│   │   │   ├── nifi/               # NiFi integration panel
│   │   │   │   ├── NiFiEmbed.tsx            # iframe wrapper
│   │   │   │   └── NiFiControls.tsx         # Start/stop/status
│   │   │   ├── chat/               # Vanna.ai SQL chat
│   │   │   │   ├── ChatPanel.tsx
│   │   │   │   ├── MessageBubble.tsx
│   │   │   │   ├── SQLPreview.tsx           # Show generated SQL
│   │   │   │   └── ResultsView.tsx          # Charts + Tables
│   │   │   ├── visualization/      # Query result visualization
│   │   │   │   ├── ChartBuilder.tsx         # Chart type selector
│   │   │   │   ├── DataTable.tsx            # Sortable/filterable table
│   │   │   │   ├── charts/
│   │   │   │   │   ├── BarChart.tsx
│   │   │   │   │   ├── LineChart.tsx
│   │   │   │   │   ├── PieChart.tsx
│   │   │   │   │   └── ScatterPlot.tsx
│   │   │   │   └── ExportButton.tsx         # CSV/PNG export
│   │   │   └── shared/
│   │   │       ├── Sidebar.tsx
│   │   │       ├── StatusBar.tsx
│   │   │       └── Toast.tsx
│   │   ├── hooks/
│   │   │   ├── usePipeline.ts
│   │   │   ├── useNiFi.ts
│   │   │   ├── useVannaChat.ts
│   │   │   └── useTrinoQuery.ts
│   │   ├── stores/                 # Zustand state management
│   │   │   ├── pipelineStore.ts
│   │   │   ├── chatStore.ts
│   │   │   └── workspaceStore.ts
│   │   ├── lib/
│   │   │   ├── api.ts              # FastAPI client
│   │   │   └── constants.ts
│   │   └── types/
│   │       ├── pipeline.ts
│   │       ├── datasource.ts
│   │       └── chat.ts
│   └── public/
│
├── backend/                        # FastAPI application
│   ├── pyproject.toml
│   ├── Dockerfile
│   ├── app/
│   │   ├── main.py                 # FastAPI app entry
│   │   ├── config.py               # Settings (env-based)
│   │   ├── database.py             # SQLite connection
│   │   ├── routers/
│   │   │   ├── pipelines.py        # Pipeline CRUD
│   │   │   ├── datasources.py      # Connection management
│   │   │   ├── nifi.py             # NiFi API proxy
│   │   │   ├── trino.py            # Trino query execution
│   │   │   ├── dbt.py              # dbt run/test triggers
│   │   │   ├── vanna.py            # Text-to-SQL chat
│   │   │   └── monitoring.py       # Health checks, metrics
│   │   ├── services/
│   │   │   ├── nifi_service.py     # NiFi REST API client
│   │   │   ├── trino_service.py    # Trino query runner (PyTrino)
│   │   │   ├── dbt_service.py      # dbt CLI subprocess wrapper
│   │   │   ├── vanna_service.py    # Vanna.ai integration
│   │   │   ├── minio_service.py    # MinIO file operations
│   │   │   └── pipeline_service.py # Pipeline orchestration
│   │   ├── models/
│   │   │   ├── pipeline.py         # SQLAlchemy/SQLite models
│   │   │   ├── datasource.py
│   │   │   └── chat_history.py
│   │   └── schemas/
│   │       ├── pipeline.py         # Pydantic schemas
│   │       ├── datasource.py
│   │       └── chat.py
│   └── tests/
│
├── dbt_project/                    # dbt Core project
│   ├── dbt_project.yml
│   ├── profiles.yml                # Trino connection profile
│   ├── models/
│   │   ├── raw/                    # Source definitions
│   │   │   └── sources.yml
│   │   ├── staging/                # Cleaned, typed, deduplicated
│   │   │   ├── stg_*.sql
│   │   │   └── staging.yml
│   │   └── mart/                   # Business-ready aggregations
│   │       ├── mart_*.sql
│   │       └── mart.yml
│   ├── macros/
│   ├── seeds/
│   ├── snapshots/
│   └── tests/
│
├── infrastructure/                 # Docker & deployment configs
│   ├── trino/
│   │   ├── Dockerfile
│   │   ├── etc/
│   │   │   ├── config.properties
│   │   │   ├── jvm.config
│   │   │   ├── node.properties
│   │   │   └── catalog/
│   │   │       ├── iceberg.properties      # Iceberg + MinIO + Hive
│   │   │       ├── mssql.properties        # MSSQL connector
│   │   │       ├── postgresql.properties   # PostgreSQL connector
│   │   │       └── mongodb.properties      # MongoDB connector
│   │   └── health-check.sh
│   ├── nifi/
│   │   ├── Dockerfile
│   │   ├── conf/
│   │   │   ├── nifi.properties
│   │   │   └── bootstrap.conf
│   │   └── flow-templates/                 # Pre-built NiFi templates
│   │       ├── api-to-minio.xml
│   │       ├── mssql-to-minio.xml
│   │       ├── postgres-to-minio.xml
│   │       └── mongodb-to-minio.xml
│   ├── minio/
│   │   ├── Dockerfile
│   │   └── init-buckets.sh                 # Create raw/staging/mart buckets
│   ├── hive-metastore/
│   │   ├── Dockerfile
│   │   └── metastore-site.xml
│   ├── grafana/
│   │   ├── provisioning/
│   │   │   ├── dashboards/
│   │   │   │   └── lakehouse-overview.json
│   │   │   └── datasources/
│   │   │       └── prometheus.yml
│   │   └── dashboards/
│   │       ├── pipeline-health.json
│   │       ├── trino-queries.json
│   │       └── nifi-throughput.json
│   ├── prometheus/
│   │   └── prometheus.yml
│
├── scripts/
│   ├── seed-vanna.py               # Train Vanna.ai on schema + sample Q&A
│   ├── init-iceberg.py             # Create initial Iceberg tables
│   └── health-check.sh             # Verify all services are up
│
└── docs/
    ├── architecture.md
    ├── getting-started.md
    ├── data-flow.md
    └── deployment.md
```

---

## Module Specifications

### Module 1: Docker Compose Stack

Create `docker-compose.yml` that orchestrates all services:

```yaml
services:
  # --- Storage Layer ---
  minio:            # MinIO S3-compatible storage (ports: 9000, 9001)
  hive-metastore:   # Hive Metastore for Iceberg catalog (port: 9083)

  # --- Processing Layer ---
  trino:            # Trino query engine (port: 8080)
  nifi:             # Apache NiFi (port: 8443 HTTPS)

  # --- Application Layer ---
  backend:          # FastAPI (port: 8000)
  frontend:         # Next.js (port: 3000)

  # --- AI Layer ---
  chromadb:         # ChromaDB for Vanna.ai embeddings (port: 8500)

  # --- Observability ---
  prometheus:       # Metrics collection (port: 9090)
  grafana:          # Dashboards (port: 3001)

  # --- Supporting ---
  metastore-db:     # PostgreSQL for Hive Metastore (port: 5432)
```

**Key requirements:**
- All services on a shared `lakehouse-net` Docker network
- MinIO buckets auto-created on startup: `lakehouse-raw`, `lakehouse-staging`, `lakehouse-mart`
- Trino catalogs pre-configured for Iceberg (MinIO + Hive), MSSQL, PostgreSQL, MongoDB
- NiFi configured with CORS headers allowing iframe embedding from `localhost:3000`
- Health checks on every service
- Named volumes for data persistence
- `.env.example` with all configurable values including `OPENROUTER_API_KEY`

### Module 2: Frontend — Next.js Workspace Canvas

**Design direction:** Dark-themed data platform aesthetic. Think: professional IDE meets data tool. Use a monospace accent font for data/code elements, a clean sans-serif for UI. Color palette anchored in deep navy/charcoal with electric blue and emerald green accents for active states and data flow lines.

**Workspace layout (single page, resizable panels):**

```
┌─────────┬────────────────────────────────┬──────────────────┐
│         │                                │                  │
│  Node   │     React Flow Canvas          │   Right Panel    │
│ Palette │     (Pipeline Builder)         │   (contextual)   │
│         │                                │                  │
│  - API  │   [Source] ──► [Transform]     │   • Node config  │
│  - MSSQL│        └──► [Destination]      │   • NiFi embed   │
│  - PG   │                                │   • Chat panel   │
│  - Mongo│                                │   • Results view │
│  - dbt  │                                │                  │
│         ├────────────────────────────────┤│                  │
│         │  Status Bar (pipeline runs,    ││                  │
│         │  NiFi status, Trino queries)   ││                  │
└─────────┴────────────────────────────────┴┘──────────────────┘
```

**React Flow custom nodes:**

| Node Type       | Drag From Palette | Config Panel Shows                    |
|-----------------|-------------------|---------------------------------------|
| API Source      | "API"             | URL, method, headers, auth, schedule  |
| MSSQL Source    | "MSSQL"           | Host, port, database, table/query     |
| PostgreSQL Src  | "PostgreSQL"      | Host, port, database, table/query     |
| MongoDB Source  | "MongoDB"         | URI, database, collection, filter     |
| NiFi Processor  | "NiFi Flow"       | Opens NiFi iframe panel               |
| dbt Transform   | "dbt Model"       | Model name, run/test buttons          |
| Iceberg Dest    | "Iceberg Table"   | Schema, table name, layer (raw/stg/mart) |

**Key frontend behaviors:**
- Drag a node from the palette → drops on canvas → opens config in right panel
- Connect nodes with edges → defines data flow → saves pipeline definition to backend
- "Run Pipeline" button triggers: NiFi flow start → wait for completion → dbt run → notify
- Right panel switches context: node config / NiFi iframe / Chat / Query Results
- Chat panel is always accessible via a tab in the right panel
- Query results render below the chat as sortable tables or selectable chart types (bar, line, pie, scatter)
- Use Zustand for state management (pipeline state, chat history, workspace layout)
- Use React Query (TanStack Query) for server state
- Recharts for data visualization

**NiFi iframe integration:**
- NiFi runs on port 8443 (HTTPS)
- Embed via `<iframe src="https://localhost:8443/nifi" />` in a resizable right panel
- The backend proxies NiFi API calls for CORS safety
- Show NiFi flow status (running/stopped/error) in the status bar

### Module 3: Backend — FastAPI

**API endpoints:**

```
# Data Sources
POST   /api/datasources              # Register a new data source
GET    /api/datasources              # List all sources
POST   /api/datasources/{id}/test    # Test connectivity
DELETE /api/datasources/{id}         # Remove source

# Pipelines
POST   /api/pipelines                # Save pipeline definition (React Flow JSON)
GET    /api/pipelines                # List all pipelines
GET    /api/pipelines/{id}           # Get pipeline detail
PUT    /api/pipelines/{id}           # Update pipeline
POST   /api/pipelines/{id}/run       # Execute pipeline (trigger NiFi + dbt)
GET    /api/pipelines/{id}/status    # Get execution status
DELETE /api/pipelines/{id}           # Delete pipeline

# NiFi Proxy
GET    /api/nifi/status              # NiFi cluster status
POST   /api/nifi/flows               # Deploy a flow definition
POST   /api/nifi/flows/{id}/start    # Start a flow
POST   /api/nifi/flows/{id}/stop     # Stop a flow
GET    /api/nifi/flows/{id}/status   # Flow execution status

# Trino
POST   /api/trino/query              # Execute SQL against Trino
GET    /api/trino/catalogs           # List available catalogs
GET    /api/trino/schemas/{catalog}  # List schemas in catalog
GET    /api/trino/tables/{catalog}/{schema}  # List tables

# dbt
POST   /api/dbt/run                  # Run dbt models
POST   /api/dbt/test                 # Run dbt tests
GET    /api/dbt/models               # List dbt models
GET    /api/dbt/run-results          # Last run results

# Vanna.ai Chat
POST   /api/chat/ask                 # Natural language → SQL → results
GET    /api/chat/history             # Chat history
POST   /api/chat/train               # Add training data (question-SQL pairs)
GET    /api/chat/training-data       # View training data

# Monitoring
GET    /api/health                   # Platform health check
GET    /api/metrics                  # Prometheus-format metrics
```

**Key backend behaviors:**
- NiFi service uses `nipyapi` or raw REST calls to manage flows
- Trino service uses `trino` Python client (PyTrino)
- dbt service runs `dbt run`, `dbt test` as subprocesses, captures output
- Vanna service initializes with ChromaDB, trains on Iceberg schema metadata
- SQLite stores: pipeline definitions, datasource configs, chat history, run logs
- All endpoints return consistent JSON: `{ "status": "success|error", "data": {...}, "message": "..." }`
- Use Pydantic v2 for all request/response schemas
- Async where possible (especially Trino queries and NiFi polling)

### Module 4: dbt Project

**Profile (`profiles.yml`):**
```yaml
lakehouse:
  target: dev
  outputs:
    dev:
      type: trino
      method: none  # No auth for MVP
      host: trino
      port: 8080
      user: dbt
      database: iceberg
      schema: staging
      catalog: iceberg
```

**Layer convention:**

| Layer    | Schema          | Purpose                              | Example Model            |
|----------|-----------------|--------------------------------------|--------------------------|
| Raw      | `raw`           | Untouched ingested data              | (NiFi lands data here)   |
| Staging  | `staging`       | Cleaned, typed, deduplicated, tested | `stg_orders.sql`         |
| Mart     | `mart`          | Business-ready, aggregated           | `mart_daily_revenue.sql` |

**dbt must:**
- Use `ref()` and `source()` properly
- Include schema tests (unique, not_null, accepted_values)
- Include at least one example model per layer as a template
- Generate docs (`dbt docs generate`) that the backend can serve

### Module 5: Vanna.ai + ChromaDB + OpenRouter Integration

**Initialization flow:**
1. On startup, FastAPI connects to ChromaDB
2. Vanna.ai is initialized with ChromaDB as the vector store and OpenRouter as the LLM
3. Backend auto-trains Vanna on:
   - Trino catalog metadata (schemas, tables, columns, types)
   - dbt model documentation and descriptions
   - Sample question-SQL pairs from a seed file (`scripts/seed-vanna.py`)

**Chat flow:**
1. User types: "Show me total revenue by month"
2. Backend calls `vanna.generate_sql("Show me total revenue by month")` (LLM call goes to OpenRouter)
3. Vanna returns SQL: `SELECT date_trunc('month', order_date) AS month, SUM(revenue) FROM mart.orders GROUP BY 1`
4. Backend shows generated SQL to user for confirmation (editable)
5. User confirms → backend executes SQL via Trino
6. Results returned as JSON → frontend renders as table + chart
7. Chat history saved to SQLite

### Module 6: Monitoring (Grafana + Prometheus)

**Pre-built dashboards:**
1. **Lakehouse Overview** — service health, uptime, request rates
2. **Pipeline Health** — NiFi flow status, throughput, errors, row counts
3. **Trino Queries** — query duration, active queries, failed queries
4. **NiFi Throughput** — bytes in/out, flowfile counts, backpressure

**Prometheus targets:**
- FastAPI (`/api/metrics` via `prometheus-fastapi-instrumentator`)
- Trino (JMX exporter)
- NiFi (reporting task or JMX)
- MinIO (built-in Prometheus endpoint)

---

## Implementation Order

Build and verify in this sequence. Each phase should be fully functional before proceeding.

### Phase 1: Infrastructure Foundation
1. `docker-compose.yml` with MinIO, Hive Metastore, Trino, metastore-db
2. Verify: Trino can query Iceberg tables on MinIO via Hive Metastore
3. Create initial buckets (`lakehouse-raw`, `lakehouse-staging`, `lakehouse-mart`)
4. Create a sample Iceberg table with test data via Trino CLI

### Phase 2: Backend Core
5. FastAPI skeleton with health check, config, SQLite setup
6. Trino service + query endpoint (execute SQL, return JSON results)
7. dbt project with profiles.yml targeting Trino, one example model per layer
8. dbt service (run/test via subprocess, return results)

### Phase 3: NiFi Integration
9. Add NiFi to Docker Compose with iframe-friendly CORS config
10. NiFi service (flow deployment, start/stop, status via REST API)
11. Pre-built NiFi flow templates for each source type (API, MSSQL, PG, Mongo)

### Phase 4: Frontend MVP
12. Next.js project with Tailwind, Zustand, React Query
13. Workspace canvas layout (resizable panels)
14. React Flow pipeline editor with custom nodes and node palette
15. Node configuration panel (forms for each source type)
16. NiFi iframe panel
17. Pipeline CRUD (save/load/run)

### Phase 5: AI Chat Layer
18. ChromaDB added to Docker Compose
19. Vanna.ai service with ChromaDB backend
20. Schema auto-training on Trino metadata
21. Chat panel in frontend (message bubbles, SQL preview, edit, confirm)
22. Query result visualization (DataTable + chart selector with Recharts)

### Phase 6: Observability
23. Prometheus + Grafana added to Docker Compose
24. FastAPI metrics instrumentation
25. Pre-built Grafana dashboards (provisioned via JSON)
26. Status bar in frontend showing live pipeline/query status

---

## Coding Standards

- **TypeScript** everywhere in frontend (strict mode)
- **Python 3.11+** with type hints everywhere in backend
- **Pydantic v2** for all API schemas
- **Async FastAPI** endpoints where I/O bound
- **ESLint + Prettier** for frontend
- **Ruff** for Python linting
- **Every file** starts with a docstring or comment explaining its purpose
- **No magic numbers** — use constants or config
- **Error handling** — try/catch with meaningful error messages, never swallow errors
- **Environment variables** for all external service URLs, ports, credentials
- Docker Compose `.env.example` fully documented with `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, and all service URLs/ports

---

## Key Integration Details

### Trino Catalog Configuration (iceberg.properties)
```properties
connector.name=iceberg
iceberg.catalog.type=hive_metastore
hive.metastore.uri=thrift://hive-metastore:9083
hive.s3.endpoint=http://minio:9000
hive.s3.aws-access-key=minioadmin
hive.s3.aws-secret-key=minioadmin
hive.s3.path-style-access=true
iceberg.file-format=PARQUET
```

### NiFi CORS for iframe embedding
NiFi must be configured to allow framing from the frontend origin. Set in `nifi.properties`:
```properties
nifi.web.proxy.host=localhost:3000
nifi.web.proxy.context.path=/
```
And configure appropriate CORS headers via a reverse proxy (nginx or Traefik) if needed.

### Vanna.ai setup (with OpenRouter)
```python
from openai import OpenAI
from vanna.chromadb import ChromaDB_VectorStore
from vanna.openai.openai_chat import OpenAI_Chat
import trino
import pandas as pd

# OpenRouter exposes an OpenAI-compatible API
openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

class LakehouseVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, client=openrouter_client, config=config)

    def run_sql(self, sql: str):
        conn = trino.dbapi.connect(host="trino", port=8080, user="vanna", catalog="iceberg")
        cursor = conn.cursor()
        cursor.execute(sql)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        return pd.DataFrame(rows, columns=columns)

# Initialize with your preferred model via OpenRouter
vn = LakehouseVanna(config={
    "model": "anthropic/claude-sonnet-4-20250514",  # or any model on OpenRouter
    "chromadb_path": "/data/chromadb",
})
```

**Supported OpenRouter models (pick any):**
- `anthropic/claude-sonnet-4-20250514` — strong for SQL generation
- `google/gemini-2.5-flash` — fast and cheap
- `deepseek/deepseek-chat-v3` — excellent value
- `meta-llama/llama-4-maverick` — open source option

Set `OPENROUTER_API_KEY` in `.env`. Typical cost is $0.001–0.03 per query depending on model.

---

## What NOT to Build (MVP Scope Control)

- No authentication or RBAC (add later)
- No multi-tenancy
- No data lineage visualization (future feature)
- No auto-generated dbt models (future feature)
- No real-time streaming (NiFi handles batch only for now)
- No mobile-responsive layout (desktop-first)
- No CI/CD pipeline (manual deploy for now)
- No cloud deployment (Docker Compose on local machine only for now)

---

## Development Methodology

Use **GSD** (Get Shit Done) and **Superpowers** as Claude Code plugins during development:

- **Superpowers** handles the quality of each coding task (brainstorm → plan → TDD → review)
- **GSD** manages multi-phase execution and prevents context rot across the 6-phase build

**Setup before starting:**
```bash
# Install Superpowers plugin
claude
> /install-plugin superpowers

# Install GSD
npx get-shit-done-cc@latest
```

---

## Cost Summary

| Item | Cost |
|------|------|
| All infrastructure (MinIO, Trino, NiFi, dbt, Grafana, etc.) | **$0** — all open source |
| OpenRouter (Vanna.ai LLM) | **~$0.001–0.03 per query** — pay-per-use |
| Claude Code subscription | **Your existing subscription** |
| Hosting | **$0** — runs on local machine |

---

## Success Criteria

The MVP is complete when:
1. A user can drag source and destination nodes onto the canvas and connect them
2. Clicking "Run Pipeline" triggers NiFi ingestion → data lands in MinIO (raw layer)
3. dbt transforms data from raw → staging → mart
4. User types English in the chat panel → Vanna generates SQL → Trino executes → results appear as a table
5. User can switch the result view to a bar/line/pie chart
6. NiFi UI is accessible via iframe in the workspace
7. Grafana dashboards show pipeline health and query metrics
8. The full stack starts with `docker-compose up`
