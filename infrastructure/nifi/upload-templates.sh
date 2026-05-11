#!/bin/bash
# Upload pre-built NiFi flow templates to a running NiFi instance.

set -e

NIFI_URL="https://localhost:8443/nifi-api"
USERNAME="${SINGLE_USER_CREDENTIALS_USERNAME:-admin}"
PASSWORD="${SINGLE_USER_CREDENTIALS_PASSWORD:-adminadminadmin}"
TEMPLATES_DIR="/opt/nifi-templates"

echo "Waiting for NiFi to be ready..."
until curl -sk "${NIFI_URL}/system-diagnostics" > /dev/null 2>&1; do
  echo "  NiFi not ready — retrying in 5s..."
  sleep 5
done
echo "NiFi is ready."

echo "Authenticating..."
TOKEN=$(curl -sk -X POST "${NIFI_URL}/access/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=${USERNAME}&password=${PASSWORD}")

ROOT_ID=$(curl -sk "${NIFI_URL}/process-groups/root" \
  -H "Authorization: Bearer ${TOKEN}" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

echo "Root process group: ${ROOT_ID}"

for template_file in "${TEMPLATES_DIR}"/*.xml; do
  name=$(basename "${template_file}")
  echo "Uploading ${name}..."
  result=$(curl -sk -X POST \
    "${NIFI_URL}/process-groups/${ROOT_ID}/templates/upload" \
    -H "Authorization: Bearer ${TOKEN}" \
    -F "template=@${template_file};type=application/xml")
  echo "  Done: ${result}" | head -c 200
  echo ""
done

echo "All templates uploaded."
