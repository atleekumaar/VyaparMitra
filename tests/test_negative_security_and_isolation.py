"""
Comprehensive Negative Security, Authentication Bypass, and Tenant Isolation Tests.
Validates:
1. Rejection of unauthenticated requests on all operational endpoints.
2. Rejection of auth-bypass via X-Merchant-Id headers or query params without valid JWT.
3. Cross-tenant data isolation and rejection with 403 Forbidden.
4. CSV import security constraints: 5MB size limit, entity type mismatch, and rejection of phantom products.
5. Strict RBAC enforcement on sensitive operational endpoints.
"""

import io
import uuid
import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.api.auth import hash_password
from src.api.db import get_db_connection

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


def test_operational_endpoints_reject_missing_auth():
    """Verify all operational endpoints strictly require Bearer JWT authentication."""
    endpoints = [
        ("GET", "/api/inventory"),
        ("POST", "/api/sales"),
        ("GET", "/api/customer-ops"),
        ("GET", "/api/audit-logs"),
        ("GET", "/api/copilot/approvals"),
    ]
    for method, path in endpoints:
        if method == "GET":
            res = client.get(path)
        else:
            res = client.post(path, json={})
        assert res.status_code == 401, f"{method} {path} allowed access without auth! Status: {res.status_code}"


def test_auth_bypass_headers_and_query_params_rejected():
    """Verify X-Merchant-Id header or merchant_id query params do not bypass authentication."""
    headers_bypass = {"X-Merchant-Id": "M015"}
    params_bypass = {"merchant_id": "M015"}

    # 1. Header bypass attempt
    res = client.get("/api/inventory", headers=headers_bypass)
    assert res.status_code == 401, f"X-Merchant-Id bypassed auth on /api/inventory! Status: {res.status_code}"

    res = client.get("/api/customer-ops", headers=headers_bypass)
    assert res.status_code == 401, f"X-Merchant-Id bypassed auth on /api/customer-ops! Status: {res.status_code}"

    # 2. Query param bypass attempt
    res = client.get("/api/inventory", params=params_bypass)
    assert res.status_code == 401, f"?merchant_id bypassed auth on /api/inventory! Status: {res.status_code}"

    res = client.get("/api/customer-ops", params=params_bypass)
    assert res.status_code == 401, f"?merchant_id bypassed auth on /api/customer-ops! Status: {res.status_code}"


def test_cross_tenant_isolation_rejected_with_403():
    """Verify an authenticated user from Tenant A cannot access Tenant B by altering merchant_id."""
    # M015 user tries to access M001 data
    token = get_token("owner")  # M015 owner

    # Attempt cross-tenant queries
    res_inv = client.get(
        "/api/inventory?merchant_id=M001",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_inv.status_code == 403, f"Cross-tenant access allowed on /api/inventory! Status: {res_inv.status_code}"
    assert "cross-tenant access prohibited" in res_inv.json()["detail"].lower()

    res_cust = client.get(
        "/api/customer-ops?merchant_id=M001",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_cust.status_code == 403, f"Cross-tenant access allowed on /api/customer-ops! Status: {res_cust.status_code}"

    res_sales = client.get(
        "/api/sales?merchant_id=M001",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_sales.status_code == 403, f"Cross-tenant access allowed on /api/sales! Status: {res_sales.status_code}"


def test_csv_import_file_size_limit():
    """Verify that CSV files exceeding 5MB are rejected."""
    token = get_token("owner")

    # Create dummy bytes > 5MB (5.8 MB)
    large_payload = b"product_id,product_name,category,current_stock,unit_cost,selling_price\n" + (b"SKU_X,Item X,Cat,1,10.0,20.0\n" * 200000)
    assert len(large_payload) > 5 * 1024 * 1024

    files = {"file": ("large_data.csv", io.BytesIO(large_payload), "text/csv")}
    res = client.post(
        "/api/import/csv?entity_type=inventory",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    assert res.status_code == 400
    assert "maximum allowed limit of 5 mb" in res.json()["error"]["message"].lower()


def test_csv_import_entity_mismatch_rejection():
    """Verify that uploading a customer CSV to the inventory endpoint is rejected."""
    token = get_token("owner")

    customer_csv = "name,phone,email,credit_limit\nAnita Roy,9876543211,anita@test.com,5000\n"
    files = {"file": ("customers.csv", io.BytesIO(customer_csv.encode("utf-8")), "text/csv")}

    res = client.post(
        "/api/import/csv?entity_type=inventory",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    assert res.status_code == 400
    assert "customers" in res.json()["error"]["message"].lower()


def test_sales_import_rejects_nonexistent_product_without_auto_create():
    """Verify sales CSV import rejects unknown SKUs and never auto-creates fake inventory."""
    token = get_token("owner")

    phantom_sku = f"PHANTOM_SKU_{uuid.uuid4().hex[:8]}"
    sales_csv = f"product_id,quantity,payment_method\n{phantom_sku},2,CASH\n"
    files = {"file": ("sales.csv", io.BytesIO(sales_csv.encode("utf-8")), "text/csv")}

    res = client.post(
        "/api/import/csv?entity_type=sales",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_rows"] == 1
    assert data["failed_rows"] == 1
    assert data["inserted_rows"] == 0
    assert "not found in inventory" in data["errors"][0]["error"].lower()

    # Confirm phantom product was NOT created in DB
    conn = get_db_connection()
    phantom_check = conn.execute("SELECT * FROM inventory WHERE product_id = ?", (phantom_sku,)).fetchone()
    conn.close()
    assert phantom_check is None


def test_staff_role_negative_access():
    """Verify Staff role cannot perform privileged management or audit operations."""
    staff_token = get_token("staff")

    # Cannot view audit logs
    res_audit = client.get("/api/audit-logs", headers={"Authorization": f"Bearer {staff_token}"})
    assert res_audit.status_code == 403

    # Cannot import CSV
    dummy_csv = "product_name,selling_price\nTea,10.0\n"
    res_import = client.post(
        "/api/import/csv?entity_type=inventory",
        headers={"Authorization": f"Bearer {staff_token}"},
        files={"file": ("test.csv", io.BytesIO(dummy_csv.encode("utf-8")), "text/csv")},
    )
    assert res_import.status_code == 403

    # Cannot create users
    res_create_usr = client.post(
        "/api/auth/users",
        headers={"Authorization": f"Bearer {staff_token}"},
        json={"username": "hack_mgr", "role": "manager", "password": "Password123!"},
    )
    assert res_create_usr.status_code == 403
