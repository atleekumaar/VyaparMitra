"""
External Benchmark Dataset Adapter for VyaparMitra.
Normalizes third-party customer and product CSV schemas (e.g., Datablist 100 & 2M datasets)
into VyaparMitra canonical operational and ML feature formats.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterator, Optional, Union
import numpy as np
import pandas as pd

USD_TO_INR_DEFAULT = 84.0


def normalize_phone(raw_phone: object) -> str:
    """Extracts clean digits from international phone strings (strips extensions)."""
    if raw_phone is None or (isinstance(raw_phone, float) and np.isnan(raw_phone)):
        return ""
    text = str(raw_phone).split("x")[0].split("X")[0]
    digits = re.sub(r"\D", "", text)
    return digits[-10:] if len(digits) >= 10 else digits


def normalize_external_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Maps external customer CSV columns to VyaparMitra canonical customer schema."""
    out = pd.DataFrame()
    if "Customer Id" in df.columns:
        out["customer_id"] = df["Customer Id"].astype(str).str.strip()
    elif "customer_id" in df.columns:
        out["customer_id"] = df["customer_id"].astype(str).str.strip()
    else:
        out["customer_id"] = [f"CUST_EXT_{i+1:06d}" for i in range(len(df))]

    if "First Name" in df.columns or "Last Name" in df.columns:
        first = df.get("First Name", pd.Series([""] * len(df))).fillna("").astype(str).str.strip()
        last = df.get("Last Name", pd.Series([""] * len(df))).fillna("").astype(str).str.strip()
        out["name"] = (first + " " + last).str.strip()
    else:
        out["name"] = df.get("name", df.get("customer_name", "Unknown Customer")).fillna("Unknown Customer").astype(str).str.strip()

    phone_col = "Phone 1" if "Phone 1" in df.columns else ("phone" if "phone" in df.columns else None)
    out["phone"] = df[phone_col].apply(normalize_phone) if phone_col else ""

    out["email"] = df.get("Email", df.get("email", "")).fillna("").astype(str).str.strip()
    out["company"] = df.get("Company", df.get("company", "")).fillna("").astype(str).str.strip()
    out["city"] = df.get("City", df.get("city", "Unknown")).fillna("Unknown").astype(str).str.strip()
    out["country"] = df.get("Country", df.get("country", "India")).fillna("India").astype(str).str.strip()

    sub_col = "Subscription Date" if "Subscription Date" in df.columns else ("created_at" if "created_at" in df.columns else None)
    if sub_col:
        out["subscription_date"] = pd.to_datetime(df[sub_col], errors="coerce").dt.strftime("%Y-%m-%d").fillna("2026-01-01")
    else:
        out["subscription_date"] = "2026-01-01"

    out["credit_limit"] = 10000.0
    return out


def normalize_external_products(
    df: pd.DataFrame,
    usd_to_inr: float = USD_TO_INR_DEFAULT,
    default_margin: float = 0.25,
) -> pd.DataFrame:
    """Maps external product CSV columns to VyaparMitra canonical product/inventory schema."""
    out = pd.DataFrame()
    if "Internal ID" in df.columns:
        out["product_id"] = "PRD_EXT_" + df["Internal ID"].astype(str).str.strip()
    elif "product_id" in df.columns:
        out["product_id"] = df["product_id"].astype(str).str.strip()
    else:
        out["product_id"] = [f"PRD_EXT_{i+1:06d}" for i in range(len(df))]

    name_col = "Name" if "Name" in df.columns else ("product_name" if "product_name" in df.columns else None)
    out["product_name"] = df[name_col].fillna("Unnamed Product").astype(str).str.strip() if name_col else "Unnamed Product"

    cat_col = "Category" if "Category" in df.columns else ("category" if "category" in df.columns else None)
    out["category"] = df[cat_col].fillna("General").astype(str).str.strip() if cat_col else "General"

    out["brand"] = df.get("Brand", df.get("brand", "")).fillna("").astype(str).str.strip()
    out["barcode"] = df.get("EAN", df.get("barcode", "")).fillna("").astype(str).str.strip()

    price_col = "Price" if "Price" in df.columns else ("selling_price" if "selling_price" in df.columns else None)
    raw_price = pd.to_numeric(df[price_col], errors="coerce").fillna(0.0) if price_col else pd.Series(0.0, index=df.index)
    currency = df.get("Currency", pd.Series(["INR"] * len(df))).fillna("INR").astype(str).str.upper()
    fx = np.where(currency == "USD", usd_to_inr, 1.0)
    selling_inr = np.round(raw_price * fx, 2)

    out["selling_price"] = selling_inr
    out["unit_cost"] = np.round(selling_inr * (1.0 - default_margin), 2)

    stock_col = "Stock" if "Stock" in df.columns else ("current_stock" if "current_stock" in df.columns else None)
    out["current_stock"] = pd.to_numeric(df[stock_col], errors="coerce").fillna(0).astype(int) if stock_col else 0
    out["min_stock_threshold"] = np.maximum(10, (out["current_stock"] * 0.20).astype(int))
    out["availability"] = df.get("Availability", "in_stock").fillna("in_stock").astype(str).str.strip()
    return out


def stream_normalized_external_csv(
    csv_path: Union[str, Path],
    entity_type: str,
    chunksize: int = 50_000,
) -> Iterator[pd.DataFrame]:
    """Memory-safe chunked generator for large (up to 2M+ row) external CSV files."""
    norm_type = entity_type.strip().lower()
    for chunk in pd.read_csv(csv_path, chunksize=chunksize):
        if norm_type == "customers":
            yield normalize_external_customers(chunk)
        elif norm_type in {"products", "inventory"}:
            yield normalize_external_products(chunk)
        else:
            raise ValueError(f"Unsupported entity_type for external adapter: {entity_type}")
