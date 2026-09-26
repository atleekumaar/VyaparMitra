"""
Product demand forecasting training pipeline.
Benchmarks Seasonal Naive baseline against Gradient Boosted Demand Forecaster.
Applies Quality Gate, computes category and volume tier breakdowns, persists champion model and metadata, and exports forecasts.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List
import joblib
import numpy as np
import pandas as pd
import yaml

from src.ml.data.forecasting_dataset import build_product_demand_panel
from src.ml.data.split import chronological_split
from src.ml.evaluation.forecasting_metrics import compute_forecasting_metrics
from src.ml.features.demand_features import extract_demand_forecasting_features
from src.ml.models.baselines import ProductDemandBaseline
from src.ml.models.demand_forecaster import ProductDemandForecaster
from src.schemas.ml_schema import ModelMetadata

logger = logging.getLogger(__name__)


def train_demand_forecaster(config_path: str = "configs/config.yaml") -> Dict[str, Any]:
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    paths = config.get("paths", {})
    processed_dir = Path(paths.get("processed", "data/processed"))
    features_dir = Path(paths.get("features", "data/features"))
    models_dir = Path(paths.get("models", "models")) / "demand"
    ml_data_dir = Path(paths.get("ml", "data/ml"))
    models_dir.mkdir(parents=True, exist_ok=True)
    (ml_data_dir / "forecasts").mkdir(parents=True, exist_ok=True)
    (ml_data_dir / "explainability").mkdir(parents=True, exist_ok=True)

    # 1. Ingest Data
    clean_tx_file = processed_dir / "clean_transactions.parquet"
    if not clean_tx_file.exists():
        clean_tx_file = processed_dir / "cleaned_transactions.parquet"
    prod_feat_file = features_dir / "product_features.parquet"
    if not clean_tx_file.exists() or not prod_feat_file.exists():
        raise FileNotFoundError(f"Missing clean_transactions ({clean_tx_file}) or product_features ({prod_feat_file}).")

    clean_tx = pd.read_parquet(clean_tx_file)
    prod_feats = pd.read_parquet(prod_feat_file)

    # 2. Build Panel & Extract Features
    panel_df = build_product_demand_panel(clean_tx, prod_feats)
    feat_df, feature_cols = extract_demand_forecasting_features(panel_df)

    # 3. Chronological Split (Split dates strictly to keep date cohorts together)
    split_cfg = config.get("ml", {}).get("split", {})
    unique_dates = pd.Series(sorted(feat_df["date"].unique()))
    n_dates = len(unique_dates)
    train_end_idx = int(n_dates * split_cfg.get("train_ratio", 0.70))
    val_end_idx = int(n_dates * (split_cfg.get("train_ratio", 0.70) + split_cfg.get("validation_ratio", 0.15)))

    train_dates = set(unique_dates.iloc[:train_end_idx])
    val_dates = set(unique_dates.iloc[train_end_idx:val_end_idx])
    test_dates = set(unique_dates.iloc[val_end_idx:])

    train_df = feat_df[feat_df["date"].isin(train_dates)].copy()
    val_df = feat_df[feat_df["date"].isin(val_dates)].copy()
    test_df = feat_df[feat_df["date"].isin(test_dates)].copy()

    X_train, y_train = train_df[feature_cols], train_df["units_sold"]
    X_val, y_val = val_df[feature_cols], val_df["units_sold"]
    X_test, y_test = test_df[feature_cols], test_df["units_sold"]

    # 4. Evaluate Baseline
    baseline = ProductDemandBaseline()
    baseline.fit(X_train, y_train)
    base_val_preds = baseline.predict(X_val)
    base_test_preds = baseline.predict(X_test)
    baseline_val_metrics = compute_forecasting_metrics(y_val.values, base_val_preds)
    baseline_test_metrics = compute_forecasting_metrics(y_test.values, base_test_preds)

    # 5. Train & Evaluate Candidate ML Model
    seed = config.get("ml", {}).get("random_seed", 42)
    ml_model = ProductDemandForecaster(random_seed=seed)
    ml_model.fit(X_train, y_train)
    ml_val_preds = ml_model.predict(X_val)
    ml_test_preds = ml_model.predict(X_test)
    ml_val_metrics = compute_forecasting_metrics(y_val.values, ml_val_preds)
    ml_test_metrics = compute_forecasting_metrics(y_test.values, ml_test_preds)

    # 6. Quality Gate
    if ml_val_metrics["wape"] < baseline_val_metrics["wape"]:
        selected_model = ml_model
        selected_name = ml_model.name
        selected_val_metrics = ml_val_metrics
        selected_test_metrics = ml_test_metrics
        reason = f"Candidate ML model beat baseline WAPE ({baseline_val_metrics['wape']:.2f}% vs {ml_val_metrics['wape']:.2f}%)"
    else:
        selected_model = baseline
        selected_name = baseline.name
        selected_val_metrics = baseline_val_metrics
        selected_test_metrics = baseline_test_metrics
        reason = f"Candidate ML did not beat baseline WAPE. Retained baseline {selected_name}."

    # 7. Category Breakdown on Test Set
    test_df = test_df.copy()
    test_df["predicted_units"] = selected_model.predict(X_test)
    category_metrics: Dict[str, Dict[str, float]] = {}
    for cat, cat_grp in test_df.groupby("product_category"):
        cat_metrics = compute_forecasting_metrics(cat_grp["units_sold"].values, cat_grp["predicted_units"].values)
        category_metrics[str(cat)] = cat_metrics

    # 8. Feature Importance
    if hasattr(ml_model, "get_feature_importance"):
        # Sample for validation permutation to keep execution swift
        val_sample = val_df.sample(min(len(val_df), 3000), random_state=seed)
        feat_imp_df = ml_model.get_feature_importance(val_sample[feature_cols], val_sample["units_sold"])
        feat_imp_df.to_parquet(ml_data_dir / "explainability" / "demand_feature_importance.parquet", index=False)
        feat_imp_df.to_csv(ml_data_dir / "explainability" / "demand_feature_importance.csv", index=False)
    else:
        feat_imp_df = pd.DataFrame()

    # 9. Retrain champion on Train + Val
    full_train_df = pd.concat([train_df, val_df], ignore_index=True)
    if hasattr(selected_model, "fit"):
        selected_model.fit(full_train_df[feature_cols], full_train_df["units_sold"])

    # 10. Persist Model and Metadata
    joblib.dump(selected_model, models_dir / "selected_model.joblib")
    metadata = ModelMetadata(
        model_name=selected_name,
        model_version="v1.0",
        training_date=pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        training_data_range={"start": str(unique_dates.iloc[0]), "end": str(unique_dates.iloc[val_end_idx - 1])},
        feature_list=feature_cols,
        target="units_sold",
        hyperparameters={"random_seed": seed, "model_type": getattr(selected_model, "name", "baseline")},
        validation_metrics=selected_val_metrics,
        test_metrics=selected_test_metrics,
        baseline_comparison={"baseline_val_wape": baseline_val_metrics["wape"], "ml_val_wape": ml_val_metrics["wape"]},
        selection_reason=reason,
    )
    with open(models_dir / "metadata.json", "w", encoding="utf-8") as f:
        f.write(metadata.model_dump_json(indent=2))

    # 11. Generate Forecasts (7-day and 30-day)
    forecast_7d = ml_model.forecast_products(panel_df, prod_feats, horizon_days=7)
    forecast_30d = ml_model.forecast_products(panel_df, prod_feats, horizon_days=30)

    forecast_7d.to_parquet(ml_data_dir / "forecasts" / "product_demand_forecast_7d.parquet", index=False)
    forecast_7d.to_csv(ml_data_dir / "forecasts" / "product_demand_forecast_7d.csv", index=False)
    forecast_30d.to_parquet(ml_data_dir / "forecasts" / "product_demand_forecast_30d.parquet", index=False)
    forecast_30d.to_csv(ml_data_dir / "forecasts" / "product_demand_forecast_30d.csv", index=False)

    logger.info("Product demand model trained. Selected: %s (Test WAPE: %.2f%%)", selected_name, selected_test_metrics["wape"])
    return {
        "selected_model": selected_name,
        "validation_metrics": selected_val_metrics,
        "test_metrics": selected_test_metrics,
        "baseline_comparison": baseline_val_metrics,
        "category_metrics": category_metrics,
        "reason": reason,
    }
