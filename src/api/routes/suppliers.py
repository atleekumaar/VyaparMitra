"""
Supplier and Vendor Management Routes for VyaparMitra.
Provides supplier directories, purchase order/inward stock recording, and payable reconciliations.
"""

from __future__ import annotations

import json
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
    SupplierCreateRequest,
    SupplierInvoiceRequest,
    SupplierInvoiceResponse,
    SupplierListResponse,
    SupplierOutput,
    SupplierPaymentRequest,
    SupplierPaymentResponse,
    SupplierUpdateRequest,
)
from src.api.db import get_db

logger = logging.getLogger("vyaparmitra.api.suppliers")
router = APIRouter(prefix="/suppliers", tags=["Suppliers & Purchase Management"])


@router.get(
    "",
    response_model=SupplierListResponse,
    summary="List suppliers with pending payables",
)
def list_suppliers(
    search: Optional[str] = Query(None, description="Search supplier name or contact"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: CurrentUser = Depends(require_roles(["owner", "admin", "manager"])),
    db: sqlite3.Connection = Depends(get_db),
) -> SupplierListResponse:
    """Lists suppliers for the current merchant business."""
    query = "SELECT * FROM suppliers WHERE business_id = ?"
    params: List[Any] = [current_user.business_id]

    if search:
        query += " AND (LOWER(name) LIKE ? OR phone LIKE ?)"
        term = f"%{search.lower().strip()}%"
        params.extend([term, term])

    agg_query = query.replace("SELECT *", "SELECT COUNT(*), SUM(current_payable)")
    agg_row = db.execute(agg_query, params).fetchone()
    total_count = agg_row[0] or 0
    total_payables = float(agg_row[1] or 0.0)

    query += " ORDER BY current_payable DESC, name ASC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = db.execute(query, params).fetchall()
    suppliers = [
        SupplierOutput(
            id=r["id"],
            business_id=r["business_id"],
            name=r["name"],
            contact_person=r["contact_person"],
            phone=r["phone"],
            email=r["email"],
            address=r["address"],
            gstin=r["gstin"],
            current_payable=float(r["current_payable"]),
            payment_terms=r["payment_terms"],
            status=r["status"],
            created_at=r["created_at"],
        )
        for r in rows
    ]

    return SupplierListResponse(
        total_suppliers=total_count,
        total_payables=round(total_payables, 2),
        suppliers=suppliers,
    )


@router.post(
    "",
    response_model=SupplierOutput,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new supplier (Manager/Owner only)",
)
def create_supplier(
    req: SupplierCreateRequest,
    request: Request,
    current_user: CurrentUser = Depends(require_roles(["owner", "admin", "manager"])),
    db: sqlite3.Connection = Depends(get_db),
) -> SupplierOutput:
    """Registers a new supplier."""
    sup_id = f"SUP_{uuid.uuid4().hex[:8].upper()}"
    now_str = datetime.now(timezone.utc).isoformat()

    db.execute("""
        INSERT INTO suppliers (
            id, business_id, name, contact_person, phone, email, address, gstin, current_payable, payment_terms, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0.0, ?, 'ACTIVE', ?)
    """, (
        sup_id,
        current_user.business_id,
        req.name.strip(),
        req.contact_person.strip() if req.contact_person else None,
        req.phone.strip() if req.phone else None,
        req.email.strip().lower() if req.email else None,
        req.address.strip() if req.address else None,
        req.gstin.strip().upper() if req.gstin else None,
        req.payment_terms.strip(),
        now_str,
    ))

    record_audit_log(
        db=db,
        business_id=current_user.business_id,
        branch_id=current_user.branch_id,
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="CREATE_SUPPLIER",
        resource="suppliers",
        resource_id=sup_id,
        details={"name": req.name, "contact": req.contact_person},
        ip_address=request.client.host if request.client else "127.0.0.1",
    )

    return SupplierOutput(
        id=sup_id,
        business_id=current_user.business_id,
        name=req.name.strip(),
        contact_person=req.contact_person,
        phone=req.phone,
        email=req.email,
        address=req.address,
        gstin=req.gstin,
        current_payable=0.0,
        payment_terms=req.payment_terms,
        status="ACTIVE",
        created_at=now_str,
    )


@router.get(
    "/{supplier_id}",
    response_model=SupplierOutput,
    summary="Get supplier details",
)
def get_supplier(
    supplier_id: str,
    current_user: CurrentUser = Depends(require_roles(["owner", "admin", "manager"])),
    db: sqlite3.Connection = Depends(get_db),
) -> SupplierOutput:
    """Returns details for a single supplier."""
    r = db.execute(
        "SELECT * FROM suppliers WHERE id = ? AND business_id = ?",
        (supplier_id, current_user.business_id),
    ).fetchone()

    if not r:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supplier '{supplier_id}' was not found.",
        )

    return SupplierOutput(
        id=r["id"],
        business_id=r["business_id"],
        name=r["name"],
        contact_person=r["contact_person"],
        phone=r["phone"],
        email=r["email"],
        address=r["address"],
        gstin=r["gstin"],
        current_payable=float(r["current_payable"]),
        payment_terms=r["payment_terms"],
        status=r["status"],
        created_at=r["created_at"],
    )


@router.put(
    "/{supplier_id}",
    response_model=SupplierOutput,
    summary="Update supplier details (Manager/Owner only)",
)
def update_supplier(
    supplier_id: str,
    req: SupplierUpdateRequest,
    request: Request,
    current_user: CurrentUser = Depends(require_roles(["owner", "admin", "manager"])),
    db: sqlite3.Connection = Depends(get_db),
) -> SupplierOutput:
    """Updates supplier information."""
    sup = db.execute(
        "SELECT * FROM suppliers WHERE id = ? AND business_id = ?",
        (supplier_id, current_user.business_id),
    ).fetchone()

    if not sup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supplier '{supplier_id}' was not found.",
        )

    name = req.name.strip() if req.name else sup["name"]
    contact = req.contact_person.strip() if req.contact_person else sup["contact_person"]
    phone = req.phone.strip() if req.phone else sup["phone"]
    email = req.email.strip().lower() if req.email else sup["email"]
    address = req.address.strip() if req.address else sup["address"]
    gstin = req.gstin.strip().upper() if req.gstin else sup["gstin"]
    terms = req.payment_terms.strip() if req.payment_terms else sup["payment_terms"]
    status_val = req.status.strip() if req.status else sup["status"]

    db.execute("""
        UPDATE suppliers
        SET name = ?, contact_person = ?, phone = ?, email = ?, address = ?, gstin = ?, payment_terms = ?, status = ?
        WHERE id = ?
    """, (name, contact, phone, email, address, gstin, terms, status_val, supplier_id))

    record_audit_log(
        db=db,
        business_id=current_user.business_id,
        branch_id=current_user.branch_id,
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="UPDATE_SUPPLIER",
        resource="suppliers",
        resource_id=supplier_id,
        details={"name": name, "status": status_val},
        ip_address=request.client.host if request.client else "127.0.0.1",
    )

    return SupplierOutput(
        id=supplier_id,
        business_id=sup["business_id"],
        name=name,
        contact_person=contact,
        phone=phone,
        email=email,
        address=address,
        gstin=gstin,
        current_payable=float(sup["current_payable"]),
        payment_terms=terms,
        status=status_val,
        created_at=sup["created_at"],
    )


@router.post(
    "/{supplier_id}/invoices",
    response_model=SupplierInvoiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record supplier purchase invoice and inward stock (Manager/Owner only)",
)
def record_supplier_invoice(
    supplier_id: str,
    req: SupplierInvoiceRequest,
    request: Request,
    current_user: CurrentUser = Depends(require_roles(["owner", "admin", "manager"])),
    db: sqlite3.Connection = Depends(get_db),
) -> SupplierInvoiceResponse:
    """Records a vendor purchase invoice and updates stock in branch inventory."""
    sup = db.execute(
        "SELECT * FROM suppliers WHERE id = ? AND business_id = ?",
        (supplier_id, current_user.business_id),
    ).fetchone()

    if not sup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supplier '{supplier_id}' was not found.",
        )

    branch_id = enforce_branch_isolation(current_user, req.branch_id)
    if not branch_id:
        b_row = db.execute("SELECT id FROM branches WHERE business_id = ? ORDER BY is_main DESC LIMIT 1", (current_user.business_id,)).fetchone()
        branch_id = b_row["id"] if b_row else f"BR_{current_user.business_id}_MAIN"

    invoice_id = f"SINV_{uuid.uuid4().hex[:8].upper()}"
    now_str = datetime.now(timezone.utc).isoformat()
    unpaid = max(0.0, req.total_amount - req.paid_amount)
    status_val = "PAID" if unpaid == 0 else ("PARTIAL" if req.paid_amount > 0 else "UNPAID")

    # Update supplier payable
    if unpaid > 0:
        new_payable = float(sup["current_payable"]) + unpaid
        db.execute("UPDATE suppliers SET current_payable = ? WHERE id = ?", (new_payable, supplier_id))

    # Auto update inventory stock
    updated_items = 0
    if req.auto_update_inventory and req.items:
        for item in req.items:
            inv_row = db.execute("""
                SELECT id, current_stock FROM inventory
                WHERE business_id = ? AND branch_id = ? AND product_id = ?
            """, (current_user.business_id, branch_id, item.product_id)).fetchone()

            if inv_row:
                new_st = inv_row["current_stock"] + item.quantity
                db.execute("""
                    UPDATE inventory
                    SET current_stock = ?, unit_cost = ?, updated_at = ?
                    WHERE id = ?
                """, (new_st, item.unit_cost, now_str, inv_row["id"]))
                updated_items += 1

    # Save supplier invoice
    items_json = json.dumps([i.model_dump() for i in req.items])
    db.execute("""
        INSERT INTO supplier_invoices (
            id, invoice_number, business_id, branch_id, supplier_id,
            total_amount, paid_amount, status, items_json, notes, created_by, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        invoice_id,
        req.invoice_number.strip(),
        current_user.business_id,
        branch_id,
        supplier_id,
        req.total_amount,
        req.paid_amount,
        status_val,
        items_json,
        req.notes,
        current_user.id,
        now_str,
    ))

    # If any amount was paid immediately, record expense
    if req.paid_amount > 0:
        db.execute("""
            INSERT INTO expenses (id, business_id, branch_id, category, amount, payment_method, description, created_by, created_at)
            VALUES (?, ?, ?, 'PURCHASE', ?, 'BANK_TRANSFER', ?, ?, ?)
        """, (
            f"EXP_{uuid.uuid4().hex[:8].upper()}",
            current_user.business_id,
            branch_id,
            req.paid_amount,
            f"Payment for Supplier Invoice {req.invoice_number} ({sup['name']})",
            current_user.id,
            now_str,
        ))

    # Audit log
    record_audit_log(
        db=db,
        business_id=current_user.business_id,
        branch_id=branch_id,
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="SUPPLIER_INVOICE_RECORDED",
        resource="suppliers",
        resource_id=invoice_id,
        details={
            "invoice_number": req.invoice_number,
            "total_amount": req.total_amount,
            "paid_amount": req.paid_amount,
            "stock_items_updated": updated_items,
        },
        ip_address=request.client.host if request.client else "127.0.0.1",
    )

    return SupplierInvoiceResponse(
        invoice_id=invoice_id,
        invoice_number=req.invoice_number,
        supplier_name=sup["name"],
        total_amount=round(req.total_amount, 2),
        paid_amount=round(req.paid_amount, 2),
        unpaid_amount=round(unpaid, 2),
        status=status_val,
        inventory_items_inwarded=updated_items,
        created_at=now_str,
    )


@router.post(
    "/{supplier_id}/payments",
    response_model=SupplierPaymentResponse,
    status_code=status.HTTP_200_OK,
    summary="Record payment made to supplier (Manager/Owner only)",
)
def record_supplier_payment(
    supplier_id: str,
    req: SupplierPaymentRequest,
    request: Request,
    current_user: CurrentUser = Depends(require_roles(["owner", "admin", "manager"])),
    db: sqlite3.Connection = Depends(get_db),
) -> SupplierPaymentResponse:
    """Records payment made to supplier, reducing pending payables and creating financial outflow."""
    sup = db.execute(
        "SELECT * FROM suppliers WHERE id = ? AND business_id = ?",
        (supplier_id, current_user.business_id),
    ).fetchone()

    if not sup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supplier '{supplier_id}' was not found.",
        )

    prev_payable = float(sup["current_payable"])
    new_payable = max(0.0, prev_payable - req.amount)
    now_str = datetime.now(timezone.utc).isoformat()
    branch_id = current_user.branch_id or f"BR_{current_user.business_id}_MAIN"

    # Update supplier payable
    db.execute("UPDATE suppliers SET current_payable = ? WHERE id = ?", (new_payable, supplier_id))

    # Record expense / outflow
    exp_id = f"EXP_{uuid.uuid4().hex[:8].upper()}"
    db.execute("""
        INSERT INTO expenses (id, business_id, branch_id, category, amount, payment_method, description, created_by, created_at)
        VALUES (?, ?, ?, 'PURCHASE', ?, ?, ?, ?, ?)
    """, (
        exp_id,
        current_user.business_id,
        branch_id,
        req.amount,
        req.payment_method.upper(),
        f"Supplier Repayment to {sup['name']}" + (f": {req.notes}" if req.notes else ""),
        current_user.id,
        now_str,
    ))

    # Audit log
    record_audit_log(
        db=db,
        business_id=current_user.business_id,
        branch_id=branch_id,
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="SUPPLIER_PAYMENT_MADE",
        resource="suppliers",
        resource_id=supplier_id,
        details={
            "amount": req.amount,
            "payment_method": req.payment_method,
            "previous_payable": prev_payable,
            "new_payable": new_payable,
        },
        ip_address=request.client.host if request.client else "127.0.0.1",
    )

    return SupplierPaymentResponse(
        supplier_id=supplier_id,
        supplier_name=sup["name"],
        amount_paid=round(req.amount, 2),
        previous_payable=round(prev_payable, 2),
        remaining_payable=round(new_payable, 2),
        expense_id=exp_id,
        paid_at=now_str,
    )
