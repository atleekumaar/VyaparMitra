"""
Unit and integration tests for Phase 6 Analytics Endpoints.
"""

from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_api_analytics_sales():
    response = client.get("/api/analytics/sales")
    assert response.status_code == 200
    data = response.json()
    assert data["total_revenue"] > 0
    assert data["total_orders"] > 0
    assert "daily_series" in data
    assert len(data["daily_series"]) > 0


def test_api_analytics_customers():
    response = client.get("/api/analytics/customers")
    assert response.status_code == 200
    data = response.json()
    assert data["total_customers"] > 0
    assert "segments" in data
    assert len(data["segments"]) > 0


def test_api_analytics_products():
    response = client.get("/api/analytics/products")
    assert response.status_code == 200
    data = response.json()
    assert data["total_products_tracked"] > 0
    assert len(data["top_performers"]) > 0
    assert data["pareto_80_20_ratio"] is not None


def test_api_analytics_categories():
    response = client.get("/api/analytics/categories")
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert len(data["categories"]) > 0


def test_api_analytics_payments():
    response = client.get("/api/analytics/payments")
    assert response.status_code == 200
    data = response.json()
    assert "payment_methods" in data
    assert len(data["payment_methods"]) > 0
    assert data["primary_payment_method"] in ["UPI", "Cash", "Card", "Credit"]


def test_api_analytics_trends():
    response = client.get("/api/analytics/trends")
    assert response.status_code == 200
    data = response.json()
    assert "predicted_trend" in data
    assert data["confidence"] > 0


def test_api_analytics_anomalies():
    response = client.get("/api/analytics/anomalies")
    assert response.status_code == 200
    data = response.json()
    assert "total_anomalies_detected" in data
