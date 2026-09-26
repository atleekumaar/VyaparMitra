"""
Forecasting dataset builder for daily sales and product demand panels.
Correctly handles zero-demand days through full cross-product grids.
"""

from __future__ import annotations

import logging
from typing import Optional
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def build_daily_sales_dataset(
    daily_features_df: pd.DataFrame,
    transactions_df: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """
    Build clean daily sales time-series dataset.
    Extracts date, revenue, orders, units, and environmental context.
    """
    df = daily_features_df.copy()
    if "date" not in df.columns:
        raise ValueError("daily_features_df must contain 'date' column.")

    # Standardize target column
    if "daily_total_revenue" in df.columns:
        df["revenue"] = df["daily_total_revenue"]
    elif "net_amount" in df.columns:
        df["revenue"] = df["net_amount"]

    # Fill default environmental features if missing
    if "is_festival" not in df.columns:
        df["is_festival"] = 0
    if "festival_intensity" not in df.columns:
        df["festival_intensity"] = 0.0
    if "avg_temperature" in df.columns:
        df["temperature"] = df["avg_temperature"]
    elif "temperature" not in df.columns:
        df["temperature"] = 27.0
    if "total_rainfall" in df.columns:
        df["rainfall"] = df["total_rainfall"]
    elif "rainfall" not in df.columns:
        df["rainfall"] = 0.0
    if "is_rainy_day" in df.columns:
        df["is_rainy"] = df["is_rainy_day"]
    elif "is_rainy" not in df.columns:
        df["is_rainy"] = (df["rainfall"] > 0).astype(int)

    df = df.sort_values(by="date").reset_index(drop=True)
    return df


def build_product_demand_panel(
    transactions_df: pd.DataFrame,
    products_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Constructs a complete balanced panel of Product x Date.
    Crucial: Handles zero-sales days explicitly by filling units_sold = 0 and revenue = 0.
    """
    logger.info("Building balanced Product x Date demand panel...")
    tx = transactions_df.copy()
    if "date" not in tx.columns and "timestamp" in tx.columns:
        tx["date"] = pd.to_datetime(tx["timestamp"]).dt.strftime("%Y-%m-%d")
    if "net_amount" not in tx.columns:
        if "quantity" in tx.columns and "unit_price" in tx.columns:
            discount = tx["discount"] if "discount" in tx.columns else 0.0
            tx["net_amount"] = (tx["quantity"] * tx["unit_price"] - discount).clip(lower=0.0)
        else:
            tx["net_amount"] = 0.0

    all_dates = sorted(tx["date"].unique())
    all_products = products_df["product_id"].unique()

    # 1. Aggregate actual observed sales at (date, product_id)
    observed = tx.groupby(["date", "product_id"]).agg(
        units_sold=("quantity", "sum"),
        revenue=("net_amount", "sum"),
        orders_count=("transaction_id", "count"),
    ).reset_index()

    # 2. Build full Cartesian grid
    grid = pd.MultiIndex.from_product(
        [all_dates, all_products], names=["date", "product_id"]
    ).to_frame().reset_index(drop=True)

    # 3. Merge observed sales onto grid
    panel = pd.merge(grid, observed, on=["date", "product_id"], how="left")
    panel["units_sold"] = panel["units_sold"].fillna(0).astype(int)
    panel["revenue"] = panel["revenue"].fillna(0.0).round(2)
    panel["orders_count"] = panel["orders_count"].fillna(0).astype(int)

    # 4. Merge product catalog metadata
    prod_meta = products_df[["product_id", "product_name", "product_category", "unit_cost", "selling_price"]].drop_duplicates()
    panel = pd.merge(panel, prod_meta, on="product_id", how="left")

    panel = panel.sort_values(by=["product_id", "date"]).reset_index(drop=True)
    logger.info("Constructed demand panel: %d records (%d products x %d dates)", len(panel), len(all_products), len(all_dates))
    return panel
