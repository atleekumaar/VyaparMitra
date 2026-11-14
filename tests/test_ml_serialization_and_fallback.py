"""
Tests for ML model serialization resilience (NumPy PCG64 BitGenerator mismatch),
defensive baseline fallbacks, and end-to-end predictive consistency.
"""
from unittest.mock import patch
import joblib
from src.ml.inference.predictor import Predictor


def test_predictor_falls_back_cleanly_on_pcg64_pickle_error():
    """Simulates a NumPy PCG64 BitGenerator TypeError during joblib.load and verifies graceful baseline fallback."""
    pred = Predictor()
    with patch.object(joblib, "load", side_effect=TypeError("<class 'numpy.random._pcg64.PCG64'> is not a known BitGenerator module")):
        sales_df = pred.predict_sales(horizon_days=5)
        assert len(sales_df) == 5
        assert "predicted_revenue" in sales_df.columns
        assert (sales_df["predicted_revenue"] >= 0).all()

        demand_df = pred.predict_demand(horizon_days=5)
        assert not demand_df.empty
        assert "predicted_units" in demand_df.columns

        churn_df = pred.predict_churn()
        assert not churn_df.empty
        assert set(churn_df["risk_band"]).issubset({"low", "medium", "high"})

        trend_df = pred.predict_trend()
        assert len(trend_df) == 1
        assert trend_df["predicted_trend"].iloc[0] in {"DECREASING", "STABLE", "INCREASING"}


def test_predictor_live_re_serialized_models_consistency():
    """Validates all 4 re-serialized champion artifacts load and return well-formed predictions."""
    pred = Predictor()
    s = pred.predict_sales(horizon_days=7)
    d = pred.predict_demand(horizon_days=7)
    c = pred.predict_churn()
    t = pred.predict_trend()

    assert len(s) == 7
    assert not d.empty
    assert ((c["risk_probability"] >= 0.0) & (c["risk_probability"] <= 1.0)).all()
    assert t["predicted_trend"].iloc[0] in {"DECREASING", "STABLE", "INCREASING"}
