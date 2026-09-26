"""
Merchant-level feature engineering and aggregations.
Computes merchant performance, customer reach, catalog breadth, and daily velocity.
"""

from __future__ import annotations

import logging
from typing import Optional
import pandas as pd

logger = logging.getLogger(__name__)


def extract_merchant_features(
    transactions_df: pd.DataFrame,
    merchants_df: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """
    Generate merchant-level features:
    - merchant_total_revenue
    - merchant_total_orders
    - average_order_value
    - unique_customers
    - unique_products
    - active_days
    - revenue_per_day
    - orders_per_day
    Joins with merchant metadata (name, business_type, city, state, coords).
    """
    logger.info("Extracting merchant-level features...")
    df = transactions_df.copy()

    # Base aggregations
    grouped = df.groupby("merchant_id")
    agg_df = grouped.agg(
        merchant_total_revenue=("net_amount", "sum"),
        merchant_total_orders=("transaction_id", "count"),
        average_order_value=("net_amount", "mean"),
        unique_customers=("customer_id", "nunique"),
        unique_products=("product_id", "nunique"),
        active_days=("date", "nunique"),
    ).reset_index()

    # Derived rates per active day
    agg_df["merchant_total_revenue"] = agg_df["merchant_total_revenue"].round(2)
    agg_df["average_order_value"] = agg_df["average_order_value"].round(2)
    agg_df["revenue_per_day"] = (agg_df["merchant_total_revenue"] / agg_df["active_days"].clip(lower=1)).round(2)
    agg_df["orders_per_day"] = (agg_df["merchant_total_orders"] / agg_df["active_days"].clip(lower=1)).round(2)

    # Join metadata if provided
    if merchants_df is not None and not merchants_df.empty:
        agg_df = pd.merge(merchants_df, agg_df, on="merchant_id", how="left")
        # Fill zeros for merchants with no transactions
        agg_df["merchant_total_revenue"] = agg_df["merchant_total_revenue"].fillna(0.0)
        agg_df["merchant_total_orders"] = agg_df["merchant_total_orders"].fillna(0).astype(int)
        agg_df["average_order_value"] = agg_df["average_order_value"].fillna(0.0)
        agg_df["unique_customers"] = agg_df["unique_customers"].fillna(0).astype(int)
        agg_df["unique_products"] = agg_df["unique_products"].fillna(0).astype(int)
        agg_df["active_days"] = agg_df["active_days"].fillna(0).astype(int)
        agg_df["revenue_per_day"] = agg_df["revenue_per_day"].fillna(0.0)
        agg_df["orders_per_day"] = agg_df["orders_per_day"].fillna(0.0)

    logger.info("Extracted merchant features for %d merchants.", len(agg_df))
    return agg_df
