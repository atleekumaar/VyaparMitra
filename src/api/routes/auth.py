"""
Authentication and User Management Routes for VyaparMitra.
Provides user registration, login, role enforcement, and user administration.
"""

from __future__ import annotations

import logging
import secrets
import sqlite3
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status

from src.api.audit import record_audit_log
from src.api.auth import (
    CurrentUser,
    ROLE_PERMISSIONS,
    UserRole,
    create_access_token,
    get_current_user,
    hash_password,
    require_roles,
    verify_password,
)
from src.api.backend_schemas import (
    CreateUserRequest,
    LoginRequest,
    RegisterBusinessRequest,
    RequestOtpRequest,
    RequestOtpResponse,
    RoleInfoItem,
    RolesListResponse,
    TokenResponse,
    UserResponse,
    VerifyOtpRequest,
)
from src.api.config import get_api_config
from src.api.db import get_db
from src.api.services.email_service import get_email_service

logger = logging.getLogger("vyaparmitra.api.auth")
router = APIRouter(prefix="/auth", tags=["Authentication & Access Control"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new business and owner account",
)
def register_business(
    req: RegisterBusinessRequest,
    request: Request,
    db: sqlite3.Connection = Depends(get_db),
) -> TokenResponse:
    """Registers a new merchant business along with an Owner/Admin account."""
    now_str = datetime.now(timezone.utc).isoformat()

    # Check if username or email already taken
    existing_user = db.execute(
        "SELECT id FROM users WHERE username = ? OR email = ?",
        (req.owner_username.strip(), req.owner_email.strip().lower()),
    ).fetchone()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered.",
        )

    biz_id = f"BIZ_{uuid.uuid4().hex[:8].upper()}"
    branch_id = f"BR_{biz_id}_MAIN"
    user_id = f"USR_{uuid.uuid4().hex[:8].upper()}"

    # 1. Create Business
    db.execute("""
        INSERT INTO businesses (id, name, business_type, gstin, phone, email, address, city, state, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        biz_id,
        req.business_name.strip(),
        req.business_type.strip(),
        req.gstin.strip() if req.gstin else None,
        req.phone.strip(),
        req.owner_email.strip().lower(),
        req.address.strip() if req.address else None,
        req.city.strip(),
        req.state.strip(),
        now_str,
    ))

    # 2. Create Main Branch
    db.execute("""
        INSERT INTO branches (id, business_id, name, code, city, state, address, phone, is_main, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
    """, (
        branch_id,
        biz_id,
        f"{req.business_name} - Main Branch",
        "MAIN",
        req.city.strip(),
        req.state.strip(),
        req.address.strip() if req.address else None,
        req.phone.strip(),
        now_str,
    ))

    # 3. Create Owner User
    hashed = hash_password(req.owner_password)
    db.execute("""
        INSERT INTO users (id, business_id, branch_id, username, email, full_name, password_hash, role, phone, is_active, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
    """, (
        user_id,
        biz_id,
        branch_id,
        req.owner_username.strip(),
        req.owner_email.strip().lower(),
        req.owner_full_name.strip(),
        hashed,
        UserRole.OWNER.value,
        req.phone.strip(),
        now_str,
    ))

    # Record Audit Log
    record_audit_log(
        db=db,
        business_id=biz_id,
        branch_id=branch_id,
        user_id=user_id,
        user_name=req.owner_full_name.strip(),
        user_role=UserRole.OWNER.value,
        action="REGISTER_BUSINESS",
        resource="business",
        resource_id=biz_id,
        details={"business_name": req.business_name, "owner_username": req.owner_username},
        ip_address=request.client.host if request.client else "127.0.0.1",
    )

    # Issue Token
    token_payload = {
        "sub": user_id,
        "username": req.owner_username.strip(),
        "email": req.owner_email.strip().lower(),
        "business_id": biz_id,
        "branch_id": branch_id,
        "role": UserRole.OWNER.value,
    }
    access_token = create_access_token(token_payload)

    user_resp = UserResponse(
        id=user_id,
        business_id=biz_id,
        branch_id=branch_id,
        username=req.owner_username.strip(),
        email=req.owner_email.strip().lower(),
        full_name=req.owner_full_name.strip(),
        role=UserRole.OWNER.value,
        phone=req.phone.strip(),
        is_active=True,
        created_at=now_str,
    )

    return TokenResponse(
        access_token=access_token,
        user=user_resp,
        permissions=ROLE_PERMISSIONS.get(UserRole.OWNER.value, []),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login to receive an access token and user role profile",
)
def login(
    req: LoginRequest,
    request: Request,
    db: sqlite3.Connection = Depends(get_db),
) -> TokenResponse:
    """Authenticates credentials and returns a signed JWT token."""
    login_id = req.username_or_email.strip().lower()
    user_row = db.execute(
        "SELECT * FROM users WHERE LOWER(username) = ? OR LOWER(email) = ?",
        (login_id, login_id),
    ).fetchone()

    if not user_row or not verify_password(req.password, user_row["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Check your username/email and password.",
        )

    if not user_row["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Contact the business owner.",
        )

    role = user_row["role"]
    token_payload = {
        "sub": user_row["id"],
        "username": user_row["username"],
        "email": user_row["email"],
        "business_id": user_row["business_id"],
        "branch_id": user_row["branch_id"],
        "role": role,
    }
    access_token = create_access_token(token_payload)

    # Record login audit
    record_audit_log(
        db=db,
        business_id=user_row["business_id"],
        branch_id=user_row["branch_id"],
        user_id=user_row["id"],
        user_name=user_row["full_name"],
        user_role=role,
        action="LOGIN",
        resource="auth",
        resource_id=user_row["id"],
        details={"username": user_row["username"]},
        ip_address=request.client.host if request.client else "127.0.0.1",
    )

    user_resp = UserResponse(
        id=user_row["id"],
        business_id=user_row["business_id"],
        branch_id=user_row["branch_id"],
        username=user_row["username"],
        email=user_row["email"],
        full_name=user_row["full_name"],
        role=role,
        phone=user_row["phone"],
        is_active=bool(user_row["is_active"]),
        created_at=user_row["created_at"],
    )

    return TokenResponse(
        access_token=access_token,
        user=user_resp,
        permissions=ROLE_PERMISSIONS.get(role, []),
    )


@router.post(
    "/otp/send",
    response_model=RequestOtpResponse,
    summary="Generate and send a 6-digit OTP via Brevo SMTP relay",
)
@router.post("/otp/request", response_model=RequestOtpResponse, include_in_schema=False)
def request_otp(
    req: RequestOtpRequest,
    request: Request,
    db: sqlite3.Connection = Depends(get_db),
) -> RequestOtpResponse:
    """
    Generates a secure 6-digit OTP, invalidates prior active codes, persists to SQLite,
    and delivers via Brevo SMTP relay.
    """
    clean_email = req.email.strip().lower()
    if "@" not in clean_email or "." not in clean_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A valid email address is required to receive your verification code.",
        )

    config = get_api_config()
    now_utc = datetime.now(timezone.utc)
    expiry_utc = now_utc + timedelta(minutes=config.otp_expiry_minutes)
    now_str = now_utc.isoformat()
    expiry_str = expiry_utc.isoformat()

    # Generate secure 6-digit numeric OTP
    otp_code = f"{secrets.randbelow(900000) + 100000}"
    otp_id = f"OTP_{uuid.uuid4().hex[:10].upper()}"

    # Invalidate previous unused OTPs for this identifier
    db.execute(
        "UPDATE otps SET is_used = 1 WHERE identifier = ? AND is_used = 0",
        (clean_email,),
    )

    # Store fresh OTP record
    db.execute(
        """
        INSERT INTO otps (id, identifier, otp_code, purpose, expires_at, attempts, is_used, created_at)
        VALUES (?, ?, ?, 'LOGIN', ?, 0, 0, ?)
        """,
        (otp_id, clean_email, otp_code, expiry_str, now_str),
    )

    # Dispatch email via Brevo SMTP Service
    email_service = get_email_service()
    delivery_result = email_service.send_otp_email(
        to_email=clean_email,
        otp_code=otp_code,
        merchant_name=req.name,
    )

    # In demo mode, or when running in simulation, provide demo_otp so testing is seamless
    is_simulated = delivery_result.get("mode") == "simulation" or config.demo_mode
    demo_otp = otp_code if is_simulated else None

    # Audit logging
    record_audit_log(
        db=db,
        business_id="M015",
        branch_id="BR_M015_MAIN",
        user_id="SYSTEM",
        user_name=req.name or "Merchant User",
        user_role="GUEST",
        action="REQUEST_OTP",
        resource="auth",
        resource_id=otp_id,
        details={
            "email": clean_email,
            "status": delivery_result.get("status"),
            "delivery_mode": delivery_result.get("mode", "live"),
        },
        ip_address=request.client.host if request.client else "127.0.0.1",
    )

    return RequestOtpResponse(
        success=delivery_result.get("success", True),
        status=delivery_result.get("status", "sent"),
        message=delivery_result.get("message", f"Verification code sent to {clean_email}."),
        destination=clean_email,
        expires_in_seconds=config.otp_expiry_minutes * 60,
        demo_otp=demo_otp,
        delivery_mode=delivery_result.get("mode", "live"),
    )


@router.post(
    "/otp/verify",
    response_model=TokenResponse,
    summary="Verify 6-digit OTP and issue JWT access token",
)
def verify_otp(
    req: VerifyOtpRequest,
    request: Request,
    db: sqlite3.Connection = Depends(get_db),
) -> TokenResponse:
    """
    Validates a 6-digit OTP against SQLite store with expiry check and attempt lockout.
    Upon successful verification, loads or auto-provisions merchant account and returns signed JWT.
    """
    clean_email = req.email.strip().lower()
    clean_otp = req.otp.strip()
    config = get_api_config()
    now_utc = datetime.now(timezone.utc)

    # Check for demo bypass code if demo_mode is enabled
    is_demo_bypass = config.demo_mode and clean_otp == "425026"

    if not is_demo_bypass:
        otp_row = db.execute(
            """
            SELECT * FROM otps 
            WHERE identifier = ? AND is_used = 0 
            ORDER BY created_at DESC LIMIT 1
            """,
            (clean_email,),
        ).fetchone()

        if not otp_row:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active verification code found for this email. Please request a new OTP.",
            )

        # Check maximum retry attempts (locks after 5 failures)
        if otp_row["attempts"] >= 5:
            db.execute("UPDATE otps SET is_used = 1 WHERE id = ?", (otp_row["id"],))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Too many invalid attempts. This verification code has been locked. Please request a new one.",
            )

        # Check expiration
        try:
            expires_at = datetime.fromisoformat(otp_row["expires_at"])
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
        except Exception:
            expires_at = now_utc

        if now_utc > expires_at:
            db.execute("UPDATE otps SET is_used = 1 WHERE id = ?", (otp_row["id"],))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification code has expired. Please request a new code.",
            )

        # Check code match
        if otp_row["otp_code"] != clean_otp:
            db.execute(
                "UPDATE otps SET attempts = attempts + 1 WHERE id = ?",
                (otp_row["id"],),
            )
            attempts_left = 4 - otp_row["attempts"]
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid verification code. {max(0, attempts_left)} attempts remaining.",
            )

        # Mark OTP as successfully used
        db.execute("UPDATE otps SET is_used = 1 WHERE id = ?", (otp_row["id"],))

    # Lookup existing user or auto-provision active merchant
    user_row = db.execute(
        "SELECT * FROM users WHERE LOWER(email) = ?",
        (clean_email,),
    ).fetchone()

    now_str = now_utc.isoformat()
    if not user_row:
        # Auto-provision merchant profile
        user_id = f"USR_{uuid.uuid4().hex[:8].upper()}"
        business_id = req.store_id or "M015"
        branch_id = f"BR_{business_id}_MAIN"

        # Verify business exists or fallback
        biz_exists = db.execute("SELECT id FROM businesses WHERE id = ?", (business_id,)).fetchone()
        if not biz_exists:
            first_biz = db.execute("SELECT id FROM businesses LIMIT 1").fetchone()
            business_id = first_biz["id"] if first_biz else "M015"
            branch_id = f"BR_{business_id}_MAIN"

        base_username = clean_email.split("@")[0].replace(".", "_")
        username = base_username
        suffix = 1
        while db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone():
            username = f"{base_username}_{suffix}"
            suffix += 1

        full_name = req.name.strip() if req.name else username.replace("_", " ").title()
        role = UserRole.OWNER.value

        db.execute(
            """
            INSERT INTO users (id, business_id, branch_id, username, email, full_name, password_hash, role, phone, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
            """,
            (
                user_id,
                business_id,
                branch_id,
                username,
                clean_email,
                full_name,
                hash_password(secrets.token_urlsafe(16)),
                role,
                req.phone.strip() if req.phone else None,
                now_str,
            ),
        )
        user_row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

    role = user_row["role"]
    token_payload = {
        "sub": user_row["id"],
        "username": user_row["username"],
        "email": user_row["email"],
        "business_id": user_row["business_id"],
        "branch_id": user_row["branch_id"],
        "role": role,
    }
    access_token = create_access_token(token_payload)

    # Record login audit log
    record_audit_log(
        db=db,
        business_id=user_row["business_id"],
        branch_id=user_row["branch_id"],
        user_id=user_row["id"],
        user_name=user_row["full_name"],
        user_role=role,
        action="LOGIN_OTP",
        resource="auth",
        resource_id=user_row["id"],
        details={"email": clean_email, "auth_method": "brevo_otp"},
        ip_address=request.client.host if request.client else "127.0.0.1",
    )

    user_resp = UserResponse(
        id=user_row["id"],
        business_id=user_row["business_id"],
        branch_id=user_row["branch_id"],
        username=user_row["username"],
        email=user_row["email"],
        full_name=user_row["full_name"],
        role=role,
        phone=user_row["phone"],
        is_active=bool(user_row["is_active"]),
        created_at=user_row["created_at"],
    )

    return TokenResponse(
        access_token=access_token,
        user=user_resp,
        permissions=ROLE_PERMISSIONS.get(role, []),
    )



@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get profile and role permissions of current user",
)
def get_current_user_profile(
    current_user: CurrentUser = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
) -> UserResponse:
    """Returns current authenticated user details."""
    row = db.execute("SELECT * FROM users WHERE id = ?", (current_user.id,)).fetchone()
    if not row:
        return UserResponse(
            id=current_user.id,
            business_id=current_user.business_id,
            branch_id=current_user.branch_id,
            username=current_user.username,
            email=current_user.email,
            full_name=current_user.full_name,
            role=current_user.role,
            is_active=current_user.is_active,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    return UserResponse(
        id=row["id"],
        business_id=row["business_id"],
        branch_id=row["branch_id"],
        username=row["username"],
        email=row["email"],
        full_name=row["full_name"],
        role=row["role"],
        phone=row["phone"],
        is_active=bool(row["is_active"]),
        created_at=row["created_at"],
    )


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user (Staff or Manager)",
)
def create_user(
    req: CreateUserRequest,
    request: Request,
    current_user: CurrentUser = Depends(require_roles(["owner", "admin", "manager"])),
    db: sqlite3.Connection = Depends(get_db),
) -> UserResponse:
    """Creates a user within the same business. Managers can only create Staff."""
    role_target = req.role.lower().strip()
    if role_target not in [UserRole.OWNER.value, UserRole.ADMIN.value, UserRole.MANAGER.value, UserRole.STAFF.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role '{req.role}'. Allowed: owner, manager, staff",
        )

    # Manager restriction: cannot create owner or admin
    if current_user.role.lower() == UserRole.MANAGER.value:
        if role_target in [UserRole.OWNER.value, UserRole.ADMIN.value, UserRole.MANAGER.value]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Managers are only authorized to create Staff users.",
            )
        # Force staff to same branch as manager
        if current_user.branch_id:
            req.branch_id = current_user.branch_id

    # Check unique username/email
    exists = db.execute(
        "SELECT id FROM users WHERE username = ? OR email = ?",
        (req.username.strip(), req.email.strip().lower()),
    ).fetchone()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email is already registered.",
        )

    user_id = f"USR_{uuid.uuid4().hex[:8].upper()}"
    now_str = datetime.now(timezone.utc).isoformat()
    hashed = hash_password(req.password)
    branch_target = req.branch_id or current_user.branch_id

    db.execute("""
        INSERT INTO users (id, business_id, branch_id, username, email, full_name, password_hash, role, phone, is_active, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
    """, (
        user_id,
        current_user.business_id,
        branch_target,
        req.username.strip(),
        req.email.strip().lower(),
        req.full_name.strip(),
        hashed,
        role_target,
        req.phone.strip() if req.phone else None,
        now_str,
    ))

    # Audit log
    record_audit_log(
        db=db,
        business_id=current_user.business_id,
        branch_id=branch_target,
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="CREATE_USER",
        resource="users",
        resource_id=user_id,
        details={"username": req.username, "role": role_target, "branch_id": branch_target},
        ip_address=request.client.host if request.client else "127.0.0.1",
    )

    return UserResponse(
        id=user_id,
        business_id=current_user.business_id,
        branch_id=branch_target,
        username=req.username.strip(),
        email=req.email.strip().lower(),
        full_name=req.full_name.strip(),
        role=role_target,
        phone=req.phone,
        is_active=True,
        created_at=now_str,
    )


@router.get(
    "/users",
    response_model=List[UserResponse],
    summary="List all users for current business",
)
def list_users(
    current_user: CurrentUser = Depends(require_roles(["owner", "admin", "manager"])),
    db: sqlite3.Connection = Depends(get_db),
) -> List[UserResponse]:
    """Lists users for the merchant business with multi-branch isolation."""
    if current_user.role.lower() == UserRole.MANAGER.value and current_user.branch_id:
        rows = db.execute(
            "SELECT * FROM users WHERE business_id = ? AND branch_id = ? ORDER BY created_at DESC",
            (current_user.business_id, current_user.branch_id),
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT * FROM users WHERE business_id = ? ORDER BY created_at DESC",
            (current_user.business_id,),
        ).fetchall()

    return [
        UserResponse(
            id=r["id"],
            business_id=r["business_id"],
            branch_id=r["branch_id"],
            username=r["username"],
            email=r["email"],
            full_name=r["full_name"],
            role=r["role"],
            phone=r["phone"],
            is_active=bool(r["is_active"]),
            created_at=r["created_at"],
        )
        for r in rows
    ]


@router.get(
    "/roles",
    response_model=RolesListResponse,
    summary="List the 3 merchant roles with permission matrices",
)
def list_roles() -> RolesListResponse:
    """Returns permission breakdown for Owner/Admin, Manager, and Staff."""
    items = [
        RoleInfoItem(
            role="owner",
            title="Business Owner / Administrator",
            description="Complete authority across all branches, full P&L visibility, user management, and audit logs.",
            permissions=ROLE_PERMISSIONS["owner"],
        ),
        RoleInfoItem(
            role="manager",
            title="Store / Branch Manager",
            description="Manages assigned branch inventory adjustments, sales records, customer Khata, supplier purchases, and branch staff.",
            permissions=ROLE_PERMISSIONS["manager"],
        ),
        RoleInfoItem(
            role="staff",
            title="POS Cashier / Sales Staff",
            description="Fast point-of-sale checkout, customer lookups, and inventory availability checks within their assigned branch.",
            permissions=ROLE_PERMISSIONS["staff"],
        ),
    ]
    return RolesListResponse(roles=items)

