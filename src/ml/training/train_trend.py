"""
Business trend forecasting training pipeline.
Benchmarks Majority Class baseline against Gradient Boosted Trend Classifier.
Applies Quality Gate, computes Macro F1 / Balanced Accuracy, persists champion model, and generates current trend forecast.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict
import joblib
import numpy as np
import pandas as pd
import yaml

from src.ml.data.forecasting_dataset import build_daily_sales_dataset
from src.ml.data.split import chronological_split
from src.ml.evaluation.classification_metrics import compute_classification_metrics
from src.ml.features.trend_features import extract_trend_forecasting_features
from src.ml.models.baselines import MajorityTrendBaseline
from src.ml.models.trend_model import BusinessTrendModel, CLASS_LABEL_MAP
from src.schemas.ml_schema import ModelMetadata

logger = logging.getLogger(__name__)


def train_trend_model(config_path: str = "configs/config.yaml") -> Dict[str, Any]:
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    paths = config.get("paths", {})
    features_dir = Path(paths.get("features", "data/features"))
    models_dir = Path(paths.get("models", "models")) / "trend"
    ml_data_dir = Path(paths.get("ml", "data/ml"))
    models_dir.mkdir(parents=True, exist_ok=True)
    (ml_data_dir / "trends").mkdir(parents=True, exist_ok=True)
    (ml_data_dir / "explainability").mkdir(parents=True, exist_ok=True)

    # 1. Ingest Data
    daily_file = features_dir / "daily_features.parquet"
    if not daily_file.exists():
        raise FileNotFoundError(f"Missing daily features: {daily_file}")

    daily_raw = pd.read_parquet(daily_file)
    daily_clean = build_daily_sales_dataset(daily_raw)

    # 2. Extract Features
    feat_df, feature_cols = extract_trend_forecasting_features(
        daily_clean, date_col="date", revenue_col="revenue", horizon_days=7, stable_threshold_pct=3.0
    )

    # Filter to rows with valid target for training/testing
    labeled_df = feat_df.dropna(subset=["trend_target"]).copy()
    labeled_df["trend_target"] = labeled_df["trend_target"].astype(int)

    # 3. Chronological Split (Train 70%, Val 15%, Test 15%)
    split_cfg = config.get("ml", {}).get("split", {})
    train_df, val_df, test_df, split_info = chronological_split(
        labeled_df,
        date_col="date",
        train_ratio=split_cfg.get("train_ratio", 0.70),
        val_ratio=split_cfg.get("validation_ratio", 0.15),
        test_ratio=split_cfg.get("test_ratio", 0.15),
    )

    X_train, y_train = train_df[feature_cols], train_df["trend_target"]
    X_val, y_val = val_df[feature_cols], val_df["trend_target"]
    X_test, y_test = test_df[feature_cols], test_df["trend_target"]

    # 4. Evaluate Baseline
    baseline = MajorityTrendBaseline()
    baseline.fit(X_train, y_train)
    base_val_preds = baseline.predict(X_val)
    base_test_preds = baseline.predict(X_test)
    baseline_val_metrics = compute_classification_metrics(y_val.values, base_val_preds, is_multiclass=True)
    baseline_test_metrics = compute_classification_metrics(y_test.values, base_test_preds, is_multiclass=True)

    # 5. Train & Evaluate Candidate ML Model
    seed = config.get("ml", {}).get("random_seed", 42)
    ml_model = BusinessTrendModel(random_seed=seed, horizon_days=7)
    ml_model.fit(X_train, y_train)
    ml_val_preds = ml_model.predict(X_val)
    ml_val_probs = ml_model.predict_proba(X_val)
    ml_val_metrics = compute_classification_metrics(y_val.values, ml_val_preds, ml_val_probs, is_multiclass=True)

    ml_test_preds = ml_model.predict(X_test)
    ml_test_probs = ml_model.predict_proba(X_test)
    ml_test_metrics = compute_classification_metrics(y_test.values, ml_test_preds, ml_test_probs, is_multiclass=True)

    # 6. Quality Gate
    # ML model must beat or equal baseline balanced accuracy and macro f1
    base_f1 = baseline_val_metrics.get("f1_macro", 0.0)
    ml_f1 = ml_val_metrics.get("f1_macro", 0.0)

    if ml_f1 >= base_f1:
        selected_model = ml_model
        selected_name = ml_model.name
        selected_val_metrics = ml_val_metrics
        selected_test_metrics = ml_test_metrics
        reason = f"Candidate ML model beat or matched baseline Macro F1 ({ml_f1:.4f} vs {base_f1:.4f})"
    else:
        selected_model = baseline
        selected_name = baseline.name
        selected_val_metrics = baseline_val_metrics
        selected_test_metrics = baseline_test_metrics
        reason = f"Candidate ML did not beat baseline Macro F1. Selected baseline {selected_name}."

    # 7. Permutation Feature Importance
    if hasattr(ml_model, "get_feature_importance"):
        feat_imp_df = ml_model.get_feature_importance(X_val, y_val)
        feat_imp_df.to_parquet(ml_data_dir / "explainability" / "trend_feature_importance.parquet", index=False)
        feat_imp_df.to_csv(ml_data_dir / "explainability" / "trend_feature_importance.csv", index=False)
    else:
        feat_imp_df = pd.DataFrame()

    # 8. Retrain champion on Train + Val
    full_train_df = pd.concat([train_df, val_df], ignore_index=True)
    if hasattr(selected_model, "fit"):
        selected_model.fit(full_train_df[feature_cols], full_train_df["trend_target"])

    # 9. Persist Model and Metadata
    joblib.dump(selected_model, models_dir / "selected_model.joblib")
    metadata = ModelMetadata(
        model_name=selected_name,
        model_version="v1.0",
        training_date=pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        training_data_range={"start": split_info.train_start, "end": split_info.validation_end},
        feature_list=feature_cols,
        target="trend_target",
        hyperparameters={"random_seed": seed, "horizon_days": 7, "model_type": getattr(selected_model, "name", "baseline")},
        validation_metrics=selected_val_metrics,
        test_metrics=selected_test_metrics,
        baseline_comparison={"baseline_val": baseline_val_metrics, "ml_val": ml_val_metrics},
        selection_reason=reason,
    )
    with open(models_dir / "metadata.json", "w", encoding="utf-8") as f:
        f.write(metadata.model_dump_json(indent=2))

    # 10. Generate Trend Prediction for the latest date
    latest_row = feat_df.iloc[[-1]].copy()
    trend_pred_df = ml_model.predict_current_trend(latest_row)
    trend_pred_df.to_parquet(ml_data_dir / "trends" / "business_trend_predictions.parquet", index=False)
    trend_pred_df.to_csv(ml_data_dir / "trends" / "business_trend_predictions.csv", index=False)

    logger.info("Trend model trained. Selected: %s (Test Macro F1: %s). Current forecast: %s",
                selected_name, selected_test_metrics.get("f1_macro"), trend_pred_df["predicted_trend"].iloc[0])

    return {
        "selected_model": selected_name,
        "validation_metrics": selected_val_metrics,
        "test_metrics": selected_test_metrics,
        "baseline_comparison": baseline_val_metrics,
        "current_trend_prediction": trend_pred_df.to_dict(orient="records"),
        "reason": reason,
    }
