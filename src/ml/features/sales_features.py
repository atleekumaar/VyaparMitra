"""
Daily sales forecasting feature engineering.
Constructs lags, trailing rolling statistics, calendar indicators, and external drivers.
Strict anti-leakage rule: All moving windows are shifted by 1.
"""

from __future__ import annotations

import logging
from typing import List, Tuple
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def extract_sales_forecasting_features(
    daily_df: pd.DataFrame,
    date_col: str = "date",
    target_col: str = "revenue",
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Extract leakage-free features for daily revenue forecasting.
    Features:
    - lag_1d_revenue, lag_7d_revenue, lag_14d_revenue, lag_28d_revenue
    - rolling_7d_avg_revenue, rolling_14d_avg_revenue, rolling_28d_avg_revenue
    - day_of_week, day_of_month, week_of_year, month, quarter, is_weekend
    - is_festival, festival_intensity, temperature, rainfall, is_rainy
    - recent_order_count_7d, recent_aov_7d
    """
    df = daily_df.sort_values(by=date_col).copy().reset_index(drop=True)

    # 1. Historical Target Lags
    df["lag_1d_revenue"] = df[target_col].shift(1)
    df["lag_7d_revenue"] = df[target_col].shift(7)
    df["lag_14d_revenue"] = df[target_col].shift(14)
    df["lag_28d_revenue"] = df[target_col].shift(28)

    # 2. Trailing Rolling Statistics (Strictly shift(1) to avoid lookahead leakage)
    rev_shifted = df[target_col].shift(1)
    df["rolling_7d_avg_revenue"] = rev_shifted.rolling(window=7, min_periods=1).mean().round(2)
    df["rolling_14d_avg_revenue"] = rev_shifted.rolling(window=14, min_periods=1).mean().round(2)
    df["rolling_28d_avg_revenue"] = rev_shifted.rolling(window=28, min_periods=1).mean().round(2)

    # 3. Calendar attributes
    dt = pd.to_datetime(df[date_col])
    df["day_of_week"] = dt.dt.dayofweek
    df["day_of_month"] = dt.dt.day
    df["week_of_year"] = dt.dt.isocalendar().week.astype(int)
    df["month"] = dt.dt.month
    df["quarter"] = dt.dt.quarter
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)

    # 4. External environmental context
    if "is_festival" not in df.columns:
        df["is_festival"] = 0
    if "festival_intensity" not in df.columns:
        df["festival_intensity"] = 0.0
    if "temperature" not in df.columns:
        df["temperature"] = 27.0
    if "rainfall" not in df.columns:
        df["rainfall"] = 0.0
    if "is_rainy" not in df.columns:
        df["is_rainy"] = (df["rainfall"] > 0).astype(int)

    # 5. Recent trailing operational volume
    if "daily_total_orders" in df.columns:
        df["recent_order_count_7d"] = df["daily_total_orders"].shift(1).rolling(7, min_periods=1).mean().round(1)
    elif "orders" in df.columns:
        df["recent_order_count_7d"] = df["orders"].shift(1).rolling(7, min_periods=1).mean().round(1)
    else:
        df["recent_order_count_7d"] = 1.0

    df["recent_aov_7d"] = (df["rolling_7d_avg_revenue"] / df["recent_order_count_7d"].clip(lower=1.0)).round(2)

    # Fill initial boundary missing lags with 0.0 to strictly prevent lookahead leakage
    lag_cols = ["lag_1d_revenue", "lag_7d_revenue", "lag_14d_revenue", "lag_28d_revenue"]
    for c in lag_cols:
        df[c] = df[c].fillna(0.0)

    feature_cols = [
        "lag_1d_revenue", "lag_7d_revenue", "lag_14d_revenue", "lag_28d_revenue",
        "rolling_7d_avg_revenue", "rolling_14d_avg_revenue", "rolling_28d_avg_revenue",
        "day_of_week", "day_of_month", "week_of_year", "month", "quarter", "is_weekend",
        "is_festival", "festival_intensity", "temperature", "rainfall", "is_rainy",
        "recent_order_count_7d", "recent_aov_7d"
    ]

    return df, feature_cols
