"""
Product demand forecasting model implementation.
Predicts item-level demand across the product catalog and supports evaluation by category.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.inspection import permutation_importance

logger = logging.getLogger(__name__)


class ProductDemandForecaster:
    """Gradient boosted regression forecaster for product-level daily unit demand."""

    def __init__(
        self,
        random_seed: int = 42,
        **kwargs: Any,
    ) -> None:
        self.random_seed = random_seed
        self.model = HistGradientBoostingRegressor(
            max_iter=120,
            max_depth=6,
            min_samples_leaf=10,
            learning_rate=0.08,
            random_state=random_seed,
            **kwargs,
        )
        self.name = "HistGradientBoostingRegressor_Demand"
        self.feature_cols: List[str] = []

    def fit(self, X: pd.DataFrame, y: pd.Series) -> ProductDemandForecaster:
        self.feature_cols = list(X.columns)
        self.model.fit(X, y)
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        preds = self.model.predict(X[self.feature_cols])
        return np.maximum(0.0, np.round(preds, 2))

    def get_feature_importance(self, X_val: pd.DataFrame, y_val: pd.Series) -> pd.DataFrame:
        """Computes permutation feature importance."""
        perm = permutation_importance(
            self.model, X_val[self.feature_cols], y_val, n_repeats=5, random_state=self.random_seed
        )
        imp_df = pd.DataFrame({
            "feature": self.feature_cols,
            "importance": perm.importances_mean.round(4),
            "std": perm.importances_std.round(4),
        }).sort_values(by="importance", ascending=False).reset_index(drop=True)
        return imp_df

    def forecast_products(
        self,
        panel_df: pd.DataFrame,
        products_df: pd.DataFrame,
        horizon_days: int = 7,
    ) -> pd.DataFrame:
        """Generates future product demand forecasts for the catalog."""
        last_date = pd.to_datetime(panel_df["date"].max())
        all_products = products_df[["product_id", "product_category"]].drop_duplicates()

        forecast_rows = []
        for step in range(1, horizon_days + 1):
            next_date = (last_date + pd.Timedelta(days=step)).strftime("%Y-%m-%d")
            dt = pd.to_datetime(next_date)

            for _, prod in all_products.iterrows():
                pid = prod["product_id"]
                pcat = prod["product_category"]

                # Extract latest product history
                prod_history = panel_df[panel_df["product_id"] == pid].sort_values(by="date")
                latest_units = prod_history["units_sold"].values if not prod_history.empty else np.array([0.0])

                lag_1 = float(latest_units[-1]) if len(latest_units) >= 1 else 0.0
                lag_7 = float(latest_units[-7]) if len(latest_units) >= 7 else lag_1
                lag_14 = float(latest_units[-14]) if len(latest_units) >= 14 else lag_7
                lag_28 = float(latest_units[-28]) if len(latest_units) >= 28 else lag_14

                roll_7 = float(np.mean(latest_units[-7:])) if len(latest_units) >= 7 else lag_1
                roll_14 = float(np.mean(latest_units[-14:])) if len(latest_units) >= 14 else roll_7
                roll_28 = float(np.mean(latest_units[-28:])) if len(latest_units) >= 28 else roll_14

                sp = float(prod["selling_price"]) if "selling_price" in prod and pd.notna(prod["selling_price"]) else 100.0
                uc = float(prod["unit_cost"]) if "unit_cost" in prod and pd.notna(prod["unit_cost"]) else 70.0
                step_feat = {
                    "lag_1_units": lag_1,
                    "lag_7_units": lag_7,
                    "lag_14_units": lag_14,
                    "lag_28_units": lag_28,
                    "rolling_7_units": roll_7,
                    "rolling_14_units": roll_14,
                    "rolling_28_units": roll_28,
                    "day_of_week": dt.dayofweek,
                    "day_of_month": dt.day,
                    "month": dt.month,
                    "is_weekend": 1 if dt.dayofweek in [5, 6] else 0,
                    "selling_price": sp,
                    "unit_cost": uc,
                    "unit_margin": round(sp - uc, 2),
                }

                feat_df = pd.DataFrame([step_feat])[self.feature_cols]
                pred_units = float(self.predict(feat_df)[0])

                forecast_rows.append({
                    "forecast_date": next_date,
                    "product_id": pid,
                    "product_category": pcat,
                    "predicted_units": round(pred_units, 2),
                    "model_name": self.name,
                    "model_version": "v1.0",
                })

        return pd.DataFrame(forecast_rows)
