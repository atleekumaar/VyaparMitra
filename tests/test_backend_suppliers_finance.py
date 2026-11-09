"""
Tests for Suppliers and Finance Backend APIs.
Validates vendor purchase inwarding, expense tracking, and P&L calculations.
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


def test_supplier_crud_and_inward_invoice():
    """Validates supplier registration, inward purchase invoice, and automatic stock inwarding."""
    token = get_token("manager")

    # 1. Add supplier
    sup_res = client.post(
        "/api/suppliers",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Agra Flour Mills",
            "contact_person": "Mohan Lal",
            "phone": "+919837001122",
            "email": "agraflour@mills.in",
            "address": "Transport Nagar, Agra",
            "payment_terms": "Net 15",
        },
    )
    assert sup_res.status_code == 201
    sup_id = sup_res.json()["id"]

    # 2. Get an inventory item to test inward stock
    inv_res = client.get("/api/inventory?branch_id=BR_M015_MAIN", headers={"Authorization": f"Bearer {token}"})
    item = inv_res.json()["items"][0]
    prod_id = item["product_id"]
    initial_stock = item["current_stock"]

    # 3. Record inward supplier invoice
    invoice_payload = {
        "branch_id": "BR_M015_MAIN",
        "invoice_number": "AGR-INV-101",
        "total_amount": 5000.0,
        "paid_amount": 2000.0,  # Unpaid 3000
        "items": [
            {"product_id": prod_id, "quantity": 20, "unit_cost": float(item["unit_cost"])}
        ],
        "auto_update_inventory": True,
        "notes": "Weekly raw material delivery",
    }
    inv_proc_res = client.post(
        f"/api/suppliers/{sup_id}/invoices",
        headers={"Authorization": f"Bearer {token}"},
        json=invoice_payload,
    )
    assert inv_proc_res.status_code == 201
    assert inv_proc_res.json()["unpaid_amount"] == 3000.0
    assert inv_proc_res.json()["inventory_items_inwarded"] == 1

    # 4. Verify inventory stock increased by 20
    inv_check = client.get("/api/inventory?branch_id=BR_M015_MAIN", headers={"Authorization": f"Bearer {token}"})
    updated_prod = [x for x in inv_check.json()["items"] if x["product_id"] == prod_id][0]
    assert updated_prod["current_stock"] == initial_stock + 20

    # 5. Verify supplier payable increased by 3000
    sup_check = client.get(f"/api/suppliers/{sup_id}", headers={"Authorization": f"Bearer {token}"})
    assert sup_check.json()["current_payable"] == 3000.0

    # 6. Make payment to supplier
    pay_res = client.post(
        f"/api/suppliers/{sup_id}/payments",
        headers={"Authorization": f"Bearer {token}"},
        json={"amount": 1000.0, "payment_method": "BANK_TRANSFER", "notes": "NEFT ref 12345"},
    )
    assert pay_res.status_code == 200
    assert pay_res.json()["remaining_payable"] == 2000.0


def test_expenses_and_finance_summary():
    """Validates expense logging, P&L calculations, and cashflow."""
    owner_token = get_token("owner")

    # Record expense
    exp_payload = {
        "branch_id": "BR_M015_MAIN",
        "category": "UTILITY",
        "amount": 1500.0,
        "payment_method": "UPI",
        "description": "Internet broadband connection",
    }
    exp_res = client.post("/api/finance/expenses", headers={"Authorization": f"Bearer {owner_token}"}, json=exp_payload)
    assert exp_res.status_code == 201
    assert exp_res.json()["amount"] == 1500.0

    # List expenses
    exp_list = client.get("/api/finance/expenses", headers={"Authorization": f"Bearer {owner_token}"})
    assert exp_list.status_code == 200
    assert exp_list.json()["total_count"] >= 1

    # Finance P&L summary
    summary_res = client.get("/api/finance/summary", headers={"Authorization": f"Bearer {owner_token}"})
    assert summary_res.status_code == 200
    s_data = summary_res.json()
    assert "total_sales_revenue" in s_data
    assert "gross_profit" in s_data
    assert "net_profit" in s_data
    assert "total_receivables_khata" in s_data
    assert "total_payables_suppliers" in s_data

    # Cashflow summary
    cf_res = client.get("/api/finance/cashflow", headers={"Authorization": f"Bearer {owner_token}"})
    assert cf_res.status_code == 200
    assert "daily_breakdown" in cf_res.json()
