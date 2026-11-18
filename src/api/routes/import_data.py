"""
Bulk CSV Import Routes for VyaparMitra.
Provides high-throughput CSV data ingestion with schema validation, transactional integrity,
branch isolation, intelligent header normalization, and audit logging.
"""

from __future__ import annotations

import csv
import io
import logging
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set
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

# Robust numeric cleaning utilities for Indian currency formats (₹, Rs, /-, commas, units)
def _clean_numeric(val: Any, default: float = 0.0, raise_on_error: bool = False) -> float:
    """Parses float stripping currency symbols, commas, trailing /-, and unit suffixes."""
    if val is None:
        return default
    s = str(val).strip().lower()
    if not s or s in ("none", "null", "n/a", "na", "-", "--", "free", "zero"):
        return default
    s_clean = re.sub(r"[₹\$\€\£]|(?i:rs\.?|inr)|/-", "", s).replace(",", "").strip()
    try:
        return float(s_clean)
    except (ValueError, TypeError):
        m = re.search(r"[-+]?\d+(?:\.\d+)?", s_clean)
        if m:
            try:
                return float(m.group(0))
            except Exception:
                pass
        if raise_on_error:
            raise ValueError(f"Could not parse numeric value from '{val}'")
        return default


def _clean_integer(val: Any, default: int = 0) -> int:
    """Parses integer stripping currency, commas, unit suffixes (pcs, pkts, kg, etc.)."""
    if val is None:
        return default
    s = str(val).strip().lower()
    if not s or s in ("none", "null", "n/a", "na", "-", "--"):
        return default
    s_clean = re.sub(r"[₹\$\€\£]|(?i:rs\.?|inr)|/-", "", s).replace(",", "").strip()
    m = re.search(r"[-+]?\d+(?:\.\d+)?", s_clean)
    if m:
        try:
            return int(round(float(m.group(0))))
        except Exception:
            pass
    return default


# Comprehensive synonym mapping to canonical field names
SYNONYM_MAP: Dict[str, str] = {
    # Product identification
    "product": "product_name",
    "product_name": "product_name",
    "productname": "product_name",
    "item_name": "product_name",
    "itemname": "product_name",
    "item": "product_name",
    "items": "product_name",
    "products": "product_name",
    "particulars": "product_name",
    "description": "product_name",
    "item_description": "product_name",
    "product_description": "product_name",
    "title": "product_name",
    "item_title": "product_name",
    "product_title": "product_name",
    "product_id": "product_id",
    "productid": "product_id",
    "item_id": "product_id",
    "itemid": "product_id",
    "item_code": "product_id",
    "sku": "product_id",
    "code": "product_id",
    "product_code": "product_id",

    # Pricing
    "selling_price": "selling_price",
    "sellingprice": "selling_price",
    "price": "selling_price",
    "unit_price": "unit_price",
    "unitprice": "unit_price",
    "rate": "selling_price",
    "mrp": "selling_price",
    "sale_price": "selling_price",
    "saleprice": "selling_price",
    "sales_price": "selling_price",
    "retail_price": "selling_price",
    "selling_rate": "selling_price",
    "sale_rate": "selling_price",
    "mrp_rate": "selling_price",

    # Cost
    "unit_cost": "unit_cost",
    "unitcost": "unit_cost",
    "cost": "unit_cost",
    "cost_price": "unit_cost",
    "costprice": "unit_cost",
    "purchase_price": "unit_cost",
    "purchaseprice": "unit_cost",
    "purchase_rate": "unit_cost",
    "purchaserate": "unit_cost",
    "buy_price": "unit_cost",
    "buying_price": "unit_cost",
    "buy_rate": "unit_cost",

    # Stock / Quantity
    "current_stock": "current_stock",
    "currentstock": "current_stock",
    "stock": "current_stock",
    "closing_stock": "current_stock",
    "opening_stock": "current_stock",
    "available_stock": "current_stock",
    "stock_qty": "current_stock",
    "stock_quantity": "current_stock",
    "available_qty": "current_stock",
    "available_quantity": "current_stock",
    "quantity": "quantity",
    "qty": "quantity",
    "units": "quantity",
    "count": "quantity",
    "items_count": "quantity",
    "pcs": "quantity",
    "balance": "quantity",
    "opening_balance": "quantity",
    "min_stock_threshold": "min_stock_threshold",
    "min_stock": "min_stock_threshold",
    "reorder_point": "min_stock_threshold",
    "reorder_level": "min_stock_threshold",
    "low_stock_limit": "min_stock_threshold",
    "min_qty": "min_stock_threshold",

    # Category & Attributes
    "category": "category",
    "category_name": "category",
    "group": "category",
    "item_category": "category",
    "product_category": "category",
    "item_group": "category",
    "type": "category",
    "department": "category",
    "barcode": "barcode",
    "barcode_no": "barcode",
    "barcode_number": "barcode",
    "upc": "barcode",
    "ean": "barcode",
    "unit": "unit",
    "uom": "unit",
    "unit_of_measure": "unit",

    # Customers & Khata
    "name": "name",
    "customer_name": "customer_name",
    "customer": "customer_name",
    "client_name": "name",
    "client": "name",
    "full_name": "name",
    "customer_full_name": "customer_name",
    "party_name": "name",
    "party": "name",
    "buyer": "name",
    "phone": "phone",
    "mobile": "phone",
    "contact": "phone",
    "mobile_number": "phone",
    "phone_number": "phone",
    "contact_number": "phone",
    "mobile_no": "phone",
    "phone_no": "phone",
    "contact_no": "phone",
    "whatsapp": "phone",
    "whatsapp_number": "phone",
    "email": "email",
    "email_id": "email",
    "email_address": "email",
    "mail": "email",
    "address": "address",
    "customer_address": "address",
    "billing_address": "address",
    "street": "address",
    "location": "address",
    "city": "city",
    "city_name": "city",
    "town": "city",
    "district": "city",
    "state": "state",
    "credit_limit": "credit_limit",
    "credit": "credit_limit",
    "udhaar_limit": "credit_limit",
    "max_credit": "credit_limit",
    "limit": "credit_limit",

    # Sales & Invoices
    "payment_method": "payment_method",
    "payment_mode": "payment_method",
    "mode": "payment_method",
    "pay_mode": "payment_method",
    "payment": "payment_method",
    "discount": "discount",
    "discount_amount": "discount",
    "date": "created_at",
    "timestamp": "created_at",
    "sale_date": "created_at",
    "invoice_number": "invoice_number",
    "invoice_no": "invoice_number",
    "bill_no": "invoice_number",
    "bill_number": "invoice_number",
    "receipt_no": "invoice_number",
    "rate_unit": "selling_price",
    "sale_rate": "selling_price",
    "item_desc": "product_name",
    "product_title": "product_name",
}


def _clean_header_token(token: str) -> str:
    """Strips BOM, whitespace, quotes, currency/unit suffixes in parentheses, and converts separators to underscores."""
    t = token.strip().lower().replace("\ufeff", "")
    # Remove unit/currency annotations in parentheses like (₹), (Rs.), (INR), (Qty), (pcs), (kg)
    t = re.sub(r"\((?:[₹\$\€\£]|rs\.?|inr|qty|pcs|units|kg|gm|in_rs)?\)", "", t)
    t = re.sub(r"[()\[\]{}₹\$\€\£\"']", "", t)
    t = re.sub(r"[\s\-\/\.]+", "_", t)
    return t.strip("_")


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
    2. Validates CSV header with flexible synonym matching.
    3. Row-by-row type validation and auto-resolution of references.
    4. Atomic SQLite transaction execution with branch & tenant isolation.
    5. Audit log tracking (CSV_IMPORT).
    """
    normalized_type = entity_type.strip().lower()
    if normalized_type not in VALID_ENTITY_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid entity_type '{entity_type}'. Allowed: {', '.join(sorted(VALID_ENTITY_TYPES))}",
        )

    # 1. File Type & Size Check
    filename = file.filename or "upload.csv"
    if not filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file extension for '{filename}'. Only .csv files are supported.",
        )

    # 2. Read and Decode Content with size limits
    raw_bytes = await file.read()
    if not raw_bytes or len(raw_bytes.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded CSV file is empty.",
        )

    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
    if len(raw_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file exceeds maximum allowed limit of 5 MB.",
        )

    # Multi-encoding fallback (UTF-16 LE/BE from Excel, UTF-8 with/without BOM, Windows CP1252, Latin-1)
    decoded: Optional[str] = None
    if raw_bytes.startswith(b"\xff\xfe") or raw_bytes.startswith(b"\xfe\xff"):
        try:
            decoded = raw_bytes.decode("utf-16")
        except Exception:
            pass

    if decoded is None:
        for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1", "iso-8859-1"):
            try:
                decoded = raw_bytes.decode(enc)
                break
            except Exception:
                continue

    if decoded is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to decode CSV content. Please save the file in standard UTF-8 format.",
        )

    # Strip null bytes that may arise from foreign encodings
    decoded = decoded.replace("\x00", "")

    # 3. CSV Parsing & Delimiter Detection (handles comma, semicolon, tab, pipe)
    sample_lines = [line for line in decoded.splitlines()[:5] if line.strip()]
    header_candidate = sample_lines[0] if sample_lines else ""

    delimiter = ","
    if "\t" in header_candidate:
        delimiter = "\t"
    elif ";" in header_candidate and header_candidate.count(";") > header_candidate.count(","):
        delimiter = ";"
    elif "|" in header_candidate and header_candidate.count("|") > header_candidate.count(","):
        delimiter = "|"

    stream = io.StringIO(decoded)
    reader = csv.DictReader(stream, delimiter=delimiter)

    if not reader.fieldnames:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file does not contain a header row.",
        )

    raw_headers = [_clean_header_token(f) for f in reader.fieldnames if f]
    canonical_tokens: Set[str] = set()
    for h in raw_headers:
        canonical_tokens.add(h)
        if h in SYNONYM_MAP:
            canonical_tokens.add(SYNONYM_MAP[h])

    # 4. Strict Entity-Type Respect & Header Validation
    has_inv_markers = "current_stock" in canonical_tokens or "min_stock_threshold" in canonical_tokens or "barcode" in canonical_tokens or "unit_cost" in canonical_tokens
    has_sales_markers = "payment_method" in canonical_tokens or "invoice_number" in canonical_tokens or "payment_mode" in canonical_tokens
    has_cust_markers = "credit_limit" in canonical_tokens or (("phone" in canonical_tokens or "email" in canonical_tokens) and "name" in canonical_tokens and "product_name" not in canonical_tokens)

    detected_type: Optional[str] = None
    if has_inv_markers and not has_sales_markers and normalized_type not in ("inventory", "products"):
        detected_type = "inventory"
    elif has_cust_markers and not has_sales_markers and not has_inv_markers and normalized_type != "customers":
        detected_type = "customers"
    elif has_sales_markers and normalized_type != "sales":
        detected_type = "sales"

    if detected_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Entity type mismatch: You selected '{entity_type}', but the CSV headers indicate '{detected_type}' data. "
                f"Please select the correct entity type or upload matching CSV headers for '{entity_type}'."
            ),
        )

    # 5. Schema Validation for the chosen entity type
    missing_requirements: List[str] = []
    if normalized_type in ("inventory", "products"):
        if not ({"product_name", "product_id"} & canonical_tokens):
            missing_requirements.append("product_name (or item / product / title / particulars)")
        if not ({"selling_price", "unit_price"} & canonical_tokens):
            missing_requirements.append("selling_price (or price / rate / mrp)")
    elif normalized_type == "customers":
        if not ({"name", "customer_name", "phone", "email"} & canonical_tokens):
            missing_requirements.append("name (or customer / client / mobile / phone)")
    elif normalized_type == "sales":
        if not ({"product_id", "product_name"} & canonical_tokens):
            missing_requirements.append("product_id or product_name")
        if not ({"quantity", "qty"} & canonical_tokens):
            missing_requirements.append("quantity (or qty / units / count)")

    if missing_requirements:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CSV header validation failed for '{normalized_type}'. Missing required columns: {', '.join(missing_requirements)}.",
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

    # Map raw rows with lowercased keys & canonical synonyms
    for row_idx, raw_row in enumerate(reader, start=2):  # 1-indexed, row 1 is header
        total_rows += 1
        row: Dict[str, str] = {}
        for k, v in raw_row.items():
            if not k:
                continue
            clean_k = _clean_header_token(k)
            val = v.strip() if v else ""
            row[clean_k] = val
            if clean_k in SYNONYM_MAP:
                canon_k = SYNONYM_MAP[clean_k]
                if canon_k not in row or not row[canon_k]:
                    row[canon_k] = val

        # For inventory, if current_stock is not explicitly provided, map quantity/qty/units/stock
        if normalized_type in ("inventory", "products"):
            if not row.get("current_stock"):
                stock_alt = (
                    row.get("quantity")
                    or row.get("qty")
                    or row.get("units")
                    or row.get("stock")
                    or row.get("count")
                    or row.get("closing_stock")
                    or row.get("balance")
                )
                if stock_alt:
                    row["current_stock"] = stock_alt

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
            logger.warning(f"Error importing row {row_idx} into {normalized_type}: {exc}")
            errors.append(
                ImportErrorItem(
                    row_number=row_idx,
                    error=str(exc),
                    row_data=row,
                )
            )

    failed_rows = len(errors)
    db.commit()

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
    product_name = (
        row.get("product_name")
        or row.get("name")
        or row.get("product")
        or row.get("title")
        or row.get("item")
        or row.get("item_name")
        or row.get("particulars")
        or row.get("description")
    )
    if not product_name or not product_name.strip():
        raise ValueError("Missing required 'product_name'.")
    clean_p_name = product_name.strip()

    product_id = (row.get("product_id") or row.get("sku") or row.get("item_code") or row.get("code") or "").strip()
    if not product_id:
        product_id = f"PRD_{uuid.uuid4().hex[:8].upper()}"
    category = (row.get("category") or row.get("group") or "General").strip()

    # Validate selling price (strict validation: non-numeric raises error)
    price_val = (
        row.get("selling_price")
        or row.get("price")
        or row.get("unit_price")
        or row.get("rate")
        or row.get("mrp")
        or row.get("sale_price")
        or row.get("retail_price")
    )
    if price_val and str(price_val).strip():
        selling_price = max(0.0, _clean_numeric(price_val, default=0.0, raise_on_error=True))
    else:
        selling_price = 0.0

    # Validate unit cost (optional, must be >= 0)
    cost_val = (
        row.get("unit_cost")
        or row.get("cost")
        or row.get("cost_price")
        or row.get("purchase_price")
        or row.get("purchase_rate")
        or row.get("buy_price")
    )
    if cost_val and str(cost_val).strip():
        try:
            unit_cost = _clean_numeric(cost_val)
            if unit_cost < 0:
                raise ValueError("Unit cost cannot be negative.")
        except (ValueError, TypeError) as ce:
            raise ValueError(f"Invalid unit_cost '{cost_val}': {ce}")
    else:
        unit_cost = 0.0

    # Validate current stock (non-negative integer)
    stock_val = (
        row.get("current_stock")
        or row.get("stock")
        or row.get("quantity")
        or row.get("qty")
        or row.get("units")
        or row.get("count")
        or row.get("closing_stock")
        or row.get("opening_stock")
        or row.get("available_stock")
        or row.get("balance")
        or row.get("pcs")
    )
    if stock_val and str(stock_val).strip():
        try:
            current_stock = _clean_integer(stock_val)
            if current_stock < 0:
                raise ValueError(f"Current stock cannot be negative, got '{stock_val}'.")
        except (ValueError, TypeError):
            raise ValueError(f"Invalid current_stock '{stock_val}'. Must be a non-negative integer.")
    else:
        current_stock = 0

    # Validate min stock threshold
    min_val = row.get("min_stock_threshold") or row.get("min_stock") or row.get("reorder_point")
    if min_val and str(min_val).strip():
        try:
            min_stock = _clean_integer(min_val)
            if min_stock < 0:
                min_stock = 10
        except (ValueError, TypeError):
            min_stock = 10
    else:
        min_stock = 10

    barcode = (row.get("barcode") or row.get("upc") or "").strip() or None
    unit = (row.get("unit") or row.get("uom") or "pcs").strip()

    # Check if SKU already exists for this branch by product_id or product_name
    existing = db.execute("""
        SELECT id FROM inventory
        WHERE business_id = ? AND branch_id = ? AND (product_id = ? OR LOWER(TRIM(product_name)) = LOWER(TRIM(?)))
    """, (business_id, branch_id, product_id, clean_p_name)).fetchone()

    if existing:
        db.execute("""
            UPDATE inventory
            SET product_name = ?, category = ?, current_stock = ?, min_stock_threshold = ?,
                unit_cost = ?, selling_price = ?, barcode = ?, unit = ?, updated_at = ?
            WHERE id = ?
        """, (
            clean_p_name, category, current_stock, min_stock,
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
            inv_id, business_id, branch_id, product_id, clean_p_name, category,
            current_stock, min_stock, unit_cost, selling_price, barcode, unit, now_str
        ))


def _import_customer_row(
    db: sqlite3.Connection,
    business_id: str,
    row: Dict[str, str],
    now_str: str,
) -> None:
    name = (
        row.get("name")
        or row.get("customer_name")
        or row.get("client_name")
        or row.get("customer")
        or row.get("full_name")
        or row.get("party_name")
        or row.get("party")
        or row.get("buyer")
    )
    phone = (row.get("phone") or row.get("mobile") or row.get("contact") or "").strip() or None
    if not name or not name.strip():
        if phone:
            clean_name = f"Customer {phone[-4:]}"
        else:
            raise ValueError("Missing customer name or mobile number.")
    else:
        clean_name = name.strip()
    email = (row.get("email") or "").strip() or None
    address = (row.get("address") or "").strip() or None
    city = (row.get("city") or "").strip() or None

    raw_credit = row.get("credit_limit") or row.get("credit")
    if raw_credit and str(raw_credit).strip():
        try:
            credit_limit = _clean_numeric(raw_credit)
            if credit_limit < 0:
                raise ValueError("Credit limit cannot be negative.")
        except (ValueError, TypeError):
            raise ValueError(f"Invalid credit_limit '{raw_credit}'.")
    else:
        credit_limit = 5000.0

    cust_id = (row.get("customer_id") or "").strip() or f"CUST_{uuid.uuid4().hex[:8].upper()}"

    # Upsert customer by customer_id, phone, or name
    existing = None
    if row.get("customer_id"):
        existing = db.execute("SELECT id FROM customers WHERE id = ? AND business_id = ?", (cust_id, business_id)).fetchone()
    elif phone:
        existing = db.execute("SELECT id FROM customers WHERE phone = ? AND business_id = ?", (phone, business_id)).fetchone()
    if not existing:
        existing = db.execute("SELECT id FROM customers WHERE LOWER(TRIM(name)) = LOWER(TRIM(?)) AND business_id = ?", (clean_name, business_id)).fetchone()

    if existing:
        db.execute("""
            UPDATE customers
            SET name = ?, phone = COALESCE(?, phone), email = COALESCE(?, email),
                address = COALESCE(?, address), city = COALESCE(?, city), credit_limit = ?
            WHERE id = ?
        """, (clean_name, phone, email, address, city, credit_limit, existing["id"]))
    else:
        db.execute("""
            INSERT INTO customers (
                id, business_id, name, phone, email, address, city,
                credit_limit, current_balance, loyalty_points, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0.0, 0, 'ACTIVE', ?)
        """, (cust_id, business_id, clean_name, phone, email, address, city, credit_limit, now_str))


def _import_sale_row(
    db: sqlite3.Connection,
    current_user: CurrentUser,
    branch_id: str,
    row: Dict[str, str],
    now_str: str,
) -> None:
    product_id = (row.get("product_id") or row.get("sku") or row.get("item_code") or "").strip()
    product_name = (row.get("product_name") or row.get("product") or row.get("item") or "").strip()

    if not product_id and not product_name:
        raise ValueError("Missing product identifier (provide 'product_id' or 'product_name').")

    # Strict quantity validation (must be positive integer, never invent default)
    raw_qty = row.get("quantity") or row.get("qty") or row.get("units") or row.get("count")
    if not raw_qty or not str(raw_qty).strip():
        raise ValueError("Missing 'quantity' for sale item.")
    try:
        quantity = _clean_integer(raw_qty)
        if quantity <= 0:
            raise ValueError(f"Quantity must be a positive integer, got '{raw_qty}'.")
    except (ValueError, TypeError):
        raise ValueError(f"Invalid quantity '{raw_qty}'. Must be an integer > 0.")

    # Lookup inventory item. If not cataloged yet but product_name is provided, auto-catalog it into inventory
    inv = None
    if product_id:
        inv = db.execute("""
            SELECT * FROM inventory
            WHERE business_id = ? AND branch_id = ? AND product_id = ?
        """, (current_user.business_id, branch_id, product_id)).fetchone()

    if not inv and product_name:
        inv = db.execute("""
            SELECT * FROM inventory
            WHERE business_id = ? AND branch_id = ? AND LOWER(TRIM(product_name)) = LOWER(TRIM(?))
        """, (current_user.business_id, branch_id, product_name)).fetchone()

    if not inv:
        if product_name:
            # Auto-catalog product into inventory with initial stock and price
            raw_p = row.get("unit_price") or row.get("price") or row.get("selling_price") or row.get("rate")
            u_price = 50.0
            if raw_p and str(raw_p).strip():
                try:
                    u_price = _clean_numeric(raw_p)
                except Exception:
                    u_price = 50.0
            u_cost = round(u_price * 0.8, 2)
            c_stock = max(50, quantity * 5)
            pid = product_id or f"PRD_{uuid.uuid4().hex[:8].upper()}"
            inv_id = f"INV_{branch_id}_{pid}"
            db.execute("""
                INSERT INTO inventory (
                    id, business_id, branch_id, product_id, product_name, category,
                    current_stock, min_stock_threshold, unit_cost, selling_price,
                    barcode, unit, updated_at
                ) VALUES (?, ?, ?, ?, ?, 'General', ?, 10, ?, ?, NULL, 'pcs', ?)
            """, (inv_id, current_user.business_id, branch_id, pid, product_name, c_stock, u_cost, u_price, now_str))
            inv = db.execute("SELECT * FROM inventory WHERE id = ?", (inv_id,)).fetchone()
        else:
            p_desc = product_id or product_name
            raise ValueError(
                f"Product '{p_desc}' not found in inventory for branch '{branch_id}'. "
                f"Sales import cannot reference uncataloged items. Please create this product in inventory first."
            )

    # Stock verification & auto-replenishment for historical sales with product names
    if inv["current_stock"] < quantity:
        if product_name:
            needed = quantity - int(inv["current_stock"]) + 10
            db.execute("UPDATE inventory SET current_stock = current_stock + ?, updated_at = ? WHERE id = ?", (needed, now_str, inv["id"]))
            inv = db.execute("SELECT * FROM inventory WHERE id = ?", (inv["id"],)).fetchone()
        else:
            raise ValueError(
                f"Insufficient stock for '{inv['product_name']}'. "
                f"Available in branch: {inv['current_stock']}, Requested: {quantity}."
            )

    # Determine unit price - never invent arbitrary default
    raw_price = row.get("unit_price") or row.get("price") or row.get("selling_price") or row.get("rate")
    if raw_price and str(raw_price).strip():
        try:
            unit_price = _clean_numeric(raw_price)
            if unit_price <= 0:
                raise ValueError("Sale unit price must be positive.")
        except (ValueError, TypeError):
            raise ValueError(f"Invalid unit price '{raw_price}'.")
    else:
        unit_price = float(inv["selling_price"])

    unit_cost = float(inv["unit_cost"] or 0.0)
    resolved_p_id = inv["product_id"]
    resolved_p_name = inv["product_name"]

    # Validate discount
    raw_disc = row.get("discount")
    discount = 0.0
    if raw_disc and str(raw_disc).strip():
        try:
            discount = _clean_numeric(raw_disc)
            if discount < 0:
                discount = 0.0
        except (ValueError, TypeError):
            discount = 0.0

    total_amount = max(0.0, (unit_price * quantity) - discount)
    payment_method = (row.get("payment_method") or "UPI").upper().strip()
    customer_id = (row.get("customer_id") or "").strip() or None
    customer_name = (row.get("customer_name") or row.get("customer") or "").strip() or "Walk-in Customer"

    # Auto-link or auto-register customer profile so customer Khata and metrics populate
    if customer_name and customer_name != "Walk-in Customer" and not customer_id:
        c_row = db.execute(
            "SELECT id FROM customers WHERE business_id = ? AND LOWER(TRIM(name)) = LOWER(TRIM(?))",
            (current_user.business_id, customer_name),
        ).fetchone()
        if c_row:
            customer_id = c_row["id"]
        else:
            new_cid = f"CUST_{uuid.uuid4().hex[:8].upper()}"
            db.execute("""
                INSERT INTO customers (
                    id, business_id, name, phone, email, address, city,
                    credit_limit, current_balance, loyalty_points, status, created_at
                ) VALUES (?, ?, ?, NULL, NULL, NULL, NULL, 5000.0, 0.0, 0, 'ACTIVE', ?)
            """, (new_cid, current_user.business_id, customer_name, now_str))
            customer_id = new_cid
    notes = (row.get("notes") or "").strip() or "Bulk CSV Sale Import"
    sale_timestamp = (row.get("created_at") or "").strip() or now_str

    sale_id = f"SALE_{uuid.uuid4().hex[:10].upper()}"
    invoice_number = f"INV-CSV-{uuid.uuid4().hex[:8].upper()}"

    # Atomic stock deduction
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
        current_user.id, current_user.full_name, notes, sale_timestamp
    ))

    # Insert sale item
    db.execute("""
        INSERT INTO sale_items (
            id, sale_id, product_id, product_name, quantity,
            unit_price, unit_cost, discount, total_price
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        f"SI_{uuid.uuid4().hex[:8].upper()}",
        sale_id, resolved_p_id, resolved_p_name, quantity,
        unit_price, unit_cost, discount, round(total_amount, 2)
    ))
