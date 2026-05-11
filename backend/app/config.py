"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central settings object — all values override-able via env vars or .env file."""

    # Trino
    trino_host: str = "trino"
    trino_port: int = 8080
    trino_user: str = "admin"
    trino_catalog: str = "iceberg"

    # NiFi (Phase 3)
    nifi_host: str = "nifi"
    nifi_port: int = 8443
    nifi_username: str = "admin"
    nifi_password: str = "adminadminadmin"

    # ChromaDB (Phase 5)
    chromadb_host: str = "chromadb"
    chromadb_port: int = 8500

    # OpenRouter (Phase 5)
    openrouter_api_key: str = ""
    openrouter_model: str = "anthropic/claude-sonnet-4-20250514"

    # MinIO
    minio_endpoint: str = "http://minio:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"

    # SQLite
    sqlite_path: str = "/data/lakehouse.db"

    # dbt
    dbt_project_dir: str = "/dbt_project"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
