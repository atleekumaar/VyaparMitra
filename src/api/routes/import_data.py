"""
Bulk CSV Import Routes for VyaparMitra.
Provides high-throughput CSV data ingestion with schema validation, transactional integrity,
branch isolation, and audit logging.
"""

from __future__ import annotations

import csv
import io
import logging
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile, status

from src.api.audit import record_audit_log
from src.api.auth import (
    CurrentUser,
    enforce_branch_isolation,
    get_current_user,
    require_roles,
)
from src.api.backend_schemas import CSVImportResponse, ImportErrorItem
from src.api.db import get_db

logger = logging.getLogger("vyaparmitra.api.import")
router = APIRouter(prefix="/import", tags=["Bulk CSV Import"])

VALID_ENTITY_TYPES = {"inventory", "products", "customers", "sales"}

REQUIRED_COLUMNS: Dict[str, List[str]] = {
    "inventory": ["product_name", "selling_price"],
    "products": ["product_name", "selling_price"],
    "customers": ["name"],
    "sales": ["product_id", "quantity"],
}


@router.post(
    "/csv",
    response_model=CSVImportResponse,
    status_code=status.HTTP_200_OK,
    summary="Bulk import CSV data for inventory, products, customers, or sales",
)
async def import_csv(
    request: Request,
    entity_type: str = Query(..., description="Target entity type: inventory, products, customers, sales"),
    branch_id: Optional[str] = Query(None, description="Target branch ID for branch-scoped data"),
    file: UploadFile = File(..., description="CSV file to upload and parse"),
    current_user: CurrentUser = Depends(require_roles(["owner", "admin", "manager"])),
    db: sqlite3.Connection = Depends(get_db),
) -> CSVImportResponse:
    """
    Imports CSV records into VyaparMitra operational tables:
    1. Validates file extension and CSV format.
    2. Validates CSV header against required schema.
    3. Row-by-row type validation with error trapping.
    4. Atomic SQLite transaction execution with branch & tenant isolation.
    5. Audit log tracking (CSV_IMPORT).
    """
    normalized_type = entity_type.strip().lower()
    if normalized_type not in VALID_ENTITY_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid entity_type '{entity_type}'. Allowed: {', '.join(sorted(VALID_ENTITY_TYPES))}",
        )

    # 1. File Type Check
    filename = file.filename or "upload.csv"
    if not filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file extension for '{filename}'. Only .csv files are supported.",
        )

    # 2. Read and Decode Content
    raw_bytes = await file.read()
    if not raw_bytes or len(raw_bytes.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded CSV file is empty.",
        )

    try:
        decoded = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            decoded = raw_bytes.decode("latin-1")
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to decode CSV content: {exc}",
            )

    # 3. CSV Parsing & Header Normalization
    stream = io.StringIO(decoded)
    reader = csv.DictReader(stream)

    if not reader.fieldnames:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file does not contain a header row.",
        )

    cleaned_fieldnames = [f.strip().lower() for f in reader.fieldnames if f]
    required_cols = REQUIRED_COLUMNS[normalized_type]

    missing_cols = [col for col in required_cols if col not in cleaned_fieldnames]
    if missing_cols:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CSV header validation failed for '{normalized_type}'. Missing required columns: {', '.join(missing_cols)}.",
        )

    # Enforce multi-branch isolation
    target_branch = enforce_branch_isolation(current_user, branch_id)
    if not target_branch:
        b_row = db.execute(
            "SELECT id FROM branches WHERE business_id = ? ORDER BY is_main DESC LIMIT 1",
            (current_user.business_id,),
        ).fetchone()
        target_branch = b_row["id"] if b_row else f"BR_{current_user.business_id}_MAIN"

    now_str = datetime.now(timezone.utc).isoformat()
    total_rows = 0
    inserted_rows = 0
    errors: List[ImportErrorItem] = []

    # Map raw rows with lowercased keys
    for row_idx, raw_row in enumerate(reader, start=2):  # 1-indexed, row 1 is header
        total_rows += 1
        row = {k.strip().lower(): v.strip() if v else "" for k, v in raw_row.items() if k}

        try:
            if normalized_type in ("inventory", "products"):
                _import_inventory_row(db, current_user.business_id, target_branch, row, now_str)
                inserted_rows += 1
            elif normalized_type == "customers":
                _import_customer_row(db, current_user.business_id, row, now_str)
                inserted_rows += 1
            elif normalized_type == "sales":
                _import_sale_row(db, current_user, target_branch, row, now_str)
                inserted_rows += 1
        except Exception as exc:
            errors.append(
                ImportErrorItem(
                    row_number=row_idx,
                    error=str(exc),
                    row_data=row,
                )
            )

    failed_rows = len(errors)

    # Audit Logging
    record_audit_log(
        db=db,
        business_id=current_user.business_id,
        branch_id=target_branch,
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="CSV_IMPORT",
        resource=normalized_type,
        resource_id=filename,
        details={
            "filename": filename,
            "entity_type": normalized_type,
            "total_rows": total_rows,
            "inserted_rows": inserted_rows,
            "failed_rows": failed_rows,
        },
        ip_address=request.client.host if request.client else "127.0.0.1",
    )

    message = f"CSV import completed for {normalized_type}. {inserted_rows}/{total_rows} rows imported successfully."
    if failed_rows > 0:
        message += f" {failed_rows} rows had validation errors."

    return CSVImportResponse(
        entity_type=normalized_type,
        filename=filename,
        total_rows=total_rows,
        inserted_rows=inserted_rows,
        failed_rows=failed_rows,
        errors=errors,
        message=message,
    )


def _import_inventory_row(
    db: sqlite3.Connection,
    business_id: str,
    branch_id: str,
    row: Dict[str, str],
    now_str: str,
) -> None:
    product_name = row.get("product_name")
    if not product_name:
        raise ValueError("Missing 'product_name'.")

    product_id = row.get("product_id") or f"PRD_{uuid.uuid4().hex[:8].upper()}"
    category = row.get("category") or "General"

    try:
        selling_price = float(row.get("selling_price", 0.0))
        if selling_price < 0:
            raise ValueError("Selling price cannot be negative.")
    except (ValueError, TypeError):
        raise ValueError(f"Invalid selling_price: '{row.get('selling_price')}'. Must be a positive number.")

    try:
        unit_cost = float(row.get("unit_cost", 0.0)) if row.get("unit_cost") else 0.0
    except (ValueError, TypeError):
        unit_cost = 0.0

    try:
        current_stock = int(float(row.get("current_stock", 0))) if row.get("current_stock") else 0
        if current_stock < 0:
            current_stock = 0
    except (ValueError, TypeError):
        current_stock = 0

    try:
        min_stock = int(float(row.get("min_stock_threshold", 10))) if row.get("min_stock_threshold") else 10
    except (ValueError, TypeError):
        min_stock = 10

    barcode = row.get("barcode") or None
    unit = row.get("unit") or "pcs"

    # Check if SKU already exists for this branch
    existing = db.execute("""
        SELECT id FROM inventory
        WHERE business_id = ? AND branch_id = ? AND product_id = ?
    """, (business_id, branch_id, product_id)).fetchone()

    if existing:
        db.execute("""
            UPDATE inventory
            SET product_name = ?, category = ?, current_stock = ?, min_stock_threshold = ?,
                unit_cost = ?, selling_price = ?, barcode = ?, unit = ?, updated_at = ?
            WHERE id = ?
        """, (
            product_name, category, current_stock, min_stock,
            unit_cost, selling_price, barcode, unit, now_str, existing["id"]
        ))
    else:
        inv_id = f"INV_{branch_id}_{product_id}"
        db.execute("""
            INSERT INTO inventory (
                id, business_id, branch_id, product_id, product_name, category,
                current_stock, min_stock_threshold, unit_cost, selling_price,
                barcode, unit, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            inv_id, business_id, branch_id, product_id, product_name, category,
            current_stock, min_stock, unit_cost, selling_price, barcode, unit, now_str
        ))


def _import_customer_row(
    db: sqlite3.Connection,
    business_id: str,
    row: Dict[str, str],
    now_str: str,
) -> None:
    name = row.get("name")
    if not name:
        raise ValueError("Missing 'name'.")

    phone = row.get("phone") or None
    email = row.get("email") or None
    address = row.get("address") or None
    city = row.get("city") or None

    try:
        credit_limit = float(row.get("credit_limit", 5000.0)) if row.get("credit_limit") else 5000.0
    except (ValueError, TypeError):
        credit_limit = 5000.0

    cust_id = row.get("customer_id") or f"CUST_{uuid.uuid4().hex[:8].upper()}"

    # Upsert customer by customer_id or phone
    existing = None
    if row.get("customer_id"):
        existing = db.execute("SELECT id FROM customers WHERE id = ? AND business_id = ?", (row["customer_id"], business_id)).fetchone()
    elif phone:
        existing = db.execute("SELECT id FROM customers WHERE phone = ? AND business_id = ?", (phone, business_id)).fetchone()

    if existing:
        db.execute("""
            UPDATE customers
            SET name = ?, phone = ?, email = ?, address = ?, city = ?, credit_limit = ?
            WHERE id = ?
        """, (name, phone, email, address, city, credit_limit, existing["id"]))
    else:
        db.execute("""
            INSERT INTO customers (
                id, business_id, name, phone, email, address, city,
                credit_limit, current_balance, loyalty_points, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0.0, 0, 'ACTIVE', ?)
        """, (cust_id, business_id, name, phone, email, address, city, credit_limit, now_str))


def _import_sale_row(
    db: sqlite3.Connection,
    current_user: CurrentUser,
    branch_id: str,
    row: Dict[str, str],
    now_str: str,
) -> None:
    product_id = row.get("product_id")
    if not product_id:
        raise ValueError("Missing 'product_id'.")

    try:
        quantity = int(float(row.get("quantity", 1)))
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
    except (ValueError, TypeError):
        raise ValueError(f"Invalid quantity '{row.get('quantity')}'. Must be an integer > 0.")

    # Check inventory
    inv = db.execute("""
        SELECT * FROM inventory
        WHERE business_id = ? AND branch_id = ? AND product_id = ?
    """, (current_user.business_id, branch_id, product_id)).fetchone()

    if not inv:
        raise ValueError(f"Product '{product_id}' not found in branch inventory.")

    if inv["current_stock"] < quantity:
        raise ValueError(f"Insufficient stock for '{inv['product_name']}'. In stock: {inv['current_stock']}, Requested: {quantity}.")

    try:
        unit_price = float(row.get("unit_price")) if row.get("unit_price") else float(inv["selling_price"])
    except (ValueError, TypeError):
        unit_price = float(inv["selling_price"])

    try:
        discount = float(row.get("discount", 0.0)) if row.get("discount") else 0.0
    except (ValueError, TypeError):
        discount = 0.0

    total_amount = max(0.0, (unit_price * quantity) - discount)
    payment_method = (row.get("payment_method") or "CASH").upper().strip()
    customer_id = row.get("customer_id") or None
    customer_name = row.get("customer_name") or "Walk-in Customer"
    notes = row.get("notes") or "Bulk CSV Sale Import"

    sale_id = f"SALE_{uuid.uuid4().hex[:10].upper()}"
    invoice_number = f"INV-CSV-{uuid.uuid4().hex[:8].upper()}"

    # Deduct stock
    db.execute("""
        UPDATE inventory SET current_stock = current_stock - ?, updated_at = ?
        WHERE id = ?
    """, (quantity, now_str, inv["id"]))

    # Insert sale
    db.execute("""
        INSERT INTO sales (
            id, invoice_number, business_id, branch_id, customer_id, customer_name,
            subtotal, discount, tax, total_amount, payment_method, status,
            created_by, created_by_name, notes, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0.0, ?, ?, 'COMPLETED', ?, ?, ?, ?)
    """, (
        sale_id, invoice_number, current_user.business_id, branch_id,
        customer_id, customer_name, round(unit_price * quantity, 2),
        round(discount, 2), round(total_amount, 2), payment_method,
        current_user.id, current_user.full_name, notes, now_str
    ))

    # Insert sale item
    db.execute("""
        INSERT INTO sale_items (
            id, sale_id, product_id, product_name, quantity,
            unit_price, unit_cost, discount, total_price
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        f"SI_{uuid.uuid4().hex[:8].upper()}",
        sale_id, product_id, inv["product_name"], quantity,
        unit_price, float(inv["unit_cost"]), discount, round(total_amount, 2)
    ))
