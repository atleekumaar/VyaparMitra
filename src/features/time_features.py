"""
Time-based feature engineering and multi-scale temporal aggregation (daily, weekly, monthly).
Designed with strict anti-data-leakage safeguards for future Phase 3 time-series forecasting.
"""

from __future__ import annotations

import logging
from typing import Optional
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def extract_time_features(df: pd.DataFrame, timestamp_col: str = "timestamp") -> pd.DataFrame:
    """
    Extract calendar breakdown features:
    - hour
    - day_of_week (0=Monday, 6=Sunday)
    - day_of_month
    - week_of_year
    - month
    - quarter
    - year
    - is_weekend
    - is_month_start
    - is_month_end
    """
    out = df.copy()
    ts = pd.to_datetime(out[timestamp_col])
    out["hour"] = ts.dt.hour
    out["day_of_week"] = ts.dt.dayofweek
    out["day_name"] = ts.dt.day_name()
    out["day_of_month"] = ts.dt.day
    out["week_of_year"] = ts.dt.isocalendar().week.astype(int)
    out["month"] = ts.dt.month
    out["quarter"] = ts.dt.quarter
    out["year"] = ts.dt.year
    out["is_weekend"] = out["day_of_week"].isin([5, 6]).astype(int)
    out["is_month_start"] = ts.dt.is_month_start.astype(int)
    out["is_month_end"] = ts.dt.is_month_end.astype(int)
    return out


def extract_daily_features(
    enriched_transactions_df: pd.DataFrame,
    date_col: str = "date",
) -> pd.DataFrame:
    """
    Aggregate transaction volume, revenue, merchant activity, and external context by calendar day.
    Adds trailing lags (7-day trailing moving average) strictly computed using past dates (shift=1)
    to protect against target leakage.
    """
    logger.info("Extracting daily aggregated time-window features...")
    df = enriched_transactions_df.copy()

    # 1. Base aggregations per date
    daily = (
        df.groupby(date_col)
        .agg(
            daily_total_revenue=("net_amount", "sum"),
            daily_total_orders=("transaction_id", "count"),
            daily_total_units=("quantity", "sum"),
            daily_active_merchants=("merchant_id", "nunique"),
            daily_active_customers=("customer_id", "nunique"),
            daily_avg_order_value=("net_amount", "mean"),
            # External context summaries if available
            is_festival=("is_festival", "max") if "is_festival" in df.columns else ("transaction_id", lambda x: 0),
            festival_intensity=("festival_intensity", "max") if "festival_intensity" in df.columns else ("transaction_id", lambda x: 0.0),
            days_to_festival=("days_to_festival", "first") if "days_to_festival" in df.columns else ("transaction_id", lambda x: 999),
            days_after_festival=("days_after_festival", "first") if "days_after_festival" in df.columns else ("transaction_id", lambda x: 999),
            avg_temperature=("temperature", "mean") if "temperature" in df.columns else ("transaction_id", lambda x: 27.0),
            avg_humidity=("humidity", "mean") if "humidity" in df.columns else ("transaction_id", lambda x: 55.0),
            total_rainfall=("rainfall", "sum") if "rainfall" in df.columns else ("transaction_id", lambda x: 0.0),
            is_rainy_day=("is_rainy", "max") if "is_rainy" in df.columns else ("transaction_id", lambda x: 0),
        )
        .reset_index()
    )

    daily["daily_total_revenue"] = daily["daily_total_revenue"].round(2)
    daily["daily_avg_order_value"] = daily["daily_avg_order_value"].round(2)
    daily["avg_temperature"] = daily["avg_temperature"].round(1)
    daily["avg_humidity"] = daily["avg_humidity"].round(1)
    daily["total_rainfall"] = daily["total_rainfall"].round(1)

    # Sort strictly chronologically
    daily = daily.sort_values(by=date_col).reset_index(drop=True)

    # Add temporal calendar features
    dt = pd.to_datetime(daily[date_col])
    daily["day_of_week"] = dt.dt.dayofweek
    daily["day_name"] = dt.dt.day_name()
    daily["day_of_month"] = dt.dt.day
    daily["week_of_year"] = dt.dt.isocalendar().week.astype(int)
    daily["month"] = dt.dt.month
    daily["quarter"] = dt.dt.quarter
    daily["year"] = dt.dt.year
    daily["is_weekend"] = daily["day_of_week"].isin([5, 6]).astype(int)
    daily["is_month_start"] = dt.dt.is_month_start.astype(int)
    daily["is_month_end"] = dt.dt.is_month_end.astype(int)

    # Anti-leakage trailing features (Strict shift(1) ensures no future knowledge is used)
    daily["lag_1d_revenue"] = daily["daily_total_revenue"].shift(1).fillna(daily["daily_total_revenue"].iloc[0])
    daily["lag_7d_revenue"] = daily["daily_total_revenue"].shift(7).fillna(daily["daily_total_revenue"].iloc[0])
    daily["rolling_7d_avg_revenue"] = (
        daily["daily_total_revenue"]
        .shift(1)  # Only use strictly past days
        .rolling(window=7, min_periods=1)
        .mean()
        .round(2)
        .fillna(daily["daily_total_revenue"].iloc[0])
    )

    logger.info("Extracted daily features for %d days.", len(daily))
    return daily
