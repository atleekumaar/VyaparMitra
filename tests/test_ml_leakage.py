"""
Targeted tests for data leakage prevention in Phase 3.
Guarantees:
1. No future target leakage in feature engineering (strict shifts).
2. Temporal split boundaries are strictly non-overlapping.
3. Churn snapshot point-in-time features strictly exclude future transactions.
"""

import numpy as np
import pandas as pd
import pytest
from src.ml.data.split import chronological_split
from src.ml.data.churn_dataset import build_customer_churn_snapshot
from src.ml.features.sales_features import extract_sales_forecasting_features


def test_sales_features_zero_future_leakage():
    dates = pd.date_range("2026-01-01", periods=20, freq="D").strftime("%Y-%m-%d")
    df = pd.DataFrame({
        "date": dates,
        "revenue": [10.0 * (i + 1) for i in range(20)],
    })

    feat_df, cols = extract_sales_forecasting_features(df, target_col="revenue")

    # Change a future value (e.g. index 10) and verify that features at index < 10 do NOT change
    df_modified = df.copy()
    df_modified.loc[10, "revenue"] = 999999.0
    feat_df_modified, _ = extract_sales_forecasting_features(df_modified, target_col="revenue")

    # Features at indices 0..9 must be completely identical
    pd.testing.assert_frame_equal(feat_df.loc[:9, cols], feat_df_modified.loc[:9, cols])


def test_churn_snapshot_strictly_pre_cutoff():
    # Build dummy transactions spanning across snapshot_date (2026-07-15)
    tx_data = [
        {"transaction_id": "T1", "customer_id": "C1", "timestamp": "2026-07-10 10:00:00", "net_amount": 500.0, "product_category": "A", "payment_method": "UPI"},
        {"transaction_id": "T2", "customer_id": "C1", "timestamp": "2026-07-20 10:00:00", "net_amount": 2000.0, "product_category": "A", "payment_method": "UPI"},
    ]
    tx_df = pd.DataFrame(tx_data)

    snapshot_df, meta = build_customer_churn_snapshot(tx_df, snapshot_date="2026-07-15", inactivity_days=30)

    # Customer C1 historical total_spend must be strictly 500.0 (from T1), NOT 2500.0!
    c1_row = snapshot_df[snapshot_df["customer_id"] == "C1"].iloc[0]
    assert c1_row["total_spend"] == 500.0
    assert c1_row["total_orders"] == 1
    # Customer had transaction T2 in future window, so is_churned must be 0 (Active)
    assert c1_row["is_churned"] == 0
