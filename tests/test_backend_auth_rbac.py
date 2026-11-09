"""
Tests for Backend Authentication, Authorization and Role-Based Access Control (RBAC).
Validates Owner/Admin, Manager, and Staff roles and permissions.
"""

import uuid
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_seed_owner_login():
    """Validates login with default seed Owner credentials."""
    response = client.post(
        "/api/auth/login",
        json={"username_or_email": "owner_m015", "password": "OwnerPassword123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "owner"
    assert data["user"]["business_id"] == "M015"
    assert "sales:create" in data["permissions"]
    assert "auth:manage_users" in data["permissions"]


def test_seed_manager_login():
    """Validates login with default seed Manager credentials."""
    response = client.post(
        "/api/auth/login",
        json={"username_or_email": "manager_m015", "password": "ManagerPassword123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["role"] == "manager"
    assert "sales:create" in data["permissions"]
    assert "auth:manage_users" not in data["permissions"]


def test_seed_staff_login():
    """Validates login with default seed Staff credentials."""
    response = client.post(
        "/api/auth/login",
        json={"username_or_email": "staff_m015", "password": "StaffPassword123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["role"] == "staff"
    assert "sales:create" in data["permissions"]
    assert "sales:refund" not in data["permissions"]


def test_login_invalid_password():
    """Validates rejection of incorrect passwords."""
    response = client.post(
        "/api/auth/login",
        json={"username_or_email": "owner_m015", "password": "WrongPassword!"},
    )
    assert response.status_code == 401
    assert "error" in response.json()


def test_register_new_business_and_owner():
    """Validates new business self-registration flow."""
    uid = uuid.uuid4().hex[:6]
    unique_user = f"owner_{uid}"
    unique_email = f"owner_{uid}@testbiz.com"
    payload = {
        "business_name": "Sharma Supermarket",
        "business_type": "Grocery",
        "gstin": "07AAAAA1111A1Z1",
        "city": "Ghaziabad",
        "state": "Uttar Pradesh",
        "address": "Shop 4, Raj Nagar",
        "phone": "+919876500999",
        "owner_username": unique_user,
        "owner_email": unique_email,
        "owner_full_name": "Ramesh Sharma",
        "owner_password": "SecureOwnerPassword1!",
    }

    # Register
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert "access_token" in data
    assert data["user"]["username"] == unique_user
    assert data["user"]["role"] == "owner"
    token = data["access_token"]

    # Verify /me with Bearer token
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["username"] == unique_user

    # Duplicate registration should be rejected
    dup_res = client.post("/api/auth/register", json=payload)
    assert dup_res.status_code == 400


def test_owner_creates_manager_and_staff():
    """Validates Owner creating subordinate roles."""
    login_res = client.post(
        "/api/auth/login",
        json={"username_or_email": "owner_m015", "password": "OwnerPassword123!"},
    )
    owner_token = login_res.json()["access_token"]

    uid = uuid.uuid4().hex[:6]
    mgr_payload = {
        "username": f"mgr_{uid}",
        "email": f"mgr_{uid}@vyaparmitra.com",
        "full_name": "Sub Manager One",
        "password": "Password123!",
        "role": "manager",
        "branch_id": "BR_M015_MAIN",
    }
    mgr_res = client.post(
        "/api/auth/users",
        headers={"Authorization": f"Bearer {owner_token}"},
        json=mgr_payload,
    )
    assert mgr_res.status_code == 201

    # List users
    users_res = client.get("/api/auth/users", headers={"Authorization": f"Bearer {owner_token}"})
    assert users_res.status_code == 200
    assert len(users_res.json()) >= 3


def test_staff_cannot_create_user():
    """Validates RBAC: Staff role cannot create other users."""
    staff_login = client.post(
        "/api/auth/login",
        json={"username_or_email": "staff_m015", "password": "StaffPassword123!"},
    )
    staff_token = staff_login.json()["access_token"]

    res = client.post(
        "/api/auth/users",
        headers={"Authorization": f"Bearer {staff_token}"},
        json={
            "username": "unauthorized_user",
            "email": "unauth@test.com",
            "full_name": "Unauthorized",
            "password": "Password123!",
            "role": "staff",
        },
    )
    assert res.status_code == 403


def test_roles_directory():
    """Validates the 3-role permission matrix endpoint."""
    res = client.get("/api/auth/roles")
    assert res.status_code == 200
    roles = res.json()["roles"]
    role_names = [r["role"] for r in roles]
    assert "owner" in role_names
    assert "manager" in role_names
    assert "staff" in role_names
