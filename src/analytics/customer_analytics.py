"""
Customer analytics module for VyaparMitra Phase 2.
Computes volume/engagement KPIs, customer type distributions,
quantile-based RFM behavioral segmentation, and historical monthly cohort retention.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Tuple
import numpy as np
import pandas as pd

from src.schemas.analytics_schema import CustomerKPISet, RFMSegmentRecord

logger = logging.getLogger(__name__)


class CustomerAnalytics:
    """Computes descriptive customer insights, RFM analytics, and cohort matrices."""

    def __init__(
        self,
        customer_features_df: pd.DataFrame,
        transactions_df: pd.DataFrame,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.customer_df = customer_features_df.copy()
        self.transactions_df = transactions_df.copy()
        self.config = config or {}

    def get_customer_kpis(self, merchant_id: Optional[str] = None) -> CustomerKPISet:
        """
        Calculate customer base KPIs:
        - total_customers
        - active_customers
        - repeat_customers
        - one_time_customers
        - average_customer_spend
        - average_orders_per_customer
        """
        if merchant_id:
            tx = self.transactions_df[self.transactions_df["merchant_id"] == merchant_id]
            if tx.empty:
                return CustomerKPISet(
                    total_customers=0, active_customers=0, repeat_customers=0,
                    one_time_customers=0, average_customer_spend=0.0, average_orders_per_customer=0.0
                )
            cust_agg = tx.groupby("customer_id").agg(
                orders=("transaction_id", "count"),
                spend=("net_amount", "sum"),
            ).reset_index()
            total_customers = len(cust_agg)
            active_customers = total_customers
            repeat_customers = int((cust_agg["orders"] > 1).sum())
            one_time_customers = total_customers - repeat_customers
            avg_spend = round(cust_agg["spend"].mean(), 2)
            avg_orders = round(cust_agg["orders"].mean(), 2)
        else:
            cust = self.customer_df
            total_customers = len(cust)
            active_customers = int((cust["customer_order_count"] > 0).sum())
            repeat_customers = int((cust["customer_order_count"] > 1).sum())
            one_time_customers = int((cust["customer_order_count"] == 1).sum())
            avg_spend = round(cust["customer_total_spend"].mean(), 2) if total_customers > 0 else 0.0
            avg_orders = round(cust["customer_order_count"].mean(), 2) if total_customers > 0 else 0.0

        return CustomerKPISet(
            total_customers=total_customers,
            active_customers=active_customers,
            repeat_customers=repeat_customers,
            one_time_customers=one_time_customers,
            average_customer_spend=avg_spend,
            average_orders_per_customer=avg_orders,
        )

    def get_customer_distribution(self, merchant_id: Optional[str] = None) -> pd.DataFrame:
        """
        Calculates customer type distribution and their revenue/order contribution.
        Returns DataFrame with columns:
        [customer_type, customer_count, customer_share, total_revenue, revenue_share, total_orders, orders_share]
        """
        if merchant_id:
            tx = self.transactions_df[self.transactions_df["merchant_id"] == merchant_id]
            cust_types = self.customer_df[["customer_id", "customer_type"]].drop_duplicates()
            merged = pd.merge(tx, cust_types, on="customer_id", how="left")
            merged["customer_type"] = merged["customer_type"].fillna("Regular")
        else:
            # Join transactions with customer_type
            cust_types = self.customer_df[["customer_id", "customer_type"]].drop_duplicates()
            merged = pd.merge(self.transactions_df, cust_types, on="customer_id", how="left")
            merged["customer_type"] = merged["customer_type"].fillna("Regular")

        total_rev = merged["net_amount"].sum()
        total_ord = len(merged)

        dist = merged.groupby("customer_type").agg(
            customer_count=("customer_id", "nunique"),
            total_revenue=("net_amount", "sum"),
            total_orders=("transaction_id", "count"),
        ).reset_index()

        total_cust = dist["customer_count"].sum()
        dist["total_revenue"] = dist["total_revenue"].round(2)
        dist["customer_share"] = (dist["customer_count"] / max(1, total_cust)).round(4)
        dist["revenue_share"] = (dist["total_revenue"] / max(1e-9, total_rev)).round(4)
        dist["orders_share"] = (dist["total_orders"] / max(1, total_ord)).round(4)

        return dist

    def get_rfm_segmentation(self) -> pd.DataFrame:
        """
        Calculates quantile-based RFM scoring (1-5) and assigns descriptive behavioral segments.
        Segments: Champions, Loyal, Potential Loyalists, New Customers, At Risk, Low Engagement.
        """
        df = self.customer_df.copy()
        if df.empty:
            return pd.DataFrame(columns=[
                "customer_id", "recency", "order_count", "total_spend",
                "r_score", "f_score", "m_score", "rfm_score", "rfm_segment"
            ])

        # R score: Lower recency days = higher score (5)
        # Using ranking method to handle identical values cleanly
        df["r_score"] = pd.qcut(df["customer_recency"].rank(method="first"), 5, labels=[5, 4, 3, 2, 1]).astype(int)

        # F score: Higher order count = higher score (5)
        df["f_score"] = pd.qcut(df["customer_order_count"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)

        # M score: Higher spend = higher score (5)
        df["m_score"] = pd.qcut(df["customer_total_spend"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)

        df["rfm_score"] = df["r_score"].astype(str) + df["f_score"].astype(str) + df["m_score"].astype(str)

        # Rule-based descriptive segmentation mapping
        def assign_segment(r: int, f: int, m: int) -> str:
            if r >= 4 and f >= 4 and m >= 4:
                return "Champions"
            elif f >= 3 and m >= 3:
                return "Loyal"
            elif r >= 4 and f <= 2 and m >= 2:
                return "Potential Loyalists"
            elif r >= 4 and f == 1:
                return "New Customers"
            elif r <= 2 and f >= 2:
                return "At Risk"
            else:
                return "Low Engagement"

        df["rfm_segment"] = [
            assign_segment(r, f, m) for r, f, m in zip(df["r_score"], df["f_score"], df["m_score"])
        ]

        cols = [
            "customer_id", "customer_name", "customer_type", "city",
            "customer_recency", "customer_order_count", "customer_total_spend",
            "r_score", "f_score", "m_score", "rfm_score", "rfm_segment"
        ]
        return df[[c for c in cols if c in df.columns]]

    def get_cohort_matrix(self) -> pd.DataFrame:
        """
        Performs historical cohort retention analysis:
        Determines customer first transaction month, tracks retention across subsequent calendar months (M0, M1, M2...).
        Output format: Cohort Month | Total Customers | M0 | M1 | M2 | M3 ...
        """
        tx = self.transactions_df.copy()
        if tx.empty:
            return pd.DataFrame()

        tx["order_month"] = pd.to_datetime(tx["timestamp"]).dt.to_period("M")
        
        # Determine cohort month per customer
        first_month = tx.groupby("customer_id")["order_month"].min().reset_index()
        first_month.rename(columns={"order_month": "cohort_month"}, inplace=True)

        merged = pd.merge(tx, first_month, on="customer_id")
        
        # Calculate cohort index (months elapsed)
        merged["cohort_index"] = (
            (merged["order_month"].dt.year - merged["cohort_month"].dt.year) * 12 +
            (merged["order_month"].dt.month - merged["cohort_month"].dt.month)
        )

        cohort_data = merged.groupby(["cohort_month", "cohort_index"])["customer_id"].nunique().reset_index()
        cohort_pivot = cohort_data.pivot(index="cohort_month", columns="cohort_index", values="customer_id").fillna(0)

        # Rename columns to M0, M1, M2...
        cohort_pivot.columns = [f"M{int(c)}" for c in cohort_pivot.columns]
        cohort_pivot = cohort_pivot.reset_index()
        cohort_pivot["cohort_month"] = cohort_pivot["cohort_month"].astype(str)
        cohort_pivot.rename(columns={"M0": "cohort_size"}, inplace=True)

        return cohort_pivot
