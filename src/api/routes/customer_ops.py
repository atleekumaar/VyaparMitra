"""
Customer Management and Khata (Udhaar/Credit Ledger) Routes for VyaparMitra.
Provides customer directory, credit limit tracking, ledger statements, and debt recovery payments.
"""

from __future__ import annotations

import logging
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from src.api.audit import record_audit_log
from src.api.auth import CurrentUser, get_current_user, require_roles
from src.api.backend_schemas import (
    CustomerCreateRequest,
    CustomerKhataPaymentRequest,
    CustomerLedgerResponse,
    CustomerManageListResponse,
    CustomerManageOutput,
    CustomerUpdateRequest,
    LedgerEntryOutput,
)
from src.api.db import get_db

logger = logging.getLogger("vyaparmitra.api.customer_ops")
router = APIRouter(prefix="/customer-ops", tags=["Customers & Khata (Udhaar)"])


@router.get(
    "",
    response_model=CustomerManageListResponse,
    summary="List merchant customers with Khata balances and credit limits",
)
def list_customers(
    search: Optional[str] = Query(None, description="Search name, phone, or ID"),
    has_udhaar_only: bool = Query(False, description="Filter customers with positive Udhaar balance"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: CurrentUser = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
) -> CustomerManageListResponse:
    """Lists customers with multi-tenant business data isolation."""
    query = "SELECT * FROM customers WHERE business_id = ?"
    params: List[Any] = [current_user.business_id]

    if has_udhaar_only:
        query += " AND current_balance > 0"

    if search:
        query += " AND (LOWER(name) LIKE ? OR phone LIKE ? OR LOWER(id) LIKE ?)"
        term = f"%{search.lower().strip()}%"
        params.extend([term, term, term])

    agg_query = query.replace("SELECT *", "SELECT COUNT(*), SUM(current_balance)")
    agg_row = db.execute(agg_query, params).fetchone()
    total_count = agg_row[0] or 0
    total_credit = float(agg_row[1] or 0.0)

    query += " ORDER BY current_balance DESC, name ASC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = db.execute(query, params).fetchall()
    customers = [
        CustomerManageOutput(
            id=r["id"],
            business_id=r["business_id"],
            name=r["name"],
            phone=r["phone"],
            email=r["email"],
            address=r["address"],
            city=r["city"],
            credit_limit=float(r["credit_limit"]),
            current_balance=float(r["current_balance"]),
            loyalty_points=r["loyalty_points"],
            status=r["status"],
            created_at=r["created_at"],
        )
        for r in rows
    ]

    return CustomerManageListResponse(
        total_customers=total_count,
        total_outstanding_credit=round(total_credit, 2),
        customers=customers,
    )


@router.post(
    "",
    response_model=CustomerManageOutput,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new customer to merchant directory",
)
def create_customer(
    req: CustomerCreateRequest,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
) -> CustomerManageOutput:
    """Creates a new customer record."""
    cust_id = f"CUST_{uuid.uuid4().hex[:8].upper()}"
    now_str = datetime.now(timezone.utc).isoformat()

    db.execute("""
        INSERT INTO customers (id, business_id, name, phone, email, address, city, credit_limit, current_balance, loyalty_points, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0.0, 0, 'ACTIVE', ?)
    """, (
        cust_id,
        current_user.business_id,
        req.name.strip(),
        req.phone.strip() if req.phone else None,
        req.email.strip().lower() if req.email else None,
        req.address.strip() if req.address else None,
        req.city.strip() if req.city else None,
        float(req.credit_limit),
        now_str,
    ))

    record_audit_log(
        db=db,
        business_id=current_user.business_id,
        branch_id=current_user.branch_id,
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="CREATE_CUSTOMER",
        resource="customers",
        resource_id=cust_id,
        details={"name": req.name, "credit_limit": req.credit_limit},
        ip_address=request.client.host if request.client else "127.0.0.1",
    )

    return CustomerManageOutput(
        id=cust_id,
        business_id=current_user.business_id,
        name=req.name.strip(),
        phone=req.phone,
        email=req.email,
        address=req.address,
        city=req.city,
        credit_limit=float(req.credit_limit),
        current_balance=0.0,
        loyalty_points=0,
        status="ACTIVE",
        created_at=now_str,
    )


@router.get(
    "/{customer_id}",
    response_model=CustomerManageOutput,
    summary="Get customer profile and credit balance",
)
def get_customer(
    customer_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
) -> CustomerManageOutput:
    """Retrieves single customer profile."""
    r = db.execute(
        "SELECT * FROM customers WHERE id = ? AND business_id = ?",
        (customer_id, current_user.business_id),
    ).fetchone()

    if not r:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer '{customer_id}' was not found.",
        )

    return CustomerManageOutput(
        id=r["id"],
        business_id=r["business_id"],
        name=r["name"],
        phone=r["phone"],
        email=r["email"],
        address=r["address"],
        city=r["city"],
        credit_limit=float(r["credit_limit"]),
        current_balance=float(r["current_balance"]),
        loyalty_points=r["loyalty_points"],
        status=r["status"],
        created_at=r["created_at"],
    )


@router.put(
    "/{customer_id}",
    response_model=CustomerManageOutput,
    summary="Update customer profile or credit limit (Manager/Owner only)",
)
def update_customer(
    customer_id: str,
    req: CustomerUpdateRequest,
    request: Request,
    current_user: CurrentUser = Depends(require_roles(["owner", "admin", "manager"])),
    db: sqlite3.Connection = Depends(get_db),
) -> CustomerManageOutput:
    """Updates customer contact details or adjusts credit limit."""
    cust = db.execute(
        "SELECT * FROM customers WHERE id = ? AND business_id = ?",
        (customer_id, current_user.business_id),
    ).fetchone()

    if not cust:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer '{customer_id}' was not found.",
        )

    name = req.name.strip() if req.name else cust["name"]
    phone = req.phone.strip() if req.phone else cust["phone"]
    email = req.email.strip().lower() if req.email else cust["email"]
    address = req.address.strip() if req.address else cust["address"]
    city = req.city.strip() if req.city else cust["city"]
    credit_limit = float(req.credit_limit) if req.credit_limit is not None else float(cust["credit_limit"])
    status_val = req.status.strip() if req.status else cust["status"]

    db.execute("""
        UPDATE customers
        SET name = ?, phone = ?, email = ?, address = ?, city = ?, credit_limit = ?, status = ?
        WHERE id = ?
    """, (name, phone, email, address, city, credit_limit, status_val, customer_id))

    record_audit_log(
        db=db,
        business_id=current_user.business_id,
        branch_id=current_user.branch_id,
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="UPDATE_CUSTOMER",
        resource="customers",
        resource_id=customer_id,
        details={"name": name, "credit_limit": credit_limit, "status": status_val},
        ip_address=request.client.host if request.client else "127.0.0.1",
    )

    return CustomerManageOutput(
        id=customer_id,
        business_id=cust["business_id"],
        name=name,
        phone=phone,
        email=email,
        address=address,
        city=city,
        credit_limit=credit_limit,
        current_balance=float(cust["current_balance"]),
        loyalty_points=cust["loyalty_points"],
        status=status_val,
        created_at=cust["created_at"],
    )


@router.get(
    "/{customer_id}/ledger",
    response_model=CustomerLedgerResponse,
    summary="Get complete Khata ledger statement for a customer",
)
def get_customer_ledger(
    customer_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
) -> CustomerLedgerResponse:
    """Returns running ledger of credit purchases and payment repayments."""
    cust = db.execute(
        "SELECT * FROM customers WHERE id = ? AND business_id = ?",
        (customer_id, current_user.business_id),
    ).fetchone()

    if not cust:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer '{customer_id}' was not found.",
        )

    rows = db.execute("""
        SELECT * FROM customer_ledgers
        WHERE business_id = ? AND customer_id = ?
        ORDER BY created_at ASC
    """, (current_user.business_id, customer_id)).fetchall()

    entries = [
        LedgerEntryOutput(
            id=r["id"],
            business_id=r["business_id"],
            customer_id=r["customer_id"],
            entry_type=r["entry_type"],
            amount=float(r["amount"]),
            balance_after=float(r["balance_after"]),
            reference_id=r["reference_id"],
            notes=r["notes"],
            created_by=r["created_by"],
            created_at=r["created_at"],
        )
        for r in rows
    ]

    return CustomerLedgerResponse(
        customer_id=customer_id,
        customer_name=cust["name"],
        credit_limit=float(cust["credit_limit"]),
        current_balance=float(cust["current_balance"]),
        total_entries=len(entries),
        entries=entries,
    )


@router.post(
    "/{customer_id}/payment",
    response_model=CustomerLedgerResponse,
    summary="Record an Udhaar repayment from customer",
)
def record_khata_payment(
    customer_id: str,
    req: CustomerKhataPaymentRequest,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
) -> CustomerLedgerResponse:
    """Records payment received against Udhaar, reducing customer's outstanding balance."""
    cust = db.execute(
        "SELECT * FROM customers WHERE id = ? AND business_id = ?",
        (customer_id, current_user.business_id),
    ).fetchone()

    if not cust:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer '{customer_id}' was not found.",
        )

    prev_balance = float(cust["current_balance"])
    new_balance = max(0.0, prev_balance - req.amount)
    now_str = datetime.now(timezone.utc).isoformat()
    payment_id = f"PAY_{uuid.uuid4().hex[:8].upper()}"

    # Update customer balance
    db.execute("UPDATE customers SET current_balance = ? WHERE id = ?", (new_balance, customer_id))

    # Add ledger entry
    db.execute("""
        INSERT INTO customer_ledgers (id, business_id, customer_id, entry_type, amount, balance_after, reference_id, notes, created_by, created_at)
        VALUES (?, ?, ?, 'CREDIT', ?, ?, ?, ?, ?, ?)
    """, (
        f"LED_{uuid.uuid4().hex[:8].upper()}",
        current_user.business_id,
        customer_id,
        req.amount,
        new_balance,
        payment_id,
        f"Khata Repayment via {req.payment_method.upper()}" + (f": {req.notes}" if req.notes else ""),
        current_user.id,
        now_str,
    ))

    # Audit log
    record_audit_log(
        db=db,
        business_id=current_user.business_id,
        branch_id=current_user.branch_id,
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="CUSTOMER_PAYMENT_RECEIVED",
        resource="customers",
        resource_id=customer_id,
        details={
            "amount": req.amount,
            "payment_method": req.payment_method,
            "previous_balance": prev_balance,
            "new_balance": new_balance,
        },
        ip_address=request.client.host if request.client else "127.0.0.1",
    )

    return get_customer_ledger(customer_id=customer_id, current_user=current_user, db=db)

