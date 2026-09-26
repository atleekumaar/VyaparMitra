"""
End-to-end integration test for VyaparMitra Phase 2 Business Intelligence Engine.
Tests full pipeline against Phase 1 feature store artifacts, verifies output data mart,
and checks strict reconciliation.
"""

from pathlib import Path
import pandas as pd
import pytest
from src.analytics.analytics_engine import AnalyticsEngine


def test_full_analytics_engine_execution():
    engine = AnalyticsEngine()
    results = engine.run_all_analytics()

    # 1. Pipeline status
    assert results["elapsed_seconds"] > 0
    assert results["datasets_generated"] >= 20
    assert results["validation"]["status"] == "PASS"

    # 2. Strict reconciliation against Phase 1 feature store
    rec = results["reconciliation"]
    assert rec["status"] == "PASS"
    assert rec["revenue_match"] is True
    assert rec["orders_match"] is True
    assert rec["phase2_orders"] == 9995
    assert abs(rec["phase2_revenue"] - 15510039.34) < 0.01

    # 3. Check physical Parquet files in data/analytics/
    analytics_dir = Path("data/analytics")
    expected_files = [
        "sales_summary.parquet",
        "sales_daily.parquet",
        "sales_weekly.parquet",
        "sales_monthly.parquet",
        "customer_summary.parquet",
        "customer_segments.parquet",
        "customer_cohorts.parquet",
        "product_summary.parquet",
        "product_rankings.parquet",
        "category_summary.parquet",
        "category_monthly.parquet",
        "time_hourly.parquet",
        "time_weekday.parquet",
        "time_monthly.parquet",
        "payment_summary.parquet",
        "merchant_summary.parquet",
        "merchant_benchmarks.parquet",
        "festival_analysis.parquet",
        "weather_analysis.parquet",
        "trend_analysis.parquet",
        "anomaly_analysis.parquet",
    ]

    for f_name in expected_files:
        f_path = analytics_dir / f_name
        assert f_path.exists(), f"Missing analytics file: {f_path}"
        df = pd.read_parquet(f_path)
        assert len(df) > 0, f"Analytics dataset {f_path} is empty"

    # 4. Check business summary report files
    assert (analytics_dir / "business_summary.json").exists()
    assert (analytics_dir / "business_summary.md").exists()


def test_analytics_api_methods():
    engine = AnalyticsEngine()

    sales = engine.sales(period="monthly")
    assert not sales.empty
    assert "revenue" in sales.columns

    cust_summary = engine.customer_summary()
    assert cust_summary.total_customers == 3308

    prod_summary = engine.product_summary()
    assert len(prod_summary) == 64

    cat_summary = engine.category_summary()
    assert len(cat_summary) == 32

    trends = engine.trends()
    assert not trends.empty

    benchmarks = engine.merchant_benchmarks()
    assert len(benchmarks) == 50
    assert "benchmark_type" in benchmarks.columns
