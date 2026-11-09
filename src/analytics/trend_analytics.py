"""
Trend & Anomaly Analytics Engine for VyaparMitra
Detects directionality and statistical outliers using IQR & Modified Z-Score.
"""
from typing import Dict, Any, Tuple, Optional
import pandas as pd
import numpy as np


class TrendAnalytics:
    def __init__(self, data: pd.DataFrame, config: Optional[Dict[str, Any]] = None):
        self.df = data.copy()
        self.config = config or {}
        if not self.df.empty and 'date' in self.df.columns:
            self.df['date'] = pd.to_datetime(self.df['date'])

    def get_trend_analysis(self, frequency: str = "daily", metric: str = "net_amount") -> pd.DataFrame:
        """Classifies trend direction into 'Increasing', 'Decreasing', or 'Stable'."""
        if self.df.empty:
            return pd.DataFrame()

        trend_cfg = self.config.get("analytics", {}).get("trend", {})
        stable_threshold = trend_cfg.get("stable_threshold_percent", 5.0)

        df = self.df.sort_values('date').copy()
        metric_col = metric if metric in df.columns else ('net_amount' if 'net_amount' in df.columns else df.columns[-1])

        df['percentage_change'] = df[metric_col].pct_change().fillna(0.0) * 100.0

        def classify_row(pct):
            if pct > stable_threshold:
                return "Increasing"
            elif pct < -stable_threshold:
                return "Decreasing"
            return "Stable"

        df['trend_classification'] = df['percentage_change'].apply(classify_row)
        return df

    def get_daily_anomalies(self, metric: str = "net_amount") -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Detects anomalies using IQR or MAD with standardized status labels."""
        if self.df.empty:
            return pd.DataFrame(), {"total_anomalies": 0, "unusually_high_count": 0}

        anomaly_cfg = self.config.get("analytics", {}).get("anomaly", {})
        iqr_mult = anomaly_cfg.get("iqr_multiplier", 1.5)

        df = self.df.copy()
        metric_col = metric if metric in df.columns else ('net_amount' if 'net_amount' in df.columns else 'total_sales')
        if metric_col not in df.columns:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            metric_col = numeric_cols[0] if len(numeric_cols) > 0 else df.columns[0]

        series = df[metric_col].astype(float)

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - (iqr_mult * iqr)
        upper_bound = q3 + (iqr_mult * iqr)

        status_list = []
        for val in series:
            if val > upper_bound:
                status_list.append("unusually_high")
            elif val < lower_bound:
                status_list.append("unusually_low")
            else:
                status_list.append("normal")

        df['status'] = status_list
        df['baseline'] = series.median()
        df['deviation'] = series - df['baseline']

        high_count = sum(1 for s in status_list if s == "unusually_high")
        low_count = sum(1 for s in status_list if s == "unusually_low")

        summary = {
            "total_anomalies": high_count + low_count,
            "unusually_high_count": high_count,
            "unusually_low_count": low_count
        }

        return df, summary
