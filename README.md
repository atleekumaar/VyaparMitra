# VyaparMitra — AI-Powered Business Assistant for Small Merchants

> **Phase 1 & Phase 2: Data Foundation, Feature Store & Business Intelligence Engine**

VyaparMitra is an intelligent, localized decision-support system designed for small and medium retail merchants across India. This repository contains the complete implementation of:
- **Phase 1: Data Foundation & Merchant Feature Store** — Ingestion, validation, cleaning, quarantine isolation, feature engineering, and temporal feature store.
- **Phase 2: Business Intelligence & Analytics Engine** — Aggregations, metrics, RFM segmentation, Pareto analysis, time & payment patterns, festival/weather contextual analytics, trend classification, and executive reporting.

---

## 1. System Architecture

```text
RAW INGESTION & DATA GENERATION
               │
               ▼
       DATA VALIDATION
   (Referential Integrity & Sanity)
          │            │
      [Invalid]     [Valid]
          │            │
          ▼            ▼
     QUARANTINE     CLEANING
     ISOLATION         │
                       ▼
             FEATURE ENGINEERING
   (Transactions, Merchants, Customers, Products, Daily)
                       │
                       ▼
              PHASE 1 FEATURE STORE
         (Parquet & CSV in data/features/)
                       │
         ┌─────────────┴─────────────┐
         ▼                           ▼
ANALYTICS ENGINE              REPORTING ENGINE
├── Sales & Revenue KPIs      ├── Executive Markdown Reports
├── RFM Customer Segments     └── Diagnostic JSON Summaries
├── Product Pareto 80/20
├── Category Margins & Shares
├── Hourly & Peak Time
├── Payment Channels (UPI/Cash)
├── Festival & Weather Context
└── Trends & IQR Anomalies
         │
         ▼
PHASE 2 ANALYTICS MARTS
 (data/analytics/ in Parquet & CSV)
```

---

## 2. Repository Structure

```text
VyaparMitra/
├── configs/
│   └── config.yaml                     # Pipeline parameters, paths, thresholds, seeds
├── data/
│   ├── raw/                            # Ingested dimension & fact tables
│   ├── processed/                      # Sanitized clean tables
│   ├── quarantine/                     # Quarantined invalid records with rejection reasons
│   ├── quality_reports/                # Automated validation reports (JSON & Markdown)
│   ├── features/                       # Phase 1 Feature Store (5 Parquet & CSV datasets)
│   └── analytics/                      # Phase 2 Business Intelligence Marts
│       ├── sales/                      # Sales KPIs & daily metrics
│       ├── customers/                  # RFM segmentations & cohort retention
│       ├── products/                   # Performance matrix, rankings, Pareto 80/20
│       ├── categories/                 # Category contribution & margins
│       ├── time/                       # Hourly distributions & peak shopping windows
│       ├── payments/                   # UPI, Cash, Card shares & velocity
│       ├── context/                    # Festival lift & weather elasticity
│       ├── trends/                     # Rolling trend vectors & IQR anomalies
│       └── reports/                    # Executive summaries
├── docs/
│   ├── data_dictionary.md              # Phase 1 Feature Store dictionary & leakage rules
│   ├── analytics_architecture.md       # Phase 2 Analytics Engine architecture
│   └── analytics_dictionary.md         # Phase 2 Metric definitions & calculation rules
├── src/
│   ├── cleaning/                       # Data sanitization & quarantine routing
│   ├── data_generation/                # Realistic synthetic data & enriched source normalizer
│   ├── features/                       # Multi-scale temporal & contextual feature extractors
│   ├── ingestion/                      # Ingestion loaders
│   ├── validation/                     # Schema, referential integrity & range validation
│   ├── pipeline.py                     # Phase 1 Pipeline CLI orchestrator
│   ├── analytics/                      # Phase 2 Business Intelligence Engine
│   │   ├── analytics_engine.py         # Master orchestrator for all analytical domains
│   │   ├── sales_analytics.py          # Sales KPIs, daily sales, period comparisons
│   │   ├── customer_analytics.py       # Customer KPIs, RFM scores, retention cohorts
│   │   ├── product_analytics.py        # Product matrix, Pareto 80/20, velocity
│   │   ├── category_analytics.py       # Category summaries & margin contributions
│   │   ├── time_analytics.py           # Hourly patterns, weekday vs weekend, peak hours
│   │   ├── payment_analytics.py        # UPI vs Cash volume & order value breakdown
│   │   ├── context_analytics.py        # Festival uplift & weather impact correlations
│   │   ├── trend_analytics.py          # Trend classification & IQR anomaly detection
│   │   └── merchant_analytics.py       # Single-merchant profile & performance cards
│   ├── reporting/                      # Automated Markdown & JSON summary report generators
│   └── schemas/                        # Typed Pydantic schemas for analytics entities
├── tests/                              # Pytest test suite (37 unit & integration tests)
├── pytest.ini                          # Pytest configurations
├── requirements.txt                    # Project dependencies
└── README.md
```

---

## 3. Quick Start

### Installation

```bash
git clone https://github.com/atleekumaar/VyaparMitra.git
cd VyaparMitra
pip install -r requirements.txt
```

### Running Phase 1 (Data Foundation & Feature Store)

```bash
python -m src.pipeline
```

Sample output:
```text
============================================================
VYAPARMITRA PHASE 1 EXECUTION SUMMARY
============================================================
Clean Transactions: 9,995
Quarantined Records: 5
Merchants in Feature Store: 50
Customers in Feature Store: 3,308
Products in Feature Store: 64
Daily Time-Window Records: 358
Overall Quality Status: PASS
============================================================
```

### Running Phase 2 (Business Intelligence & Analytics Engine)

```bash
python -m src.analytics
```

Sample output:
```text
============================================================
VYAPARMITRA PHASE 2 EXECUTION SUMMARY
============================================================
Elapsed Time: 0.89 seconds
Analytics Output Directory: data/analytics
Marts Generated: 9 Analytical Domains
Executive Report: data/analytics/reports/executive_summary.md
Status: SUCCESS
============================================================
```

---

## 4. Key Capabilities

### Phase 1: Data Foundation
- **Non-Destructive Quarantine**: Corrupt records (invalid discounts, negative prices, dangling foreign keys) are isolated in `data/quarantine/` with explicit rejection reasons rather than silently dropped.
- **Strict Anti-Leakage Feature Store**: Daily aggregations compute 7-day trailing rolling statistics using only historical observations ($T-7$ to $T-1$) with zero future lookahead.
- **Context Integration**: Enriches transactions with multi-festival calendars (supporting multiple concurrent festivals) and daily city meteorological observations with graceful fallback imputation.

### Phase 2: Business Intelligence
- **Sales & Revenue Dynamics**: Total revenue, orders, units, average order value (AOV), growth rates, and daily revenue curves.
- **RFM Customer Segmentation**: Scores customers on Recency, Frequency, and Monetary dimensions (1–5) and assigns segments (`Champions`, `Loyal Customers`, `At Risk`, `Hibernating`, `Lost`).
- **Pareto 80/20 Analysis**: Automatically ranks catalog products to isolate the vital 20% driving 80% of store revenue.
- **Payment Method Shares**: Analyzes adoption of UPI, Cash, Cards, and Net Banking, identifying high-ticket payment channels.
- **Festival & Weather Elasticity**: Compares baseline vs. festival sales uplifts and analyzes temperature/rainfall correlations.
- **Trend & Anomaly Detection**: 7-day vs. 30-day moving average velocity classifications (`Strong Growth`, `Moderate Growth`, `Stable`, `Decline`) and IQR anomaly detection on daily volume spikes.

---

## 5. Testing & Verification

The repository includes a comprehensive 37-test suite covering both Phase 1 and Phase 2:

```bash
python -m pytest -v
```

```text
tests/test_analytics_integration.py::test_full_analytics_engine_execution PASSED
tests/test_analytics_integration.py::test_analytics_api_methods PASSED
tests/test_category_analytics.py::test_category_summary_calculation PASSED
tests/test_category_analytics.py::test_category_monthly_slice PASSED
tests/test_cleaning.py::test_quarantine_isolation PASSED
tests/test_cleaning.py::test_merchant_and_customer_cleaning PASSED
tests/test_context_analytics.py::test_festival_comparison_and_sample_sizes PASSED
tests/test_context_analytics.py::test_weather_comparison_and_correlations PASSED
tests/test_customer_analytics.py::test_customer_kpis_calculation PASSED
tests/test_customer_analytics.py::test_customer_rfm_scoring_and_segmentation PASSED
tests/test_customer_analytics.py::test_customer_cohort_matrix PASSED
tests/test_features.py::test_transaction_feature_calculations PASSED
tests/test_features.py::test_merchant_feature_aggregations PASSED
tests/test_features.py::test_customer_feature_aggregations PASSED
tests/test_features.py::test_product_feature_aggregations PASSED
tests/test_features.py::test_festival_merge_and_distances PASSED
tests/test_features.py::test_weather_merge_and_graceful_imputation PASSED
tests/test_features.py::test_daily_time_window_features_no_future_leakage PASSED
tests/test_payment_analytics.py::test_payment_summary_and_shares PASSED
tests/test_pipeline_integration.py::test_full_pipeline_integration PASSED
tests/test_product_analytics.py::test_product_performance_matrix PASSED
tests/test_product_analytics.py::test_product_rankings PASSED
tests/test_product_analytics.py::test_pareto_concentration_analysis PASSED
tests/test_sales_analytics.py::test_core_kpis_calculation PASSED
tests/test_sales_analytics.py::test_period_comparison_growth PASSED
tests/test_sales_analytics.py::test_zero_division_guard PASSED
tests/test_sales_analytics.py::test_daily_sales_analytics PASSED
tests/test_time_analytics.py::test_hourly_analytics PASSED
tests/test_time_analytics.py::test_weekday_analytics PASSED
tests/test_time_analytics.py::test_peak_period_detection PASSED
tests/test_trend_analytics.py::test_trend_classification_and_thresholds PASSED
tests/test_trend_analytics.py::test_iqr_anomaly_detection PASSED
tests/test_validation.py::test_clean_transactions_pass_validation PASSED
tests/test_validation.py::test_duplicate_transaction_detection PASSED
tests/test_validation.py::test_invalid_prices_and_quantities PASSED
tests/test_validation.py::test_referential_integrity_violation PASSED
tests/test_validation.py::test_invalid_discounts PASSED

============================= 37 passed in 4.95s ==============================
```

---

## 6. License & Roadmap

* **Phase 1 (Complete)**: Data Foundation & Merchant Feature Store
* **Phase 2 (Complete)**: Business Intelligence & Analytics Engine
* **Phase 3 (Next)**: Predictive ML Engine (Sales & SKU Demand Forecasting, Customer Churn Risk)
* **Phase 4**: AI Recommendation & Decision Support System
* **Phase 5**: Multilingual Hindi/Hinglish Business Copilot
* **Phase 6**: Merchant Command Center & Dashboard Web Application
