"""
Tests for static SPA serving in VyaparMitra Phase 6.
"""

from fastapi.testclient import TestClient
from src.api.main import create_app

app = create_app()
client = TestClient(app)


def test_serve_spa_index():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "VyaparMitra" in response.text
    assert "root" in response.text


def test_serve_spa_client_side_routing():
    # Any non-api route should fall back to index.html for SPA router
    response = client.get("/analytics")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "VyaparMitra" in response.text


def test_serve_spa_api_404_not_index():
    # Any route starting with api/ that is unmatched should return 404 JSON, NOT index.html
    response = client.get("/api/unknown_route")
    assert response.status_code == 404
    assert response.headers.get("content-type") == "application/json"
    data = response.json()
    assert data["error"]["code"] == "RESOURCE_NOT_FOUND"
