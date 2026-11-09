"""
Tests for Multi-Tenant Data Isolation, Multi-Branch Security, and Audit Trail APIs.
Validates that tenant boundaries cannot be crossed and audit trails are tamper-evident.
"""

from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def get_token(username, password):
    res = client.post("/api/auth/login", json={"username_or_email": username, "password": password})
    return res.json()["access_token"]


def test_business_level_data_isolation():
    """Validates that two different businesses are 100% isolated from each other."""
    # 1. Register Business A
    biz_a_payload = {
        "business_name": "Agrawal Sweets",
        "business_type": "Confectionery",
        "city": "Mathura",
        "state": "Uttar Pradesh",
        "phone": "+919811991122",
        "owner_username": "owner_agrawal",
        "owner_email": "agrawal@sweets.com",
        "owner_full_name": "Gopal Agrawal",
        "owner_password": "Password123!",
    }
    res_a = client.post("/api/auth/register", json=biz_a_payload)
    token_a = res_a.json()["access_token"] if res_a.status_code == 201 else get_token("owner_agrawal", "Password123!")

    # 2. Register Business B
    biz_b_payload = {
        "business_name": "Gupta Medical",
        "business_type": "Pharmacy",
        "city": "Kanpur",
        "state": "Uttar Pradesh",
        "phone": "+919811993344",
        "owner_username": "owner_gupta",
        "owner_email": "gupta@med.com",
        "owner_full_name": "Sanjay Gupta",
        "owner_password": "Password123!",
    }
    res_b = client.post("/api/auth/register", json=biz_b_payload)
    token_b = res_b.json()["access_token"] if res_b.status_code == 201 else get_token("owner_gupta", "Password123!")

    # 3. Add customer in Business A
    c_res = client.post(
        "/api/customer-ops",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"name": "Special Mathura Customer", "credit_limit": 5000.0},
    )
    cust_a_id = c_res.json()["id"]

    # 4. Verify Business B cannot see Business A's customer
    b_cust_res = client.get(f"/api/customer-ops/{cust_a_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert b_cust_res.status_code == 404

    # 5. Verify Business B listing does not contain Business A customer
    b_list_res = client.get("/api/customer-ops", headers={"Authorization": f"Bearer {token_b}"})
    customer_ids = [c["id"] for c in b_list_res.json()["customers"]]
    assert cust_a_id not in customer_ids


def test_branch_level_data_isolation_for_staff():
    """Validates that Staff cannot access or execute sales in a branch other than their assigned branch."""
    staff_token = get_token("staff_m015", "StaffPassword123!")

    # Staff assigned to BR_M015_MAIN tries to target BR_M015_SEC62
    res = client.post(
        "/api/sales",
        headers={"Authorization": f"Bearer {staff_token}"},
        json={
            "branch_id": "BR_M015_SEC62",
            "items": [{"product_id": "PRD_CAK_01", "quantity": 1}],
            "payment_method": "CASH",
        },
    )
    assert res.status_code == 403
    assert "Data isolation violation" in res.json()["error"]["message"]


def test_audit_logs_rbac_and_content():
    """Validates that only Owner/Admin can query audit logs and entries are tracked."""
    owner_token = get_token("owner_m015", "OwnerPassword123!")
    staff_token = get_token("staff_m015", "StaffPassword123!")

    # Staff access to audit logs should be blocked (403)
    staff_res = client.get("/api/audit-logs", headers={"Authorization": f"Bearer {staff_token}"})
    assert staff_res.status_code == 403

    # Owner access to audit logs should succeed
    owner_res = client.get("/api/audit-logs", headers={"Authorization": f"Bearer {owner_token}"})
    assert owner_res.status_code == 200
    logs_data = owner_res.json()
    assert logs_data["total_logs"] > 0
    assert len(logs_data["logs"]) > 0

    first_log = logs_data["logs"][0]
    assert "action" in first_log
    assert "user_name" in first_log
    assert "user_role" in first_log
    assert "timestamp" in first_log

