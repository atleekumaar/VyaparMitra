"""
Contextual analytics module for VyaparMitra Phase 2.
Analyzes observational associations with cultural festivals and meteorological conditions.
Includes sample sizes and avoids causal claims.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Tuple
import pandas as pd

logger = logging.getLogger(__name__)


class ContextAnalytics:
    """Computes observational metrics for festivals and weather conditions."""

    def __init__(
        self,
        transactions_df: pd.DataFrame,
        daily_df: Optional[pd.DataFrame] = None,
        min_sample_size: int = 3,
    ) -> None:
        self.transactions_df = transactions_df.copy()
        self.daily_df = daily_df.copy() if daily_df is not None else None
        self.min_sample_size = min_sample_size

    def get_festival_analysis(self, merchant_id: Optional[str] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Calculates observational comparison: Festival vs Non-Festival days,
        and per-festival performance with sample size.
        """
        tx = self.transactions_df.copy()
        if merchant_id:
            tx = tx[tx["merchant_id"] == merchant_id]

        if tx.empty or "is_festival" not in tx.columns:
            return pd.DataFrame(), {}

        # Daily aggregation first to ensure fair day-to-day comparisons
        daily_fest = tx.groupby(["date", "is_festival", "festival_name"]).agg(
            revenue=("net_amount", "sum"),
            orders=("transaction_id", "count"),
        ).reset_index()

        fest_days = daily_fest[daily_fest["is_festival"] == 1]
        non_fest_days = daily_fest[daily_fest["is_festival"] == 0]

        n_fest_days = len(fest_days)
        n_non_fest_days = len(non_fest_days)

        mean_fest_rev = float(round(fest_days["revenue"].mean(), 2)) if n_fest_days > 0 else 0.0
        mean_non_fest_rev = float(round(non_fest_days["revenue"].mean(), 2)) if n_non_fest_days > 0 else 0.0

        mean_fest_ord = float(round(fest_days["orders"].mean(), 1)) if n_fest_days > 0 else 0.0
        mean_non_fest_ord = float(round(non_fest_days["orders"].mean(), 1)) if n_non_fest_days > 0 else 0.0

        rev_diff = round(mean_fest_rev - mean_non_fest_rev, 2)
        rev_diff_pct = round((rev_diff / max(1e-9, mean_non_fest_rev)) * 100.0, 2) if mean_non_fest_rev > 0 else 0.0

        ord_diff = round(mean_fest_ord - mean_non_fest_ord, 1)
        ord_diff_pct = round((ord_diff / max(1e-9, mean_non_fest_ord)) * 100.0, 2) if mean_non_fest_ord > 0 else 0.0

        summary = {
            "festival_days_count": n_fest_days,
            "non_festival_days_count": n_non_fest_days,
            "festival_day_avg_revenue": mean_fest_rev,
            "non_festival_day_avg_revenue": mean_non_fest_rev,
            "festival_day_avg_orders": mean_fest_ord,
            "non_festival_day_avg_orders": mean_non_fest_ord,
            "festival_revenue_difference": rev_diff,
            "festival_revenue_difference_pct": rev_diff_pct,
            "festival_order_difference": ord_diff,
            "festival_order_difference_pct": ord_diff_pct,
            "observational_note": f"Festival days were associated with {abs(rev_diff_pct)}% {'higher' if rev_diff >= 0 else 'lower'} observed daily revenue compared to non-festival days.",
        }

        # Per-festival metrics
        per_fest = (
            daily_fest[daily_fest["is_festival"] == 1]
            .groupby("festival_name")
            .agg(
                sample_size=("date", "count"),
                avg_daily_revenue=("revenue", "mean"),
                avg_daily_orders=("orders", "mean"),
                total_festival_revenue=("revenue", "sum"),
            )
            .reset_index()
        )
        per_fest["avg_daily_revenue"] = per_fest["avg_daily_revenue"].round(2)
        per_fest["avg_daily_orders"] = per_fest["avg_daily_orders"].round(1)
        per_fest["total_festival_revenue"] = per_fest["total_festival_revenue"].round(2)

        # Baseline comparison
        per_fest["vs_non_festival_revenue_pct"] = (
            ((per_fest["avg_daily_revenue"] - mean_non_fest_rev) / max(1e-9, mean_non_fest_rev)) * 100.0
        ).round(2)

        return per_fest.sort_values(by="total_festival_revenue", ascending=False).reset_index(drop=True), summary

    def get_weather_analysis(self, merchant_id: Optional[str] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Calculates observational comparison: Rainy vs Non-Rainy days,
        breakdown by weather_condition, and statistical correlations.
        """
        tx = self.transactions_df.copy()
        if merchant_id:
            tx = tx[tx["merchant_id"] == merchant_id]

        if tx.empty or "is_rainy" not in tx.columns:
            return pd.DataFrame(), {}

        # Daily aggregation
        daily_weather = tx.groupby(["date", "is_rainy", "weather_condition"]).agg(
            revenue=("net_amount", "sum"),
            orders=("transaction_id", "count"),
            temperature=("temperature", "mean"),
            rainfall=("rainfall", "mean"),
            humidity=("humidity", "mean"),
        ).reset_index()

        rainy_days = daily_weather[daily_weather["is_rainy"] == 1]
        dry_days = daily_weather[daily_weather["is_rainy"] == 0]

        n_rainy = len(rainy_days)
        n_dry = len(dry_days)

        mean_rainy_rev = float(round(rainy_days["revenue"].mean(), 2)) if n_rainy > 0 else 0.0
        mean_dry_rev = float(round(dry_days["revenue"].mean(), 2)) if n_dry > 0 else 0.0

        mean_rainy_ord = float(round(rainy_days["orders"].mean(), 1)) if n_rainy > 0 else 0.0
        mean_dry_ord = float(round(dry_days["orders"].mean(), 1)) if n_dry > 0 else 0.0

        rain_rev_diff = round(mean_rainy_rev - mean_dry_rev, 2)
        rain_rev_diff_pct = round((rain_rev_diff / max(1e-9, mean_dry_rev)) * 100.0, 2) if mean_dry_rev > 0 else 0.0

        # Correlations
        corr_rainfall = float(round(daily_weather["revenue"].corr(daily_weather["rainfall"]), 4)) if n_rainy > 0 else 0.0
        corr_temp = float(round(daily_weather["revenue"].corr(daily_weather["temperature"]), 4))

        summary = {
            "rainy_days_count": n_rainy,
            "non_rainy_days_count": n_dry,
            "rainy_day_avg_revenue": mean_rainy_rev,
            "non_rainy_day_avg_revenue": mean_dry_rev,
            "rainy_day_avg_orders": mean_rainy_ord,
            "non_rainy_day_avg_orders": mean_dry_ord,
            "rainy_revenue_difference": rain_rev_diff,
            "rainy_revenue_difference_pct": rain_rev_diff_pct,
            "rainfall_revenue_correlation": corr_rainfall,
            "temperature_revenue_correlation": corr_temp,
            "observational_note": f"Rainy days were associated with {abs(rain_rev_diff_pct)}% {'higher' if rain_rev_diff >= 0 else 'lower'} observed daily revenue compared to non-rainy days.",
        }

        # Breakdown by weather condition
        cond_df = daily_weather.groupby("weather_condition").agg(
            sample_size=("date", "count"),
            avg_daily_revenue=("revenue", "mean"),
            avg_daily_orders=("orders", "mean"),
            total_revenue=("revenue", "sum"),
        ).reset_index()

        cond_df["avg_daily_revenue"] = cond_df["avg_daily_revenue"].round(2)
        cond_df["avg_daily_orders"] = cond_df["avg_daily_orders"].round(1)
        cond_df["total_revenue"] = cond_df["total_revenue"].round(2)

        return cond_df.sort_values(by="total_revenue", ascending=False).reset_index(drop=True), summary
