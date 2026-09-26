"""
End-to-End Orchestrator for VyaparMitra Phase 1: Data Foundation & Merchant Feature Store.

Executes:
1. Ingestion / Data Generation
2. Validation & Data Quality Reporting
3. Data Cleaning & Quarantine Isolation
4. Feature Engineering (Transactions, Festivals, Weather, Merchants, Customers, Products, Daily Time Windows)
5. Final Feature Store Export (Parquet & CSV)
"""

from __future__ import annotations

import argparse
import logging
import time
from pathlib import Path
from typing import Any, Dict, Optional
import pandas as pd
import yaml

from src.cleaning.cleaner import DataCleaner
from src.data_generation.generate_dataset import generate_all_datasets
from src.features.customer_features import extract_customer_features
from src.features.festival_features import merge_festival_features
from src.features.merchant_features import extract_merchant_features
from src.features.product_features import extract_product_features
from src.features.time_features import extract_daily_features
from src.features.transaction_features import extract_transaction_features
from src.features.weather_features import merge_weather_features
from src.ingestion.loader import DataLoader
from src.validation.validator import DataValidator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("VyaparMitra.Pipeline")


def run_pipeline(
    config_path: str = "configs/config.yaml",
    force_regenerate: bool = False,
) -> Dict[str, Any]:
    """
    Run complete Phase 1 pipeline end-to-end.
    Returns dictionary of execution statistics, report, and feature counts.
    """
    start_time = time.time()
    logger.info("=================================================================")
    logger.info("Starting VyaparMitra Phase 1 Pipeline: Data Foundation & Feature Store")
    logger.info("=================================================================")

    # 1. Load Configuration
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    raw_dir = Path(config["paths"]["raw"])
    processed_dir = Path(config["paths"]["processed"])
    features_dir = Path(config["paths"]["features"])
    quarantine_dir = Path(config["paths"]["quarantine"])
    reports_dir = Path(config["paths"]["reports"])

    for d in [raw_dir, processed_dir, features_dir, quarantine_dir, reports_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # 2. Check Raw Data or Generate
    tx_file = raw_dir / "transactions.csv"
    if force_regenerate or not tx_file.exists():
        logger.info("Generating / initializing raw relational tables...")
        generate_all_datasets(config_path)

    # 3. Data Ingestion
    logger.info("Step 1: Loading raw data...")
    loader = DataLoader(raw_dir=str(raw_dir), config_path=config_path)
    raw_data = loader.load_all()
    logger.info(
        "Ingested: %d transactions, %d merchants, %d customers, %d products, %d festivals, %d weather rows",
        len(raw_data["transactions"]),
        len(raw_data["merchants"]),
        len(raw_data["customers"]),
        len(raw_data["products"]),
        len(raw_data["festivals"]),
        len(raw_data["weather"]),
    )

    # 4. Data Quality Validation
    logger.info("Step 2: Validating transactions and referential integrity...")
    validator = DataValidator(
        max_discount_rate=config.get("validation", {}).get("max_discount_rate", 0.90)
    )
    quality_report, rejection_reasons = validator.validate(
        transactions=raw_data["transactions"],
        merchants=raw_data["merchants"],
        customers=raw_data["customers"],
        products=raw_data["products"],
    )
    json_rep_path, md_rep_path = validator.save_reports(
        quality_report, reports_dir=str(reports_dir)
    )

    # 5. Data Cleaning & Quarantine
    logger.info("Step 3: Cleaning data and routing invalid records to quarantine...")
    cleaner = DataCleaner(
        processed_dir=str(processed_dir),
        quarantine_dir=str(quarantine_dir),
    )
    cleaned_data = cleaner.clean_all(raw_data, rejection_reasons)
    clean_tx = cleaned_data["transactions"]
    quarantined_tx = cleaned_data["quarantined"]

    # 6. Feature Engineering
    logger.info("Step 4: Executing Feature Engineering pipeline...")
    
    # 6a. Transaction-level features
    tx_features = extract_transaction_features(clean_tx)

    # 6b. Festival features merge
    tx_features = merge_festival_features(
        tx_features, cleaned_data["festivals"], date_col="date"
    )

    # 6c. Weather features merge
    weather_defaults = config.get("weather", {})
    tx_features = merge_weather_features(
        tx_features,
        cleaned_data["weather"],
        merchants_df=cleaned_data["merchants"],
        defaults=weather_defaults,
    )

    # 6d. Merchant-level features
    merchant_features = extract_merchant_features(
        tx_features, cleaned_data["merchants"]
    )

    # 6e. Customer-level features
    customer_features = extract_customer_features(
        tx_features, cleaned_data["customers"]
    )

    # 6f. Product-level features
    product_features = extract_product_features(
        tx_features, cleaned_data["products"]
    )

    # 6g. Daily aggregated time-window features
    daily_features = extract_daily_features(tx_features, date_col="date")

    # 7. Persist Final Feature Store
    logger.info("Step 5: Exporting final Feature Store to Parquet and CSV in %s...", features_dir)
    
    feature_store_artifacts = {
        "transaction_features": tx_features,
        "merchant_features": merchant_features,
        "customer_features": customer_features,
        "product_features": product_features,
        "daily_features": daily_features,
    }

    for name, f_df in feature_store_artifacts.items():
        parquet_path = features_dir / f"{name}.parquet"
        csv_path = features_dir / f"{name}.csv"
        f_df.to_parquet(parquet_path, index=False)
        f_df.to_csv(csv_path, index=False)
        logger.info(
            "Exported %s: %d records, %d columns -> %s",
            name,
            len(f_df),
            len(f_df.columns),
            parquet_path,
        )

    elapsed_time = round(time.time() - start_time, 2)
    logger.info("=================================================================")
    logger.info("Phase 1 Pipeline Execution COMPLETED successfully in %.2f seconds", elapsed_time)
    logger.info("=================================================================")

    return {
        "elapsed_seconds": elapsed_time,
        "quality_report": quality_report,
        "counts": {
            "raw_transactions": len(raw_data["transactions"]),
            "clean_transactions": len(clean_tx),
            "quarantined_transactions": len(quarantined_tx),
            "merchants": len(merchant_features),
            "customers": len(customer_features),
            "products": len(product_features),
            "daily_records": len(daily_features),
            "transaction_features": len(tx_features),
        },
        "report_paths": {
            "json": str(json_rep_path),
            "markdown": str(md_rep_path),
        },
    }


def main() -> None:
    """CLI Entry point for python -m src.pipeline."""
    parser = argparse.ArgumentParser(description="VyaparMitra Phase 1 Data Pipeline")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/config.yaml",
        help="Path to YAML configuration file",
    )
    parser.add_argument(
        "--regenerate",
        action="store_true",
        help="Force regeneration of raw datasets from source",
    )
    args = parser.parse_args()

    results = run_pipeline(
        config_path=args.config,
        force_regenerate=args.regenerate,
    )

    print("\n" + "=" * 60)
    print("VYAPARMITRA PHASE 1 EXECUTION SUMMARY")
    print("=" * 60)
    print(f"Elapsed Time: {results['elapsed_seconds']} seconds")
    print(f"Clean Transactions: {results['counts']['clean_transactions']:,}")
    print(f"Quarantined Records: {results['counts']['quarantined_transactions']}")
    print(f"Merchants in Feature Store: {results['counts']['merchants']}")
    print(f"Customers in Feature Store: {results['counts']['customers']}")
    print(f"Products in Feature Store: {results['counts']['products']}")
    print(f"Daily Time-Window Records: {results['counts']['daily_records']}")
    print(f"Overall Quality Status: {results['quality_report'].overall_status}")
    print("=" * 60)


if __name__ == "__main__":
    main()
