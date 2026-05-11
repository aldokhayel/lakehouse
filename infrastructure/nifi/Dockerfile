FROM apache/nifi:latest

USER root

# Copy pre-built flow templates so they're available inside the container
COPY flow-templates/ /opt/nifi-templates/

# Upload helper: waits for NiFi to be ready then uploads all templates
COPY upload-templates.sh /opt/nifi-templates/upload-templates.sh
RUN chmod +x /opt/nifi-templates/upload-templates.sh

USER nifi
