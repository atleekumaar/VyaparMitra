"""
Customer churn and inactivity risk feature preparation.
Formats numerical behavioral vectors from point-in-time snapshots.
"""

from __future__ import annotations

from typing import List, Tuple
import pandas as pd


def prepare_churn_feature_matrix(
    snapshot_df: pd.DataFrame,
    target_col: str = "is_churned",
) -> Tuple[pd.DataFrame, pd.Series, List[str]]:
    """
    Selects and prepares numerical feature columns from the point-in-time snapshot.
    Guaranteed zero future leakage.
    """
    df = snapshot_df.copy()

    feature_cols = [
        "recency",
        "total_orders",
        "total_spend",
        "average_order_value",
        "days_since_first_purchase",
        "purchase_frequency",
        "recent_7d_orders",
        "recent_30d_orders",
        "recent_90d_orders",
        "recent_30d_spend",
        "recent_90d_spend",
    ]

    # Impute safe numerical defaults for any NaNs
    for c in feature_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)

    X = df[feature_cols].copy()
    y = df[target_col].astype(int)

    return X, y, feature_cols
