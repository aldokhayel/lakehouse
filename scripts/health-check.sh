#!/bin/bash
# scripts/health-check.sh
# Verifies that all Phase 1 lakehouse services are reachable and healthy.
# Run via:  make health
#
# Exit codes:
#   0  — all services healthy
#   1  — one or more services failed

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'   # no colour

FAILED=0

# Check an HTTP endpoint
check_service() {
  local name="$1"
  local url="$2"
  if curl -sf "$url" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} $name is healthy"
    return 0
  else
    echo -e "${RED}✗${NC} $name is NOT healthy  (url: $url)"
    FAILED=$((FAILED + 1))
    return 1
  fi
}

# Check a raw TCP port
check_port() {
  local name="$1"
  local host="$2"
  local port="$3"
  if nc -z "$host" "$port" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} $name is reachable at $host:$port"
    return 0
  else
    echo -e "${RED}✗${NC} $name is NOT reachable at $host:$port"
    FAILED=$((FAILED + 1))
    return 1
  fi
}

echo "=== Lakehouse Phase 1 Health Check ==="
echo ""

check_service "MinIO API"       "http://localhost:9000/minio/health/live" || true
check_service "MinIO Console"   "http://localhost:9001"                   || true
check_port    "Hive Metastore"  "localhost" "9083"                        || true
check_service "Trino"           "http://localhost:8080/v1/info"           || true
check_port    "PostgreSQL (metastore-db)" "localhost" "5432"              || true

echo ""
if [ "$FAILED" -eq 0 ]; then
  echo -e "${GREEN}All Phase 1 services are healthy!${NC}"
  echo ""
  echo "Next steps:"
  echo "  make trino-cli                    # Open Trino SQL shell"
  echo "  make init-iceberg                 # Create Iceberg schemas"
  echo "  python scripts/init-iceberg.py   # Full init with test data"
else
  echo -e "${RED}${FAILED} service(s) failed health checks.${NC}"
  echo "Run 'make logs' to investigate."
  exit 1
fi
