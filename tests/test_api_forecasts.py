"""
Unit and integration tests for Phase 6 Forecast Endpoints.
"""

from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_api_forecasts_sales():
    response = client.get("/api/forecasts/sales")
    assert response.status_code == 200
    data = response.json()
    assert data["forecast_7d_total_revenue"] > 0
    assert "daily_forecasts" in data
    assert len(data["daily_forecasts"]) > 0
    assert "trend_direction" in data


def test_api_forecasts_demand():
    response = client.get("/api/forecasts/demand?limit=15")
    assert response.status_code == 200
    data = response.json()
    assert "top_demand_skus" in data
    assert len(data["top_demand_skus"]) <= 15
    assert len(data["top_demand_skus"]) > 0
    first = data["top_demand_skus"][0]
    assert "predicted_7d_units" in first
