"""
Category analytics module for VyaparMitra Phase 2.
Aggregates product category metrics and generates multidimensional slices:
category x month, category x weekday, and category x merchant.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional
import pandas as pd

logger = logging.getLogger(__name__)


class CategoryAnalytics:
    """Computes category-level revenue, units, orders, AOV, and multidimensional cross-tabulations."""

    def __init__(self, transactions_df: pd.DataFrame) -> None:
        self.transactions_df = transactions_df.copy()

    def get_category_summary(self, merchant_id: Optional[str] = None) -> pd.DataFrame:
        """
        Calculates category-level KPIs:
        [product_category, category_revenue, category_units, category_orders,
         unique_customers, average_order_value, revenue_share]
        """
        tx = self.transactions_df
        if merchant_id:
            tx = tx[tx["merchant_id"] == merchant_id]

        if tx.empty:
            return pd.DataFrame(columns=[
                "product_category", "category_revenue", "category_units", "category_orders",
                "unique_customers", "average_order_value", "revenue_share"
            ])

        total_rev = tx["net_amount"].sum()

        grouped = tx.groupby("product_category").agg(
            category_revenue=("net_amount", "sum"),
            category_units=("quantity", "sum"),
            category_orders=("transaction_id", "count"),
            unique_customers=("customer_id", "nunique"),
        ).reset_index()

        grouped["category_revenue"] = grouped["category_revenue"].round(2)
        grouped["average_order_value"] = (grouped["category_revenue"] / grouped["category_orders"].clip(lower=1)).round(2)
        grouped["revenue_share"] = (grouped["category_revenue"] / max(1e-9, total_rev)).round(4)

        return grouped.sort_values(by="category_revenue", ascending=False).reset_index(drop=True)

    def get_category_monthly(self, merchant_id: Optional[str] = None) -> pd.DataFrame:
        """Category x Month cross-tabulation."""
        tx = self.transactions_df.copy()
        if merchant_id:
            tx = tx[tx["merchant_id"] == merchant_id]
        if tx.empty:
            return pd.DataFrame()

        tx["month_key"] = pd.to_datetime(tx["timestamp"]).dt.strftime("%Y-%m")
        grouped = tx.groupby(["product_category", "month_key"]).agg(
            category_revenue=("net_amount", "sum"),
            category_units=("quantity", "sum"),
            category_orders=("transaction_id", "count"),
        ).reset_index()
        grouped["category_revenue"] = grouped["category_revenue"].round(2)
        return grouped.sort_values(by=["month_key", "category_revenue"], ascending=[True, False]).reset_index(drop=True)

    def get_category_weekday(self, merchant_id: Optional[str] = None) -> pd.DataFrame:
        """Category x Weekday cross-tabulation."""
        tx = self.transactions_df.copy()
        if merchant_id:
            tx = tx[tx["merchant_id"] == merchant_id]
        if tx.empty:
            return pd.DataFrame()

        tx["day_name"] = pd.to_datetime(tx["timestamp"]).dt.day_name()
        tx["day_of_week"] = pd.to_datetime(tx["timestamp"]).dt.dayofweek

        grouped = tx.groupby(["product_category", "day_name", "day_of_week"]).agg(
            category_revenue=("net_amount", "sum"),
            category_orders=("transaction_id", "count"),
        ).reset_index()
        grouped["category_revenue"] = grouped["category_revenue"].round(2)
        return grouped.sort_values(by=["day_of_week", "category_revenue"], ascending=[True, False]).reset_index(drop=True)

    def get_category_merchant(self) -> pd.DataFrame:
        """Category x Merchant cross-tabulation."""
        tx = self.transactions_df.copy()
        grouped = tx.groupby(["product_category", "merchant_id"]).agg(
            category_revenue=("net_amount", "sum"),
            category_orders=("transaction_id", "count"),
        ).reset_index()
        grouped["category_revenue"] = grouped["category_revenue"].round(2)
        return grouped.sort_values(by=["merchant_id", "category_revenue"], ascending=[True, False]).reset_index(drop=True)
