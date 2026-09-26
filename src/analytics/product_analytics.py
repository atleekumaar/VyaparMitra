"""
Product analytics module for VyaparMitra Phase 2.
Calculates catalog SKU performance matrix, independent multidimensional rankings,
and cumulative Pareto revenue concentration analysis.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class ProductAnalytics:
    """Computes product catalog metrics, rankings, and concentration distributions."""

    def __init__(
        self,
        product_features_df: pd.DataFrame,
        transactions_df: pd.DataFrame,
    ) -> None:
        self.product_df = product_features_df.copy()
        self.transactions_df = transactions_df.copy()

    def get_performance_matrix(self, merchant_id: Optional[str] = None) -> pd.DataFrame:
        """
        Creates product performance matrix:
        [product_id, product_name, product_category, revenue, units, orders, unique_customers,
         average_price, revenue_share, unit_share]
        """
        if merchant_id:
            tx = self.transactions_df[self.transactions_df["merchant_id"] == merchant_id]
            if tx.empty:
                return pd.DataFrame(columns=[
                    "product_id", "product_name", "product_category", "revenue", "units",
                    "orders", "unique_customers", "average_price", "revenue_share", "unit_share"
                ])
            grouped = tx.groupby("product_id").agg(
                units=("quantity", "sum"),
                revenue=("net_amount", "sum"),
                orders=("transaction_id", "count"),
                unique_customers=("customer_id", "nunique"),
            ).reset_index()
            # Merge catalog metadata
            meta = self.product_df[["product_id", "product_name", "product_category"]].drop_duplicates()
            df = pd.merge(meta, grouped, on="product_id", how="inner")
        else:
            df = self.product_df.copy()
            df.rename(
                columns={
                    "product_sales": "units",
                    "product_revenue": "revenue",
                    "product_order_count": "orders",
                },
                inplace=True,
            )

        total_rev = df["revenue"].sum()
        total_units = df["units"].sum()

        df["revenue"] = df["revenue"].round(2)
        df["average_price"] = (df["revenue"] / df["units"].clip(lower=1)).round(2)
        df["revenue_share"] = (df["revenue"] / max(1e-9, total_rev)).round(4)
        df["unit_share"] = (df["units"] / max(1, total_units)).round(4)

        cols = [
            "product_id", "product_name", "product_category", "revenue", "units",
            "orders", "unique_customers", "average_price", "revenue_share", "unit_share"
        ]
        return df[[c for c in cols if c in df.columns]].sort_values(by="revenue", ascending=False).reset_index(drop=True)

    def get_product_rankings(self, merchant_id: Optional[str] = None) -> pd.DataFrame:
        """
        Generates independent rankings across multiple dimensions:
        - rank_by_revenue
        - rank_by_units
        - rank_by_orders
        - rank_by_customers
        Does not combine into an arbitrary single score.
        """
        matrix = self.get_performance_matrix(merchant_id=merchant_id)
        if matrix.empty:
            return pd.DataFrame()

        ranked = matrix.copy()
        ranked["rank_by_revenue"] = ranked["revenue"].rank(ascending=False, method="min").astype(int)
        ranked["rank_by_units"] = ranked["units"].rank(ascending=False, method="min").astype(int)
        ranked["rank_by_orders"] = ranked["orders"].rank(ascending=False, method="min").astype(int)
        ranked["rank_by_customers"] = ranked["unique_customers"].rank(ascending=False, method="min").astype(int)

        cols = [
            "product_id", "product_name", "product_category", "revenue", "units", "orders",
            "unique_customers", "rank_by_revenue", "rank_by_units", "rank_by_orders", "rank_by_customers"
        ]
        return ranked[cols].sort_values(by="rank_by_revenue").reset_index(drop=True)

    def get_pareto_concentration(self, merchant_id: Optional[str] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Calculates cumulative Pareto revenue contribution across products.
        Returns:
        1. Full cumulative distribution DataFrame.
        2. Key concentration milestone statistics (top 20%, top 50% revenue contribution).
        """
        matrix = self.get_performance_matrix(merchant_id=merchant_id)
        if matrix.empty:
            return pd.DataFrame(), {}

        sorted_df = matrix.sort_values(by="revenue", ascending=False).reset_index(drop=True)
        total_rev = sorted_df["revenue"].sum()
        total_skus = len(sorted_df)

        sorted_df["cumulative_revenue"] = sorted_df["revenue"].cumsum().round(2)
        sorted_df["cumulative_revenue_pct"] = ((sorted_df["cumulative_revenue"] / max(1e-9, total_rev)) * 100.0).round(2)
        sorted_df["sku_rank"] = range(1, total_skus + 1)
        sorted_df["cumulative_sku_pct"] = ((sorted_df["sku_rank"] / total_skus) * 100.0).round(2)

        # Milestone lookups
        idx_20 = max(0, int(round(total_skus * 0.20)) - 1)
        idx_50 = max(0, int(round(total_skus * 0.50)) - 1)

        summary = {
            "total_products": total_skus,
            "total_catalog_revenue": float(round(total_rev, 2)),
            "top_20_pct_skus_count": idx_20 + 1,
            "top_20_pct_sku_revenue_share": float(sorted_df.loc[idx_20, "cumulative_revenue_pct"]),
            "top_50_pct_skus_count": idx_50 + 1,
            "top_50_pct_sku_revenue_share": float(sorted_df.loc[idx_50, "cumulative_revenue_pct"]),
        }

        cols = [
            "sku_rank", "product_id", "product_name", "revenue", "revenue_share",
            "cumulative_revenue", "cumulative_revenue_pct", "cumulative_sku_pct"
        ]
        return sorted_df[cols], summary
