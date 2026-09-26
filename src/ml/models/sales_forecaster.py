"""
Sales forecasting model implementation using Gradient Boosted Decision Trees.
Supports walk-forward training, iterative multi-step forecasting, and feature importance extraction.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.inspection import permutation_importance

logger = logging.getLogger(__name__)


class SalesForecaster:
    """Gradient boosted regression forecaster for daily merchant sales."""

    def __init__(
        self,
        model_type: str = "hist_gb",
        random_seed: int = 42,
        **kwargs: Any,
    ) -> None:
        self.model_type = model_type
        self.random_seed = random_seed
        self.feature_cols: List[str] = []

        if model_type == "rf":
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=8,
                random_state=random_seed,
                n_jobs=-1,
                **kwargs,
            )
            self.name = "RandomForestRegressor"
        else:
            self.model = HistGradientBoostingRegressor(
                max_iter=150,
                max_depth=6,
                min_samples_leaf=5,
                learning_rate=0.08,
                random_state=random_seed,
                **kwargs,
            )
            self.name = "HistGradientBoostingRegressor"

    def fit(self, X: pd.DataFrame, y: pd.Series) -> SalesForecaster:
        self.feature_cols = list(X.columns)
        self.model.fit(X, y)
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        preds = self.model.predict(X[self.feature_cols])
        return np.maximum(0.0, preds)  # Revenue cannot be negative

    def get_feature_importance(self, X_val: pd.DataFrame, y_val: pd.Series) -> pd.DataFrame:
        """Computes permutation feature importance on validation data."""
        perm = permutation_importance(
            self.model, X_val[self.feature_cols], y_val, n_repeats=5, random_state=self.random_seed
        )
        imp_df = pd.DataFrame({
            "feature": self.feature_cols,
            "importance": perm.importances_mean.round(4),
            "std": perm.importances_std.round(4),
        }).sort_values(by="importance", ascending=False).reset_index(drop=True)
        return imp_df

    def forecast_horizon(
        self,
        recent_daily_df: pd.DataFrame,
        horizon_days: int = 7,
    ) -> pd.DataFrame:
        """
        Iterative recursive multi-step forecasting for future dates.
        Updates lags and rolling statistics step-by-step.
        """
        history = recent_daily_df.sort_values(by="date").copy()
        last_date = pd.to_datetime(history["date"].max())
        forecast_rows = []

        for step in range(1, horizon_days + 1):
            next_date = last_date + pd.Timedelta(days=step)
            next_date_str = next_date.strftime("%Y-%m-%d")

            # Extract lag and rolling statistics from current history state
            rev_series = history["revenue"]
            lag_1 = float(rev_series.iloc[-1])
            lag_7 = float(rev_series.iloc[-7]) if len(rev_series) >= 7 else lag_1
            lag_14 = float(rev_series.iloc[-14]) if len(rev_series) >= 14 else lag_7
            lag_28 = float(rev_series.iloc[-28]) if len(rev_series) >= 28 else lag_14

            roll_7 = float(rev_series.tail(7).mean())
            roll_14 = float(rev_series.tail(14).mean())
            roll_28 = float(rev_series.tail(28).mean())

            dow = next_date.dayofweek
            dom = next_date.day
            woy = int(next_date.isocalendar().week)
            mo = next_date.month
            qtr = next_date.quarter
            is_wknd = 1 if dow in [5, 6] else 0

            # Step features
            step_features = {
                "lag_1d_revenue": lag_1,
                "lag_7d_revenue": lag_7,
                "lag_14d_revenue": lag_14,
                "lag_28d_revenue": lag_28,
                "rolling_7d_avg_revenue": roll_7,
                "rolling_14d_avg_revenue": roll_14,
                "rolling_28d_avg_revenue": roll_28,
                "day_of_week": dow,
                "day_of_month": dom,
                "week_of_year": woy,
                "month": mo,
                "quarter": qtr,
                "is_weekend": is_wknd,
                "is_festival": 0,
                "festival_intensity": 0.0,
                "temperature": 27.0,
                "rainfall": 0.0,
                "is_rainy": 0,
                "recent_order_count_7d": float(history["daily_total_orders"].tail(7).mean()) if "daily_total_orders" in history else 25.0,
                "recent_aov_7d": roll_7 / 25.0,
            }

            feat_df = pd.DataFrame([step_features])[self.feature_cols]
            pred_rev = float(round(self.predict(feat_df)[0], 2))

            forecast_rows.append({
                "forecast_date": next_date_str,
                "predicted_revenue": pred_rev,
                "lower_bound": None,  # Not fabricated without probabilistic model
                "upper_bound": None,
                "model_name": self.name,
                "model_version": "v1.0",
                "generated_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            })

            # Append synthetic row to history for recursive lags
            new_row = {"date": next_date_str, "revenue": pred_rev, "daily_total_orders": 25}
            history = pd.concat([history, pd.DataFrame([new_row])], ignore_index=True)

        return pd.DataFrame(forecast_rows)
