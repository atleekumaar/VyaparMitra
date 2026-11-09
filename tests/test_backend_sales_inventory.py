"""
Tests for Sales and Inventory Backend APIs.
Validates atomic stock updates, POS checkout, low-stock threshold alerts, and refunds.
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


def test_inventory_list_and_details():
    """Validates inventory listing with valuation."""
    token = get_token("manager")
    res = client.get("/api/inventory?branch_id=BR_M015_MAIN", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["total_count"] > 0
    assert data["total_stock_units"] > 0
    assert data["total_valuation_cost"] > 0
    first_item = data["items"][0]
    assert "current_stock" in first_item
    assert "min_stock_threshold" in first_item
    assert "unit_cost" in first_item


def test_stock_adjustment_and_rbac():
    """Validates stock adjustments by Manager and rejection for Staff."""
    mgr_token = get_token("manager")
    staff_token = get_token("staff")

    # Get an inventory item
    inv_res = client.get("/api/inventory", headers={"Authorization": f"Bearer {mgr_token}"})
    item = inv_res.json()["items"][0]
    item_id = item["id"]
    initial_stock = item["current_stock"]

    # Staff attempt to adjust stock should fail (403)
    staff_res = client.post(
        "/api/inventory/adjust",
        headers={"Authorization": f"Bearer {staff_token}"},
        json={
            "inventory_id": item_id,
            "adjustment_type": "INCREASE",
            "quantity": 10,
            "reason": "RESTOCK",
        },
    )
    assert staff_res.status_code == 403

    # Manager adjust stock (INCREASE)
    mgr_res = client.post(
        "/api/inventory/adjust",
        headers={"Authorization": f"Bearer {mgr_token}"},
        json={
            "inventory_id": item_id,
            "adjustment_type": "INCREASE",
            "quantity": 25,
            "reason": "RESTOCK",
        },
    )
    assert mgr_res.status_code == 200
    assert mgr_res.json()["current_stock"] == initial_stock + 25


def test_pos_sale_atomic_stock_deduction():
    """Validates that a POS sale atomically decrements stock in the inventory table."""
    staff_token = get_token("staff")

    # Pick an item
    inv_res = client.get("/api/inventory?branch_id=BR_M015_MAIN", headers={"Authorization": f"Bearer {staff_token}"})
    item = inv_res.json()["items"][0]
    prod_id = item["product_id"]
    initial_stock = item["current_stock"]

    sale_qty = 3
    sale_payload = {
        "branch_id": "BR_M015_MAIN",
        "items": [
            {"product_id": prod_id, "quantity": sale_qty}
        ],
        "payment_method": "UPI",
        "discount": 10.0,
        "tax": 5.0,
        "notes": "Test POS Checkout",
    }

    # Execute Sale
    res = client.post(
        "/api/sales",
        headers={"Authorization": f"Bearer {staff_token}"},
        json=sale_payload,
    )
    assert res.status_code == 201
    sale_data = res.json()
    assert sale_data["status"] == "COMPLETED"
    assert sale_data["payment_method"] == "UPI"
    assert len(sale_data["items"]) == 1
    assert "INV-" in sale_data["invoice_number"]

    # Verify inventory was decremented in DB
    updated_inv_res = client.get("/api/inventory?branch_id=BR_M015_MAIN", headers={"Authorization": f"Bearer {staff_token}"})
    updated_item = [x for x in updated_inv_res.json()["items"] if x["product_id"] == prod_id][0]
    assert updated_item["current_stock"] == initial_stock - sale_qty


def test_pos_sale_insufficient_stock_rejection():
    """Validates that sales exceeding available inventory are rejected."""
    staff_token = get_token("staff")

    inv_res = client.get("/api/inventory?branch_id=BR_M015_MAIN", headers={"Authorization": f"Bearer {staff_token}"})
    item = inv_res.json()["items"][0]
    prod_id = item["product_id"]
    current_stock = item["current_stock"]

    # Attempt to sell more than available
    sale_payload = {
        "branch_id": "BR_M015_MAIN",
        "items": [
            {"product_id": prod_id, "quantity": current_stock + 1000}
        ],
        "payment_method": "CASH",
    }

    res = client.post("/api/sales", headers={"Authorization": f"Bearer {staff_token}"}, json=sale_payload)
    assert res.status_code == 400
    assert "Insufficient stock" in res.json()["error"]["message"]


def test_refund_sale_restores_stock():
    """Validates refund process and inventory restoration."""
    staff_token = get_token("staff")
    mgr_token = get_token("manager")

    inv_res = client.get("/api/inventory?branch_id=BR_M015_MAIN", headers={"Authorization": f"Bearer {staff_token}"})
    item = inv_res.json()["items"][0]
    prod_id = item["product_id"]
    initial_stock = item["current_stock"]

    # Create sale
    sale_res = client.post(
        "/api/sales",
        headers={"Authorization": f"Bearer {staff_token}"},
        json={
            "branch_id": "BR_M015_MAIN",
            "items": [{"product_id": prod_id, "quantity": 2}],
            "payment_method": "CASH",
        },
    )
    sale_id = sale_res.json()["id"]

    # Staff attempt to refund should fail (403)
    staff_refund = client.post(f"/api/sales/{sale_id}/refund", headers={"Authorization": f"Bearer {staff_token}"})
    assert staff_refund.status_code == 403

    # Manager refund should succeed
    mgr_refund = client.post(f"/api/sales/{sale_id}/refund", headers={"Authorization": f"Bearer {mgr_token}"})
    assert mgr_refund.status_code == 200
    assert mgr_refund.json()["status"] == "REFUNDED"

    # Verify stock restored back to initial_stock
    inv_check = client.get("/api/inventory?branch_id=BR_M015_MAIN", headers={"Authorization": f"Bearer {staff_token}"})
    curr_item = [x for x in inv_check.json()["items"] if x["product_id"] == prod_id][0]
    assert curr_item["current_stock"] == initial_stock

