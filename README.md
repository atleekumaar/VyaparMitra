# VyaparMitra — AI-Powered Business Assistant for Small Merchants

> **Phase 1 Completed: Data Foundation & Merchant Feature Store**

VyaparMitra is an intelligent, localized decision-support system designed for small and medium retail merchants across India. This repository contains the complete implementation of **Phase 1: Data Foundation & Merchant Feature Store**, providing a modular data engineering pipeline that ingests, validates, cleans, enriches, and transforms raw transaction logs into an ML-ready feature store.

---

## 1. Project Overview

Small merchants face inventory bottlenecks, seasonal cash-flow volatility, and demand fluctuations driven by local festivals, weather patterns, and regional economic cycles. VyaparMitra addresses these challenges by transforming daily operational data into actionable predictive insights.

Phase 1 establishes the rock-solid data foundation required for all downstream modeling, including:
* Referential integrity and data hygiene.
* Quarantine mechanisms that prevent data corruption without silent deletion.
* Multi-scale temporal aggregations with strict anti-leakage protections.
* Seamless integration of external context (multi-event festival calendars and meteorological conditions).

---

## 2. Phase 1 Objective

Build a production-ready data pipeline that converts raw merchant transaction data into a clean, validated, and ML-ready **Merchant Feature Store**.

```text
Raw Transaction & External Data
              ↓
  Data Quality Validation
              ↓
 Data Cleaning & Quarantine Isolation
              ↓
      Feature Engineering
              ↓
   Merchant-Level Aggregation
              ↓
  External Context Integration (Festivals & Weather)
              ↓
 Final Feature Store (Parquet & CSV)
```

---

## 3. Architecture & Project Structure

```text
vyaparmitra/
├── configs/
│   └── config.yaml               # Pipeline parameters, paths, thresholds, seeds
├── data/
│   ├── raw/                      # Raw ingested relational CSV tables
│   ├── processed/                # Standardized Parquet & CSV tables
│   ├── quarantine/               # Isolated invalid records with rejection reasons
│   ├── quality_reports/          # Validation outputs (JSON & Markdown)
│   └── features/                 # Final Feature Store (Parquet & CSV)
├── docs/
│   └── data_dictionary.md        # Comprehensive data dictionary & leakage rules
├── src/
│   ├── data_generation/
│   │   ├── __init__.py
│   │   └── generate_dataset.py   # Realistic generator and enriched source normalizer
│   ├── ingestion/
│   │   ├── __init__.py
│   │   └── loader.py             # Strongly-typed data loader
│   ├── validation/
│   │   ├── __init__.py
│   │   └── validator.py          # Quality checks and Markdown/JSON reporter
│   ├── cleaning/
│   │   ├── __init__.py
│   │   └── cleaner.py            # Sanitizer and quarantine router
│   ├── features/
│   │   ├── __init__.py
│   │   ├── transaction_features.py # Unit prices, net amounts, calendar flags
│   │   ├── merchant_features.py    # Merchant lifetime revenue, velocity, AOV
│   │   ├── customer_features.py    # RFM metrics, frequency, recency
│   │   ├── product_features.py     # SKU volume sales, realized prices
│   │   ├── time_features.py        # Daily time windows, rolling trailing averages
│   │   ├── festival_features.py    # Multi-festival handling, days-to/after metrics
│   │   └── weather_features.py     # Meteorological joins & graceful imputation
│   └── pipeline.py               # End-to-end pipeline orchestrator & CLI
├── tests/
│   ├── __init__.py
│   ├── test_validation.py        # Validation & referential integrity unit tests
│   ├── test_cleaning.py          # Sanitization & quarantine unit tests
│   ├── test_features.py          # Revenue math, aggregations, festival & weather tests
│   └── test_pipeline_integration.py # Full end-to-end integration test
├── pytest.ini                    # Pytest test execution configurations
├── requirements.txt              # Production dependency specifications
└── README.md
```

---

## 4. Dataset Schemas

Phase 1 manages 6 relational entities:

1. **Transactions (`transactions.csv`)**: 10,000+ records containing `transaction_id`, `merchant_id`, `customer_id`, `timestamp`, `product_id`, `product_category`, `quantity`, `unit_price`, `discount`, `payment_method`.
2. **Merchants (`merchants.csv`)**: 50 merchants containing `merchant_id`, `merchant_name`, `business_type`, `city`, `state`, `pincode`, `latitude`, `longitude`.
3. **Customers (`customers.csv`)**: 3,308 customers containing `customer_id`, `customer_name`, `customer_type`, `city`, `signup_date`.
4. **Products (`products.csv`)**: 64 products across 32 categories containing `product_id`, `product_name`, `product_category`, `unit_cost`, `selling_price`.
5. **Festivals (`festivals.csv`)**: Festival events supporting multiple festivals on the same date (e.g., Ambedkar Jayanti & Baisakhi), containing `date`, `festival_name`, `festival_type`, `is_festival`, `festival_intensity`.
6. **Weather (`weather.csv`)**: 2,921 daily city observations containing `date`, `city`, `temperature`, `humidity`, `rainfall`, `weather_condition`.

Full field-by-field definitions, constraints, and data types are detailed in [`docs/data_dictionary.md`](docs/data_dictionary.md).

---

## 5. How to Generate Data

Data can be generated or normalized directly using:

```bash
python -m src.data_generation.generate_dataset
```

* **Enriched Normalization**: Automatically transforms `data/raw/vyaparmitra_10000_transactions_enriched.csv` into fully normalized relational entities.
* **Pure Synthetic Generation**: If no enriched source is present, generates reproducible data with realistic shopping correlations (weekend volume bumps, evening rushes, festival demand surges, weather impacts, and Zipfian customer frequencies) using `random_seed: 42`.
* **Controlled Anomaly Injection**: Injects test anomalies (duplicate IDs, invalid prices, out-of-bounds discounts) to verify automated quarantine handling.

---

## 6. How to Run the Pipeline

Execute the complete Phase 1 pipeline with a single command:

```bash
python -m src.pipeline
```

Optional arguments:
* `--config configs/config.yaml`: Use a custom configuration file.
* `--regenerate`: Force re-normalization/re-generation of raw data tables.

Sample execution output:
```text
============================================================
VYAPARMITRA PHASE 1 EXECUTION SUMMARY
============================================================
Elapsed Time: 2.08 seconds
Clean Transactions: 9,995
Quarantined Records: 5
Merchants in Feature Store: 50
Customers in Feature Store: 3,308
Products in Feature Store: 64
Daily Time-Window Records: 358
Overall Quality Status: PASS
============================================================
```

---

## 7. Data Quality & Quarantine Pipeline

The automated validation system verifies:
* **Missing values**: Nulls, NaNs, empty strings across critical fields.
* **Duplicate records**: Duplicate `transaction_id`.
* **Value sanity**: `quantity <= 0`, `unit_price < 0`, `discount < 0`, `discount > (quantity * unit_price)`.
* **Referential integrity**: Validates foreign keys against product, merchant, and customer dimension tables.
* **Timestamp validity**: Ensures parseable ISO timestamps within acceptable date bounds.

### Never Silently Delete Data
Corrupt or invalid records are routed directly to:
* `data/quarantine/quarantined_transactions.csv`

Each quarantined record includes an explicit `rejection_reason` explaining why it was flagged (e.g., `DUPLICATE_TRANSACTION_ID`, `INVALID_QUANTITY`, `INVALID_UNIT_PRICE`).

### Quality Reports
Saved automatically after every pipeline run:
* `data/quality_reports/data_quality_report.json`
* `data/quality_reports/data_quality_report.md`

---

## 8. Final Feature Store

The feature store is persisted in `data/features/` in high-performance **Apache Parquet** format (along with companion CSV files for easy inspection):

1. **`merchant_features.parquet`** (50 rows, 16 features): Total revenue, total orders, average order value, unique customers, catalog breadth, active days, revenue per day, orders per day, plus location metadata.
2. **`customer_features.parquet`** (3,308 rows, 12 features): Total spend, order count, average order value, customer recency, purchase frequency, lifetime timestamps.
3. **`product_features.parquet`** (64 rows, 11 features): Physical units sold, net revenue, order frequency, distinct purchasers, average quantity per basket, effective realized selling price.
4. **`daily_features.parquet`** (358 rows, 28 features): Daily total revenue, orders, units, active merchants/customers, average order value, festival metrics, weather averages, calendar flags, and anti-leakage 7-day trailing rolling averages.
5. **`transaction_features.parquet`** (9,995 rows, 37 features): Full transaction records enriched with calculated net amounts, temporal indicators, festival proximities, and local meteorological observations.

---

## 9. Testing & Verification

VyaparMitra includes unit and integration tests covering validation, cleaning, feature math, festival merging, weather imputation, and end-to-end pipeline execution.

Run the entire test suite:

```bash
python -m pytest -v
```

Output:
```text
tests/test_cleaning.py::test_quarantine_isolation PASSED                 [  6%]
tests/test_cleaning.py::test_merchant_and_customer_cleaning PASSED       [ 13%]
tests/test_features.py::test_transaction_feature_calculations PASSED     [ 20%]
tests/test_features.py::test_merchant_feature_aggregations PASSED        [ 26%]
tests/test_features.py::test_customer_feature_aggregations PASSED        [ 33%]
tests/test_features.py::test_product_feature_aggregations PASSED         [ 40%]
tests/test_features.py::test_festival_merge_and_distances PASSED         [ 46%]
tests/test_features.py::test_weather_merge_and_graceful_imputation PASSED [ 53%]
tests/test_features.py::test_daily_time_window_features_no_future_leakage PASSED [ 60%]
tests/test_pipeline_integration.py::test_full_pipeline_integration PASSED [ 66%]
tests/test_validation.py::test_clean_transactions_pass_validation PASSED [ 73%]
tests/test_validation.py::test_duplicate_transaction_detection PASSED    [ 80%]
tests/test_validation.py::test_invalid_prices_and_quantities PASSED      [ 86%]
tests/test_validation.py::test_referential_integrity_violation PASSED    [ 93%]
tests/test_validation.py::test_invalid_discounts PASSED                  [100%]

============================= 15 passed in 3.08s ==============================
```

---

## 10. Future Phase 2 Integration

The Phase 1 Feature Store exposes clean, standardized interfaces for future modules:
* **Phase 2 (Analytics & Dashboards)**: Consumes `merchant_features.parquet` and `daily_features.parquet` to display sales velocity, AOV trends, and merchant performance cohorts.
* **Phase 3 (Predictive ML & Forecasting)**: Leverages `daily_features.parquet` (with pre-computed trailing lags, festival proximity, and weather variables) for demand forecasting without risk of data leakage.
* **Phase 4 (Customer Recommendation & Retention)**: Uses `customer_features.parquet` and `product_features.parquet` for RFM segmentation, affinity basket analysis, and re-order reminders.
