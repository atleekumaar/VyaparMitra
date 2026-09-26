"""
Customer-level feature engineering and aggregations.
Computes RFM (Recency, Frequency, Monetary) attributes and lifetime order metrics.
"""

from __future__ import annotations

import logging
from typing import Optional
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def extract_customer_features(
    transactions_df: pd.DataFrame,
    customers_df: Optional[pd.DataFrame] = None,
    reference_date: Optional[str] = None,
) -> pd.DataFrame:
    """
    Generate customer-level features:
    - customer_total_spend
    - customer_order_count
    - customer_average_order_value
    - customer_first_purchase
    - customer_last_purchase
    - customer_purchase_frequency
    - customer_recency
    Joins with customer dimension table.
    """
    logger.info("Extracting customer-level features...")
    df = transactions_df.copy()
    df["ts_parsed"] = pd.to_datetime(df["timestamp"])

    # Reference date for recency calculation (default: max transaction timestamp)
    ref_dt = pd.to_datetime(reference_date) if reference_date else df["ts_parsed"].max()

    grouped = df.groupby("customer_id")
    agg_df = grouped.agg(
        customer_total_spend=("net_amount", "sum"),
        customer_order_count=("transaction_id", "count"),
        customer_average_order_value=("net_amount", "mean"),
        first_ts=("ts_parsed", "min"),
        last_ts=("ts_parsed", "max"),
    ).reset_index()

    agg_df["customer_total_spend"] = agg_df["customer_total_spend"].round(2)
    agg_df["customer_average_order_value"] = agg_df["customer_average_order_value"].round(2)
    
    # Recency in days relative to dataset reference cutoff
    agg_df["customer_recency"] = ((ref_dt - agg_df["last_ts"]) / np.timedelta64(1, "D")).round(1)

    # Purchase frequency: orders per 30-day active window (or total lifespan)
    lifespan_days = ((agg_df["last_ts"] - agg_df["first_ts"]) / np.timedelta64(1, "D")).clip(lower=1.0)
    agg_df["customer_purchase_frequency"] = (agg_df["customer_order_count"] / lifespan_days * 30.0).round(2)

    # Format timestamp strings
    agg_df["customer_first_purchase"] = agg_df["first_ts"].dt.strftime("%Y-%m-%d %H:%M:%S")
    agg_df["customer_last_purchase"] = agg_df["last_ts"].dt.strftime("%Y-%m-%d %H:%M:%S")
    agg_df.drop(columns=["first_ts", "last_ts"], inplace=True)

    # Join metadata if provided
    if customers_df is not None and not customers_df.empty:
        agg_df = pd.merge(customers_df, agg_df, on="customer_id", how="left")
        agg_df["customer_total_spend"] = agg_df["customer_total_spend"].fillna(0.0)
        agg_df["customer_order_count"] = agg_df["customer_order_count"].fillna(0).astype(int)
        agg_df["customer_average_order_value"] = agg_df["customer_average_order_value"].fillna(0.0)
        agg_df["customer_purchase_frequency"] = agg_df["customer_purchase_frequency"].fillna(0.0)
        agg_df["customer_recency"] = agg_df["customer_recency"].fillna(999.0)

    logger.info("Extracted customer features for %d customers.", len(agg_df))
    return agg_df
