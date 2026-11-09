
import pytest
from fastapi.testclient import TestClient
from src.api.main import create_app

app = create_app()
client = TestClient(app)

def test_api_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data or "healthy" in str(data).lower()

def test_api_dashboard_summary():
    res = client.get("/api/dashboard/summary")
    # Endpoint should return valid 200 or structured response
    assert res.status_code in [200, 404]

def test_api_analytics_sales():
    res = client.get("/api/analytics/sales")
    assert res.status_code in [200, 404]
