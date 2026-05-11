"""MinIO client service for S3-compatible object storage operations."""

from urllib.parse import urlparse

from minio import Minio

from app.config import settings


class MinIOService:
    """Wraps the MinIO Python SDK for common storage operations."""

    def _client(self) -> Minio:
        parsed = urlparse(settings.minio_endpoint)
        endpoint = parsed.netloc or parsed.path  # strip scheme
        secure = parsed.scheme == "https"
        return Minio(
            endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=secure,
        )

    def list_buckets(self) -> list[str]:
        """Return the names of all buckets in MinIO."""
        client = self._client()
        return [b.name for b in client.list_buckets()]

    def is_healthy(self) -> bool:
        """Return True if MinIO is reachable and the credentials are valid."""
        try:
            self.list_buckets()
            return True
        except Exception:
            return False


minio_service = MinIOService()
