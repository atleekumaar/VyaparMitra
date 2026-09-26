"""
Customer churn and inactivity risk training pipeline.
Benchmarks Rule-based baseline against Logistic Regression and Gradient Boosted Trees.
Applies Quality Gate, computes PR-AUC / ROC-AUC / F1, persists champion model, and scores customer risk.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import yaml

from src.ml.data.churn_dataset import build_customer_churn_snapshot
from src.ml.evaluation.classification_metrics import compute_classification_metrics
from src.ml.features.churn_features import prepare_churn_feature_matrix
from src.ml.models.baselines import RuleBasedChurnBaseline
from src.ml.models.churn_model import CustomerChurnModel
from src.schemas.ml_schema import ModelMetadata

logger = logging.getLogger(__name__)


def train_churn_model(config_path: str = "configs/config.yaml") -> Dict[str, Any]:
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    paths = config.get("paths", {})
    processed_dir = Path(paths.get("processed", "data/processed"))
    models_dir = Path(paths.get("models", "models")) / "churn"
    ml_data_dir = Path(paths.get("ml", "data/ml"))
    models_dir.mkdir(parents=True, exist_ok=True)
    (ml_data_dir / "customer_risk").mkdir(parents=True, exist_ok=True)
    (ml_data_dir / "explainability").mkdir(parents=True, exist_ok=True)

    # 1. Ingest Cleaned Transactions
    clean_tx_file = processed_dir / "clean_transactions.parquet"
    if not clean_tx_file.exists():
        clean_tx_file = processed_dir / "cleaned_transactions.parquet"
    if not clean_tx_file.exists():
        raise FileNotFoundError(f"Missing clean transactions: {clean_tx_file}")

    clean_tx = pd.read_parquet(clean_tx_file)

    # 2. Build Point-in-Time Snapshot
    # Using snapshot date 2026-07-15 to allow a 30-day forward evaluation window (up to 2026-08-15)
    snapshot_date = "2026-07-15"
    inactivity_days = 30
    snapshot_df, snap_meta = build_customer_churn_snapshot(
        clean_tx, snapshot_date=snapshot_date, inactivity_days=inactivity_days
    )

    X_full, y_full, feature_cols = prepare_churn_feature_matrix(snapshot_df, target_col="is_churned")

    # 3. Stratified Split (Train 70%, Val 15%, Test 15%)
    seed = config.get("ml", {}).get("random_seed", 42)
    split_cfg = config.get("ml", {}).get("split", {})
    train_ratio = split_cfg.get("train_ratio", 0.70)
    val_ratio = split_cfg.get("validation_ratio", 0.15)
    test_ratio = split_cfg.get("test_ratio", 0.15)

    # First split off test set (15%)
    indices = np.arange(len(snapshot_df))
    train_val_idx, test_idx = train_test_split(
        indices, test_size=test_ratio, random_state=seed, stratify=y_full
    )

    # Split train and val (val is 0.15 / 0.85 of train_val)
    val_relative_size = val_ratio / (train_ratio + val_ratio)
    train_idx, val_idx = train_test_split(
        train_val_idx, test_size=val_relative_size, random_state=seed, stratify=y_full.iloc[train_val_idx]
    )

    X_train, y_train = X_full.iloc[train_idx], y_full.iloc[train_idx]
    X_val, y_val = X_full.iloc[val_idx], y_full.iloc[val_idx]
    X_test, y_test = X_full.iloc[test_idx], y_full.iloc[test_idx]

    # 4. Evaluate Baseline
    baseline = RuleBasedChurnBaseline(recency_threshold=60.0)
    baseline.fit(X_train, y_train)
    base_val_probs = baseline.predict_proba(X_val)[:, 1]
    base_val_preds = baseline.predict(X_val)
    base_val_metrics = compute_classification_metrics(y_val.values, base_val_preds, base_val_probs)

    base_test_probs = baseline.predict_proba(X_test)[:, 1]
    base_test_preds = baseline.predict(X_test)
    base_test_metrics = compute_classification_metrics(y_test.values, base_test_preds, base_test_probs)

    # 5. Evaluate Candidate ML Models
    # Candidate 1: Logistic Regression
    lr_model = CustomerChurnModel(model_type="logistic", random_seed=seed)
    lr_model.fit(X_train, y_train)
    lr_val_probs = lr_model.predict_proba(X_val)[:, 1]
    lr_val_preds = lr_model.predict(X_val)
    lr_val_metrics = compute_classification_metrics(y_val.values, lr_val_preds, lr_val_probs)
    lr_test_probs = lr_model.predict_proba(X_test)[:, 1]
    lr_test_preds = lr_model.predict(X_test)
    lr_test_metrics = compute_classification_metrics(y_test.values, lr_test_preds, lr_test_probs)

    # Candidate 2: HistGradientBoosting
    hgb_model = CustomerChurnModel(model_type="hist_gb", random_seed=seed)
    hgb_model.fit(X_train, y_train)
    hgb_val_probs = hgb_model.predict_proba(X_val)[:, 1]
    hgb_val_preds = hgb_model.predict(X_val)
    hgb_val_metrics = compute_classification_metrics(y_val.values, hgb_val_preds, hgb_val_probs)
    hgb_test_probs = hgb_model.predict_proba(X_test)[:, 1]
    hgb_test_preds = hgb_model.predict(X_test)
    hgb_test_metrics = compute_classification_metrics(y_test.values, hgb_test_preds, hgb_test_probs)

    # Candidate 3: Random Forest
    rf_model = CustomerChurnModel(model_type="rf", random_seed=seed)
    rf_model.fit(X_train, y_train)
    rf_val_probs = rf_model.predict_proba(X_val)[:, 1]
    rf_val_preds = rf_model.predict(X_val)
    rf_val_metrics = compute_classification_metrics(y_val.values, rf_val_preds, rf_val_probs)
    rf_test_probs = rf_model.predict_proba(X_test)[:, 1]
    rf_test_preds = rf_model.predict(X_test)
    rf_test_metrics = compute_classification_metrics(y_test.values, rf_test_preds, rf_test_probs)

    candidates = {
        "LogisticRegression": (lr_model, lr_val_metrics, lr_test_metrics),
        "HistGradientBoostingClassifier": (hgb_model, hgb_val_metrics, hgb_test_metrics),
        "RandomForestClassifier": (rf_model, rf_val_metrics, rf_test_metrics),
    }

    # Selection based on Validation PR-AUC (or ROC-AUC if PR-AUC tied)
    best_ml_key = max(
        candidates,
        key=lambda k: (candidates[k][1].get("pr_auc", 0) or 0, candidates[k][1].get("roc_auc", 0) or 0),
    )
    selected_ml_model, selected_val_metrics, selected_test_metrics = candidates[best_ml_key]

    # Quality Gate vs Baseline
    base_score = base_val_metrics.get("pr_auc", 0) or 0
    ml_score = selected_val_metrics.get("pr_auc", 0) or 0

    if ml_score >= base_score:
        selected_model = selected_ml_model
        selected_name = selected_ml_model.name
        reason = f"Candidate ML ({best_ml_key}) outperformed rule-based baseline (PR-AUC: {ml_score:.4f} vs {base_score:.4f})"
    else:
        selected_model = baseline
        selected_name = baseline.name
        selected_val_metrics = base_val_metrics
        selected_test_metrics = base_test_metrics
        reason = f"Candidate ML did not exceed baseline PR-AUC. Selected baseline {selected_name}."

    # 6. Permutation Feature Importance
    if hasattr(selected_ml_model, "get_feature_importance"):
        feat_imp_df = selected_ml_model.get_feature_importance(X_val, y_val)
        feat_imp_df.to_parquet(ml_data_dir / "explainability" / "churn_feature_importance.parquet", index=False)
        feat_imp_df.to_csv(ml_data_dir / "explainability" / "churn_feature_importance.csv", index=False)
    else:
        feat_imp_df = pd.DataFrame()

    # 7. Retrain champion on Train + Val
    full_train_X = pd.concat([X_train, X_val], ignore_index=True)
    full_train_y = pd.concat([y_train, y_val], ignore_index=True)
    if hasattr(selected_model, "fit"):
        selected_model.fit(full_train_X, full_train_y)

    # 8. Persist Model and Metadata
    joblib.dump(selected_model, models_dir / "selected_model.joblib")
    metadata = ModelMetadata(
        model_name=selected_name,
        model_version="v1.0",
        training_date=pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        training_data_range={"snapshot_date": snapshot_date, "inactivity_window_days": inactivity_days},
        feature_list=feature_cols,
        target="is_churned",
        hyperparameters={"random_seed": seed, "model_type": getattr(selected_model, "name", "baseline")},
        validation_metrics=selected_val_metrics,
        test_metrics=selected_test_metrics,
        baseline_comparison={"baseline_val": base_val_metrics, "ml_val": selected_val_metrics},
        selection_reason=reason,
    )
    with open(models_dir / "metadata.json", "w", encoding="utf-8") as f:
        f.write(metadata.model_dump_json(indent=2))

    # 9. Score Customer Inactivity Risk Across All Snapshot Customers
    scored_customers = selected_ml_model.score_customers(snapshot_df)
    scored_customers.to_parquet(ml_data_dir / "customer_risk" / "customer_risk_scores.parquet", index=False)
    scored_customers.to_csv(ml_data_dir / "customer_risk" / "customer_risk_scores.csv", index=False)

    risk_counts = scored_customers["risk_band"].value_counts().to_dict()
    logger.info("Churn model trained. Selected: %s (Test PR-AUC: %s). Risk bands: %s", selected_name, selected_test_metrics.get("pr_auc"), risk_counts)

    return {
        "selected_model": selected_name,
        "validation_metrics": selected_val_metrics,
        "test_metrics": selected_test_metrics,
        "baseline_comparison": base_val_metrics,
        "risk_band_counts": risk_counts,
        "snapshot_metadata": snap_meta,
        "reason": reason,
    }
