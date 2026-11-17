"""
MerchantOS Independent Final Release Security, Integrity & Workflow Audit Suite.
Acts as an adversarial auditor verifying:
1. Deep Security: Tampered JWTs, Expired JWTs, Alg 'none', X-Merchant-Id Spoofing, Cross-tenant isolation, RBAC.
2. Data Integrity: POS atomic checkout, Insufficient stock, Refund stock restoration, Khata limits & balance, CSV errors, Rollback.
3. AI & Approval Safety: Grounded vs fake data, L3 draft persistence, 2-step approval + goods receipt, double-execution prevention.
4. Production Hardening: Password hash leakage in responses, Startup guards for JWT secrets.
"""

from datetime import timedelta
import base64
import json
import hmac
import hashlib
import time
import uuid
import io
import pytest
from fastapi.testclient import TestClient

from src.api.main import create_app
from src.api.config import APIConfig, _resolve_jwt_secret
from src.api.db import init_db, get_db_connection, hash_password
from src.api.auth import create_access_token, decode_access_token, normalize_role, UserRole

# Use live test app instance
app = create_app()
client = TestClient(app)


# ==============================================================================
# 1. SECURITY & AUTHENTICATION AUDIT
# ==============================================================================

def test_audit_unauthenticated_requests_rejected():
    """Verify all critical operational endpoints reject unauthenticated calls."""
    protected_endpoints = [
        ("GET", "/api/inventory"),
        ("POST", "/api/inventory"),
        ("GET", "/api/sales"),
        ("POST", "/api/sales"),
        ("GET", "/api/customer-ops"),
        ("POST", "/api/customer-ops"),
        ("GET", "/api/audit-logs"),
        ("POST", "/api/import/csv?entity_type=inventory"),
        ("GET", "/api/copilot/approvals"),
        ("POST", "/api/copilot/approvals/appr_123/approve"),
        ("POST", "/api/copilot/approvals/appr_123/receive-goods"),
    ]
    for method, path in protected_endpoints:
        if method == "GET":
            res = client.get(path)
        else:
            res = client.post(path, json={})
        assert res.status_code == 401, f"Security Breach: {method} {path} returned {res.status_code} without auth!"


def test_audit_tampered_jwt_signature_rejected():
    """Verify modified JWT payload or forged signature is rejected with 401."""
    # Obtain a genuine token
    login_res = client.post("/api/auth/login", json={"username_or_email": "owner_m015", "password": "OwnerPassword123!"})
    valid_token = login_res.json()["access_token"]
    parts = valid_token.split(".")
    assert len(parts) == 3

    # Tamper with signature
    tampered_sig = parts[2][:-4] + "ABCD"
    tampered_token = f"{parts[0]}.{parts[1]}.{tampered_sig}"
    res_tampered = client.get("/api/inventory", headers={"Authorization": f"Bearer {tampered_token}"})
    assert res_tampered.status_code == 401, "Security Breach: Tampered JWT signature was accepted!"

    # Tamper with payload (escalate role to owner while using manager's token)
    mgr_login = client.post("/api/auth/login", json={"username_or_email": "manager_m015", "password": "ManagerPassword123!"})
    mgr_token = mgr_login.json()["access_token"]
    m_parts = mgr_token.split(".")
    # Decode payload
    padded = m_parts[1] + "=" * (-len(m_parts[1]) % 4)
    payload = json.loads(base64.urlsafe_b64decode(padded.encode()).decode())
    payload["role"] = "owner"  # privilege escalation attempt
    new_payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    escalated_token = f"{m_parts[0]}.{new_payload_b64}.{m_parts[2]}"

    res_escalated = client.get("/api/audit-logs", headers={"Authorization": f"Bearer {escalated_token}"})
    assert res_escalated.status_code == 401, "Security Breach: Escalated payload with original signature was accepted!"


def test_audit_expired_jwt_rejected():
    """Verify expired JWT tokens are strictly rejected."""
    # Create a token expired 1 hour ago
    expired_token = create_access_token(
        {"sub": "USR_OWNER_M015", "business_id": "M015", "branch_id": "BR_M015_MAIN", "role": "owner"},
        expires_delta=timedelta(minutes=-60),
    )
    res = client.get("/api/inventory", headers={"Authorization": f"Bearer {expired_token}"})
    assert res.status_code == 401
    assert "expired" in res.json()["detail"].lower()


def test_audit_jwt_algorithm_none_rejected():
    """Verify tokens with 'alg': 'none' are rejected."""
    header = base64.urlsafe_b64encode(json.dumps({"alg": "none", "typ": "JWT"}).encode()).decode().rstrip("=")
    payload = base64.urlsafe_b64encode(json.dumps({"sub": "USR_OWNER_M015", "business_id": "M015", "role": "owner"}).encode()).decode().rstrip("=")
    none_token = f"{header}.{payload}."

    res = client.get("/api/inventory", headers={"Authorization": f"Bearer {none_token}"})
    assert res.status_code == 401, "Security Breach: 'alg: none' token was accepted!"


def test_audit_x_merchant_id_spoofing_attempts():
    """Verify X-Merchant-Id header cannot bypass auth or switch tenant context."""
    # 1. Without Bearer token
    res_no_auth = client.get("/api/inventory", headers={"X-Merchant-Id": "M015"})
    assert res_no_auth.status_code == 401

    # 2. With Bearer token of M015 attempting to spoof M001
    login_res = client.post("/api/auth/login", json={"username_or_email": "owner_m015", "password": "OwnerPassword123!"})
    token = login_res.json()["access_token"]
    res_spoof = client.get("/api/inventory?merchant_id=M001", headers={"Authorization": f"Bearer {token}", "X-Merchant-Id": "M001"})
    assert res_spoof.status_code == 403
    assert "cross-tenant" in res_spoof.json()["detail"].lower()


def test_audit_no_password_hash_leakage():
    """Verify password hashes are never returned in user listings or profile responses."""
    login_res = client.post("/api/auth/login", json={"username_or_email": "owner_m015", "password": "OwnerPassword123!"})
    token = login_res.json()["access_token"]

    # 1. Login response
    user_data = login_res.json()["user"]
    assert "password" not in user_data
    assert "password_hash" not in user_data

    # 2. User list endpoint
    users_res = client.get("/api/auth/users", headers={"Authorization": f"Bearer {token}"})
    assert users_res.status_code == 200
    for u in users_res.json():
        assert "password" not in u
        assert "password_hash" not in u


def test_audit_production_secret_guard(monkeypatch):
    """Verify application configuration rejects weak/missing JWT secret in production."""
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("JWT_SECRET_KEY", "short_secret")
    with pytest.raises(RuntimeError, match="CRITICAL SECURITY HALT"):
        _resolve_jwt_secret()

    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError, match="CRITICAL SECURITY HALT"):
        _resolve_jwt_secret()


# ==============================================================================
# 2. DATA INTEGRITY & POS BILLING AUDIT
# ==============================================================================

@pytest.fixture
def audit_db_env():
    """Creates isolated merchant records in database for integrity tests."""
    init_db()
    conn = get_db_connection()
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ")
    biz_id = f"biz_aud_{uuid.uuid4().hex[:6]}"
    branch_id = f"br_aud_{uuid.uuid4().hex[:6]}"
    owner_id = f"usr_aud_own_{uuid.uuid4().hex[:6]}"
    cust_id = f"cus_aud_{uuid.uuid4().hex[:6]}"
    sku = f"SKU_AUD_{uuid.uuid4().hex[:6]}"

    conn.execute(
        "INSERT INTO businesses (id, name, city, state, created_at) VALUES (?, 'Audit Kirana', 'Noida', 'UP', ?)",
        (biz_id, now),
    )
    conn.execute(
        "INSERT INTO branches (id, business_id, name, code, is_main, created_at) VALUES (?, ?, 'Audit Branch', 'AUD', 1, ?)",
        (branch_id, biz_id, now),
    )
    conn.execute(
        """INSERT INTO users (id, business_id, branch_id, username, email, full_name, password_hash, role, is_active, created_at)
           VALUES (?, ?, ?, ?, ?, 'Audit Owner', ?, 'owner', 1, ?)""",
        (owner_id, biz_id, branch_id, f"aud_own_{biz_id}", f"aud_own_{biz_id}@test.com", hash_password("AuditPass123!"), now),
    )
    # Seed 10 units in stock
    conn.execute(
        """INSERT INTO inventory (id, business_id, branch_id, product_id, product_name, category, current_stock, min_stock_threshold, unit_cost, selling_price, updated_at)
           VALUES (?, ?, ?, ?, 'Audit Organic Ghee 1L', 'Dairy', 10, 5, 450.0, 600.0, ?)""",
        (f"inv_{uuid.uuid4().hex[:8]}", biz_id, branch_id, sku, now),
    )
    # Seed customer with 5000 credit limit and 0 balance
    conn.execute(
        """INSERT INTO customers (id, business_id, name, phone, current_balance, credit_limit, created_at)
           VALUES (?, ?, 'Vikram Singh', '9811122233', 0.0, 5000.0, ?)""",
        (cust_id, biz_id, now),
    )
    conn.commit()
    conn.close()

    token = create_access_token({"sub": owner_id, "business_id": biz_id, "branch_id": branch_id, "role": "owner"})
    return {"token": token, "biz_id": biz_id, "branch_id": branch_id, "sku": sku, "cust_id": cust_id}


def test_audit_pos_checkout_atomic_stock_and_khata(audit_db_env):
    """Verify atomic stock deduction and Khata balance increment on CREDIT sale."""
    token = audit_db_env["token"]
    sku = audit_db_env["sku"]
    cust_id = audit_db_env["cust_id"]

    # Sell 4 units on CREDIT (4 * 600 = 2400)
    sale_payload = {
        "customer_id": cust_id,
        "payment_method": "CREDIT",
        "items": [
            {"product_id": sku, "product_name": "Audit Organic Ghee 1L", "quantity": 4, "unit_price": 600.0}
        ],
        "discount_amount": 0.0,
    }
    res = client.post("/api/sales", json=sale_payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 201, f"POS Sale failed: {res.text}"
    sale_data = res.json()
    assert sale_data["status"] == "COMPLETED"
    assert sale_data["total_amount"] == 2400.0
    assert sale_data["payment_method"] == "CREDIT"
    sale_id = sale_data["id"]

    # Verify inventory was decremented from 10 to 6
    conn = get_db_connection()
    inv_row = conn.execute("SELECT current_stock FROM inventory WHERE product_id = ?", (sku,)).fetchone()
    assert inv_row["current_stock"] == 6

    # Verify customer Khata balance was incremented to 2400
    cust_row = conn.execute("SELECT current_balance FROM customers WHERE id = ?", (cust_id,)).fetchone()
    assert cust_row["current_balance"] == 2400.0

    # Verify customer ledger entry was recorded (DEBIT increases customer receivable debt)
    ledger_row = conn.execute("SELECT * FROM customer_ledgers WHERE customer_id = ? AND reference_id = ?", (cust_id, sale_id)).fetchone()
    assert ledger_row is not None
    assert ledger_row["entry_type"] == "DEBIT"
    assert ledger_row["amount"] == 2400.0
    conn.close()


def test_audit_pos_checkout_insufficient_stock_rejected(audit_db_env):
    """Verify sale is rejected and rolled back when requested quantity exceeds available stock."""
    token = audit_db_env["token"]
    sku = audit_db_env["sku"]

    # Available stock is 10. Attempt to sell 15 units.
    sale_payload = {
        "payment_method": "UPI",
        "items": [
            {"product_id": sku, "product_name": "Audit Organic Ghee 1L", "quantity": 15, "unit_price": 600.0}
        ],
    }
    res = client.post("/api/sales", json=sale_payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 400
    assert "insufficient stock" in res.json()["detail"].lower()

    # Verify stock remained untouched at 10
    conn = get_db_connection()
    inv_row = conn.execute("SELECT current_stock FROM inventory WHERE product_id = ?", (sku,)).fetchone()
    conn.close()
    assert inv_row["current_stock"] == 10


def test_audit_pos_checkout_credit_limit_exceeded_rejected(audit_db_env):
    """Verify CREDIT sale is rejected when resulting balance exceeds customer credit limit."""
    token = audit_db_env["token"]
    sku = audit_db_env["sku"]
    cust_id = audit_db_env["cust_id"]

    # Customer credit limit is 5000. 9 units * 600 = 5400 > 5000.
    sale_payload = {
        "customer_id": cust_id,
        "payment_method": "CREDIT",
        "items": [
            {"product_id": sku, "product_name": "Audit Organic Ghee 1L", "quantity": 9, "unit_price": 600.0}
        ],
    }
    res = client.post("/api/sales", json=sale_payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 400
    assert "credit limit" in res.json()["detail"].lower()


def test_audit_sales_refund_restores_inventory_and_khata(audit_db_env):
    """Verify refunding a completed sale restores physical inventory and reverses Khata balance."""
    token = audit_db_env["token"]
    sku = audit_db_env["sku"]
    cust_id = audit_db_env["cust_id"]

    # 1. Create a credit sale of 2 units (1200 INR)
    sale_payload = {
        "customer_id": cust_id,
        "payment_method": "CREDIT",
        "items": [
            {"product_id": sku, "product_name": "Audit Organic Ghee 1L", "quantity": 2, "unit_price": 600.0}
        ],
    }
    sale_res = client.post("/api/sales", json=sale_payload, headers={"Authorization": f"Bearer {token}"})
    sale_id = sale_res.json()["id"]

    # Stock is now 8, Khata is 1200
    conn = get_db_connection()
    assert conn.execute("SELECT current_stock FROM inventory WHERE product_id = ?", (sku,)).fetchone()[0] == 8
    assert conn.execute("SELECT current_balance FROM customers WHERE id = ?", (cust_id,)).fetchone()[0] == 1200.0
    conn.close()

    # 2. Refund the sale
    refund_res = client.post(
        f"/api/sales/{sale_id}/refund",
        json={"reason": "Customer changed mind"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert refund_res.status_code == 200
    refund_data = refund_res.json()
    assert refund_data["status"] == "REFUNDED"

    # 3. Verify stock is restored to 10 and Khata balance restored to 0
    conn = get_db_connection()
    restored_stock = conn.execute("SELECT current_stock FROM inventory WHERE product_id = ?", (sku,)).fetchone()[0]
    restored_khata = conn.execute("SELECT current_balance FROM customers WHERE id = ?", (cust_id,)).fetchone()[0]
    conn.close()
    assert restored_stock == 10
    assert restored_khata == 0.0


# ==============================================================================
# 3. AI AGENT & APPROVAL LIFECYCLE SAFETY AUDIT
# ==============================================================================

def test_audit_ai_agent_uses_live_operational_data(audit_db_env):
    """Verify copilot agent responds with actual database stock rather than synthetic hallucinations."""
    token = audit_db_env["token"]
    sku = audit_db_env["sku"]
    biz_id = audit_db_env["biz_id"]

    # Set stock to 3 (below threshold 5) to trigger low stock alert
    conn = get_db_connection()
    conn.execute("UPDATE inventory SET current_stock = 3, min_stock_threshold = 10 WHERE product_id = ?", (sku,))
    conn.commit()
    conn.close()

    res = client.post(
        "/api/copilot/agent/execute",
        json={"query": "Check low stock alert"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "INVENTORY_QUERY"
    assert "Audit Organic Ghee 1L" in data["response"]
    assert "3 left" in data["response"]


def test_audit_approval_lifecycle_and_double_execution_prevention(audit_db_env):
    """Verify full approval lifecycle: Draft -> PO Approval (Stock Unchanged) -> Goods Receipt (Stock Inwarded) -> No Double Execution."""
    token = audit_db_env["token"]
    sku = audit_db_env["sku"]

    # 1. Trigger Reorder Draft for 25 units
    draft_res = client.post(
        "/api/copilot/agent/execute",
        json={"query": "Reorder 25 units of Audit Organic Ghee"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert draft_res.status_code == 200
    draft_actions = draft_res.json()["draft_actions"]
    assert len(draft_actions) == 1
    approval_id = draft_actions[0]["approval_id"]
    assert draft_actions[0]["status"] == "PENDING_APPROVAL"

    # 2. Owner approves draft -> Issues PO, Status = APPROVED, Stock STILL 10
    appr_res = client.post(
        f"/api/copilot/approvals/{approval_id}/approve",
        json={"notes": "Procurement approved"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert appr_res.status_code == 200
    appr_data = appr_res.json()
    assert appr_data["status"] == "APPROVED"
    assert "po_number" in appr_data
    assert appr_data["po_number"].startswith("PO-")

    conn = get_db_connection()
    stock_check = conn.execute("SELECT current_stock FROM inventory WHERE product_id = ?", (sku,)).fetchone()[0]
    conn.close()
    assert stock_check == 10, "Safety Violation: Physical stock increased before physical goods receipt!"

    # 3. Double-approval prevention: Attempt to approve again must fail
    dup_appr = client.post(
        f"/api/copilot/approvals/{approval_id}/approve",
        json={"notes": "Duplicate approve"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert dup_appr.status_code == 400
    assert "already approved" in dup_appr.json()["detail"].lower()

    # 4. Goods Receipt: Inward physical delivery -> Stock becomes 35
    grn_res = client.post(
        f"/api/copilot/approvals/{approval_id}/receive-goods",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert grn_res.status_code == 200
    grn_data = grn_res.json()
    assert grn_data["status"] == "GOODS_RECEIVED"
    assert grn_data["quantity_added"] == 25
    assert grn_data["updated_stock"] == 35

    conn = get_db_connection()
    stock_final = conn.execute("SELECT current_stock FROM inventory WHERE product_id = ?", (sku,)).fetchone()[0]
    conn.close()
    assert stock_final == 35

    # 5. Double goods receipt prevention: Attempt to inward again must fail
    dup_grn = client.post(
        f"/api/copilot/approvals/{approval_id}/receive-goods",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert dup_grn.status_code == 400
    assert "status must be 'approved'" in dup_grn.json()["detail"].lower()
