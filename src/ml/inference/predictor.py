"""
Unified inference engine for Phase 3 ML models.
Loads persisted champions from models/ directory and produces forecasts and risk assessments,
with defensive fallback to statistical baselines if serialization (e.g., NumPy PCG64) fails.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Callable, Optional

import joblib
import numpy as np
import pandas as pd
import yaml

from src.ml.data.churn_dataset import build_customer_churn_snapshot
from src.ml.data.forecasting_dataset import build_daily_sales_dataset, build_product_demand_panel
from src.ml.features.churn_features import prepare_churn_feature_matrix
from src.ml.features.demand_features import extract_demand_forecasting_features
from src.ml.features.sales_features import extract_sales_forecasting_features
from src.ml.features.trend_features import extract_trend_forecasting_features
from src.ml.models.baselines import (
    MajorityTrendBaseline,
    NaiveSalesBaseline,
    ProductDemandBaseline,
    RuleBasedChurnBaseline,
)

logger = logging.getLogger(__name__)


class Predictor:
    """Unified inference engine serving all Phase 3 predictive models with defensive fallbacks."""

    def __init__(self, config_path: str = "configs/config.yaml") -> None:
        self.config_path = config_path
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        paths = self.config.get("paths", {})
        self.models_dir = Path(paths.get("models", "models"))
        self.features_dir = Path(paths.get("features", "data/features"))
        self.processed_dir = Path(paths.get("processed", "data/processed"))

        self._sales_model = None
        self._demand_model = None
        self._churn_model = None
        self._trend_model = None

    def _safe_load_model(
        self,
        model_path: Path,
        model_label: str,
        fallback_factory: Optional[Callable[[], Any]] = None,
    ) -> Any:
        """
        Safely loads a serialized .joblib model artifact.
        Protects inference against cross-version NumPy PCG64 BitGenerator pickling errors
        or missing artifacts by falling back to deterministic statistical baselines.
        """
        if not model_path.exists():
            if fallback_factory is not None:
                logger.warning(
                    "Model artifact missing at %s. Activating defensive baseline fallback for %s.",
                    model_path,
                    model_label,
                )
                return fallback_factory()
            raise FileNotFoundError(f"Trained {model_label} model not found at {model_path}. Run training first.")

        try:
            return joblib.load(model_path)
        except (TypeError, ValueError, ModuleNotFoundError, EOFError, AttributeError, Exception) as exc:
            logger.error(
                "Serialization/deserialization failure loading %s model from %s (%s: %s). "
                "Falling back to statistical baseline.",
                model_label,
                model_path,
                type(exc).__name__,
                exc,
            )
            if fallback_factory is not None:
                return fallback_factory()
            raise

    def _build_sales_baseline_fallback(self) -> Any:
        return NaiveSalesBaseline()

    def _build_demand_baseline_fallback(self) -> Any:
        return ProductDemandBaseline()

    def _build_churn_baseline_fallback(self) -> Any:
        return RuleBasedChurnBaseline()

    def _build_trend_baseline_fallback(self) -> Any:
        return MajorityTrendBaseline()

    def get_sales_model(self) -> Any:
        if self._sales_model is None:
            path = self.models_dir / "sales" / "selected_model.joblib"
            self._sales_model = self._safe_load_model(path, "sales", self._build_sales_baseline_fallback)
        return self._sales_model

    def get_demand_model(self) -> Any:
        if self._demand_model is None:
            path = self.models_dir / "demand" / "selected_model.joblib"
            self._demand_model = self._safe_load_model(path, "demand", self._build_demand_baseline_fallback)
        return self._demand_model

    def get_churn_model(self) -> Any:
        if self._churn_model is None:
            path = self.models_dir / "churn" / "selected_model.joblib"
            self._churn_model = self._safe_load_model(path, "churn", self._build_churn_baseline_fallback)
        return self._churn_model

    def get_trend_model(self) -> Any:
        if self._trend_model is None:
            path = self.models_dir / "trend" / "selected_model.joblib"
            self._trend_model = self._safe_load_model(path, "trend", self._build_trend_baseline_fallback)
        return self._trend_model

    def predict_sales(self, horizon_days: int = 7) -> pd.DataFrame:
        """Generates future total sales forecasts for specified horizon."""
        model = self.get_sales_model()
        daily_file = self.features_dir / "daily_features.parquet"
        daily_df = build_daily_sales_dataset(pd.read_parquet(daily_file))

        if hasattr(model, "forecast_horizon"):
            return model.forecast_horizon(daily_df, horizon_days=horizon_days)

        # Baseline fallback
        feat_df, cols = extract_sales_forecasting_features(daily_df)
        last_row = feat_df.iloc[[-1]]
        last_date = pd.to_datetime(daily_df["date"].max())
        pred_val = float(model.predict(last_row[cols])[0])

        rows = []
        for step in range(1, horizon_days + 1):
            next_date = (last_date + pd.Timedelta(days=step)).strftime("%Y-%m-%d")
            rows.append({
                "forecast_date": next_date,
                "predicted_revenue": round(pred_val, 2),
                "lower_bound_80": round(pred_val * 0.85, 2),
                "upper_bound_80": round(pred_val * 1.15, 2),
                "model_name": getattr(model, "name", "naive_sales_baseline"),
                "model_version": "v1.0-fallback",
            })
        return pd.DataFrame(rows)

    def predict_demand(self, horizon_days: int = 7) -> pd.DataFrame:
        """Generates future item-level demand forecasts."""
        model = self.get_demand_model()
        tx_file = self.processed_dir / "clean_transactions.parquet"
        if not tx_file.exists():
            tx_file = self.processed_dir / "cleaned_transactions.parquet"
        prod_file = self.features_dir / "product_features.parquet"

        clean_tx = pd.read_parquet(tx_file)
        prod_feats = pd.read_parquet(prod_file)
        panel_df = build_product_demand_panel(clean_tx, prod_feats)

        if hasattr(model, "forecast_products"):
            return model.forecast_products(panel_df, prod_feats, horizon_days=horizon_days)

        # Baseline fallback
        feat_df, cols = extract_demand_forecasting_features(panel_df)
        latest_date = panel_df["date"].max()
        latest_panel = feat_df[feat_df["date"] == latest_date].copy()
        preds = model.predict(latest_panel[cols])
        latest_panel["predicted_units"] = np.round(preds, 2)
        latest_panel["model_name"] = getattr(model, "name", "product_demand_baseline")
        latest_panel["model_version"] = "v1.0-fallback"
        return latest_panel[["date", "product_id", "product_category", "predicted_units", "model_name", "model_version"]].rename(
            columns={"date": "forecast_date"}
        )

    def predict_churn(self, snapshot_date: str = "2026-07-15") -> pd.DataFrame:
        """Evaluates customer churn and assigns risk probabilities and bands."""
        model = self.get_churn_model()
        tx_file = self.processed_dir / "clean_transactions.parquet"
        if not tx_file.exists():
            tx_file = self.processed_dir / "cleaned_transactions.parquet"
        clean_tx = pd.read_parquet(tx_file)
        snapshot_df, _ = build_customer_churn_snapshot(clean_tx, snapshot_date=snapshot_date)

        if hasattr(model, "score_customers"):
            return model.score_customers(snapshot_df)

        probs = model.predict_proba(snapshot_df)[:, 1]
        snapshot_df["risk_probability"] = np.round(probs, 4)
        snapshot_df["risk_band"] = snapshot_df["risk_probability"].apply(
            lambda p: "high" if p >= 0.60 else ("medium" if p >= 0.30 else "low")
        )
        return snapshot_df[["customer_id", "snapshot_date", "risk_probability", "risk_band"]]

    def predict_trend(self) -> pd.DataFrame:
        """Forecasts directional trend for the latest available operational period."""
        model = self.get_trend_model()
        daily_file = self.features_dir / "daily_features.parquet"
        daily_df = build_daily_sales_dataset(pd.read_parquet(daily_file))
        feat_df, cols = extract_trend_forecasting_features(daily_df)
        latest_row = feat_df.iloc[[-1]].copy()

        if hasattr(model, "predict_current_trend"):
            return model.predict_current_trend(latest_row)

        pred_class = int(model.predict(latest_row[cols])[0])
        labels = {0: "DECREASING", 1: "STABLE", 2: "INCREASING"}
        return pd.DataFrame([{
            "prediction_date": latest_row["date"].values[0],
            "horizon_days": 7,
            "predicted_trend": labels.get(pred_class, "STABLE"),
            "confidence": 0.50,
            "model_name": getattr(model, "name", "majority_trend_baseline"),
            "model_version": "v1.0-fallback",
        }])
