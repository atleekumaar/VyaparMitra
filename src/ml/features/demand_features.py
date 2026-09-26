"""
Product demand forecasting feature engineering.
Computes item-level demand lags, rolling averages, category signals, and pricing attributes.
"""

from __future__ import annotations

import logging
from typing import List, Tuple
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def extract_demand_forecasting_features(
    panel_df: pd.DataFrame,
    date_col: str = "date",
    product_col: str = "product_id",
    target_col: str = "units_sold",
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Generate product demand features:
    - lag_1_units, lag_7_units, lag_14_units, lag_28_units (grouped by product)
    - rolling_7_units, rolling_14_units, rolling_28_units (grouped by product, shift 1)
    - selling_price, unit_cost
    - day_of_week, day_of_month, month, is_weekend
    """
    df = panel_df.sort_values(by=[product_col, date_col]).copy().reset_index(drop=True)

    # 1. Product-level Lags (Shifted strictly)
    grouped = df.groupby(product_col)[target_col]
    df["lag_1_units"] = grouped.shift(1).fillna(0.0)
    df["lag_7_units"] = grouped.shift(7).fillna(0.0)
    df["lag_14_units"] = grouped.shift(14).fillna(0.0)
    df["lag_28_units"] = grouped.shift(28).fillna(0.0)

    # 2. Product-level Trailing Moving Averages (Shift 1)
    shifted_units = grouped.shift(1)
    # Using transform with rolling on shifted series
    df["_shifted"] = shifted_units
    df["rolling_7_units"] = df.groupby(product_col)["_shifted"].transform(lambda s: s.rolling(7, min_periods=1).mean()).round(2).fillna(0.0)
    df["rolling_14_units"] = df.groupby(product_col)["_shifted"].transform(lambda s: s.rolling(14, min_periods=1).mean()).round(2).fillna(0.0)
    df["rolling_28_units"] = df.groupby(product_col)["_shifted"].transform(lambda s: s.rolling(28, min_periods=1).mean()).round(2).fillna(0.0)
    df.drop(columns=["_shifted"], inplace=True)

    # 3. Calendar attributes
    dt = pd.to_datetime(df[date_col])
    df["day_of_week"] = dt.dt.dayofweek
    df["day_of_month"] = dt.dt.day
    df["month"] = dt.dt.month
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)

    # 4. Product catalog attributes
    if "selling_price" not in df.columns:
        df["selling_price"] = 100.0
    if "unit_cost" not in df.columns:
        df["unit_cost"] = 70.0

    df["unit_margin"] = (df["selling_price"] - df["unit_cost"]).round(2)

    feature_cols = [
        "lag_1_units", "lag_7_units", "lag_14_units", "lag_28_units",
        "rolling_7_units", "rolling_14_units", "rolling_28_units",
        "day_of_week", "day_of_month", "month", "is_weekend",
        "selling_price", "unit_cost", "unit_margin"
    ]

    return df, feature_cols
