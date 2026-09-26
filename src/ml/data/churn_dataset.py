"""
Customer churn and inactivity risk snapshot dataset constructor.
Implements strict point-in-time snapshot logic without lookahead bias.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Tuple
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def build_customer_churn_snapshot(
    transactions_df: pd.DataFrame,
    snapshot_date: str = "2026-07-15",
    inactivity_days: int = 30,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Constructs a point-in-time customer snapshot at `snapshot_date`.
    Features: Strictly derived from transactions occurring BEFORE snapshot_date.
    Target: 1 if customer placed ZERO orders between [snapshot_date, snapshot_date + inactivity_days], 0 otherwise.
    """
    tx = transactions_df.copy()
    tx["ts"] = pd.to_datetime(tx["timestamp"])
    if "net_amount" not in tx.columns:
        if "quantity" in tx.columns and "unit_price" in tx.columns:
            discount = tx["discount"] if "discount" in tx.columns else 0.0
            tx["net_amount"] = (tx["quantity"] * tx["unit_price"] - discount).clip(lower=0.0)
        else:
            tx["net_amount"] = 0.0

    snapshot_ts = pd.to_datetime(snapshot_date)
    cutoff_future_ts = snapshot_ts + pd.Timedelta(days=inactivity_days)

    # 1. Historical transactions strictly before snapshot_date
    history_tx = tx[tx["ts"] < snapshot_ts].copy()
    if history_tx.empty:
        raise ValueError(f"No transactions found before snapshot date {snapshot_date}")

    # 2. Evaluation window transactions [snapshot_ts, cutoff_future_ts]
    future_tx = tx[(tx["ts"] >= snapshot_ts) & (tx["ts"] <= cutoff_future_ts)].copy()
    active_customers_in_window = set(future_tx["customer_id"].unique())

    # 3. Derive point-in-time features per customer
    all_past_customers = history_tx["customer_id"].unique()

    # Pre-compute time windows
    ts_7d = snapshot_ts - pd.Timedelta(days=7)
    ts_30d = snapshot_ts - pd.Timedelta(days=30)
    ts_90d = snapshot_ts - pd.Timedelta(days=90)

    # Aggregations
    overall_agg = history_tx.groupby("customer_id").agg(
        total_orders=("transaction_id", "count"),
        total_spend=("net_amount", "sum"),
        first_purchase=("ts", "min"),
        last_purchase=("ts", "max"),
        preferred_category=("product_category", lambda s: s.mode()[0] if not s.empty else "General"),
        preferred_payment_method=("payment_method", lambda s: s.mode()[0] if not s.empty else "UPI"),
    ).reset_index()

    # Windowed features
    tx_7d = history_tx[history_tx["ts"] >= ts_7d].groupby("customer_id")["transaction_id"].count().rename("recent_7d_orders")
    tx_30d = history_tx[history_tx["ts"] >= ts_30d].groupby("customer_id").agg(
        recent_30d_orders=("transaction_id", "count"),
        recent_30d_spend=("net_amount", "sum"),
    )
    tx_90d = history_tx[history_tx["ts"] >= ts_90d].groupby("customer_id").agg(
        recent_90d_orders=("transaction_id", "count"),
        recent_90d_spend=("net_amount", "sum"),
    )

    # Merge features
    feat_df = pd.merge(overall_agg, tx_7d, on="customer_id", how="left").fillna({"recent_7d_orders": 0})
    feat_df = pd.merge(feat_df, tx_30d, on="customer_id", how="left").fillna({"recent_30d_orders": 0, "recent_30d_spend": 0.0})
    feat_df = pd.merge(feat_df, tx_90d, on="customer_id", how="left").fillna({"recent_90d_orders": 0, "recent_90d_spend": 0.0})

    # Continuous recency and tenure metrics
    feat_df["recency"] = ((snapshot_ts - feat_df["last_purchase"]) / np.timedelta64(1, "D")).round(1)
    feat_df["days_since_first_purchase"] = ((snapshot_ts - feat_df["first_purchase"]) / np.timedelta64(1, "D")).round(1)
    feat_df["days_since_last_purchase"] = feat_df["recency"]
    feat_df["average_order_value"] = (feat_df["total_spend"] / feat_df["total_orders"].clip(lower=1)).round(2)
    feat_df["purchase_frequency"] = (feat_df["total_orders"] / (feat_df["days_since_first_purchase"].clip(lower=1.0)) * 30.0).round(2)

    # 4. Target variable assignment: 1 = Inactive/Churned (0 purchases in future window), 0 = Active
    feat_df["is_churned"] = (~feat_df["customer_id"].isin(active_customers_in_window)).astype(int)
    feat_df["snapshot_date"] = snapshot_date

    churn_rate = float(feat_df["is_churned"].mean())
    meta = {
        "snapshot_date": snapshot_date,
        "inactivity_horizon_days": inactivity_days,
        "total_customers_in_snapshot": len(feat_df),
        "churned_inactive_count": int(feat_df["is_churned"].sum()),
        "active_retained_count": int((feat_df["is_churned"] == 0).sum()),
        "churn_rate": round(churn_rate, 4),
    }

    logger.info("Built churn snapshot (%s): %d customers, churn rate: %.2f%%", snapshot_date, len(feat_df), churn_rate * 100)
    return feat_df, meta
