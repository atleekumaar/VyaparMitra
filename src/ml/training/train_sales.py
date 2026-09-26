"""
Sales forecasting training pipeline.
Benchmarks Naive, Seasonal Naive, Moving Average against Gradient Boosted Trees.
Applies Quality Gate, persists selected champion model and metadata, and exports forecasts.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Tuple
import joblib
import numpy as np
import pandas as pd
import yaml

from src.ml.data.forecasting_dataset import build_daily_sales_dataset
from src.ml.data.split import chronological_split
from src.ml.evaluation.backtesting import walk_forward_backtest
from src.ml.evaluation.forecasting_metrics import compute_forecasting_metrics
from src.ml.features.sales_features import extract_sales_forecasting_features
from src.ml.models.baselines import (
    MovingAverageSalesBaseline,
    NaiveSalesBaseline,
    SeasonalNaiveSalesBaseline,
)
from src.ml.models.sales_forecaster import SalesForecaster
from src.schemas.ml_schema import ModelMetadata

logger = logging.getLogger(__name__)


def train_sales_forecaster(config_path: str = "configs/config.yaml") -> Dict[str, Any]:
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    paths = config.get("paths", {})
    features_dir = Path(paths.get("features", "data/features"))
    models_dir = Path(paths.get("models", "models")) / "sales"
    ml_data_dir = Path(paths.get("ml", "data/ml"))
    models_dir.mkdir(parents=True, exist_ok=True)
    (ml_data_dir / "forecasts").mkdir(parents=True, exist_ok=True)
    (ml_data_dir / "explainability").mkdir(parents=True, exist_ok=True)

    # 1. Ingest Data
    daily_file = features_dir / "daily_features.parquet"
    if not daily_file.exists():
        raise FileNotFoundError(f"Missing daily features: {daily_file}")
    daily_raw = pd.read_parquet(daily_file)
    daily_clean = build_daily_sales_dataset(daily_raw)

    # 2. Extract Features
    feat_df, feature_cols = extract_sales_forecasting_features(daily_clean, date_col="date", target_col="revenue")

    # 3. Chronological Split
    split_cfg = config.get("ml", {}).get("split", {})
    train_df, val_df, test_df, split_info = chronological_split(
        feat_df,
        date_col="date",
        train_ratio=split_cfg.get("train_ratio", 0.70),
        val_ratio=split_cfg.get("validation_ratio", 0.15),
        test_ratio=split_cfg.get("test_ratio", 0.15),
    )

    X_train, y_train = train_df[feature_cols], train_df["revenue"]
    X_val, y_val = val_df[feature_cols], val_df["revenue"]
    X_test, y_test = test_df[feature_cols], test_df["revenue"]

    # 4. Evaluate Baselines
    baselines = {
        "naive": NaiveSalesBaseline(),
        "seasonal_naive": SeasonalNaiveSalesBaseline(),
        "moving_average": MovingAverageSalesBaseline(),
    }
    baseline_val_metrics = {}
    baseline_test_metrics = {}
    for b_key, b_model in baselines.items():
        b_model.fit(X_train, y_train)
        val_preds = b_model.predict(X_val)
        test_preds = b_model.predict(X_test)
        baseline_val_metrics[b_key] = compute_forecasting_metrics(y_val.values, val_preds)
        baseline_test_metrics[b_key] = compute_forecasting_metrics(y_test.values, test_preds)

    best_baseline_key = min(baseline_val_metrics, key=lambda k: baseline_val_metrics[k]["wape"])
    best_baseline_wape = baseline_val_metrics[best_baseline_key]["wape"]

    # 5. Evaluate Candidate ML Models
    seed = config.get("ml", {}).get("random_seed", 42)
    hgb_model = SalesForecaster(model_type="hist_gb", random_seed=seed)
    hgb_model.fit(X_train, y_train)
    hgb_val_preds = hgb_model.predict(X_val)
    hgb_val_metrics = compute_forecasting_metrics(y_val.values, hgb_val_preds)
    hgb_test_preds = hgb_model.predict(X_test)
    hgb_test_metrics = compute_forecasting_metrics(y_test.values, hgb_test_preds)

    rf_model = SalesForecaster(model_type="rf", random_seed=seed)
    rf_model.fit(X_train, y_train)
    rf_val_preds = rf_model.predict(X_val)
    rf_val_metrics = compute_forecasting_metrics(y_val.values, rf_val_preds)
    rf_test_preds = rf_model.predict(X_test)
    rf_test_metrics = compute_forecasting_metrics(y_test.values, rf_test_preds)

    # 6. Quality Gate & Selection
    candidates = {
        "HistGradientBoosting": (hgb_model, hgb_val_metrics, hgb_test_metrics),
        "RandomForest": (rf_model, rf_val_metrics, rf_test_metrics),
    }
    best_ml_key = min(candidates, key=lambda k: candidates[k][1]["wape"])
    selected_ml_model, selected_val_metrics, selected_test_metrics = candidates[best_ml_key]

    # Compare with best baseline
    if selected_val_metrics["wape"] < best_baseline_wape:
        selected_model = selected_ml_model
        selected_name = selected_ml_model.name
        reason = f"Outperformed best baseline ({best_baseline_key} WAPE: {best_baseline_wape}%) with validation WAPE: {selected_val_metrics['wape']}%"
    else:
        # Keep baseline if ML does not beat hurdle
        selected_model = baselines[best_baseline_key]
        selected_name = selected_model.name
        selected_val_metrics = baseline_val_metrics[best_baseline_key]
        selected_test_metrics = baseline_test_metrics[best_baseline_key]
        reason = f"Candidate ML models did not beat baseline. Selected {selected_name} based on Quality Gate."

    # 7. Walk-forward backtesting evaluation
    _, wf_summary = walk_forward_backtest(
        feat_df, feature_cols, "revenue", "date", lambda: SalesForecaster(model_type="hist_gb", random_seed=seed), n_splits=3, test_horizon=14
    )

    # 8. Feature Importance
    if hasattr(selected_ml_model, "get_feature_importance"):
        feat_imp_df = selected_ml_model.get_feature_importance(X_val, y_val)
        feat_imp_df.to_parquet(ml_data_dir / "explainability" / "sales_feature_importance.parquet", index=False)
        feat_imp_df.to_csv(ml_data_dir / "explainability" / "sales_feature_importance.csv", index=False)
    else:
        feat_imp_df = pd.DataFrame()

    # 9. Retrain selected champion model on Full Available Dataset (Train + Val) for forward inference
    full_train_df = pd.concat([train_df, val_df], ignore_index=True)
    if hasattr(selected_model, "fit"):
        selected_model.fit(full_train_df[feature_cols], full_train_df["revenue"])

    # 10. Persist Model and Metadata
    model_path = models_dir / "selected_model.joblib"
    meta_path = models_dir / "metadata.json"
    joblib.dump(selected_model, model_path)

    metadata = ModelMetadata(
        model_name=selected_name,
        model_version="v1.0",
        training_date=pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        training_data_range={"start": split_info.train_start, "end": split_info.validation_end},
        feature_list=feature_cols,
        target="daily_total_revenue",
        hyperparameters={"random_seed": seed, "model_type": getattr(selected_model, "model_type", "baseline")},
        validation_metrics=selected_val_metrics,
        test_metrics=selected_test_metrics,
        baseline_comparison={"baselines": baseline_val_metrics, "best_baseline": best_baseline_key},
        selection_reason=reason,
    )
    with open(meta_path, "w", encoding="utf-8") as f:
        f.write(metadata.model_dump_json(indent=2))

    # 11. Generate Forward Forecasts (7-day and 30-day)
    forecast_7d = selected_ml_model.forecast_horizon(daily_clean, horizon_days=7)
    forecast_30d = selected_ml_model.forecast_horizon(daily_clean, horizon_days=30)

    forecast_7d.to_parquet(ml_data_dir / "forecasts" / "sales_forecast_7d.parquet", index=False)
    forecast_7d.to_csv(ml_data_dir / "forecasts" / "sales_forecast_7d.csv", index=False)
    forecast_30d.to_parquet(ml_data_dir / "forecasts" / "sales_forecast_30d.parquet", index=False)
    forecast_30d.to_csv(ml_data_dir / "forecasts" / "sales_forecast_30d.csv", index=False)

    logger.info("Sales forecaster trained. Selected: %s (Test WAPE: %.2f%%)", selected_name, selected_test_metrics["wape"])
    return {
        "selected_model": selected_name,
        "validation_metrics": selected_val_metrics,
        "test_metrics": selected_test_metrics,
        "baseline_comparison": baseline_val_metrics,
        "walk_forward_summary": wf_summary,
        "split_info": split_info.model_dump(),
        "reason": reason,
    }
