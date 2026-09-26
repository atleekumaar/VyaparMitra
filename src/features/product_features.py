"""
Product-level feature engineering and aggregations.
Computes volume sales, revenue generated, order depth, customer spread, and pricing.
"""

from __future__ import annotations

import logging
from typing import Optional
import pandas as pd

logger = logging.getLogger(__name__)


def extract_product_features(
    transactions_df: pd.DataFrame,
    products_df: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """
    Generate product-level features:
    - product_sales (total quantity sold)
    - product_revenue (total net_amount)
    - product_order_count (total transactions)
    - unique_customers (count of unique purchasers)
    - average_quantity (mean units per transaction)
    - average_selling_price (net revenue / quantity sold)
    Joins with product catalog metadata.
    """
    logger.info("Extracting product-level features...")
    df = transactions_df.copy()

    grouped = df.groupby("product_id")
    agg_df = grouped.agg(
        product_sales=("quantity", "sum"),
        product_revenue=("net_amount", "sum"),
        product_order_count=("transaction_id", "count"),
        unique_customers=("customer_id", "nunique"),
        average_quantity=("quantity", "mean"),
    ).reset_index()

    agg_df["product_sales"] = agg_df["product_sales"].astype(int)
    agg_df["product_revenue"] = agg_df["product_revenue"].round(2)
    agg_df["average_quantity"] = agg_df["average_quantity"].round(2)
    agg_df["average_selling_price"] = (
        agg_df["product_revenue"] / agg_df["product_sales"].clip(lower=1)
    ).round(2)

    # Join metadata if provided
    if products_df is not None and not products_df.empty:
        agg_df = pd.merge(products_df, agg_df, on="product_id", how="left")
        agg_df["product_sales"] = agg_df["product_sales"].fillna(0).astype(int)
        agg_df["product_revenue"] = agg_df["product_revenue"].fillna(0.0)
        agg_df["product_order_count"] = agg_df["product_order_count"].fillna(0).astype(int)
        agg_df["unique_customers"] = agg_df["unique_customers"].fillna(0).astype(int)
        agg_df["average_quantity"] = agg_df["average_quantity"].fillna(0.0)
        agg_df["average_selling_price"] = agg_df["average_selling_price"].fillna(agg_df["selling_price"]).round(2)

    logger.info("Extracted product features for %d products.", len(agg_df))
    return agg_df
