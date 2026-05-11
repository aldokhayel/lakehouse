#!/bin/bash
# infrastructure/minio/init-buckets.sh
# One-shot script executed by the minio-init container (minio/mc image).
# Creates the three lakehouse storage buckets if they don't already exist.
# Called automatically at startup via the minio-init service in docker-compose.yml.

set -e

echo "Configuring MinIO client alias..."
mc alias set local http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD"

echo "Creating lakehouse buckets (idempotent)..."
mc mb --ignore-existing local/lakehouse-raw
mc mb --ignore-existing local/lakehouse-staging
mc mb --ignore-existing local/lakehouse-mart

echo "Buckets initialized: lakehouse-raw, lakehouse-staging, lakehouse-mart"
