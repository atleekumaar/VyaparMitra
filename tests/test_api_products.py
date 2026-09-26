"""
Unit and integration tests for Phase 6 Product Endpoints.
"""

from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_api_list_products():
    response = client.get("/api/products?limit=20")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    first = data[0]
    assert "product_id" in first
    assert "selling_price" in first
    assert "forecast_7d_units" in first


def test_api_filter_products_search():
    response = client.get("/api/products?search=PRD")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_api_product_detail():
    # First get a valid product ID
    list_res = client.get("/api/products?limit=1")
    valid_id = list_res.json()[0]["product_id"]

    response = client.get(f"/api/products/{valid_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == valid_id
    assert "margin" in data
    assert "cross_sell_recommendations" in data


def test_api_product_detail_not_found():
    response = client.get("/api/products/NON_EXISTENT_SKU_12345")
    assert response.status_code == 404
    err = response.json()
    assert "error" in err
    assert err["error"]["code"] == "RESOURCE_NOT_FOUND"
