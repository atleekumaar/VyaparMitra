"""
Integration tests for Phase 3 Predictive AI Engine.
Verifies MLEngine methods, Predictor, artifact existence, and schema conformance.
"""

from pathlib import Path
import pandas as pd
import pytest
from src.ml.ml_engine import MLEngine
from src.schemas.ml_schema import ModelMetadata


@pytest.fixture(scope="module")
def ml_engine():
    return MLEngine()


def test_models_and_metadata_exist():
    models_dir = Path("models")
    for mod in ["sales", "demand", "churn", "trend"]:
        joblib_path = models_dir / mod / "selected_model.joblib"
        meta_path = models_dir / mod / "metadata.json"
        assert joblib_path.exists(), f"Missing model binary: {joblib_path}"
        assert meta_path.exists(), f"Missing model metadata: {meta_path}"

        # Validate with pydantic schema
        metadata = ModelMetadata.model_validate_json(meta_path.read_text(encoding="utf-8"))
        assert metadata.model_name
        assert metadata.target


def test_forecast_artifacts_exist():
    ml_data_dir = Path("data/ml")
    expected_files = [
        ml_data_dir / "forecasts" / "sales_forecast_7d.parquet",
        ml_data_dir / "forecasts" / "sales_forecast_30d.parquet",
        ml_data_dir / "forecasts" / "product_demand_forecast_7d.parquet",
        ml_data_dir / "forecasts" / "product_demand_forecast_30d.parquet",
        ml_data_dir / "customer_risk" / "customer_risk_scores.parquet",
        ml_data_dir / "trends" / "business_trend_predictions.parquet",
        ml_data_dir / "reports" / "model_comparison.md",
        ml_data_dir / "reports" / "phase3_ml_report.md",
    ]
    for p in expected_files:
        assert p.exists(), f"Missing artifact: {p}"
        if p.suffix == ".parquet":
            df = pd.read_parquet(p)
            assert not df.empty, f"Artifact dataframe is empty: {p}"


def test_ml_engine_forecast_sales(ml_engine):
    sales_fc = ml_engine.forecast_sales(horizon_days=7)
    assert len(sales_fc) == 7
    assert "forecast_date" in sales_fc.columns
    assert "predicted_revenue" in sales_fc.columns
    assert (sales_fc["predicted_revenue"] >= 0).all()


def test_ml_engine_forecast_product_demand(ml_engine):
    demand_fc = ml_engine.forecast_product_demand(horizon_days=7)
    assert not demand_fc.empty
    assert "product_id" in demand_fc.columns
    assert "predicted_units" in demand_fc.columns


def test_ml_engine_score_customer_risk(ml_engine):
    risk_df = ml_engine.score_customer_risk()
    assert not risk_df.empty
    assert "customer_id" in risk_df.columns
    assert "risk_probability" in risk_df.columns
    assert "risk_band" in risk_df.columns
    assert set(risk_df["risk_band"].unique()).issubset({"low", "medium", "high"})


def test_ml_engine_predict_business_trend(ml_engine):
    trend_df = ml_engine.predict_business_trend()
    assert not trend_df.empty
    assert "predicted_trend" in trend_df.columns
    assert trend_df["predicted_trend"].iloc[0] in ["INCREASING", "STABLE", "DECREASING"]
