"""
Inventory Management Routes for VyaparMitra.
Provides stock tracking, low-stock alerts, stock adjustments, and product pricing controls.
"""

from __future__ import annotations

import logging
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from src.api.audit import record_audit_log
from src.api.auth import (
    CurrentUser,
    enforce_branch_isolation,
    get_current_user,
    require_roles,
)
from src.api.backend_schemas import (
    InventoryCreateRequest,
    InventoryItemOutput,
    InventoryListResponse,
    InventoryUpdateRequest,
    LowStockItemOutput,
    LowStockListResponse,
    StockAdjustmentRequest,
)
from src.api.db import get_db

logger = logging.getLogger("vyaparmitra.api.inventory")
router = APIRouter(prefix="/inventory", tags=["Inventory & Stock Management"])


@router.get(
    "",
    response_model=InventoryListResponse,
    summary="List inventory items with stock levels, valuations, and search",
)
def list_inventory(
    branch_id: Optional[str] = Query(None, description="Filter by branch"),
    category: Optional[str] = Query(None, description="Filter by product category"),
    search: Optional[str] = Query(None, description="Search product name or SKU"),
    low_stock_only: bool = Query(False, description="Filter only low stock items"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: CurrentUser = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
) -> InventoryListResponse:
    """Returns inventory catalog with branch stock levels and valuation."""
    target_branch = enforce_branch_isolation(current_user, branch_id)

    query = "SELECT * FROM inventory WHERE business_id = ?"
    params: List[Any] = [current_user.business_id]

    if target_branch:
        query += " AND branch_id = ?"
        params.append(target_branch)

    if category:
        query += " AND LOWER(category) = ?"
        params.append(category.lower().strip())

    if search:
        query += " AND (LOWER(product_name) LIKE ? OR LOWER(product_id) LIKE ?)"
        term = f"%{search.lower().strip()}%"
        params.extend([term, term])

    if low_stock_only:
        query += " AND current_stock <= min_stock_threshold"

    # Aggregates
    agg_query = query.replace("SELECT *", "SELECT COUNT(*), SUM(current_stock), SUM(current_stock * unit_cost)")
    agg_row = db.execute(agg_query, params).fetchone()
    total_count = agg_row[0] or 0
    total_units = int(agg_row[1] or 0)
    total_val_cost = float(agg_row[2] or 0.0)

    query += " ORDER BY current_stock ASC, product_name ASC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = db.execute(query, params).fetchall()
    items = []
    for r in rows:
        c_stock = r["current_stock"]
        u_cost = float(r["unit_cost"])
        s_price = float(r["selling_price"])
        m_thresh = r["min_stock_threshold"]

        items.append(
            InventoryItemOutput(
                id=r["id"],
                business_id=r["business_id"],
                branch_id=r["branch_id"],
                product_id=r["product_id"],
                product_name=r["product_name"],
                category=r["category"],
                current_stock=c_stock,
                min_stock_threshold=m_thresh,
                unit_cost=u_cost,
                selling_price=s_price,
                barcode=r["barcode"],
                unit=r["unit"],
                stock_value_cost=round(c_stock * u_cost, 2),
                stock_value_retail=round(c_stock * s_price, 2),
                is_low_stock=(c_stock <= m_thresh),
                updated_at=r["updated_at"],
            )
        )

    return InventoryListResponse(
        total_count=total_count,
        total_stock_units=total_units,
        total_valuation_cost=round(total_val_cost, 2),
        items=items,
    )


@router.get(
    "/low-stock",
    response_model=LowStockListResponse,
    summary="Get low-stock items with intelligent reorder suggestions",
)
def get_low_stock_items(
    branch_id: Optional[str] = Query(None, description="Filter by branch"),
    current_user: CurrentUser = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
) -> LowStockListResponse:
    """Returns items where current_stock is at or below the minimum threshold."""
    target_branch = enforce_branch_isolation(current_user, branch_id)

    query = "SELECT * FROM inventory WHERE business_id = ? AND current_stock <= min_stock_threshold"
    params: List[Any] = [current_user.business_id]

    if target_branch:
        query += " AND branch_id = ?"
        params.append(target_branch)

    query += " ORDER BY (current_stock - min_stock_threshold) ASC"
    rows = db.execute(query, params).fetchall()

    low_items = []
    for r in rows:
        c_stock = r["current_stock"]
        m_thresh = r["min_stock_threshold"]
        u_cost = float(r["unit_cost"])
        # Suggest bringing stock back up to 3x threshold
        suggested_qty = max(20, (m_thresh * 3) - c_stock)

        low_items.append(
            LowStockItemOutput(
                inventory_id=r["id"],
                branch_id=r["branch_id"],
                product_id=r["product_id"],
                product_name=r["product_name"],
                category=r["category"],
                current_stock=c_stock,
                min_stock_threshold=m_thresh,
                suggested_reorder_qty=suggested_qty,
                unit_cost=u_cost,
                estimated_reorder_cost=round(suggested_qty * u_cost, 2),
            )
        )

    return LowStockListResponse(
        total_low_stock_items=len(low_items),
        items=low_items,
    )


@router.post(
    "/adjust",
    response_model=InventoryItemOutput,
    summary="Adjust inventory stock (Manager/Owner only)",
)
def adjust_stock(
    req: StockAdjustmentRequest,
    request: Request,
    current_user: CurrentUser = Depends(require_roles(["owner", "admin", "manager"])),
    db: sqlite3.Connection = Depends(get_db),
) -> InventoryItemOutput:
    """Manual inventory adjustment for audits, breakage, damage, or restock."""
    inv = db.execute(
        "SELECT * FROM inventory WHERE id = ? AND business_id = ?",
        (req.inventory_id, current_user.business_id),
    ).fetchone()

    if not inv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory item '{req.inventory_id}' was not found.",
        )

    enforce_branch_isolation(current_user, inv["branch_id"])

    prev_stock = inv["current_stock"]
    adj_type = req.adjustment_type.upper().strip()

    if adj_type == "INCREASE":
        new_stock = prev_stock + req.quantity
    elif adj_type == "DECREASE":
        new_stock = max(0, prev_stock - req.quantity)
    elif adj_type == "SET":
        new_stock = req.quantity
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid adjustment type '{req.adjustment_type}'. Allowed: INCREASE, DECREASE, SET.",
        )

    now_str = datetime.now(timezone.utc).isoformat()
    db.execute("""
        UPDATE inventory SET current_stock = ?, updated_at = ? WHERE id = ?
    """, (new_stock, now_str, req.inventory_id))

    # Audit Logging
    record_audit_log(
        db=db,
        business_id=current_user.business_id,
        branch_id=inv["branch_id"],
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="STOCK_ADJUSTMENT",
        resource="inventory",
        resource_id=req.inventory_id,
        details={
            "product_name": inv["product_name"],
            "adjustment_type": adj_type,
            "previous_stock": prev_stock,
            "new_stock": new_stock,
            "reason": req.reason,
            "notes": req.notes,
        },
        ip_address=request.client.host if request.client else "127.0.0.1",
    )

    u_cost = float(inv["unit_cost"])
    s_price = float(inv["selling_price"])
    m_thresh = inv["min_stock_threshold"]

    return InventoryItemOutput(
        id=inv["id"],
        business_id=inv["business_id"],
        branch_id=inv["branch_id"],
        product_id=inv["product_id"],
        product_name=inv["product_name"],
        category=inv["category"],
        current_stock=new_stock,
        min_stock_threshold=m_thresh,
        unit_cost=u_cost,
        selling_price=s_price,
        barcode=inv["barcode"],
        unit=inv["unit"],
        stock_value_cost=round(new_stock * u_cost, 2),
        stock_value_retail=round(new_stock * s_price, 2),
        is_low_stock=(new_stock <= m_thresh),
        updated_at=now_str,
    )


@router.post(
    "/items",
    response_model=InventoryItemOutput,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new SKU to inventory (Manager/Owner only)",
)
def create_inventory_item(
    req: InventoryCreateRequest,
    request: Request,
    current_user: CurrentUser = Depends(require_roles(["owner", "admin", "manager"])),
    db: sqlite3.Connection = Depends(get_db),
) -> InventoryItemOutput:
    """Creates a new inventory item in branch."""
    target_branch = enforce_branch_isolation(current_user, req.branch_id)
    if not target_branch:
        b_row = db.execute("SELECT id FROM branches WHERE business_id = ? ORDER BY is_main DESC LIMIT 1", (current_user.business_id,)).fetchone()
        target_branch = b_row["id"] if b_row else f"BR_{current_user.business_id}_MAIN"

    # Check unique
    existing = db.execute(
        "SELECT id FROM inventory WHERE business_id = ? AND branch_id = ? AND product_id = ?",
        (current_user.business_id, target_branch, req.product_id.strip()),
    ).fetchone()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product SKU '{req.product_id}' already exists in branch '{target_branch}'.",
        )

    now_str = datetime.now(timezone.utc).isoformat()
    inv_id = f"INV_{target_branch}_{req.product_id.strip()}"

    db.execute("""
        INSERT INTO inventory (
            id, business_id, branch_id, product_id, product_name, category,
            current_stock, min_stock_threshold, unit_cost, selling_price,
            barcode, unit, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        inv_id,
        current_user.business_id,
        target_branch,
        req.product_id.strip(),
        req.product_name.strip(),
        req.category.strip(),
        req.current_stock,
        req.min_stock_threshold,
        float(req.unit_cost),
        float(req.selling_price),
        req.barcode.strip() if req.barcode else None,
        req.unit.strip(),
        now_str,
    ))

    # Audit Log
    record_audit_log(
        db=db,
        business_id=current_user.business_id,
        branch_id=target_branch,
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="CREATE_INVENTORY_ITEM",
        resource="inventory",
        resource_id=inv_id,
        details={"product_name": req.product_name, "product_id": req.product_id},
        ip_address=request.client.host if request.client else "127.0.0.1",
    )

    return InventoryItemOutput(
        id=inv_id,
        business_id=current_user.business_id,
        branch_id=target_branch,
        product_id=req.product_id.strip(),
        product_name=req.product_name.strip(),
        category=req.category.strip(),
        current_stock=req.current_stock,
        min_stock_threshold=req.min_stock_threshold,
        unit_cost=float(req.unit_cost),
        selling_price=float(req.selling_price),
        barcode=req.barcode,
        unit=req.unit,
        stock_value_cost=round(req.current_stock * float(req.unit_cost), 2),
        stock_value_retail=round(req.current_stock * float(req.selling_price), 2),
        is_low_stock=(req.current_stock <= req.min_stock_threshold),
        updated_at=now_str,
    )


@router.put(
    "/items/{inventory_id}",
    response_model=InventoryItemOutput,
    summary="Update product details, selling price, or threshold",
)
def update_inventory_item(
    inventory_id: str,
    req: InventoryUpdateRequest,
    request: Request,
    current_user: CurrentUser = Depends(require_roles(["owner", "admin", "manager"])),
    db: sqlite3.Connection = Depends(get_db),
) -> InventoryItemOutput:
    """Updates pricing or metadata for an inventory SKU."""
    inv = db.execute(
        "SELECT * FROM inventory WHERE id = ? AND business_id = ?",
        (inventory_id, current_user.business_id),
    ).fetchone()

    if not inv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory item '{inventory_id}' was not found.",
        )

    enforce_branch_isolation(current_user, inv["branch_id"])

    name = req.product_name.strip() if req.product_name else inv["product_name"]
    category = req.category.strip() if req.category else inv["category"]
    min_thresh = req.min_stock_threshold if req.min_stock_threshold is not None else inv["min_stock_threshold"]
    unit_cost = float(req.unit_cost) if req.unit_cost is not None else float(inv["unit_cost"])
    selling_price = float(req.selling_price) if req.selling_price is not None else float(inv["selling_price"])
    barcode = req.barcode.strip() if req.barcode else inv["barcode"]
    now_str = datetime.now(timezone.utc).isoformat()

    db.execute("""
        UPDATE inventory
        SET product_name = ?, category = ?, min_stock_threshold = ?, unit_cost = ?, selling_price = ?, barcode = ?, updated_at = ?
        WHERE id = ?
    """, (name, category, min_thresh, unit_cost, selling_price, barcode, now_str, inventory_id))

    record_audit_log(
        db=db,
        business_id=current_user.business_id,
        branch_id=inv["branch_id"],
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="UPDATE_INVENTORY_ITEM",
        resource="inventory",
        resource_id=inventory_id,
        details={"product_name": name, "selling_price": selling_price, "unit_cost": unit_cost},
        ip_address=request.client.host if request.client else "127.0.0.1",
    )

    c_stock = inv["current_stock"]
    return InventoryItemOutput(
        id=inventory_id,
        business_id=inv["business_id"],
        branch_id=inv["branch_id"],
        product_id=inv["product_id"],
        product_name=name,
        category=category,
        current_stock=c_stock,
        min_stock_threshold=min_thresh,
        unit_cost=unit_cost,
        selling_price=selling_price,
        barcode=barcode,
        unit=inv["unit"],
        stock_value_cost=round(c_stock * unit_cost, 2),
        stock_value_retail=round(c_stock * selling_price, 2),
        is_low_stock=(c_stock <= min_thresh),
        updated_at=now_str,
    )

