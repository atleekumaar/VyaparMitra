"""
Unit tests for Phase 3 feature engineering pipelines.
Tests feature construction, lag shift guarantees (no lookahead bias), and calendar extraction.
"""

import numpy as np
import pandas as pd
from src.ml.features.sales_features import extract_sales_forecasting_features
from src.ml.features.demand_features import extract_demand_forecasting_features
from src.ml.features.churn_features import prepare_churn_feature_matrix
from src.ml.features.trend_features import extract_trend_forecasting_features


def test_sales_forecasting_features_no_lookahead():
    dates = pd.date_range("2026-01-01", periods=30, freq="D")
    df = pd.DataFrame({
        "date": dates.strftime("%Y-%m-%d"),
        "revenue": np.arange(1, 31, dtype=float),
    })

    feat_df, cols = extract_sales_forecasting_features(df, date_col="date", target_col="revenue")

    assert "lag_1d_revenue" in cols
    assert "rolling_7d_avg_revenue" in cols
    assert "day_of_week" in cols

    # Lag 1 at index 1 must equal revenue at index 0 (which is 1.0)
    assert feat_df.loc[1, "lag_1d_revenue"] == 1.0
    # Lag 1 at index 0 should be 0.0 (filled NaN)
    assert feat_df.loc[0, "lag_1d_revenue"] == 0.0

    # Ensure rolling_7d_avg_revenue does NOT include the current day revenue
    # At index 1, shifted rolling 7 should be mean of [revenue[0]] = 1.0
    assert feat_df.loc[1, "rolling_7d_avg_revenue"] == 1.0


def test_demand_features_construction():
    dates = pd.date_range("2026-01-01", periods=10, freq="D").strftime("%Y-%m-%d")
    rows = []
    for d in dates:
        for p in ["P1", "P2"]:
            rows.append({"date": d, "product_id": p, "units_sold": 5, "selling_price": 100.0, "unit_cost": 60.0})
    panel = pd.DataFrame(rows)

    feat_df, cols = extract_demand_forecasting_features(panel)

    assert "lag_1_units" in cols
    assert "unit_margin" in cols
    assert (feat_df["unit_margin"] == 40.0).all()


def test_trend_features_labels():
    dates = pd.date_range("2026-01-01", periods=40, freq="D").strftime("%Y-%m-%d")
    df = pd.DataFrame({"date": dates, "revenue": [100.0] * 40})

    feat_df, cols = extract_trend_forecasting_features(df, horizon_days=7, stable_threshold_pct=3.0)

    assert "past_7d_revenue" in cols
    # For flat revenue, the trend label should be 1 (STABLE)
    valid_labels = feat_df["trend_target"].dropna()
    assert (valid_labels == 1).all()
