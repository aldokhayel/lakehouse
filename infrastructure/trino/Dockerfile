# infrastructure/trino/Dockerfile
# Builds a custom Trino image that bundles the catalog configs and a
# lightweight health-check script used by Docker Compose.

FROM trinodb/trino:435

# Copy all Trino config files (config.properties, jvm.config,
# node.properties, and catalog/*.properties) into the image.
COPY etc/ /etc/trino/

# Copy the health-check script so Docker Compose can exec it.
COPY health-check.sh /health-check.sh

USER root
RUN chmod +x /health-check.sh

USER trino
