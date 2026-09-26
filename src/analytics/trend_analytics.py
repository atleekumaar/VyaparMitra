"""
Trend and statistical anomaly detection module for VyaparMitra Phase 2.
Calculates directional trajectory (Increasing, Decreasing, Stable)
and statistical outliers via IQR and rolling median thresholds without ML models.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class TrendAnalytics:
    """Computes moving averages, directional classifications, and statistical anomalies."""

    def __init__(
        self,
        transactions_df: pd.DataFrame,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.transactions_df = transactions_df.copy()
        self.config = config or {}
        analytics_cfg = self.config.get("analytics", {})
        self.stable_threshold_pct = float(
            analytics_cfg.get("trend", {}).get("stable_threshold_percent", 3.0)
        )
        self.anomaly_method = str(analytics_cfg.get("anomaly", {}).get("method", "iqr")).lower()
        self.iqr_multiplier = float(analytics_cfg.get("anomaly", {}).get("iqr_multiplier", 1.5))

    def get_trend_analysis(
        self,
        frequency: str = "monthly",
        metric: str = "net_amount",
        merchant_id: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Calculates moving average and classifies directional trend:
        [period, period_key, metric, value, moving_average, absolute_change,
         percentage_change, trend_classification]
        """
        tx = self.transactions_df.copy()
        if merchant_id:
            tx = tx[tx["merchant_id"] == merchant_id]
        if tx.empty:
            return pd.DataFrame()

        ts = pd.to_datetime(tx["timestamp"])
        if frequency == "daily":
            tx["period_key"] = ts.dt.strftime("%Y-%m-%d")
            window = 7
        elif frequency == "weekly":
            tx["period_key"] = ts.dt.strftime("%Y-W%V")
            window = 4
        elif frequency == "monthly":
            tx["period_key"] = ts.dt.strftime("%Y-%m")
            window = 3
        else:
            raise ValueError(f"Unsupported frequency: {frequency}")

        grouped = tx.groupby("period_key")[metric].sum().reset_index()
        grouped.rename(columns={metric: "value"}, inplace=True)
        grouped["value"] = grouped["value"].round(2)
        grouped = grouped.sort_values(by="period_key").reset_index(drop=True)

        # Trailing moving average (strictly using current and past observations)
        grouped["moving_average"] = (
            grouped["value"].rolling(window=window, min_periods=1).mean().round(2)
        )

        grouped["absolute_change"] = grouped["value"].diff().round(2).fillna(0.0)
        grouped["percentage_change"] = (
            (grouped["absolute_change"] / grouped["value"].shift(1).clip(lower=1e-9)) * 100.0
        ).round(2).fillna(0.0)

        # Directional classification
        def classify_trend(pct_change: float) -> str:
            if pct_change > self.stable_threshold_pct:
                return "Increasing"
            elif pct_change < -self.stable_threshold_pct:
                return "Decreasing"
            else:
                return "Stable"

        grouped["trend_classification"] = grouped["percentage_change"].apply(classify_trend)
        grouped["period"] = frequency
        grouped["metric"] = metric

        cols = [
            "period", "period_key", "metric", "value", "moving_average",
            "absolute_change", "percentage_change", "trend_classification"
        ]
        return grouped[cols]

    def get_daily_anomalies(
        self,
        metric: str = "net_amount",
        merchant_id: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Identifies statistical anomalies in daily totals using IQR or rolling median.
        Classifies dates as: normal, unusually_high, unusually_low.
        """
        tx = self.transactions_df.copy()
        if merchant_id:
            tx = tx[tx["merchant_id"] == merchant_id]
        if tx.empty:
            return pd.DataFrame(), {}

        daily = tx.groupby("date")[metric].sum().reset_index()
        daily.rename(columns={metric: "value"}, inplace=True)
        daily["value"] = daily["value"].round(2)
        daily = daily.sort_values(by="date").reset_index(drop=True)

        n = len(daily)
        if n < 5:
            daily["baseline"] = daily["value"]
            daily["deviation"] = 0.0
            daily["method"] = self.anomaly_method.upper()
            daily["status"] = "normal"
            daily["metric"] = metric
            return daily, {"total_anomalies": 0, "unusually_high": 0, "unusually_low": 0}

        # Baseline: 7-day rolling median
        daily["baseline"] = (
            daily["value"].rolling(window=7, min_periods=1, center=False).median().round(2)
        )

        if self.anomaly_method == "iqr":
            q25 = float(daily["value"].quantile(0.25))
            q75 = float(daily["value"].quantile(0.75))
            iqr = q75 - q25
            lower_bound = q25 - (self.iqr_multiplier * iqr)
            upper_bound = q75 + (self.iqr_multiplier * iqr)

            def assign_status(val: float) -> str:
                if val > upper_bound:
                    return "unusually_high"
                elif val < lower_bound:
                    return "unusually_low"
                else:
                    return "normal"

            daily["status"] = daily["value"].apply(assign_status)
            daily["method"] = "IQR"
            daily["deviation"] = (daily["value"] - daily["baseline"]).round(2)

        else:
            # Z-Score method fallback
            mean = daily["value"].mean()
            std = daily["value"].std()
            z_scores = (daily["value"] - mean) / max(1e-9, std)

            def assign_z_status(z: float) -> str:
                if z > 2.5:
                    return "unusually_high"
                elif z < -2.5:
                    return "unusually_low"
                else:
                    return "normal"

            daily["status"] = z_scores.apply(assign_z_status)
            daily["method"] = "Z-SCORE"
            daily["deviation"] = (daily["value"] - daily["baseline"]).round(2)

        daily["metric"] = metric

        anomalies_only = daily[daily["status"] != "normal"]
        summary = {
            "total_evaluated_days": n,
            "total_anomalies": len(anomalies_only),
            "unusually_high_count": int((daily["status"] == "unusually_high").sum()),
            "unusually_low_count": int((daily["status"] == "unusually_low").sum()),
            "method": self.anomaly_method.upper(),
        }

        cols = ["date", "metric", "value", "baseline", "deviation", "method", "status"]
        return daily[cols], summary
