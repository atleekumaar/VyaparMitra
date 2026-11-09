"""
Tests for Bulk CSV Ingestion Endpoint (POST /api/import/csv).
Validates file formats, header integrity, atomic transactions, error tolerance, and audit logs.
"""

import io
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def get_token(role="owner"):
    creds = {
        "owner": ("owner_m015", "OwnerPassword123!"),
        "manager": ("manager_m015", "ManagerPassword123!"),
        "staff": ("staff_m015", "StaffPassword123!"),
    }
    username, pwd = creds[role]
    res = client.post("/api/auth/login", json={"username_or_email": username, "password": pwd})
    return res.json()["access_token"]


def test_import_invalid_file_extension():
    """Validates that non-CSV files are rejected."""
    token = get_token("manager")
    file_content = b"some random text content"
    files = {"file": ("data.txt", io.BytesIO(file_content), "text/plain")}

    res = client.post(
        "/api/import/csv?entity_type=inventory",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    assert res.status_code == 400
    assert "Only .csv files are supported" in res.json()["error"]["message"]


def test_import_empty_file():
    """Validates that empty CSV files are rejected."""
    token = get_token("manager")
    files = {"file": ("empty.csv", io.BytesIO(b""), "text/csv")}

    res = client.post(
        "/api/import/csv?entity_type=inventory",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    assert res.status_code == 400
    assert "empty" in res.json()["error"]["message"].lower()


def test_import_invalid_entity_type():
    """Validates rejection of unknown entity types."""
    token = get_token("manager")
    csv_data = "product_name,selling_price\nSugar,45.0\n"
    files = {"file": ("items.csv", io.BytesIO(csv_data.encode("utf-8")), "text/csv")}

    res = client.post(
        "/api/import/csv?entity_type=invalid_entity",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    assert res.status_code == 400
    assert "Invalid entity_type" in res.json()["error"]["message"]


def test_import_missing_required_headers():
    """Validates header schema validation per entity type."""
    token = get_token("manager")
    # Missing required 'selling_price' column
    bad_csv = "product_name,category\nBasmati Rice,Grains\n"
    files = {"file": ("bad_headers.csv", io.BytesIO(bad_csv.encode("utf-8")), "text/csv")}

    res = client.post(
        "/api/import/csv?entity_type=inventory",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    assert res.status_code == 400
    assert "Missing required columns" in res.json()["error"]["message"]


def test_import_inventory_success_and_row_error_tolerance():
    """Validates inventory CSV import with mixed valid and invalid rows."""
    token = get_token("manager")
    csv_content = (
        "product_id,product_name,category,current_stock,unit_cost,selling_price\n"
        "CSV_ITEM_01,Premium Almonds,Dry Fruits,50,600.0,750.0\n"
        "CSV_ITEM_02,Cashew Nuts,Dry Fruits,40,550.0,700.0\n"
        "CSV_ITEM_03,Corrupt Item,Grains,10,30.0,INVALID_PRICE\n"  # Invalid row
    )
    files = {"file": ("bulk_inventory.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}

    res = client.post(
        "/api/import/csv?entity_type=inventory&branch_id=BR_M015_MAIN",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["entity_type"] == "inventory"
    assert data["total_rows"] == 3
    assert data["inserted_rows"] == 2
    assert data["failed_rows"] == 1
    assert len(data["errors"]) == 1
    assert data["errors"][0]["row_number"] == 4  # Row 4 in file (header + 3 rows)

    # Verify inventory was actually inserted in DB
    inv_check = client.get(
        "/api/inventory?search=Almonds&branch_id=BR_M015_MAIN",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert inv_check.status_code == 200
    items = inv_check.json()["items"]
    assert any(i["product_id"] == "CSV_ITEM_01" and i["selling_price"] == 750.0 for i in items)


def test_import_customers_success():
    """Validates customer bulk CSV ingestion."""
    token = get_token("manager")
    csv_content = (
        "name,phone,email,city,credit_limit\n"
        "Pooja Sharma,+919876543219,pooja@example.com,Noida,10000\n"
        "Deepak Patel,+919876543218,deepak@example.com,Noida,7500\n"
    )
    files = {"file": ("customers.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}

    res = client.post(
        "/api/import/csv?entity_type=customers",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["inserted_rows"] == 2
    assert data["failed_rows"] == 0

    # Verify customer lookup
    cust_res = client.get(
        "/api/customer-ops?search=Pooja",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert cust_res.status_code == 200
    assert cust_res.json()["total_customers"] >= 1


def test_import_sales_with_stock_deduction():
    """Validates sales CSV import with real-time stock deduction."""
    token = get_token("manager")

    # First ensure a known SKU exists with 50 units
    item_csv = "product_id,product_name,category,current_stock,unit_cost,selling_price\nCSV_SALE_SKU,Test Juice,Beverages,50,40.0,60.0\n"
    client.post(
        "/api/import/csv?entity_type=inventory&branch_id=BR_M015_MAIN",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("item.csv", io.BytesIO(item_csv.encode("utf-8")), "text/csv")},
    )

    # Now import sales: 1 valid sale of 5 units, 1 invalid sale of 1000 units (insufficient stock)
    sales_csv = (
        "product_id,quantity,payment_method\n"
        "CSV_SALE_SKU,5,UPI\n"
        "CSV_SALE_SKU,1000,CASH\n"
    )
    res = client.post(
        "/api/import/csv?entity_type=sales&branch_id=BR_M015_MAIN",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("sales.csv", io.BytesIO(sales_csv.encode("utf-8")), "text/csv")},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_rows"] == 2
    assert data["inserted_rows"] == 1
    assert data["failed_rows"] == 1
    assert "Insufficient stock" in data["errors"][0]["error"]

    # Verify stock decremented by 5 (50 - 5 = 45)
    inv_check = client.get(
        "/api/inventory?search=CSV_SALE_SKU&branch_id=BR_M015_MAIN",
        headers={"Authorization": f"Bearer {token}"},
    )
    item = inv_check.json()["items"][0]
    assert item["current_stock"] == 45


def test_import_rbac_staff_rejected():
    """Validates that Staff role cannot perform bulk CSV imports."""
    staff_token = get_token("staff")
    csv_data = "product_name,selling_price\nTea,20.0\n"
    files = {"file": ("items.csv", io.BytesIO(csv_data.encode("utf-8")), "text/csv")}

    res = client.post(
        "/api/import/csv?entity_type=inventory",
        headers={"Authorization": f"Bearer {staff_token}"},
        files=files,
    )
    assert res.status_code == 403


def test_import_audit_logging():
    """Validates that CSV_IMPORT is logged into audit_logs table."""
    owner_token = get_token("owner")
    csv_data = "name,phone\nAudit Customer,+919900112233\n"
    files = {"file": ("audit_cust.csv", io.BytesIO(csv_data.encode("utf-8")), "text/csv")}

    client.post(
        "/api/import/csv?entity_type=customers",
        headers={"Authorization": f"Bearer {owner_token}"},
        files=files,
    )

    # Inspect audit logs
    audit_res = client.get(
        "/api/audit-logs?action=CSV_IMPORT",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert audit_res.status_code == 200
    logs = audit_res.json()["logs"]
    assert len(logs) > 0
    assert logs[0]["action"] == "CSV_IMPORT"
