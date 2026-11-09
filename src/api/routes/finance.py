"""
Finance, Expense Tracking, and Profit & Loss Routes for VyaparMitra.
Provides comprehensive financial summaries, expense logging, cashflow, and receivables/payables.
"""

from __future__ import annotations

import logging
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from src.api.audit import record_audit_log
from src.api.auth import (
    CurrentUser,
    enforce_branch_isolation,
    get_current_user,
    require_roles,
)
from src.api.backend_schemas import (
    CashflowDailyPoint,
    CashflowSummaryResponse,
    ExpenseCreateRequest,
    ExpenseListResponse,
    ExpenseOutput,
    FinanceSummaryResponse,
)
from src.api.db import get_db

logger = logging.getLogger("vyaparmitra.api.finance")
router = APIRouter(prefix="/finance", tags=["Finance & Profit/Loss"])


@router.get(
    "/summary",
    response_model=FinanceSummaryResponse,
    summary="Get business financial health, gross profit, net profit, and receivables/payables",
)
def get_finance_summary(
    branch_id: Optional[str] = Query(None, description="Filter by branch"),
    current_user: CurrentUser = Depends(require_roles(["owner", "admin", "manager"])),
    db: sqlite3.Connection = Depends(get_db),
) -> FinanceSummaryResponse:
    """Computes comprehensive P&L and balance metrics adhering to multi-branch isolation."""
    target_branch = enforce_branch_isolation(current_user, branch_id)

    # 1. Total Sales Revenue
    sales_sql = "SELECT SUM(total_amount) FROM sales WHERE business_id = ? AND status = 'COMPLETED'"
    sales_params: List[Any] = [current_user.business_id]
    if target_branch:
        sales_sql += " AND branch_id = ?"
        sales_params.append(target_branch)

    rev_row = db.execute(sales_sql, sales_params).fetchone()
    total_revenue = float(rev_row[0] or 0.0)

    # 2. Cost of Goods Sold (COGS)
    cogs_sql = """
        SELECT SUM(si.quantity * si.unit_cost)
        FROM sale_items si
        JOIN sales s ON si.sale_id = s.id
        WHERE s.business_id = ? AND s.status = 'COMPLETED'
    """
    cogs_params: List[Any] = [current_user.business_id]
    if target_branch:
        cogs_sql += " AND s.branch_id = ?"
        cogs_params.append(target_branch)

    cogs_row = db.execute(cogs_sql, cogs_params).fetchone()
    cogs = float(cogs_row[0] or 0.0)

    # 3. Operational Expenses
    exp_sql = "SELECT SUM(amount) FROM expenses WHERE business_id = ?"
    exp_params: List[Any] = [current_user.business_id]
    if target_branch:
        exp_sql += " AND branch_id = ?"
        exp_params.append(target_branch)

    exp_row = db.execute(exp_sql, exp_params).fetchone()
    total_expenses = float(exp_row[0] or 0.0)

    # 4. Receivables (Khata / Udhaar) & Payables (Suppliers)
    rec_row = db.execute(
        "SELECT SUM(current_balance) FROM customers WHERE business_id = ?",
        (current_user.business_id,),
    ).fetchone()
    total_receivables = float(rec_row[0] or 0.0)

    pay_row = db.execute(
        "SELECT SUM(current_payable) FROM suppliers WHERE business_id = ?",
        (current_user.business_id,),
    ).fetchone()
    total_payables = float(pay_row[0] or 0.0)

    # 5. Inflow / Outflow
    # Inflow: completed non-credit sales + khata payments received
    inflow_sales_sql = """
        SELECT SUM(total_amount) FROM sales
        WHERE business_id = ? AND status = 'COMPLETED' AND payment_method != 'CREDIT'
    """
    inflow_params: List[Any] = [current_user.business_id]
    if target_branch:
        inflow_sales_sql += " AND branch_id = ?"
        inflow_params.append(target_branch)
    inflow_sales = float(db.execute(inflow_sales_sql, inflow_params).fetchone()[0] or 0.0)

    repayments = float(db.execute(
        "SELECT SUM(amount) FROM customer_ledgers WHERE business_id = ? AND entry_type = 'CREDIT'",
        (current_user.business_id,),
    ).fetchone()[0] or 0.0)

    total_inflow = inflow_sales + repayments
    total_outflow = total_expenses

    # 6. Profit Calculations
    gross_profit = total_revenue - cogs
    gross_margin_pct = (gross_profit / total_revenue * 100.0) if total_revenue > 0 else 0.0
    net_profit = gross_profit - total_expenses
    net_margin_pct = (net_profit / total_revenue * 100.0) if total_revenue > 0 else 0.0

    return FinanceSummaryResponse(
        business_id=current_user.business_id,
        branch_id=target_branch,
        total_sales_revenue=round(total_revenue, 2),
        cost_of_goods_sold=round(cogs, 2),
        gross_profit=round(gross_profit, 2),
        gross_profit_margin_pct=round(gross_margin_pct, 2),
        total_operational_expenses=round(total_expenses, 2),
        net_profit=round(net_profit, 2),
        net_profit_margin_pct=round(net_margin_pct, 2),
        total_receivables_khata=round(total_receivables, 2),
        total_payables_suppliers=round(total_payables, 2),
        cash_inflow=round(total_inflow, 2),
        cash_outflow=round(total_outflow, 2),
    )


@router.get(
    "/expenses",
    response_model=ExpenseListResponse,
    summary="List operational expenses with category and branch filtering",
)
def list_expenses(
    branch_id: Optional[str] = Query(None, description="Filter by branch"),
    category: Optional[str] = Query(None, description="Filter category"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: CurrentUser = Depends(require_roles(["owner", "admin", "manager"])),
    db: sqlite3.Connection = Depends(get_db),
) -> ExpenseListResponse:
    """Returns expense records."""
    target_branch = enforce_branch_isolation(current_user, branch_id)

    query = "SELECT * FROM expenses WHERE business_id = ?"
    params: List[Any] = [current_user.business_id]

    if target_branch:
        query += " AND branch_id = ?"
        params.append(target_branch)

    if category:
        query += " AND UPPER(category) = ?"
        params.append(category.upper().strip())

    agg_query = query.replace("SELECT *", "SELECT COUNT(*), SUM(amount)")
    agg_row = db.execute(agg_query, params).fetchone()
    total_count = agg_row[0] or 0
    total_amount = float(agg_row[1] or 0.0)

    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = db.execute(query, params).fetchall()
    expenses = [
        ExpenseOutput(
            id=r["id"],
            business_id=r["business_id"],
            branch_id=r["branch_id"],
            category=r["category"],
            amount=float(r["amount"]),
            payment_method=r["payment_method"],
            description=r["description"],
            receipt_url=r["receipt_url"],
            created_by=r["created_by"],
            created_at=r["created_at"],
        )
        for r in rows
    ]

    return ExpenseListResponse(
        total_count=total_count,
        total_expenses=round(total_amount, 2),
        expenses=expenses,
    )


@router.post(
    "/expenses",
    response_model=ExpenseOutput,
    status_code=status.HTTP_201_CREATED,
    summary="Record an operational expense (Manager/Owner only)",
)
def create_expense(
    req: ExpenseCreateRequest,
    request: Request,
    current_user: CurrentUser = Depends(require_roles(["owner", "admin", "manager"])),
    db: sqlite3.Connection = Depends(get_db),
) -> ExpenseOutput:
    """Logs an expense with category validation and audit trail."""
    branch_id = enforce_branch_isolation(current_user, req.branch_id)
    if not branch_id:
        b_row = db.execute("SELECT id FROM branches WHERE business_id = ? ORDER BY is_main DESC LIMIT 1", (current_user.business_id,)).fetchone()
        branch_id = b_row["id"] if b_row else f"BR_{current_user.business_id}_MAIN"

    exp_id = f"EXP_{uuid.uuid4().hex[:8].upper()}"
    now_str = datetime.now(timezone.utc).isoformat()
    cat_upper = req.category.upper().strip()

    db.execute("""
        INSERT INTO expenses (id, business_id, branch_id, category, amount, payment_method, description, receipt_url, created_by, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        exp_id,
        current_user.business_id,
        branch_id,
        cat_upper,
        round(req.amount, 2),
        req.payment_method.upper().strip(),
        req.description,
        req.receipt_url,
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
        action="CREATE_EXPENSE",
        resource="finance",
        resource_id=exp_id,
        details={"category": cat_upper, "amount": req.amount, "payment_method": req.payment_method},
        ip_address=request.client.host if request.client else "127.0.0.1",
    )

    return ExpenseOutput(
        id=exp_id,
        business_id=current_user.business_id,
        branch_id=branch_id,
        category=cat_upper,
        amount=round(req.amount, 2),
        payment_method=req.payment_method.upper().strip(),
        description=req.description,
        receipt_url=req.receipt_url,
        created_by=current_user.id,
        created_at=now_str,
    )


@router.get(
    "/cashflow",
    response_model=CashflowSummaryResponse,
    summary="Get recent cashflow inflow vs outflow trends",
)
def get_cashflow_summary(
    days: int = Query(7, ge=1, le=90),
    current_user: CurrentUser = Depends(require_roles(["owner", "admin", "manager"])),
    db: sqlite3.Connection = Depends(get_db),
) -> CashflowSummaryResponse:
    """Summarizes cash movement over time."""
    # Group completed sales by date
    sales_rows = db.execute("""
        SELECT SUBSTR(created_at, 1, 10) as dt, SUM(total_amount)
        FROM sales
        WHERE business_id = ? AND status = 'COMPLETED'
        GROUP BY dt ORDER BY dt DESC LIMIT ?
    """, (current_user.business_id, days)).fetchall()

    exp_rows = db.execute("""
        SELECT SUBSTR(created_at, 1, 10) as dt, SUM(amount)
        FROM expenses
        WHERE business_id = ?
        GROUP BY dt ORDER BY dt DESC LIMIT ?
    """, (current_user.business_id, days)).fetchall()

    sales_map = {r[0]: float(r[1]) for r in sales_rows}
    exp_map = {r[0]: float(r[1]) for r in exp_rows}
    all_dates = sorted(set(list(sales_map.keys()) + list(exp_map.keys())))

    daily_points = []
    total_inflow = 0.0
    total_outflow = 0.0

    for dt in all_dates:
        inf = sales_map.get(dt, 0.0)
        outf = exp_map.get(dt, 0.0)
        total_inflow += inf
        total_outflow += outf
        daily_points.append(
            CashflowDailyPoint(
                date=dt,
                inflow=round(inf, 2),
                outflow=round(outf, 2),
                net=round(inf - outf, 2),
            )
        )

    return CashflowSummaryResponse(
        total_inflow=round(total_inflow, 2),
        total_outflow=round(total_outflow, 2),
        net_cashflow=round(total_inflow - total_outflow, 2),
        daily_breakdown=daily_points,
    )

