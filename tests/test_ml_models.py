"""
Unit tests for baseline models and ML wrappers in Phase 3.
"""

import numpy as np
import pandas as pd
from src.ml.models.baselines import (
    MovingAverageSalesBaseline,
    NaiveSalesBaseline,
    ProductDemandBaseline,
    RuleBasedChurnBaseline,
    SeasonalNaiveSalesBaseline,
    MajorityTrendBaseline,
)
from src.ml.models.sales_forecaster import SalesForecaster
from src.ml.models.demand_forecaster import ProductDemandForecaster
from src.ml.models.churn_model import CustomerChurnModel
from src.ml.models.trend_model import BusinessTrendModel


def test_sales_baselines():
    X = pd.DataFrame({
        "lag_1d_revenue": [100.0, 150.0],
        "lag_7d_revenue": [90.0, 140.0],
        "rolling_7d_avg_revenue": [95.0, 145.0],
    })

    naive = NaiveSalesBaseline()
    assert (naive.predict(X) == np.array([100.0, 150.0])).all()

    s_naive = SeasonalNaiveSalesBaseline()
    assert (s_naive.predict(X) == np.array([90.0, 140.0])).all()

    ma = MovingAverageSalesBaseline()
    assert (ma.predict(X) == np.array([95.0, 145.0])).all()


def test_product_demand_baseline():
    X = pd.DataFrame({
        "lag_7_units": [10.0, 0.0],
        "lag_1_units": [8.0, 5.0],
    })
    baseline = ProductDemandBaseline()
    preds = baseline.predict(X)
    assert preds[0] == 10.0
    assert preds[1] == 5.0  # Fallback to lag 1


def test_rule_based_churn_baseline():
    X = pd.DataFrame({"recency": [10.0, 70.0, 120.0]})
    baseline = RuleBasedChurnBaseline(recency_threshold=60.0)
    preds = baseline.predict(X)
    assert preds[0] == 0  # low recency -> active
    assert preds[2] == 1  # high recency -> churned


def test_majority_trend_baseline():
    X = pd.DataFrame({"dummy": [1, 2, 3]})
    y = pd.Series([2, 2, 1])
    baseline = MajorityTrendBaseline()
    baseline.fit(X, y)
    preds = baseline.predict(X)
    assert (preds == 2).all()


def test_sales_forecaster_fit_predict():
    X = pd.DataFrame({
        "lag_1d_revenue": [100.0, 110.0, 120.0, 130.0],
        "lag_7d_revenue": [90.0, 95.0, 100.0, 105.0],
    })
    y = pd.Series([105.0, 115.0, 125.0, 135.0])

    model = SalesForecaster(model_type="hist_gb", random_seed=42)
    model.fit(X, y)
    preds = model.predict(X)
    assert len(preds) == 4
    assert (preds >= 0).all()


def test_customer_churn_model_fit_predict():
    X = pd.DataFrame({
        "recency": [10.0, 90.0, 15.0, 80.0],
        "total_orders": [5, 1, 6, 1],
    })
    y = pd.Series([0, 1, 0, 1])

    model = CustomerChurnModel(model_type="logistic", random_seed=42)
    model.fit(X, y)
    probs = model.predict_proba(X)
    assert probs.shape == (4, 2)
    assert ((probs >= 0.0) & (probs <= 1.0)).all()
