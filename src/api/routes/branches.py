"""
Branch Management Routes for VyaparMitra Multi-Branch Architecture.
"""

from __future__ import annotations

import logging
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status

from src.api.audit import record_audit_log
from src.api.auth import CurrentUser, get_current_user, require_roles
from src.api.backend_schemas import (
    BranchCreateRequest,
    BranchListResponse,
    BranchResponse,
)
from src.api.db import get_db

logger = logging.getLogger("vyaparmitra.api.branches")
router = APIRouter(prefix="/branches", tags=["Branch Management"])


@router.get(
    "",
    response_model=BranchListResponse,
    summary="List all branches for current business",
)
def list_branches(
    current_user: CurrentUser = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
) -> BranchListResponse:
    """Returns branches belonging to the authenticated merchant business."""
    rows = db.execute(
        "SELECT * FROM branches WHERE business_id = ? ORDER BY is_main DESC, name ASC",
        (current_user.business_id,),
    ).fetchall()

    branches = [
        BranchResponse(
            id=r["id"],
            business_id=r["business_id"],
            name=r["name"],
            code=r["code"],
            city=r["city"],
            state=r["state"],
            address=r["address"],
            phone=r["phone"],
            is_main=bool(r["is_main"]),
            created_at=r["created_at"],
        )
        for r in rows
    ]
    return BranchListResponse(total=len(branches), branches=branches)


@router.post(
    "",
    response_model=BranchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new branch (Owner/Admin only)",
)
def create_branch(
    req: BranchCreateRequest,
    request: Request,
    current_user: CurrentUser = Depends(require_roles(["owner", "admin"])),
    db: sqlite3.Connection = Depends(get_db),
) -> BranchResponse:
    """Creates a new branch and initializes its baseline inventory from catalog."""
    branch_id = f"BR_{current_user.business_id}_{uuid.uuid4().hex[:6].upper()}"
    now_str = datetime.now(timezone.utc).isoformat()

    db.execute("""
        INSERT INTO branches (id, business_id, name, code, city, state, address, phone, is_main, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        branch_id,
        current_user.business_id,
        req.name.strip(),
        req.code.strip() if req.code else None,
        req.city.strip(),
        req.state.strip(),
        req.address.strip() if req.address else None,
        req.phone.strip() if req.phone else None,
        1 if req.is_main else 0,
        now_str,
    ))

    # Initialize baseline inventory for new branch from any existing products in business
    existing_products = db.execute("""
        SELECT DISTINCT product_id, product_name, category, unit_cost, selling_price
        FROM inventory WHERE business_id = ?
    """, (current_user.business_id,)).fetchall()

    for p in existing_products:
        inv_id = f"INV_{branch_id}_{p['product_id']}"
        db.execute("""
            INSERT OR IGNORE INTO inventory (
                id, business_id, branch_id, product_id, product_name, category,
                current_stock, min_stock_threshold, unit_cost, selling_price, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, 50, 10, ?, ?, ?)
        """, (
            inv_id,
            current_user.business_id,
            branch_id,
            p["product_id"],
            p["product_name"],
            p["category"],
            float(p["unit_cost"]),
            float(p["selling_price"]),
            now_str,
        ))

    # Record Audit
    record_audit_log(
        db=db,
        business_id=current_user.business_id,
        branch_id=branch_id,
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="CREATE_BRANCH",
        resource="branches",
        resource_id=branch_id,
        details={"name": req.name, "city": req.city},
        ip_address=request.client.host if request.client else "127.0.0.1",
    )

    return BranchResponse(
        id=branch_id,
        business_id=current_user.business_id,
        name=req.name.strip(),
        code=req.code,
        city=req.city.strip(),
        state=req.state.strip(),
        address=req.address,
        phone=req.phone,
        is_main=req.is_main,
        created_at=now_str,
    )


@router.get(
    "/{branch_id}",
    response_model=BranchResponse,
    summary="Get details of a specific branch",
)
def get_branch(
    branch_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
) -> BranchResponse:
    """Returns single branch details enforcing tenant isolation."""
    row = db.execute(
        "SELECT * FROM branches WHERE id = ? AND business_id = ?",
        (branch_id, current_user.business_id),
    ).fetchone()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Branch '{branch_id}' was not found in your business.",
        )

    return BranchResponse(
        id=row["id"],
        business_id=row["business_id"],
        name=row["name"],
        code=row["code"],
        city=row["city"],
        state=row["state"],
        address=row["address"],
        phone=row["phone"],
        is_main=bool(row["is_main"]),
        created_at=row["created_at"],
    )
