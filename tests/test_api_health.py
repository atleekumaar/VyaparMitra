"""
Unit and integration tests for Phase 6 Health Endpoint.
"""

from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_api_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"
    assert "checked_at" in data
    assert data["artifacts_ready"] is True
    assert "X-Request-ID" in response.headers
