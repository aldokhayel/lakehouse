#!/bin/bash
# infrastructure/trino/health-check.sh
# Used by Docker Compose HEALTHCHECK to confirm Trino has fully started.
# The /v1/info endpoint returns {"starting":true} while booting; we wait
# until "starting":false before declaring the service healthy.

curl -sf http://localhost:8080/v1/info | grep -q '"starting":false' || exit 1
