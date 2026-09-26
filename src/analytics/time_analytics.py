"""
Time analytics module for VyaparMitra Phase 2.
Analyzes hourly, weekday, monthly, and quarterly performance,
and extracts observed peak operational periods.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Tuple
import pandas as pd

logger = logging.getLogger(__name__)


class TimeAnalytics:
    """Computes temporal breakdowns and identifies observed peak operational cycles."""

    def __init__(self, transactions_df: pd.DataFrame) -> None:
        self.transactions_df = transactions_df.copy()

    def get_hourly_analytics(self, merchant_id: Optional[str] = None) -> pd.DataFrame:
        """Hourly breakdown: hour (0-23), orders, revenue, units, AOV."""
        tx = self.transactions_df.copy()
        if merchant_id:
            tx = tx[tx["merchant_id"] == merchant_id]
        if tx.empty:
            return pd.DataFrame(columns=["hour", "orders", "revenue", "units", "aov"])

        if "hour" not in tx.columns and "timestamp" in tx.columns:
            tx["hour"] = pd.to_datetime(tx["timestamp"]).dt.hour

        grouped = tx.groupby("hour").agg(
            orders=("transaction_id", "count"),
            revenue=("net_amount", "sum"),
            units=("quantity", "sum"),
        ).reset_index()

        grouped["revenue"] = grouped["revenue"].round(2)
        grouped["aov"] = (grouped["revenue"] / grouped["orders"].clip(lower=1)).round(2)
        return grouped.sort_values(by="hour").reset_index(drop=True)

    def get_weekday_analytics(self, merchant_id: Optional[str] = None) -> pd.DataFrame:
        """Day of week breakdown: Monday-Sunday, revenue, orders, units, AOV."""
        tx = self.transactions_df.copy()
        if merchant_id:
            tx = tx[tx["merchant_id"] == merchant_id]
        if tx.empty:
            return pd.DataFrame(columns=["day_of_week", "day_name", "orders", "revenue", "units", "aov"])

        if ("day_of_week" not in tx.columns or "day_name" not in tx.columns) and "timestamp" in tx.columns:
            ts = pd.to_datetime(tx["timestamp"])
            tx["day_of_week"] = ts.dt.dayofweek
            tx["day_name"] = ts.dt.day_name()

        grouped = tx.groupby(["day_of_week", "day_name"]).agg(
            orders=("transaction_id", "count"),
            revenue=("net_amount", "sum"),
            units=("quantity", "sum"),
        ).reset_index()

        grouped["revenue"] = grouped["revenue"].round(2)
        grouped["aov"] = (grouped["revenue"] / grouped["orders"].clip(lower=1)).round(2)
        return grouped.sort_values(by="day_of_week").reset_index(drop=True)

    def get_monthly_analytics(self, merchant_id: Optional[str] = None) -> pd.DataFrame:
        """Monthly breakdown: YYYY-MM, monthly revenue, monthly orders, monthly units, monthly AOV."""
        tx = self.transactions_df.copy()
        if merchant_id:
            tx = tx[tx["merchant_id"] == merchant_id]
        if tx.empty:
            return pd.DataFrame(columns=["month_key", "year", "month", "revenue", "orders", "units", "aov"])

        tx["month_key"] = pd.to_datetime(tx["timestamp"]).dt.strftime("%Y-%m")
        grouped = tx.groupby("month_key").agg(
            year=("year", "first"),
            month=("month", "first"),
            revenue=("net_amount", "sum"),
            orders=("transaction_id", "count"),
            units=("quantity", "sum"),
        ).reset_index()

        grouped["revenue"] = grouped["revenue"].round(2)
        grouped["aov"] = (grouped["revenue"] / grouped["orders"].clip(lower=1)).round(2)
        return grouped.sort_values(by="month_key").reset_index(drop=True)

    def get_quarterly_analytics(self, merchant_id: Optional[str] = None) -> pd.DataFrame:
        """Quarterly breakdown: YYYY-QX, revenue, orders, units, AOV."""
        tx = self.transactions_df.copy()
        if merchant_id:
            tx = tx[tx["merchant_id"] == merchant_id]
        if tx.empty:
            return pd.DataFrame(columns=["quarter_key", "year", "quarter", "revenue", "orders", "units", "aov"])

        tx["quarter_key"] = tx["year"].astype(str) + "-Q" + tx["quarter"].astype(str)
        grouped = tx.groupby("quarter_key").agg(
            year=("year", "first"),
            quarter=("quarter", "first"),
            revenue=("net_amount", "sum"),
            orders=("transaction_id", "count"),
            units=("quantity", "sum"),
        ).reset_index()

        grouped["revenue"] = grouped["revenue"].round(2)
        grouped["aov"] = (grouped["revenue"] / grouped["orders"].clip(lower=1)).round(2)
        return grouped.sort_values(by="quarter_key").reset_index(drop=True)

    def get_peak_periods(self, merchant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Identifies observed peak operational periods:
        - highest revenue hour
        - highest order hour
        - highest revenue weekday
        - highest order weekday
        - highest revenue month
        """
        hourly = self.get_hourly_analytics(merchant_id=merchant_id)
        weekday = self.get_weekday_analytics(merchant_id=merchant_id)
        monthly = self.get_monthly_analytics(merchant_id=merchant_id)

        if hourly.empty or weekday.empty or monthly.empty:
            return {}

        peak_rev_hour_row = hourly.loc[hourly["revenue"].idxmax()]
        peak_ord_hour_row = hourly.loc[hourly["orders"].idxmax()]

        peak_rev_wk_row = weekday.loc[weekday["revenue"].idxmax()]
        peak_ord_wk_row = weekday.loc[weekday["orders"].idxmax()]

        peak_rev_mo_row = monthly.loc[monthly["revenue"].idxmax()]

        return {
            "highest_revenue_hour": {
                "hour": int(peak_rev_hour_row["hour"]),
                "time_window": f"{int(peak_rev_hour_row['hour']):02d}:00–{int(peak_rev_hour_row['hour'])+1:02d}:00",
                "revenue": float(peak_rev_hour_row["revenue"]),
                "orders": int(peak_rev_hour_row["orders"]),
            },
            "highest_order_hour": {
                "hour": int(peak_ord_hour_row["hour"]),
                "time_window": f"{int(peak_ord_hour_row['hour']):02d}:00–{int(peak_ord_hour_row['hour'])+1:02d}:00",
                "orders": int(peak_ord_hour_row["orders"]),
                "revenue": float(peak_ord_hour_row["revenue"]),
            },
            "highest_revenue_weekday": {
                "day_name": str(peak_rev_wk_row["day_name"]),
                "day_of_week": int(peak_rev_wk_row["day_of_week"]),
                "revenue": float(peak_rev_wk_row["revenue"]),
                "orders": int(peak_rev_wk_row["orders"]),
            },
            "highest_order_weekday": {
                "day_name": str(peak_ord_wk_row["day_name"]),
                "day_of_week": int(peak_ord_wk_row["day_of_week"]),
                "orders": int(peak_ord_wk_row["orders"]),
                "revenue": float(peak_ord_wk_row["revenue"]),
            },
            "highest_revenue_month": {
                "month_key": str(peak_rev_mo_row["month_key"]),
                "revenue": float(peak_rev_mo_row["revenue"]),
                "orders": int(peak_rev_mo_row["orders"]),
            },
        }
