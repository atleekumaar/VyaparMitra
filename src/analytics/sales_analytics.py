"""
Sales analytics module for VyaparMitra Phase 2.
Computes core revenue KPIs, period comparisons (daily, weekly, monthly),
and daily distribution statistics with zero-division safety.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Tuple
import numpy as np
import pandas as pd

from src.schemas.analytics_schema import PeriodComparisonRecord, SalesKPISet

logger = logging.getLogger(__name__)


class SalesAnalytics:
    """Computes descriptive sales metrics and period-over-period performance."""

    def __init__(self, transactions_df: pd.DataFrame, daily_df: Optional[pd.DataFrame] = None) -> None:
        self.transactions_df = transactions_df.copy()
        self.daily_df = daily_df.copy() if daily_df is not None else None

    def _filter_dataset(
        self,
        df: pd.DataFrame,
        merchant_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """Helper to apply merchant and date filters safely."""
        filtered = df.copy()
        if merchant_id:
            filtered = filtered[filtered["merchant_id"] == merchant_id]
        if start_date:
            filtered = filtered[filtered["date"] >= start_date]
        if end_date:
            filtered = filtered[filtered["date"] <= end_date]
        return filtered

    def get_core_kpis(
        self,
        merchant_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> SalesKPISet:
        """
        Calculate core sales KPIs:
        - total_revenue
        - total_orders
        - total_units
        - average_order_value
        - average_units_per_order
        - discount_total
        - discount_rate
        - revenue_per_active_day
        """
        tx = self._filter_dataset(self.transactions_df, merchant_id, start_date, end_date)
        total_orders = len(tx)

        if total_orders == 0:
            return SalesKPISet(
                total_revenue=0.0,
                total_orders=0,
                total_units=0,
                average_order_value=0.0,
                average_units_per_order=0.0,
                discount_total=0.0,
                discount_rate=0.0,
                revenue_per_active_day=0.0,
            )

        total_revenue = float(round(tx["net_amount"].sum(), 2))
        total_units = int(tx["quantity"].sum())
        discount_total = float(round(tx["discount_amount"].sum() if "discount_amount" in tx.columns else tx["discount"].sum(), 2))
        gross_total = float(round(tx["total_amount"].sum(), 2)) if "total_amount" in tx.columns else total_revenue + discount_total

        aov = round(total_revenue / max(1, total_orders), 2)
        avg_units = round(total_units / max(1, total_orders), 2)
        discount_rate = round(discount_total / max(1e-9, gross_total), 4)

        active_days = tx["date"].nunique()
        rev_per_day = round(total_revenue / max(1, active_days), 2)

        return SalesKPISet(
            total_revenue=total_revenue,
            total_orders=total_orders,
            total_units=total_units,
            average_order_value=aov,
            average_units_per_order=avg_units,
            discount_total=discount_total,
            discount_rate=discount_rate,
            revenue_per_active_day=rev_per_day,
        )

    def get_period_comparison(
        self,
        frequency: str = "monthly",
        merchant_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Calculates periodic performance and sequential growth (daily, weekly, monthly).
        Returns DataFrame with columns:
        [period, period_key, period_start, period_end, revenue, orders, units, aov, discount,
         revenue_change, revenue_growth_pct, orders_change, orders_growth_pct]
        """
        tx = self._filter_dataset(self.transactions_df, merchant_id, start_date, end_date)
        if tx.empty:
            return pd.DataFrame(columns=[
                "period", "period_key", "period_start", "period_end", "revenue",
                "orders", "units", "aov", "discount", "revenue_change", "revenue_growth_pct",
                "orders_change", "orders_growth_pct"
            ])

        tx = tx.copy()
        ts = pd.to_datetime(tx["timestamp"])
        tx["_dt"] = ts

        if frequency == "daily":
            tx["period_key"] = tx["_dt"].dt.strftime("%Y-%m-%d")
        elif frequency == "weekly":
            tx["period_key"] = tx["_dt"].dt.strftime("%Y-W%V")
        elif frequency == "monthly":
            tx["period_key"] = tx["_dt"].dt.strftime("%Y-%m")
        else:
            raise ValueError(f"Unsupported frequency: {frequency}. Must be daily, weekly, or monthly.")

        grouped = tx.groupby("period_key").agg(
            period_start=("date", "min"),
            period_end=("date", "max"),
            revenue=("net_amount", "sum"),
            orders=("transaction_id", "count"),
            units=("quantity", "sum"),
            discount=("discount_amount" if "discount_amount" in tx.columns else "discount", "sum"),
        ).reset_index()

        grouped["period"] = frequency
        grouped["revenue"] = grouped["revenue"].round(2)
        grouped["discount"] = grouped["discount"].round(2)
        grouped["aov"] = (grouped["revenue"] / grouped["orders"].clip(lower=1)).round(2)

        # Sort chronologically
        grouped = grouped.sort_values(by="period_key").reset_index(drop=True)

        # Period-over-Period comparisons
        grouped["revenue_change"] = grouped["revenue"].diff().round(2)
        grouped["revenue_growth_pct"] = (
            (grouped["revenue_change"] / grouped["revenue"].shift(1).clip(lower=1e-9)) * 100.0
        ).round(2)
        grouped["orders_change"] = grouped["orders"].diff()
        grouped["orders_growth_pct"] = (
            (grouped["orders_change"] / grouped["orders"].shift(1).clip(lower=1e-9)) * 100.0
        ).round(2)

        cols = [
            "period", "period_key", "period_start", "period_end", "revenue",
            "orders", "units", "aov", "discount", "revenue_change", "revenue_growth_pct",
            "orders_change", "orders_growth_pct"
        ]
        return grouped[cols]

    def get_daily_sales_analytics(
        self,
        merchant_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Produces daily sales table and key statistical records:
        - highest_revenue_day, lowest_revenue_day
        - highest_order_day, lowest_order_day
        - median_daily_revenue, mean_daily_revenue, revenue_std
        """
        tx = self._filter_dataset(self.transactions_df, merchant_id, start_date, end_date)
        if tx.empty:
            return pd.DataFrame(), {}

        daily = tx.groupby("date").agg(
            revenue=("net_amount", "sum"),
            orders=("transaction_id", "count"),
            units=("quantity", "sum"),
            active_merchants=("merchant_id", "nunique") if "merchant_id" in tx.columns else ("transaction_id", lambda x: 1),
            active_customers=("customer_id", "nunique") if "customer_id" in tx.columns else ("transaction_id", lambda x: 1),
        ).reset_index()

        daily["revenue"] = daily["revenue"].round(2)
        daily["aov"] = (daily["revenue"] / daily["orders"].clip(lower=1)).round(2)
        daily = daily.sort_values(by="date").reset_index(drop=True)

        # Key day identification
        max_rev_idx = daily["revenue"].idxmax()
        min_rev_idx = daily["revenue"].idxmin()
        max_ord_idx = daily["orders"].idxmax()
        min_ord_idx = daily["orders"].idxmin()

        stats = {
            "highest_revenue_day": {
                "date": daily.loc[max_rev_idx, "date"],
                "revenue": float(daily.loc[max_rev_idx, "revenue"]),
                "orders": int(daily.loc[max_rev_idx, "orders"]),
            },
            "lowest_revenue_day": {
                "date": daily.loc[min_rev_idx, "date"],
                "revenue": float(daily.loc[min_rev_idx, "revenue"]),
                "orders": int(daily.loc[min_rev_idx, "orders"]),
            },
            "highest_order_day": {
                "date": daily.loc[max_ord_idx, "date"],
                "orders": int(daily.loc[max_ord_idx, "orders"]),
                "revenue": float(daily.loc[max_ord_idx, "revenue"]),
            },
            "lowest_order_day": {
                "date": daily.loc[min_ord_idx, "date"],
                "orders": int(daily.loc[min_ord_idx, "orders"]),
                "revenue": float(daily.loc[min_ord_idx, "revenue"]),
            },
            "median_daily_revenue": float(round(daily["revenue"].median(), 2)),
            "mean_daily_revenue": float(round(daily["revenue"].mean(), 2)),
            "revenue_std": float(round(daily["revenue"].std(), 2)),
        }

        return daily, stats
