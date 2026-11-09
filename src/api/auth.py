"""
Authentication, Authorization and Role-Based Access Control (RBAC) for VyaparMitra.
Provides JWT issuance, password verification, permission enforcement, and branch isolation.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import jwt
from fastapi import Depends, Header, HTTPException, Request, status
from pydantic import BaseModel, Field

from src.api.config import get_api_config
from src.api.db import get_db, hash_password

logger = logging.getLogger("vyaparmitra.api.auth")


class UserRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"


ROLE_PERMISSIONS: Dict[str, List[str]] = {
    UserRole.OWNER.value: [
        "auth:manage_users",
        "branches:manage",
        "sales:create",
        "sales:view_all",
        "sales:refund",
        "inventory:view",
        "inventory:manage",
        "inventory:adjust",
        "customers:view",
        "customers:manage",
        "customers:khata",
        "suppliers:view",
        "suppliers:manage",
        "finance:view_pl",
        "finance:expenses",
        "audit:view",
    ],
    UserRole.ADMIN.value: [
        "auth:manage_users",
        "branches:manage",
        "sales:create",
        "sales:view_all",
        "sales:refund",
        "inventory:view",
        "inventory:manage",
        "inventory:adjust",
        "customers:view",
        "customers:manage",
        "customers:khata",
        "suppliers:view",
        "suppliers:manage",
        "finance:view_pl",
        "finance:expenses",
        "audit:view",
    ],
    UserRole.MANAGER.value: [
        "sales:create",
        "sales:view_branch",
        "sales:refund",
        "inventory:view",
        "inventory:adjust",
        "customers:view",
        "customers:manage",
        "customers:khata",
        "suppliers:view",
        "suppliers:manage",
        "finance:view_branch",
        "finance:expenses",
        "auth:view_staff",
    ],
    UserRole.STAFF.value: [
        "sales:create",
        "sales:view_branch",
        "inventory:view",
        "customers:view",
        "customers:create_walkin",
    ],
}


class CurrentUser(BaseModel):
    id: str
    business_id: str
    branch_id: Optional[str] = None
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool = True
    permissions: List[str] = Field(default_factory=list)


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """Verifies a plain-text password against a stored PBKDF2 hash."""
    try:
        parts = stored_hash.split("$")
        if len(parts) != 3 or not parts[0].startswith("pbkdf2:sha256:"):
            return False
        iterations = int(parts[0].split(":")[2])
        salt = parts[1]
        expected_hex = parts[2]

        derived = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations,
        )
        return hmac.compare_digest(derived.hex(), expected_hex)
    except Exception as exc:
        logger.error(f"Error during password verification: {exc}")
        return False


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generates an RFC-compliant signed JWT access token."""
    config = get_api_config()
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=config.jwt_expire_minutes)

    to_encode.update({"exp": int(expire.timestamp())})
    encoded_jwt = jwt.encode(to_encode, config.jwt_secret_key, algorithm=config.jwt_algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decodes and validates a JWT token."""
    config = get_api_config()
    try:
        payload = jwt.decode(token, config.jwt_secret_key, algorithms=[config.jwt_algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired. Please log in again.",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token signature.",
        )


def get_current_user(
    request: Request,
    authorization: Optional[str] = Header(None),
    db: Any = Depends(get_db),
) -> CurrentUser:
    """
    FastAPI dependency extracting and verifying user identity from Authorization header.
    In demo_mode, if no Authorization header is provided, safely defaults to demo Owner.
    """
    config = get_api_config()

    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1].strip()
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload is missing subject (user_id).",
            )

        row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account no longer exists.",
            )

        if not row["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated. Contact business administrator.",
            )

        role = row["role"]
        permissions = ROLE_PERMISSIONS.get(role, [])
        return CurrentUser(
            id=row["id"],
            business_id=row["business_id"],
            branch_id=row["branch_id"],
            username=row["username"],
            email=row["email"],
            full_name=row["full_name"],
            role=role,
            is_active=bool(row["is_active"]),
            permissions=permissions,
        )

    # If demo mode is active and no Authorization header provided, fall back to seed owner
    if config.demo_mode:
        row = db.execute("SELECT * FROM users WHERE username = 'owner_m015'").fetchone()
        if row:
            return CurrentUser(
                id=row["id"],
                business_id=row["business_id"],
                branch_id=row["branch_id"],
                username=row["username"],
                email=row["email"],
                full_name=row["full_name"],
                role=row["role"],
                is_active=bool(row["is_active"]),
                permissions=ROLE_PERMISSIONS.get(row["role"], []),
            )
        # Fallback if seed user not in DB yet
        return CurrentUser(
            id="USR_OWNER_DEMO",
            business_id="M015",
            branch_id="BR_M015_MAIN",
            username="demo_owner",
            email="owner@vyaparmitra.com",
            full_name="Demo Owner",
            role="owner",
            is_active=True,
            permissions=ROLE_PERMISSIONS.get("owner", []),
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authorization header required. Format: Bearer <token>",
    )


def require_roles(allowed_roles: List[str]) -> Callable:
    """
    Role-Based Access Control decorator/dependency.
    Enforces that current user belongs to one of the authorized roles.
    Owner and Admin are mutually aliased with top permissions.
    """
    normalized_allowed = [r.lower() for r in allowed_roles]
    if "owner" in normalized_allowed and "admin" not in normalized_allowed:
        normalized_allowed.append("admin")
    if "admin" in normalized_allowed and "owner" not in normalized_allowed:
        normalized_allowed.append("owner")

    def role_dependency(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role.lower() not in normalized_allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: requires role in {allowed_roles}. Your current role is '{user.role}'.",
            )
        return user

    return role_dependency


def enforce_branch_isolation(user: CurrentUser, target_branch_id: Optional[str] = None) -> Optional[str]:
    """
    Enforces multi-branch data isolation:
    - Staff are strictly scoped to their assigned branch.
    - Managers can only operate within their assigned branch (unless multi-branch manager).
    - Owners/Admins have full visibility across all branches of their business.
    """
    if user.role.lower() == UserRole.STAFF.value:
        if target_branch_id and target_branch_id != user.branch_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Data isolation violation: Staff can only access their assigned branch '{user.branch_id}'.",
            )
        return user.branch_id

    if user.role.lower() == UserRole.MANAGER.value:
        if user.branch_id and target_branch_id and target_branch_id != user.branch_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Data isolation violation: Manager restricted to assigned branch '{user.branch_id}'.",
            )
        return target_branch_id or user.branch_id

    # Owner / Admin can target any branch or query across all branches
    return target_branch_id

