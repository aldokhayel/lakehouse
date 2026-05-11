#!/bin/bash
# infrastructure/hive-metastore/entrypoint.sh
# Container entrypoint for the Hive Metastore service.
# Steps:
#   1. Substitute environment variables into the config template.
#   2. Wait for PostgreSQL to accept connections (using nc, since pg_isready
#      is not available in the apache/hive base image).
#   3. Run schematool to initialise the metastore schema if it doesn't exist.
#   4. Start the Hive Metastore thrift service.

set -e

echo "Substituting environment variables in metastore config..."
envsubst < /opt/hive/conf/metastore-site.xml.template > /opt/hive/conf/hive-site.xml

echo "Waiting for PostgreSQL at ${HIVE_METASTORE_DB_HOST}:${HIVE_METASTORE_DB_PORT}..."
until nc -z "${HIVE_METASTORE_DB_HOST}" "${HIVE_METASTORE_DB_PORT}"; do
  echo "  PostgreSQL not ready yet — retrying in 2s..."
  sleep 2
done
echo "PostgreSQL is reachable."

echo "Initializing Hive Metastore schema (no-op if already exists)..."
$HIVE_HOME/bin/schematool -dbType postgres -initSchema 2>&1 || true

echo "Starting Hive Metastore service on port 9083..."
exec $HIVE_HOME/bin/hive --service metastore
