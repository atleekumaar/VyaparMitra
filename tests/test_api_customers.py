"""
Unit and integration tests for Phase 6 Customer Endpoints.
"""

from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_api_list_customers():
    response = client.get("/api/customers?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    first = data[0]
    assert "customer_id" in first
    assert "churn_risk_tier" in first
    assert "churn_probability" in first


def test_api_customer_detail():
    list_res = client.get("/api/customers?limit=1")
    valid_id = list_res.json()[0]["customer_id"]

    response = client.get(f"/api/customers/{valid_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["customer_id"] == valid_id
    assert "suggested_retention_action" in data


def test_api_customer_detail_not_found():
    response = client.get("/api/customers/NON_EXISTENT_CUST_99999")
    assert response.status_code == 404
    err = response.json()
    assert "error" in err
    assert err["error"]["code"] == "RESOURCE_NOT_FOUND"
