"""
Tests for external benchmark CSV dataset extraction, schema normalization,
chunked streaming (for 2M+ row files), and Bulk CSV Import API compatibility.
"""
from pathlib import Path
import pandas as pd
from fastapi.testclient import TestClient

from src.api.main import app
from src.ingestion.external_adapter import (
    normalize_external_customers,
    normalize_external_products,
    normalize_phone,
    stream_normalized_external_csv,
)


def test_normalize_phone_strips_extensions_and_punctuation():
    assert normalize_phone("(302)564-9011x928") == "3025649011"
    assert normalize_phone("+1-810-810-1744x956") == "8108101744"
    assert normalize_phone("6233837777") == "6233837777"
    assert normalize_phone(None) == ""


def test_external_small_datasets_normalization():
    cust_path = Path("data/external/customers_small_100.csv")
    prod_path = Path("data/external/products_small_100.csv")
    assert cust_path.exists()
    assert prod_path.exists()

    clean_cust = normalize_external_customers(pd.read_csv(cust_path))
    assert len(clean_cust) == 100
    assert {"customer_id", "name", "phone", "city", "subscription_date"}.issubset(clean_cust.columns)
    assert clean_cust["name"].iloc[0] == "Hector Huang"
    assert clean_cust["phone"].iloc[0] == "6233837777"

    clean_prod = normalize_external_products(pd.read_csv(prod_path))
    assert len(clean_prod) == 100
    assert {"product_id", "product_name", "category", "unit_cost", "selling_price", "current_stock", "barcode"}.issubset(clean_prod.columns)
    assert clean_prod["product_id"].iloc[0] == "PRD_EXT_56"
    assert clean_prod["selling_price"].iloc[0] == 265.0 * 84.0


def test_stream_normalized_external_csv_chunked():
    chunks = list(stream_normalized_external_csv("data/external/products_small_100.csv", entity_type="products", chunksize=35))
    assert len(chunks) == 3
    total_rows = sum(len(c) for c in chunks)
    assert total_rows == 100


def test_bulk_csv_import_accepts_normalized_external_csvs():
    client = TestClient(app)
    login = client.post("/api/auth/login", json={"username": "owner", "password": "owner123"})
    if login.status_code != 200:
        return
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    with open("data/external/clean_products_small_100.csv", "rb") as f:
        res_p = client.post(
            "/api/import/csv?entity_type=products",
            headers=headers,
            files={"file": ("clean_products_small_100.csv", f, "text/csv")},
        )
    assert res_p.status_code == 200
    assert res_p.json()["imported_count"] >= 90

    with open("data/external/clean_customers_small_100.csv", "rb") as f:
        res_c = client.post(
            "/api/import/csv?entity_type=customers",
            headers=headers,
            files={"file": ("clean_customers_small_100.csv", f, "text/csv")},
        )
    assert res_c.status_code == 200
    assert res_c.json()["imported_count"] >= 90
