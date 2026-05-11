# Makefile
# Convenience targets for the lakehouse platform.
# Run `make help` to see all available targets.

.PHONY: up down logs ps trino-cli seed dbt-run dbt-test health init-iceberg clean help \
        backend-up backend-logs backend-shell test-backend \
        nifi-up nifi-logs nifi-upload-templates nifi-shell \
        frontend-up frontend-logs frontend-install dev

# ---------------------------------------------------------------------------
# Phase 1 — Core services
# ---------------------------------------------------------------------------

## up: Start Phase 1 services (minio, metastore-db, hive-metastore, trino)
up:
	docker compose up -d

## down: Stop all running services (keeps volumes)
down:
	docker compose down

## logs: Stream logs from all running services
logs:
	docker compose logs -f

## ps: Show status of all services
ps:
	docker compose ps

## trino-cli: Open an interactive Trino SQL shell
trino-cli:
	docker exec -it lakehouse-trino trino

## health: Run the Phase 1 health-check script
health:
	bash scripts/health-check.sh

## init-iceberg: Create sample Iceberg schemas and tables inside Trino
init-iceberg:
	docker compose exec trino trino --execute \
	  "CREATE SCHEMA IF NOT EXISTS iceberg.raw       WITH (location = 's3a://lakehouse-raw/warehouse/'); \
	   CREATE SCHEMA IF NOT EXISTS iceberg.staging   WITH (location = 's3a://lakehouse-staging/warehouse/'); \
	   CREATE SCHEMA IF NOT EXISTS iceberg.mart      WITH (location = 's3a://lakehouse-mart/warehouse/');"
	@echo "Schemas created. Run 'python scripts/init-iceberg.py' for full test data."

## clean: Stop all services AND remove all named volumes (destructive!)
clean:
	docker compose down -v

# ---------------------------------------------------------------------------
# Phase 2 — Backend / dbt (requires --profile phase2)
# ---------------------------------------------------------------------------

## backend-up: Start Phase 2 services (backend + all Phase 1 deps)
backend-up:
	docker compose --profile phase2 up -d

## backend-logs: Stream backend logs
backend-logs:
	docker compose logs -f backend

## backend-shell: Open a shell in the backend container
backend-shell:
	docker exec -it lakehouse-backend bash

## test-backend: Run backend unit tests
test-backend:
	docker compose run --rm backend pytest tests/ -v

## dbt-run: Run dbt models inside the backend container
dbt-run:
	docker compose run --rm backend dbt run

## dbt-test: Run dbt tests inside the backend container
dbt-test:
	docker compose run --rm backend dbt test

# ---------------------------------------------------------------------------
# Phase 3 — NiFi (requires --profile phase3)
# ---------------------------------------------------------------------------

## nifi-up: Start Phase 3 services (NiFi + all deps)
nifi-up:
	docker compose --profile phase3 up -d

## nifi-logs: Stream NiFi logs
nifi-logs:
	docker compose logs -f nifi

## nifi-upload-templates: Upload pre-built flow templates to NiFi
nifi-upload-templates:
	docker exec lakehouse-nifi bash /opt/nifi-templates/upload-templates.sh

## nifi-shell: Open a shell in the NiFi container
nifi-shell:
	docker exec -it lakehouse-nifi bash

# ---------------------------------------------------------------------------
# Phase 4 — Frontend UI (requires --profile phase4)
# ---------------------------------------------------------------------------

## frontend-up: Start Phase 4 services in Docker (frontend + backend + Phase 1)
frontend-up:
	docker compose --profile phase2 --profile phase4 up -d

## frontend-logs: Stream frontend logs
frontend-logs:
	docker compose logs -f frontend

## frontend-install: Install frontend npm dependencies locally
frontend-install:
	cd frontend && npm install

## dev: Start infrastructure in Docker + run frontend locally (recommended for dev)
dev:
	docker compose --profile phase2 up -d
	@echo "Waiting 5s for backend to initialize..."
	@sleep 5
	@echo "Starting Next.js dev server on http://localhost:3000 ..."
	cd frontend && npm run dev

# ---------------------------------------------------------------------------
# Phase 5 — Vanna AI seed (requires --profile phase5)
# ---------------------------------------------------------------------------

## seed: Seed Vanna AI with schema + sample questions (Phase 5)
seed:
	docker compose --profile phase5 up -d chromadb
	@echo "Waiting 10s for ChromaDB to be ready..."
	@sleep 10
	docker run --rm \
	  --network lakehouse_lakehouse-net \
	  -e CHROMADB_HOST=chromadb \
	  -e CHROMADB_PORT=8500 \
	  -v $(PWD)/scripts:/scripts:ro \
	  lakehouse-backend:latest \
	  python /scripts/seed-vanna.py

## vanna-up: Start Phase 5 services (ChromaDB + backend + all deps)
vanna-up:
	docker compose --profile phase2 --profile phase5 up -d

# ---------------------------------------------------------------------------
# Phase 6 — Monitoring: Prometheus + Grafana (requires --profile phase6)
# ---------------------------------------------------------------------------

## monitoring-up: Start Phase 6 monitoring services (Prometheus + Grafana)
monitoring-up:
	docker compose --profile phase2 --profile phase6 up -d

## monitoring-logs: Stream Prometheus and Grafana logs
monitoring-logs:
	docker compose logs -f prometheus grafana

## full-up: Start all services across all phases
full-up:
	docker compose --profile phase2 --profile phase3 --profile phase5 --profile phase6 up -d

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------

## help: List all available make targets with descriptions
help:
	@echo ""
	@echo "Lakehouse Makefile targets:"
	@echo ""
	@grep -E '^## ' Makefile | sed 's/^## /  /' | column -t -s ':'
	@echo ""
