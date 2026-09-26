"""
Transaction-level feature engineering.
Computes amounts, discounts, and temporal breakdown attributes for each transaction.
"""

from __future__ import annotations

import logging
import pandas as pd

logger = logging.getLogger(__name__)


def extract_transaction_features(transactions: pd.DataFrame) -> pd.DataFrame:
    """
    Generate transaction-level features:
    - total_amount
    - discount_amount
    - net_amount
    - date, day, month, quarter, year, week, hour, day_of_week
    - is_weekend, is_month_start, is_month_end
    """
    logger.info("Extracting transaction-level features for %d rows...", len(transactions))
    df = transactions.copy()

    # Numerical calculations
    df["total_amount"] = (df["quantity"] * df["unit_price"]).round(2)
    df["discount_amount"] = df["discount"].round(2)
    df["net_amount"] = (df["total_amount"] - df["discount_amount"]).round(2)

    # Date and Time parsing
    ts = pd.to_datetime(df["timestamp"])
    df["date"] = ts.dt.strftime("%Y-%m-%d")
    df["day"] = ts.dt.day
    df["day_of_week"] = ts.dt.dayofweek  # 0=Monday, 6=Sunday
    df["day_name"] = ts.dt.day_name()
    df["hour"] = ts.dt.hour
    df["week"] = ts.dt.isocalendar().week.astype(int)
    df["month"] = ts.dt.month
    df["quarter"] = ts.dt.quarter
    df["year"] = ts.dt.year

    # Binary calendar flags
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
    df["is_month_start"] = ts.dt.is_month_start.astype(int)
    df["is_month_end"] = ts.dt.is_month_end.astype(int)

    return df
