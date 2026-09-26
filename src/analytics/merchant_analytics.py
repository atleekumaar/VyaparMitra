"""
Merchant analytics and peer-group benchmarking module for VyaparMitra Phase 2.
Evaluates individual merchant throughput and performs descriptive peer benchmarking
against merchants of the same business vertical and geographical market.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class MerchantAnalytics:
    """Computes merchant performance indicators and descriptive peer-group benchmarks."""

    def __init__(
        self,
        merchant_features_df: pd.DataFrame,
        transactions_df: pd.DataFrame,
    ) -> None:
        self.merchant_df = merchant_features_df.copy()
        self.transactions_df = transactions_df.copy()

    def get_merchant_summary(self, merchant_id: Optional[str] = None) -> pd.DataFrame:
        """
        Calculates merchant-level KPIs:
        [merchant_id, merchant_name, business_type, city, state, merchant_revenue,
         merchant_orders, merchant_units, merchant_aov, active_days, unique_customers,
         unique_products, revenue_per_day, orders_per_day]
        """
        m_df = self.merchant_df.copy()
        # Merge transaction units if not in merchant_features
        units_per_m = self.transactions_df.groupby("merchant_id")["quantity"].sum().reset_index()
        units_per_m.rename(columns={"quantity": "merchant_units"}, inplace=True)

        merged = pd.merge(m_df, units_per_m, on="merchant_id", how="left")
        merged["merchant_units"] = merged["merchant_units"].fillna(0).astype(int)

        rename_dict = {
            "merchant_total_revenue": "merchant_revenue",
            "merchant_total_orders": "merchant_orders",
            "average_order_value": "merchant_aov",
        }
        merged.rename(columns=rename_dict, inplace=True)

        if merchant_id:
            merged = merged[merged["merchant_id"] == merchant_id]

        cols = [
            "merchant_id", "merchant_name", "business_type", "city", "state",
            "merchant_revenue", "merchant_orders", "merchant_units", "merchant_aov",
            "active_days", "unique_customers", "unique_products", "revenue_per_day", "orders_per_day"
        ]
        return merged[[c for c in cols if c in merged.columns]].reset_index(drop=True)

    def get_merchant_benchmarks(self) -> pd.DataFrame:
        """
        Calculates descriptive peer benchmarks against the same business_type.
        Metrics:
        - peer_mean_revenue, revenue_vs_peer_pct
        - peer_mean_aov, aov_vs_peer_pct
        - peer_mean_orders, orders_vs_peer_pct
        - merchant_revenue_percentile
        Labeled explicitly as DESCRIPTIVE BENCHMARK.
        """
        summary = self.get_merchant_summary()
        if summary.empty:
            return pd.DataFrame()

        benchmarked = summary.copy()

        # Calculate peer means by business_type
        peer_stats = benchmarked.groupby("business_type").agg(
            peer_mean_revenue=("merchant_revenue", "mean"),
            peer_mean_aov=("merchant_aov", "mean"),
            peer_mean_orders=("merchant_orders", "mean"),
        ).reset_index()

        benchmarked = pd.merge(benchmarked, peer_stats, on="business_type", how="left")

        benchmarked["peer_mean_revenue"] = benchmarked["peer_mean_revenue"].round(2)
        benchmarked["peer_mean_aov"] = benchmarked["peer_mean_aov"].round(2)
        benchmarked["peer_mean_orders"] = benchmarked["peer_mean_orders"].round(1)

        benchmarked["revenue_vs_peer_pct"] = (
            ((benchmarked["merchant_revenue"] - benchmarked["peer_mean_revenue"]) /
             benchmarked["peer_mean_revenue"].clip(lower=1e-9)) * 100.0
        ).round(2)

        benchmarked["aov_vs_peer_pct"] = (
            ((benchmarked["merchant_aov"] - benchmarked["peer_mean_aov"]) /
             benchmarked["peer_mean_aov"].clip(lower=1e-9)) * 100.0
        ).round(2)

        benchmarked["orders_vs_peer_pct"] = (
            ((benchmarked["merchant_orders"] - benchmarked["peer_mean_orders"]) /
             benchmarked["peer_mean_orders"].clip(lower=1e-9)) * 100.0
        ).round(2)

        # Revenue percentile rank within cohort (0 to 100)
        benchmarked["revenue_percentile"] = (
            benchmarked.groupby("business_type")["merchant_revenue"]
            .rank(pct=True) * 100.0
        ).round(1)

        benchmarked["benchmark_type"] = "DESCRIPTIVE BENCHMARK"

        cols = [
            "merchant_id", "merchant_name", "business_type", "city",
            "merchant_revenue", "peer_mean_revenue", "revenue_vs_peer_pct",
            "merchant_aov", "peer_mean_aov", "aov_vs_peer_pct",
            "merchant_orders", "peer_mean_orders", "orders_vs_peer_pct",
            "revenue_percentile", "benchmark_type"
        ]
        return benchmarked[cols].sort_values(by=["business_type", "revenue_percentile"], ascending=[True, False]).reset_index(drop=True)
