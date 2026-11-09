"""
Tests for Customer Management & Khata (Udhaar / Credit Ledger) APIs.
Validates credit limits, ledger entries, and repayment recording.
"""

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


def test_customer_creation_and_listing():
    """Validates creating and listing customers."""
    token = get_token("manager")
    payload = {
        "name": "Ajay Verma",
        "phone": "+919811002233",
        "email": "ajay.verma@example.com",
        "address": "Flat 302, ATS Village",
        "city": "Noida",
        "credit_limit": 8000.0,
    }
    create_res = client.post("/api/customer-ops", headers={"Authorization": f"Bearer {token}"}, json=payload)
    assert create_res.status_code == 201
    cust_data = create_res.json()
    assert cust_data["name"] == "Ajay Verma"
    assert cust_data["credit_limit"] == 8000.0
    assert cust_data["current_balance"] == 0.0

    # List customers
    list_res = client.get("/api/customer-ops?search=Ajay", headers={"Authorization": f"Bearer {token}"})
    assert list_res.status_code == 200
    assert list_res.json()["total_customers"] >= 1


def test_credit_sale_and_khata_ledger_flow():
    """Validates complete flow: Credit Sale -> Balance Increase -> Ledger Debit -> Repayment -> Ledger Credit."""
    token = get_token("manager")
    staff_token = get_token("staff")

    # 1. Create a customer with known credit limit
    cust_res = client.post(
        "/api/customer-ops",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Sunil Khata Test",
            "phone": "+919999888877",
            "credit_limit": 2000.0,
        },
    )
    cust_id = cust_res.json()["id"]

    # 2. Get an available inventory product
    inv_res = client.get("/api/inventory", headers={"Authorization": f"Bearer {staff_token}"})
    prod = inv_res.json()["items"][0]
    prod_id = prod["product_id"]

    # 3. Perform Credit Sale within limit
    sale_res = client.post(
        "/api/sales",
        headers={"Authorization": f"Bearer {staff_token}"},
        json={
            "branch_id": "BR_M015_MAIN",
            "customer_id": cust_id,
            "items": [{"product_id": prod_id, "quantity": 1}],
            "payment_method": "CREDIT",
        },
    )
    assert sale_res.status_code == 201
    sale_amount = sale_res.json()["total_amount"]

    # 4. Check customer balance
    c_check = client.get(f"/api/customer-ops/{cust_id}", headers={"Authorization": f"Bearer {token}"})
    assert c_check.json()["current_balance"] == sale_amount

    # 5. Check Ledger statement
    ledger_res = client.get(f"/api/customer-ops/{cust_id}/ledger", headers={"Authorization": f"Bearer {token}"})
    assert ledger_res.status_code == 200
    entries = ledger_res.json()["entries"]
    assert len(entries) >= 1
    assert entries[-1]["entry_type"] == "DEBIT"
    assert entries[-1]["amount"] == sale_amount

    # 6. Customer makes partial repayment
    pay_amount = min(50.0, sale_amount)
    pay_res = client.post(
        f"/api/customer-ops/{cust_id}/payment",
        headers={"Authorization": f"Bearer {token}"},
        json={"amount": pay_amount, "payment_method": "UPI", "notes": "Partial repayment via GPay"},
    )
    assert pay_res.status_code == 200
    assert pay_res.json()["current_balance"] == round(sale_amount - pay_amount, 2)


def test_credit_sale_limit_breach_rejection():
    """Validates that credit sales exceeding credit limit are rejected."""
    token = get_token("manager")
    staff_token = get_token("staff")

    # Create customer with very small credit limit (₹50)
    cust_res = client.post(
        "/api/customer-ops",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Low Credit Customer", "credit_limit": 50.0},
    )
    cust_id = cust_res.json()["id"]

    inv_res = client.get("/api/inventory", headers={"Authorization": f"Bearer {staff_token}"})
    prod = inv_res.json()["items"][0]

    # Attempt credit sale that exceeds ₹50
    sale_res = client.post(
        "/api/sales",
        headers={"Authorization": f"Bearer {staff_token}"},
        json={
            "branch_id": "BR_M015_MAIN",
            "customer_id": cust_id,
            "items": [{"product_id": prod["product_id"], "quantity": 10}],
            "payment_method": "CREDIT",
        },
    )
    assert sale_res.status_code == 400
    assert "Credit limit exceeded" in sale_res.json()["error"]["message"]
