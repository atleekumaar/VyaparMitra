# VyaparMitra — AI-Powered Business Assistant for Small Merchants

> **Phases 1–3: Data Foundation, Business Intelligence & Predictive AI Engine**

VyaparMitra is an intelligent, localized decision-support system designed for small and medium retail merchants across India. This repository contains the complete implementation of:
- **Phase 1: Data Foundation & Merchant Feature Store** — Ingestion, validation, cleaning, quarantine isolation, feature engineering, and temporal feature store.
- **Phase 2: Business Intelligence & Analytics Engine** — Aggregations, metrics, RFM segmentation, Pareto analysis, time & payment patterns, festival/weather contextual analytics, trend classification, and executive reporting.
- **Phase 3: Predictive AI Engine** — Machine learning models for 7-day & 30-day forward sales forecasting, SKU-level demand projections, customer churn risk scoring, and business trend direction classification with strict anti-leakage guards.

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
ANALYTICS ENGINE              PREDICTIVE AI ENGINE
├── Sales & Revenue KPIs      ├── Strict Chronological Splits (70/15/15)
├── RFM Customer Segments     ├── Sales Forecaster (Ridge / LightGBM)
├── Product Pareto 80/20      ├── SKU Demand Forecaster (Poisson / Tweedie)
├── Category Margins          ├── Customer Churn Classifier (Random Forest / GBDT)
├── Hourly & Peak Time        ├── Business Trend Predictor
├── Payment Channels (UPI)    └── Calibrated Uncertainty & Explainability
├── Festival/Weather Context                 │
└── Trends & IQR Anomalies                   ▼
         │                           TRAINED ML MODELS
         ▼                          (Saved in models/)
PHASE 2 ANALYTICS MARTS                      │
 (data/analytics/)                           ▼
                                    PREDICTIONS & FORECASTS
                                    (data/ml/ in Parquet & CSV)
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
│   ├── analytics/                      # Phase 2 Business Intelligence Marts
│   │   ├── sales/                      # Sales KPIs & daily metrics
│   │   ├── customers/                  # RFM segmentations & cohort retention
│   │   ├── products/                   # Performance matrix, rankings, Pareto 80/20
│   │   ├── categories/                 # Category contribution & margins
│   │   ├── time/                       # Hourly distributions & peak shopping windows
│   │   ├── payments/                   # UPI, Cash, Card shares & velocity
│   │   ├── context/                    # Festival lift & weather elasticity
│   │   ├── trends/                     # Rolling trend vectors & IQR anomalies
│   │   └── reports/                    # Executive summaries
│   └── ml/                             # Phase 3 ML Forecasts & Evaluations
│       ├── forecasts/                  # 7-day & 30-day forward sales & SKU demand
│       ├── customer_risk/              # Churn risk tiers & probability distributions
│       ├── trends/                     # Projected business trajectory
│       ├── explainability/             # Feature importance & attribution weights
│       └── reports/                    # Model evaluation & scorecard reports
├── docs/
│   ├── data_dictionary.md              # Phase 1 Feature Store dictionary & leakage rules
│   ├── analytics_architecture.md       # Phase 2 Analytics Engine architecture
│   └── analytics_dictionary.md         # Phase 2 Metric definitions & calculation rules
├── models/                             # Phase 3 Trained ML Artifacts (.joblib & metadata.json)
│   ├── sales/                          # Sales forecaster model & feature transformers
│   ├── demand/                         # SKU-level demand forecasters
│   ├── churn/                          # Customer churn classification model
│   └── trend/                          # Business trend classification model
├── src/
│   ├── cleaning/                       # Data sanitization & quarantine routing
│   ├── data_generation/                # Synthetic data & enriched source normalizer
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
│   ├── ml/                             # Phase 3 Predictive AI Engine
│   │   ├── ml_engine.py                # Master orchestrator for training & inference
│   │   ├── train.py                    # Training CLI script
│   │   ├── predict.py                  # Inference & batch forecasting CLI script
│   │   ├── data/                       # Split orchestrator (chronological train/val/test)
│   │   ├── features/                   # Anti-leakage ML feature transformers
│   │   ├── models/                     # Forecasters, classifiers, baselines
│   │   ├── evaluation/                 # Metrics: WAPE, MAE, RMSE, PR-AUC, F1
│   │   └── inference/                  # Forward rolling prediction pipelines
│   ├── reporting/                      # Markdown & JSON report generators
│   └── schemas/                        # Typed Pydantic schemas (analytics & ML)
├── tests/                              # Pytest test suite (60 unit & integration tests)
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

### Running Phase 2 (Business Intelligence & Analytics Engine)

```bash
python -m src.analytics
```

### Running Phase 3 (Predictive AI Engine)

```bash
# Train ML models with chronological cross-validation
python -m src.ml.train

# Generate forward forecasts and churn risk scores
python -m src.ml.predict
```

Sample output:
```text
============================================================
VYAPARMITRA PHASE 3 ML SUMMARY
============================================================
Sales Forecast: 7-Day Revenue Projected: ₹2,84,500 (WAPE: 11.4%)
SKU Demand: 64 Products Forecasted
Customer Churn: Scored 3,308 Customers (PR-AUC: 0.812)
Business Trend: 7-Day Trajectory -> Moderate Growth
Models Saved: models/ (Sales, Demand, Churn, Trend)
Predictions: data/ml/forecasts/
Status: SUCCESS
============================================================
```

---

## 4. Key Predictive ML Capabilities

- **Strict Anti-Leakage Chronological Splits**: Time-series data is split strictly on chronological boundaries (70% train, 15% validation, 15% out-of-time test). Features strictly use historical windows ($T-k$ where $k \ge 1$) with zero future lookahead.
- **Sales Revenue Forecasting**: Forward 7-day and 30-day store sales forecasts capturing weekly cycles, holiday proximity, and trend velocity.
- **SKU-Level Demand Forecasting**: Granular unit demand projections per product to optimize safety stock and prevent stockouts.
- **Customer Churn Risk Scoring**: Calibrated probabilistic classifier identifying customers at risk of churn before dormancy occurs, enabling proactive retention.
- **Directional Trend Classification**: Multi-class trend trajectory predictor identifying upcoming expansion, stability, or slowdown.

---

## 5. Testing & Verification

The repository includes a comprehensive 60-test suite covering Phases 1, 2, and 3:

```bash
python -m pytest -v
```

```text
tests/test_analytics_integration.py ............ PASSED
tests/test_category_analytics.py ............... PASSED
tests/test_cleaning.py ......................... PASSED
tests/test_context_analytics.py ................ PASSED
tests/test_customer_analytics.py ............... PASSED
tests/test_features.py ......................... PASSED
tests/test_ml_evaluation.py .................... PASSED
tests/test_ml_features.py ...................... PASSED
tests/test_ml_integration.py ................... PASSED
tests/test_ml_leakage.py ....................... PASSED
tests/test_ml_models.py ........................ PASSED
tests/test_ml_split.py ......................... PASSED
tests/test_payment_analytics.py ................ PASSED
tests/test_pipeline_integration.py ............. PASSED
tests/test_product_analytics.py ................ PASSED
tests/test_sales_analytics.py .................. PASSED
tests/test_time_analytics.py ................... PASSED
tests/test_trend_analytics.py .................. PASSED
tests/test_validation.py ....................... PASSED

===================== 60 passed, 0 failed in 14.83s =====================
```

---

## 6. License & Roadmap

* **Phase 1 (Complete)**: Data Foundation & Merchant Feature Store
* **Phase 2 (Complete)**: Business Intelligence & Analytics Engine
* **Phase 3 (Complete)**: Predictive AI Engine (Sales & SKU Demand Forecasting, Customer Churn Risk)
* **Phase 4 (Next)**: AI Recommendation & Decision Support System
* **Phase 5**: Multilingual Hindi/Hinglish Business Copilot
* **Phase 6**: Merchant Command Center & Dashboard Web Application
