"""
End-to-End Integration Test for VyaparMitra Phase 1 Pipeline.
"""

from pathlib import Path
import pandas as pd
import yaml
from src.pipeline import run_pipeline


def test_full_pipeline_integration(tmp_path):
    # Set up isolated test configuration
    raw_dir = tmp_path / "raw"
    proc_dir = tmp_path / "processed"
    feat_dir = tmp_path / "features"
    quar_dir = tmp_path / "quarantine"
    rep_dir = tmp_path / "reports"

    test_config = {
        "dataset": {
            "random_seed": 42,
            "transactions": 100,
            "merchants": 5,
            "customers": 20,
            "products": 10,
            "inject_anomalies": True,
            "use_enriched_source": False,  # Test pure synthetic generation branch
        },
        "paths": {
            "raw": str(raw_dir),
            "processed": str(proc_dir),
            "features": str(feat_dir),
            "quarantine": str(quar_dir),
            "reports": str(rep_dir),
        },
        "validation": {
            "max_discount_rate": 0.90,
            "allow_zero_unit_price": False,
            "strict_referential_integrity": True,
        },
        "weather": {
            "impute_missing": True,
            "default_temp": 26.5,
            "default_humidity": 50.0,
            "default_rainfall": 0.0,
            "default_condition": "Clear",
        },
    }

    config_file = tmp_path / "test_config.yaml"
    with open(config_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(test_config, f)

    # Execute pipeline
    result = run_pipeline(config_path=str(config_file), force_regenerate=True)

    # 1. Pipeline execution status
    assert result["elapsed_seconds"] > 0
    assert result["quality_report"].overall_status in ["PASS", "WARN"]

    # 2. Verify all 5 feature store Parquet artifacts exist and are non-empty
    required_features = [
        "merchant_features",
        "customer_features",
        "product_features",
        "daily_features",
        "transaction_features",
    ]
    for feat_name in required_features:
        parquet_file = feat_dir / f"{feat_name}.parquet"
        csv_file = feat_dir / f"{feat_name}.csv"
        assert parquet_file.exists(), f"Missing Parquet: {parquet_file}"
        assert csv_file.exists(), f"Missing CSV: {csv_file}"
        df = pd.read_parquet(parquet_file)
        assert len(df) > 0, f"Empty dataframe in {parquet_file}"

    # 3. Verify quality reports exist
    json_report = rep_dir / "data_quality_report.json"
    md_report = rep_dir / "data_quality_report.md"
    assert json_report.exists()
    assert md_report.exists()

    # 4. Verify clean datasets were saved in processed dir
    assert (proc_dir / "clean_transactions.parquet").exists()
    assert (proc_dir / "clean_merchants.parquet").exists()
