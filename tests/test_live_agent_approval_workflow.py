"""
End-to-End Live Database & JWT Auth Integration Test for MerchantOS Agents.
Demonstrates:
Inventory Alert -> Agent Recommendation -> Persistent L3 Draft -> Owner Approval -> Live DB Stock Update + Audit Log.
"""
import uuid
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

from src.api.main import create_app
from src.api.db import init_db, get_db_connection, hash_password
from src.api.auth import create_access_token


@pytest.fixture
def live_env():
    init_db()
    app = create_app()
    client = TestClient(app)

    conn = get_db_connection()
    now = datetime.now(timezone.utc).isoformat()
    biz_id = f"biz_{uuid.uuid4().hex[:8]}"
    branch_id = f"br_{uuid.uuid4().hex[:8]}"
    owner_id = f"usr_own_{uuid.uuid4().hex[:6]}"
    mgr_id = f"usr_mgr_{uuid.uuid4().hex[:6]}"
    staff_id = f"usr_stf_{uuid.uuid4().hex[:6]}"
    inv_id = f"inv_{uuid.uuid4().hex[:8]}"
    sku = "SKU-MUSTARD-1L"

    # Seed live business, branch, users, inventory, sale, and customer udhaar
    conn.execute(
        "INSERT INTO businesses (id, name, city, state, created_at) VALUES (?, 'Lucknow Kirana Mart', 'Lucknow', 'UP', ?)",
        (biz_id, now),
    )
    conn.execute(
        "INSERT INTO branches (id, business_id, name, code, is_main, created_at) VALUES (?, ?, 'Hazratganj Main', 'HZG', 1, ?)",
        (branch_id, biz_id, now),
    )
    for uid, uname, role in [
        (owner_id, f"owner_{biz_id}", "owner"),
        (mgr_id, f"mgr_{biz_id}", "manager"),
        (staff_id, f"staff_{biz_id}", "staff"),
    ]:
        conn.execute(
            """INSERT INTO users (id, business_id, branch_id, username, email, full_name, password_hash, role, is_active, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?)""",
            (uid, biz_id, branch_id, uname, f"{uname}@test.com", uname.upper(), hash_password("Pass@123"), role, now),
        )

    # Low stock item: 3 left vs min threshold 10
    conn.execute(
        """INSERT INTO inventory (id, business_id, branch_id, product_id, product_name, category, current_stock, min_stock_threshold, unit_cost, selling_price, updated_at)
           VALUES (?, ?, ?, ?, 'Fortune Mustard Oil 1L', 'Grocery', 3, 10, 120.0, 145.0, ?)""",
        (inv_id, biz_id, branch_id, sku, now),
    )
    conn.execute(
        """INSERT INTO sales (id, invoice_number, business_id, branch_id, subtotal, total_amount, payment_method, status, created_by, created_at)
           VALUES (?, ?, ?, ?, 2900.0, 2900.0, 'UPI', 'COMPLETED', ?, ?)""",
        (f"sal_{uuid.uuid4().hex[:8]}", f"INV-{uuid.uuid4().hex[:6]}", biz_id, branch_id, owner_id, now),
    )
    conn.execute(
        """INSERT INTO customers (id, business_id, name, phone, current_balance, created_at)
           VALUES (?, ?, 'Ramesh Verma', '9876543210', 850.0, ?)""",
        (f"cus_{uuid.uuid4().hex[:8]}", biz_id, now),
    )
    conn.commit()
    conn.close()

    tokens = {
        "owner": create_access_token({"sub": owner_id, "business_id": biz_id, "branch_id": branch_id, "role": "owner"}),
        "manager": create_access_token({"sub": mgr_id, "business_id": biz_id, "branch_id": branch_id, "role": "manager"}),
        "staff": create_access_token({"sub": staff_id, "business_id": biz_id, "branch_id": branch_id, "role": "staff"}),
    }
    return {"client": client, "tokens": tokens, "biz_id": biz_id, "branch_id": branch_id, "sku": sku, "inv_id": inv_id}


def test_complete_inventory_alert_to_owner_approval_workflow(live_env):
    client = live_env["client"]
    tokens = live_env["tokens"]
    sku = live_env["sku"]
    inv_id = live_env["inv_id"]

    # 1. Inventory Alert (Live DB check)
    res_alert = client.post(
        "/api/copilot/agent/execute",
        json={"query": "Check low stock alert"},
        headers={"Authorization": f"Bearer {tokens['staff']}"},
    )
    assert res_alert.status_code == 200
    body_alert = res_alert.json()
    assert body_alert["intent"] == "INVENTORY_QUERY"
    assert "Fortune Mustard Oil 1L" in body_alert["response"]
    assert "3 left" in body_alert["response"]

    # 2. Staff Finance Access Blocked
    res_staff_fin = client.post(
        "/api/copilot/agent/execute",
        json={"query": "Show profit and udhaar"},
        headers={"Authorization": f"Bearer {tokens['staff']}"},
    )
    assert res_staff_fin.status_code == 200
    assert res_staff_fin.json()["intent"] == "RESTRICTED"

    # 3. Manager triggers Reorder Recommendation -> Persisted L3 Draft
    res_draft = client.post(
        "/api/copilot/agent/execute",
        json={"query": "Reorder 20 units of Fortune Mustard Oil"},
        headers={"Authorization": f"Bearer {tokens['manager']}"},
    )
    assert res_draft.status_code == 200
    draft_data = res_draft.json()
    assert draft_data["intent"] == "PURCHASE_REORDER_DRAFT"
    assert len(draft_data["draft_actions"]) == 1
    approval_id = draft_data["draft_actions"][0]["approval_id"]
    assert draft_data["draft_actions"][0]["status"] == "PENDING_APPROVAL"
    assert draft_data["draft_actions"][0]["persisted"] is True

    # 4. Manager cannot approve own L3 draft (403 Forbidden)
    res_mgr_approve = client.post(
        f"/api/copilot/approvals/{approval_id}/approve",
        json={"notes": "Trying self-approval"},
        headers={"Authorization": f"Bearer {tokens['manager']}"},
    )
    assert res_mgr_approve.status_code == 403

    # 5. Owner approves draft -> Executes live stock update (+20 units -> 23)
    res_owner_approve = client.post(
        f"/api/copilot/approvals/{approval_id}/approve",
        json={"notes": "Approved for morning delivery"},
        headers={"Authorization": f"Bearer {tokens['owner']}"},
    )
    assert res_owner_approve.status_code == 200
    approved_payload = res_owner_approve.json()
    assert approved_payload["status"] == "APPROVED"
    assert approved_payload["quantity_added"] == 20
    assert approved_payload["updated_stock"] == 23

    # Verify live DB stock & audit log persistence
    conn = get_db_connection()
    stock_now = conn.execute("SELECT current_stock FROM inventory WHERE id = ?", (inv_id,)).fetchone()[0]
    audit_row = conn.execute("SELECT action FROM audit_logs WHERE resource_id = ?", (approval_id,)).fetchone()
    conn.close()
    assert stock_now == 23
    assert audit_row is not None
    assert audit_row[0] == "AGENT_APPROVAL_EXECUTED"


def test_live_finance_and_owner_rejection_flow(live_env):
    client = live_env["client"]
    tokens = live_env["tokens"]

    # Live Finance & Briefing check by Owner
    res_fin = client.post(
        "/api/copilot/agent/execute",
        json={"query": "Show financial summary and udhaar"},
        headers={"Authorization": f"Bearer {tokens['owner']}"},
    )
    assert res_fin.status_code == 200
    assert "2,900.00" in res_fin.json()["response"]
    assert "850.00" in res_fin.json()["response"]

    # Draft & Reject flow
    res_draft = client.post(
        "/api/copilot/agent/execute",
        json={"query": "Reorder 15 units of Fortune Mustard Oil"},
        headers={"Authorization": f"Bearer {tokens['manager']}"},
    )
    approval_id = res_draft.json()["draft_actions"][0]["approval_id"]

    res_reject = client.post(
        f"/api/copilot/approvals/{approval_id}/reject",
        json={"notes": "Already ordered offline"},
        headers={"Authorization": f"Bearer {tokens['owner']}"},
    )
    assert res_reject.status_code == 200
    assert res_reject.json()["status"] == "REJECTED"
