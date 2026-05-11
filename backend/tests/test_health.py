"""Basic smoke tests for the Lakehouse API health endpoint."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    """Health endpoint should return 200 with a success or degraded status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] in ("success", "degraded")


def test_root():
    """Root endpoint should return a welcome JSON response."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "version" in data["data"]
