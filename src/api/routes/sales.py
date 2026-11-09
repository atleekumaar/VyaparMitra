"""
Sales and POS Checkout Routes for VyaparMitra.
Provides atomic sale transactions, instant stock deduction, Khata integration, and refunds.
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
    UserRole,
    enforce_branch_isolation,
    get_current_user,
    require_roles,
)
from src.api.backend_schemas import (
    CreateSaleRequest,
    RefundSaleResponse,
    SaleItemOutput,
    SaleListResponse,
    SaleResponse,
)
from src.api.db import get_db

logger = logging.getLogger("vyaparmitra.api.sales")
router = APIRouter(prefix="/sales", tags=["Sales & POS Checkout"])


@router.post(
    "",
    response_model=SaleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new sale (POS Checkout) with automatic stock deduction",
)
def create_sale(
    req: CreateSaleRequest,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
) -> SaleResponse:
    """
    Core POS Checkout Endpoint:
    1. Validates and enforces multi-branch data isolation.
    2. Validates inventory availability for all items.
    3. Atomically decrements stock in the inventory table.
    4. Handles Khata/Udhaar credit limits & ledger update if payment_method is CREDIT.
    5. Records sale, line items, and audit log.
    6. Returns invoice and low-stock alerts if thresholds are breached.
    """
    branch_id = enforce_branch_isolation(current_user, req.branch_id)
    if not branch_id:
        # Default to user's branch or main branch of business
        b_row = db.execute(
            "SELECT id FROM branches WHERE business_id = ? ORDER BY is_main DESC LIMIT 1",
            (current_user.business_id,),
        ).fetchone()
        branch_id = b_row["id"] if b_row else f"BR_{current_user.business_id}_MAIN"

    if not req.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sale must contain at least one line item.",
        )

    now_dt = datetime.now(timezone.utc)
    now_str = now_dt.isoformat()
    sale_id = f"SALE_{uuid.uuid4().hex[:10].upper()}"
    invoice_number = f"INV-{now_dt.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    # 1. Fetch and validate inventory items
    item_records = []
    subtotal = 0.0
    low_stock_warnings = []

    for item in req.items:
        inv_row = db.execute("""
            SELECT * FROM inventory
            WHERE business_id = ? AND branch_id = ? AND product_id = ?
        """, (current_user.business_id, branch_id, item.product_id)).fetchone()

        if not inv_row:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product '{item.product_id}' is not in stock/catalog for branch '{branch_id}'.",
            )

        if inv_row["current_stock"] < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Insufficient stock for '{inv_row['product_name']}'. "
                    f"Available: {inv_row['current_stock']}, Requested: {item.quantity}."
                ),
            )

        unit_price = item.unit_price if item.unit_price is not None else float(inv_row["selling_price"])
        item_total = (unit_price * item.quantity) - item.discount
        if item_total < 0:
            item_total = 0.0

        subtotal += item_total
        item_records.append({
            "product_id": item.product_id,
            "product_name": inv_row["product_name"],
            "quantity": item.quantity,
            "unit_price": unit_price,
            "unit_cost": float(inv_row["unit_cost"]),
            "discount": item.discount,
            "total_price": item_total,
            "inv_id": inv_row["id"],
            "current_stock": inv_row["current_stock"],
            "min_threshold": inv_row["min_stock_threshold"],
        })

    # 2. Compute Total Amount
    total_amount = subtotal - req.discount + req.tax
    if total_amount < 0:
        total_amount = 0.0

    # 3. Handle CREDIT (Khata / Udhaar) Payment
    customer_id = req.customer_id
    customer_name = req.customer_name or "Walk-in Customer"

    if req.payment_method.upper() == "CREDIT":
        if not customer_id or customer_id == "WALK_IN":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer ID is required for Credit (Udhaar) sales.",
            )

        cust = db.execute(
            "SELECT * FROM customers WHERE id = ? AND business_id = ?",
            (customer_id, current_user.business_id),
        ).fetchone()

        if not cust:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer '{customer_id}' not found in business records.",
            )

        customer_name = cust["name"]
        new_balance = float(cust["current_balance"]) + total_amount
        credit_limit = float(cust["credit_limit"])

        if new_balance > credit_limit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Credit limit exceeded for {customer_name}. "
                    f"Limit: ₹{credit_limit:,.2f}, Current: ₹{cust['current_balance']:,.2f}, "
                    f"New: ₹{new_balance:,.2f}."
                ),
            )

        # Update customer balance
        db.execute(
            "UPDATE customers SET current_balance = ? WHERE id = ?",
            (new_balance, customer_id),
        )

        # Record Khata ledger debit entry
        ledger_id = f"LED_{uuid.uuid4().hex[:8].upper()}"
        db.execute("""
            INSERT INTO customer_ledgers (id, business_id, customer_id, entry_type, amount, balance_after, reference_id, notes, created_by, created_at)
            VALUES (?, ?, ?, 'DEBIT', ?, ?, ?, ?, ?, ?)
        """, (
            ledger_id,
            current_user.business_id,
            customer_id,
            total_amount,
            new_balance,
            sale_id,
            f"Credit Sale - Invoice {invoice_number}",
            current_user.id,
            now_str,
        ))

    # 4. Insert Sale Record
    db.execute("""
        INSERT INTO sales (
            id, invoice_number, business_id, branch_id, customer_id, customer_name,
            subtotal, discount, tax, total_amount, payment_method, status,
            created_by, created_by_name, notes, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'COMPLETED', ?, ?, ?, ?)
    """, (
        sale_id,
        invoice_number,
        current_user.business_id,
        branch_id,
        customer_id,
        customer_name,
        round(subtotal, 2),
        round(req.discount, 2),
        round(req.tax, 2),
        round(total_amount, 2),
        req.payment_method.upper(),
        current_user.id,
        current_user.full_name,
        req.notes,
        now_str,
    ))

    # 5. Insert Sale Items & Deduct Stock Atomically
    output_items = []
    for item in item_records:
        item_id = f"SI_{uuid.uuid4().hex[:8].upper()}"
        db.execute("""
            INSERT INTO sale_items (
                id, sale_id, product_id, product_name, quantity,
                unit_price, unit_cost, discount, total_price
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item_id,
            sale_id,
            item["product_id"],
            item["product_name"],
            item["quantity"],
            item["unit_price"],
            item["unit_cost"],
            item["discount"],
            round(item["total_price"], 2),
        ))

        # Deduct stock
        new_stock = item["current_stock"] - item["quantity"]
        db.execute("""
            UPDATE inventory SET current_stock = ?, updated_at = ? WHERE id = ?
        """, (new_stock, now_str, item["inv_id"]))

        if new_stock <= item["min_threshold"]:
            low_stock_warnings.append(
                f"Low stock alert for '{item['product_name']}': {new_stock} remaining (threshold: {item['min_threshold']})."
            )

        output_items.append(
            SaleItemOutput(
                id=item_id,
                product_id=item["product_id"],
                product_name=item["product_name"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                unit_cost=item["unit_cost"],
                discount=item["discount"],
                total_price=round(item["total_price"], 2),
            )
        )

    # 6. Audit Logging
    record_audit_log(
        db=db,
        business_id=current_user.business_id,
        branch_id=branch_id,
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="CREATE_SALE",
        resource="sales",
        resource_id=sale_id,
        details={
            "invoice_number": invoice_number,
            "total_amount": round(total_amount, 2),
            "payment_method": req.payment_method.upper(),
            "items_count": len(output_items),
        },
        ip_address=request.client.host if request.client else "127.0.0.1",
    )

    return SaleResponse(
        id=sale_id,
        invoice_number=invoice_number,
        business_id=current_user.business_id,
        branch_id=branch_id,
        customer_id=customer_id,
        customer_name=customer_name,
        subtotal=round(subtotal, 2),
        discount=round(req.discount, 2),
        tax=round(req.tax, 2),
        total_amount=round(total_amount, 2),
        payment_method=req.payment_method.upper(),
        status="COMPLETED",
        created_by=current_user.id,
        created_by_name=current_user.full_name,
        notes=req.notes,
        created_at=now_str,
        items=output_items,
        low_stock_warnings=low_stock_warnings,
    )


@router.get(
    "",
    response_model=SaleListResponse,
    summary="List sales orders with date, branch, and payment filters",
)
def list_sales(
    branch_id: Optional[str] = Query(None, description="Filter by branch ID"),
    payment_method: Optional[str] = Query(None, description="Filter CASH, UPI, CARD, CREDIT"),
    customer_id: Optional[str] = Query(None, description="Filter by customer ID"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: CurrentUser = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
) -> SaleListResponse:
    """Returns sales history adhering to multi-branch tenant isolation."""
    target_branch = enforce_branch_isolation(current_user, branch_id)

    query = "SELECT * FROM sales WHERE business_id = ?"
    params: List[Any] = [current_user.business_id]

    if target_branch:
        query += " AND branch_id = ?"
        params.append(target_branch)

    if payment_method:
        query += " AND UPPER(payment_method) = ?"
        params.append(payment_method.upper().strip())

    if customer_id:
        query += " AND customer_id = ?"
        params.append(customer_id.strip())

    # Calculate total revenue
    rev_query = query.replace("SELECT *", "SELECT COUNT(*), SUM(total_amount)")
    total_row = db.execute(rev_query, params).fetchone()
    total_count = total_row[0] or 0
    total_revenue = float(total_row[1] or 0.0)

    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = db.execute(query, params).fetchall()
    sales = []
    for r in rows:
        items_rows = db.execute("SELECT * FROM sale_items WHERE sale_id = ?", (r["id"],)).fetchall()
        items = [
            SaleItemOutput(
                id=i["id"],
                product_id=i["product_id"],
                product_name=i["product_name"],
                quantity=i["quantity"],
                unit_price=float(i["unit_price"]),
                unit_cost=float(i["unit_cost"]),
                discount=float(i["discount"]),
                total_price=float(i["total_price"]),
            )
            for i in items_rows
        ]
        sales.append(
            SaleResponse(
                id=r["id"],
                invoice_number=r["invoice_number"],
                business_id=r["business_id"],
                branch_id=r["branch_id"],
                customer_id=r["customer_id"],
                customer_name=r["customer_name"],
                subtotal=float(r["subtotal"]),
                discount=float(r["discount"]),
                tax=float(r["tax"]),
                total_amount=float(r["total_amount"]),
                payment_method=r["payment_method"],
                status=r["status"],
                created_by=r["created_by"],
                created_by_name=r["created_by_name"],
                notes=r["notes"],
                created_at=r["created_at"],
                items=items,
            )
        )

    return SaleListResponse(
        total_count=total_count,
        total_revenue=round(total_revenue, 2),
        sales=sales,
    )


@router.get(
    "/{sale_id}",
    response_model=SaleResponse,
    summary="Get single sale receipt and line item breakdown",
)
def get_sale(
    sale_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
) -> SaleResponse:
    """Retrieves full invoice details for a sale."""
    r = db.execute(
        "SELECT * FROM sales WHERE id = ? AND business_id = ?",
        (sale_id, current_user.business_id),
    ).fetchone()

    if not r:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sale transaction '{sale_id}' was not found.",
        )

    enforce_branch_isolation(current_user, r["branch_id"])

    items_rows = db.execute("SELECT * FROM sale_items WHERE sale_id = ?", (sale_id,)).fetchall()
    items = [
        SaleItemOutput(
            id=i["id"],
            product_id=i["product_id"],
            product_name=i["product_name"],
            quantity=i["quantity"],
            unit_price=float(i["unit_price"]),
            unit_cost=float(i["unit_cost"]),
            discount=float(i["discount"]),
            total_price=float(i["total_price"]),
        )
        for i in items_rows
    ]

    return SaleResponse(
        id=r["id"],
        invoice_number=r["invoice_number"],
        business_id=r["business_id"],
        branch_id=r["branch_id"],
        customer_id=r["customer_id"],
        customer_name=r["customer_name"],
        subtotal=float(r["subtotal"]),
        discount=float(r["discount"]),
        tax=float(r["tax"]),
        total_amount=float(r["total_amount"]),
        payment_method=r["payment_method"],
        status=r["status"],
        created_by=r["created_by"],
        created_by_name=r["created_by_name"],
        notes=r["notes"],
        created_at=r["created_at"],
        items=items,
    )


@router.post(
    "/{sale_id}/refund",
    response_model=RefundSaleResponse,
    summary="Refund a sale and restore inventory stock (Manager/Owner only)",
)
def refund_sale(
    sale_id: str,
    request: Request,
    current_user: CurrentUser = Depends(require_roles(["owner", "admin", "manager"])),
    db: sqlite3.Connection = Depends(get_db),
) -> RefundSaleResponse:
    """Cancels/refunds an existing sale, restores items to inventory, and adjusts credit if needed."""
    sale = db.execute(
        "SELECT * FROM sales WHERE id = ? AND business_id = ?",
        (sale_id, current_user.business_id),
    ).fetchone()

    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sale '{sale_id}' was not found.",
        )

    enforce_branch_isolation(current_user, sale["branch_id"])

    if sale["status"] == "REFUNDED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This sale has already been refunded.",
        )

    now_str = datetime.now(timezone.utc).isoformat()

    # 1. Restore inventory
    items_rows = db.execute("SELECT * FROM sale_items WHERE sale_id = ?", (sale_id,)).fetchall()
    for item in items_rows:
        db.execute("""
            UPDATE inventory
            SET current_stock = current_stock + ?, updated_at = ?
            WHERE business_id = ? AND branch_id = ? AND product_id = ?
        """, (item["quantity"], now_str, current_user.business_id, sale["branch_id"], item["product_id"]))

    # 2. Reverse Khata credit balance if applicable
    if sale["payment_method"].upper() == "CREDIT" and sale["customer_id"]:
        cust = db.execute("SELECT * FROM customers WHERE id = ?", (sale["customer_id"],)).fetchone()
        if cust:
            new_balance = max(0.0, float(cust["current_balance"]) - float(sale["total_amount"]))
            db.execute("UPDATE customers SET current_balance = ? WHERE id = ?", (new_balance, sale["customer_id"]))

            # Add CREDIT entry in ledger (canceling debit)
            db.execute("""
                INSERT INTO customer_ledgers (id, business_id, customer_id, entry_type, amount, balance_after, reference_id, notes, created_by, created_at)
                VALUES (?, ?, ?, 'CREDIT', ?, ?, ?, 'Sale Refund / Reversal', ?, ?)
            """, (
                f"LED_{uuid.uuid4().hex[:8].upper()}",
                current_user.business_id,
                sale["customer_id"],
                float(sale["total_amount"]),
                new_balance,
                sale_id,
                current_user.id,
                now_str,
            ))

    # 3. Update sale status
    db.execute("UPDATE sales SET status = 'REFUNDED' WHERE id = ?", (sale_id,))

    # 4. Audit Log
    record_audit_log(
        db=db,
        business_id=current_user.business_id,
        branch_id=sale["branch_id"],
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="REFUND_SALE",
        resource="sales",
        resource_id=sale_id,
        details={"invoice_number": sale["invoice_number"], "amount": float(sale["total_amount"])},
        ip_address=request.client.host if request.client else "127.0.0.1",
    )

    return RefundSaleResponse(
        sale_id=sale_id,
        invoice_number=sale["invoice_number"],
        status="REFUNDED",
        restored_items_count=len(items_rows),
        message=f"Sale {sale['invoice_number']} successfully refunded. Stock restored.",
    )
