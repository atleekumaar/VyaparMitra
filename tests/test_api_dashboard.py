"""
Unit and integration tests for Phase 6 Dashboard Endpoints.
"""

from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_api_dashboard_summary():
    response = client.get("/api/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["merchant_id"] is not None
    assert "kpis" in data
    assert "revenue" in data["kpis"]
    assert "orders" in data["kpis"]
    assert "aov" in data["kpis"]
    assert data["kpis"]["revenue"]["value"] > 0
    assert data["kpis"]["orders"]["value"] > 0
    assert "sales_trend_direction" in data
    assert data["forecast_7d_total_revenue"] > 0
    assert data["total_actions_pending"] > 0


def test_api_dashboard_actions():
    response = client.get("/api/dashboard/actions?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "actions" in data
    assert len(data["actions"]) <= 5
    assert len(data["actions"]) > 0
    first_action = data["actions"][0]
    assert "recommendation_id" in first_action
    assert "priority_band" in first_action
    assert "action" in first_action
