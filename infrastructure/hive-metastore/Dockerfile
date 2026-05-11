# infrastructure/hive-metastore/Dockerfile
# Extends apache/hive:4.0.0 with:
#   1. wget / gettext-base / netcat-openbsd — the base image has none of these;
#      wget fetches the JDBC driver, gettext-base provides envsubst for config
#      templating, netcat-openbsd provides nc for the PostgreSQL readiness probe.
#   2. PostgreSQL JDBC driver — required for the metastore-db backend.
#   3. Templated hive-site.xml and custom entrypoint.

FROM apache/hive:4.0.0

USER root

# Install tools missing from the minimal base image
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gettext-base \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Download PostgreSQL JDBC driver
RUN wget -q "https://jdbc.postgresql.org/download/postgresql-42.7.3.jar" \
    -O /opt/hive/lib/postgresql-42.7.3.jar

# Copy configuration template and entrypoint
COPY metastore-site.xml /opt/hive/conf/metastore-site.xml.template
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Give the hive user write access to the conf directory so the entrypoint
# can write the substituted hive-site.xml at runtime.
RUN chown -R hive:hive /opt/hive/conf/

USER hive

EXPOSE 9083

ENTRYPOINT ["/entrypoint.sh"]
