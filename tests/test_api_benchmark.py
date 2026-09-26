"""
Tests for Benchmark and Merchant API endpoints in VyaparMitra.
"""

from fastapi.testclient import TestClient
from src.api.main import create_app

app = create_app()
client = TestClient(app)


def test_list_merchants():
    response = client.get("/api/merchants")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "merchants" in data
    assert data["total"] > 0
    assert any(m["merchant_id"] == "M015" for m in data["merchants"])


def test_get_merchant_benchmark_m015():
    response = client.get("/api/merchants/M015/benchmark")
    assert response.status_code == 200
    data = response.json()
    assert data["merchant_id"] == "M015"
    assert "Bakery" in data["business_type"]
    assert "peer_group" in data
    assert data["peer_count"] >= 5  # Verified hierarchical fallback
    assert 1 <= data["rank"] <= data["peer_count"]
    assert 0 <= data["overall_score"] <= 100
    assert len(data["metrics"]) == 6

    # Verify 6 core metrics are present
    metric_names = [m["name"] for m in data["metrics"]]
    assert "repeat_rate" in metric_names
    assert "ticket_size" in metric_names
    assert "failure_rate" in metric_names
    assert "refund_rate" in metric_names
    assert "upi_share" in metric_names
    assert "monthly_growth" in metric_names

    # Check metric structure
    m0 = data["metrics"][0]
    assert "you" in m0
    assert "peer_median" in m0
    assert "percentile" in m0
    assert m0["status"] in ["green", "yellow", "red"]
    assert "action" in m0


def test_get_merchant_benchmark_alias():
    response = client.get("/api/benchmark/M001")
    assert response.status_code == 200
    data = response.json()
    assert data["merchant_id"] == "M001"
    assert len(data["metrics"]) == 6


def test_get_merchant_benchmark_not_found():
    response = client.get("/api/merchants/M999/benchmark")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
