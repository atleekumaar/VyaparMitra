"""
Top-level Python API Facade for VyaparMitra Phase 3: Predictive AI Engine.
Integrates training, evaluation, inference, and reporting into a cohesive service layer.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional
import pandas as pd
import yaml

from src.ml.inference.predictor import Predictor
from src.ml.training.train_churn import train_churn_model
from src.ml.training.train_demand import train_demand_forecaster
from src.ml.training.train_sales import train_sales_forecaster
from src.ml.training.train_trend import train_trend_model

logger = logging.getLogger(__name__)


class MLEngine:
    """Unified Facade for Phase 3 Predictive AI Engine."""

    def __init__(self, config_path: str = "configs/config.yaml") -> None:
        self.config_path = config_path
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        paths = self.config.get("paths", {})
        self.models_dir = Path(paths.get("models", "models"))
        self.ml_data_dir = Path(paths.get("ml", "data/ml"))
        self.predictor = Predictor(config_path=config_path)

    # Training APIs
    def train_sales(self) -> Dict[str, Any]:
        return train_sales_forecaster(self.config_path)

    def train_demand(self) -> Dict[str, Any]:
        return train_demand_forecaster(self.config_path)

    def train_churn(self) -> Dict[str, Any]:
        return train_churn_model(self.config_path)

    def train_trend(self) -> Dict[str, Any]:
        return train_trend_model(self.config_path)

    def train_all(self) -> Dict[str, Any]:
        """Trains and validates all 4 predictive models with full benchmarking and export."""
        logger.info("Initiating end-to-end training for all Phase 3 predictive models...")
        res_sales = self.train_sales()
        res_demand = self.train_demand()
        res_churn = self.train_churn()
        res_trend = self.train_trend()
        reports = {}
        try:
            from src.reporting.ml_report_generator import generate_ml_reports
            reports = generate_ml_reports(self.config_path)
        except Exception as e:
            logger.warning("Failed to generate ML reports: %s", e)

        return {
            "sales": res_sales,
            "demand": res_demand,
            "churn": res_churn,
            "trend": res_trend,
            "reports": reports,
        }

    # Inference APIs
    def forecast_sales(self, horizon_days: int = 7) -> pd.DataFrame:
        """Forecasts total daily revenue for horizon_days into the future."""
        return self.predictor.predict_sales(horizon_days=horizon_days)

    def forecast_product_demand(self, horizon_days: int = 7) -> pd.DataFrame:
        """Forecasts unit demand across all catalog products for horizon_days."""
        return self.predictor.predict_demand(horizon_days=horizon_days)

    def score_customer_risk(self, snapshot_date: str = "2026-07-15") -> pd.DataFrame:
        """Evaluates customer inactivity and churn risk probabilities."""
        return self.predictor.predict_churn(snapshot_date=snapshot_date)

    def predict_business_trend(self) -> pd.DataFrame:
        """Predicts directional revenue trend for the next 7-day operational cycle."""
        return self.predictor.predict_trend()

    # Metadata & Explainability APIs
    def get_model_metadata(self, model_type: str = "sales") -> Dict[str, Any]:
        meta_path = self.models_dir / model_type / "metadata.json"
        if not meta_path.exists():
            raise FileNotFoundError(f"Metadata not found for {model_type} at {meta_path}")
        with open(meta_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_feature_importances(self, model_type: str = "sales") -> pd.DataFrame:
        imp_path = self.ml_data_dir / "explainability" / f"{model_type}_feature_importance.parquet"
        if not imp_path.exists():
            raise FileNotFoundError(f"Feature importance not found for {model_type} at {imp_path}")
        return pd.read_parquet(imp_path)
