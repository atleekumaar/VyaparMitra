"""
Short-term business trend feature engineering.
Constructs forward 7-day relative direction target (INCREASING, STABLE, DECREASING)
and backward historical momentum indicators.
"""

from __future__ import annotations

import logging
from typing import List, Tuple
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def extract_trend_forecasting_features(
    daily_df: pd.DataFrame,
    date_col: str = "date",
    revenue_col: str = "revenue",
    horizon_days: int = 7,
    stable_threshold_pct: float = 3.0,
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Constructs trend target and leakage-free predictor features.
    Target:
    - Previous 7 days revenue: sum of [t-6 to t]
    - Future 7 days revenue: sum of [t+1 to t+horizon_days]
    - Change %: (Future - Previous) / Previous * 100
    - Target label: 2 = INCREASING (> +threshold), 0 = DECREASING (< -threshold), 1 = STABLE
    """
    df = daily_df.sort_values(by=date_col).copy().reset_index(drop=True)
    rev = df[revenue_col]

    # 1. Historical predictor features strictly up to date t
    df["past_7d_revenue"] = rev.rolling(7, min_periods=7).sum()
    df["past_14d_revenue"] = rev.rolling(14, min_periods=14).sum()
    df["past_28d_revenue"] = rev.rolling(28, min_periods=28).sum()

    # Momentum: Growth of past 7d vs the 7d preceding that
    prior_7d = df["past_7d_revenue"].shift(7)
    df["historical_7d_momentum"] = (
        ((df["past_7d_revenue"] - prior_7d) / prior_7d.clip(lower=1e-9)) * 100.0
    ).round(2).fillna(0.0)

    # Calendar features
    dt = pd.to_datetime(df[date_col])
    df["day_of_week"] = dt.dt.dayofweek
    df["month"] = dt.dt.month
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)

    # 2. Target Generation (Lookahead horizon [t+1 to t+horizon_days])
    # Future 7 days: shift(-horizon_days).rolling(horizon_days).sum()
    future_rev = rev.iloc[::-1].rolling(horizon_days, min_periods=horizon_days).sum().iloc[::-1].shift(-1)
    df["future_7d_revenue"] = future_rev

    change_pct = ((df["future_7d_revenue"] - df["past_7d_revenue"]) / df["past_7d_revenue"].clip(lower=1e-9)) * 100.0
    df["trend_change_pct"] = change_pct

    def assign_trend_class(pct: float) -> Optional[int]:
        if pd.isna(pct):
            return None
        if pct > stable_threshold_pct:
            return 2  # INCREASING
        elif pct < -stable_threshold_pct:
            return 0  # DECREASING
        else:
            return 1  # STABLE

    df["trend_target"] = df["trend_change_pct"].apply(assign_trend_class)

    feature_cols = [
        "past_7d_revenue",
        "past_14d_revenue",
        "past_28d_revenue",
        "historical_7d_momentum",
        "day_of_week",
        "month",
        "is_weekend",
    ]

    # Drop edge rows where past 28d or future 7d is undefined
    valid_df = df.dropna(subset=["past_28d_revenue", "trend_target"]).copy()
    valid_df["trend_target"] = valid_df["trend_target"].astype(int)

    return valid_df, feature_cols
