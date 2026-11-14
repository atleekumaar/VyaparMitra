"""
Tests for new user OTP auto-provisioning, zero-data empty states, and tenant isolation.
Verifies that:
1. New user gets an isolated business record with 0 initial sales/inventory.
2. Dashboard summary for new user returns 0s and demo_mode=False (no M001 fake data leak).
3. Recording a sale for this merchant immediately updates their operational metrics.
4. Two different merchants cannot view or affect each other's metrics.
"""

import uuid
from fastapi.testclient import TestClient
from src.api.db import get_db_connection, init_db
from src.api.main import app

client = TestClient(app)


def test_new_user_auto_provisioning_and_empty_state():
    init_db()

    clean_email = f"fresh.retailer.{uuid.uuid4().hex[:6]}@example.com"
    req_otp_res = client.post("/api/auth/otp/send", json={
        "email": clean_email,
        "name": "Priya Sharma",
        "phone": "+919876543219",
    })
    assert req_otp_res.status_code == 200

    conn = get_db_connection()
    otp_row = conn.execute(
        "SELECT otp_code FROM otps WHERE identifier = ? AND is_used = 0 ORDER BY created_at DESC LIMIT 1",
        (clean_email,)
    ).fetchone()
    assert otp_row is not None
    otp_code = otp_row["otp_code"]
    conn.close()

    # Verify OTP without specifying store_id (representing a genuine new merchant)
    verify_res = client.post("/api/auth/otp/verify", json={
        "email": clean_email,
        "otp": otp_code,
        "name": "Priya Sharma",
    })
    assert verify_res.status_code == 200
    auth_data = verify_res.json()
    token = auth_data["access_token"]
    user = auth_data["user"]

    business_id = user["business_id"]
    # Must NOT be M015 or M001
    assert business_id.startswith("BIZ_")
    assert business_id not in ("M001", "M015")

    # 1. Check dashboard summary with Bearer token
    dash_res = client.get("/api/dashboard/summary", headers={"Authorization": f"Bearer {token}"})
    assert dash_res.status_code == 200
    dash_data = dash_res.json()

    assert dash_data["merchant_id"] == business_id
    assert dash_data["demo_mode"] is False
    assert dash_data["kpis"]["revenue"]["value"] == 0.0
    assert dash_data["kpis"]["revenue"]["formatted_value"] == "₹0.00"
    assert dash_data["kpis"]["orders"]["value"] == 0
    assert dash_data["kpis"]["aov"]["value"] == 0.0
    assert dash_data["forecast_7d_total_revenue"] == 0.0

    # 2. Check sales analytics
    sales_res = client.get("/api/analytics/sales", headers={"Authorization": f"Bearer {token}"})
    assert sales_res.status_code == 200
    sales_data = sales_res.json()
    assert sales_data["total_revenue"] == 0.0
    assert sales_data["total_orders"] == 0
    assert sales_data["daily_series"] == []

    # 3. Check products list (empty)
    prods_res = client.get("/api/products", headers={"Authorization": f"Bearer {token}"})
    assert prods_res.status_code == 200
    assert prods_res.json() == []

    # 4. Record a sale for this merchant
    cash_res = client.post(
        "/api/analytics/cash-sale",
        headers={"Authorization": f"Bearer {token}"},
        json={"amount": 2500.0, "product_name": "Premium Tea Pack"},
    )
    assert cash_res.status_code == 200

    # 5. Check dashboard immediately updates
    updated_dash = client.get("/api/dashboard/summary", headers={"Authorization": f"Bearer {token}"}).json()
    assert updated_dash["kpis"]["revenue"]["value"] == 2500.0
    assert updated_dash["kpis"]["orders"]["value"] == 1
    assert updated_dash["kpis"]["aov"]["value"] == 2500.0

    # 6. Verify M001 demo dashboard remains untouched
    demo_dash = client.get("/api/dashboard/summary?merchant_id=M001").json()
    assert demo_dash["demo_mode"] is True
    assert demo_dash["kpis"]["revenue"]["value"] > 10000.0


def test_merchant_data_isolation_between_two_users():
    init_db()

    email_1 = f"merchant1.{uuid.uuid4().hex[:6]}@example.com"
    email_2 = f"merchant2.{uuid.uuid4().hex[:6]}@example.com"

    # User 1
    client.post("/api/auth/otp/send", json={"email": email_1, "name": "Merchant One"})
    conn = get_db_connection()
    otp1 = conn.execute("SELECT otp_code FROM otps WHERE identifier = ? AND is_used = 0", (email_1,)).fetchone()["otp_code"]
    conn.close()
    u1_token = client.post("/api/auth/otp/verify", json={"email": email_1, "otp": otp1}).json()["access_token"]

    # User 2
    client.post("/api/auth/otp/send", json={"email": email_2, "name": "Merchant Two"})
    conn = get_db_connection()
    otp2 = conn.execute("SELECT otp_code FROM otps WHERE identifier = ? AND is_used = 0", (email_2,)).fetchone()["otp_code"]
    conn.close()
    u2_token = client.post("/api/auth/otp/verify", json={"email": email_2, "otp": otp2}).json()["access_token"]

    # User 1 records a sale of 5000
    client.post("/api/analytics/cash-sale", headers={"Authorization": f"Bearer {u1_token}"}, json={"amount": 5000.0})

    # User 1 has 5000
    u1_dash = client.get("/api/dashboard/summary", headers={"Authorization": f"Bearer {u1_token}"}).json()
    assert u1_dash["kpis"]["revenue"]["value"] == 5000.0
    assert u1_dash["kpis"]["orders"]["value"] == 1

    # User 2 has 0 (zero leak!)
    u2_dash = client.get("/api/dashboard/summary", headers={"Authorization": f"Bearer {u2_token}"}).json()
    assert u2_dash["kpis"]["revenue"]["value"] == 0.0
    assert u2_dash["kpis"]["orders"]["value"] == 0
