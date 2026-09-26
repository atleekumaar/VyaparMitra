# VyaparMitra — AI-Powered Business Assistant for Small Merchants

> **Phases 1–4: Data Foundation, Business Intelligence, Predictive AI & Decision Engine**

VyaparMitra is an intelligent, localized decision-support system designed for small and medium retail merchants across India. This repository contains the complete implementation of:
- **Phase 1: Data Foundation & Merchant Feature Store** — Ingestion, validation, cleaning, quarantine isolation, feature engineering, and temporal feature store.
- **Phase 2: Business Intelligence & Analytics Engine** — Aggregations, metrics, RFM segmentation, Pareto analysis, time & payment patterns, festival/weather contextual analytics, trend classification, and executive reporting.
- **Phase 3: Predictive AI Engine** — Machine learning models for 7-day & 30-day forward sales forecasting, SKU-level demand projections, customer churn risk scoring, and business trend direction classification.
- **Phase 4: AI Recommendation & Decision Engine** — Prescriptive action generator providing high-impact, transparent, 6-part evidence-backed decisions across Inventory, Pricing, Customer Retention, and Product Cross-Selling with priority scoring and conflict resolution.

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
├── Sales & Revenue KPIs      ├── Chronological Splits (70/15/15)
├── RFM Customer Segments     ├── Sales Forecaster (Ridge / LightGBM)
├── Product Pareto 80/20      ├── SKU Demand Forecaster (Poisson / Tweedie)
├── Category Margins          ├── Customer Churn Classifier
├── Hourly & Peak Time        ├── Business Trend Predictor
├── Payment Channels (UPI)    └── Calibrated Uncertainty
├── Festival/Weather Context                 │
└── Trends & IQR Anomalies                   ▼
         │                          TRAINED ML MODELS
         ▼                         (Saved in models/)
PHASE 2 ANALYTICS MARTS                      │
 (data/analytics/)                           ▼
         │                          PREDICTIONS & FORECASTS
         │                          (data/ml/)
         │                                   │
         └─────────────────┬─────────────────┘
                           │
                           ▼
          PHASE 4: AI RECOMMENDATION ENGINE
          ├── Inventory Optimization (Safety Stock, ROP, Stockout Risk)
          ├── Pricing & Margin Protection (Deadstock Discount, Surge Pricing)
          ├── Customer Retention (Churn Prevention, VIP Loyalty Rewards)
          ├── Product Strategies (Star Product Focus, Affinity Cross-Sell)
          ├── Multi-Factor Priority Scoring (Impact, Urgency, Confidence)
          ├── Deduplication & Conflict Resolution (Margin > Growth)
          └── 6-Part Transparent Evidence Generation
                           │
                           ▼
          RECOMMENDATION MARTS & ACTION PLANS
          (data/recommendations/ in Parquet & CSV)
```

---

## 2. Repository Structure

```text
VyaparMitra/
├── configs/
│   ├── config.yaml                     # Pipeline parameters, paths, thresholds, seeds
│   └── recommendations.yaml            # Decision rules, priority weights, guardrails
├── data/
│   ├── raw/                            # Ingested dimension & fact tables
│   ├── processed/                      # Sanitized clean tables
│   ├── quarantine/                     # Quarantined invalid records with rejection reasons
│   ├── quality_reports/                # Automated validation reports (JSON & Markdown)
│   ├── features/                       # Phase 1 Feature Store (5 Parquet & CSV datasets)
│   ├── analytics/                      # Phase 2 Business Intelligence Marts (9 domains)
│   ├── ml/                             # Phase 3 ML Forecasts & Evaluations
│   └── recommendations/                # Phase 4 Prescriptive Actions & Action Plans
│       ├── all_recommendations.parquet # Unified priority-ranked recommendation table
│       ├── inventory_recommendations.parquet # Safety stock, reorder quantities
│       ├── pricing_recommendations.parquet   # Targeted discounts, surge prices
│       ├── customer_recommendations.parquet  # Retention & loyalty actions
│       ├── cross_sell_recommendations.parquet # Frequently bought together bundles
│       ├── recommendation_evidence.parquet  # 6-part transparent audit evidence
│       └── daily_action_plan.md        # Merchant-facing morning action briefing
├── docs/
│   ├── data_dictionary.md              # Phase 1 Feature Store dictionary & leakage rules
│   ├── analytics_architecture.md       # Phase 2 Analytics Engine architecture
│   ├── analytics_dictionary.md         # Phase 2 Metric definitions & calculation rules
│   └── phase4_recommendation_engine.md # Phase 4 Decision logic & priority algorithms
├── models/                             # Phase 3 Trained ML Artifacts (.joblib & metadata.json)
├── src/
│   ├── cleaning/                       # Data sanitization & quarantine routing
│   ├── data_generation/                # Synthetic data & enriched source normalizer
│   ├── features/                       # Multi-scale temporal & contextual feature extractors
│   ├── ingestion/                      # Ingestion loaders
│   ├── validation/                     # Schema, referential integrity & range validation
│   ├── pipeline.py                     # Phase 1 Pipeline CLI orchestrator
│   ├── analytics/                      # Phase 2 Business Intelligence Engine
│   ├── ml/                             # Phase 3 Predictive AI Engine
│   ├── recommendations/                # Phase 4 AI Decision & Recommendation Engine
│   │   ├── recommendation_engine.py    # Master engine orchestrator
│   │   ├── config.py                   # Rule weights & threshold loaders
│   │   ├── schemas.py                  # Pydantic schemas for actions & evidence
│   │   ├── inventory/                  # Reorder points, safety stock & stockout logic
│   │   ├── pricing/                    # Clearance, festival & bundle discount rules
│   │   ├── customers/                  # Churn retention & high-value customer actions
│   │   ├── products/                   # Star product promotions & slow-mover liquidation
│   │   ├── cross_sell/                 # Market basket affinity & pair recommendations
│   │   ├── scoring/                    # Multi-objective priority scoring & ranking
│   │   ├── deduplication/              # Action deduplication and frequency limiting
│   │   ├── conflicts/                  # Conflict resolution (Margin preservation > Volume)
│   │   └── explanations/               # 6-part evidence generator
│   ├── reporting/                      # Markdown & JSON report generators
│   └── schemas/                        # Typed Pydantic schemas (analytics & ML)
├── tests/                              # Pytest test suite (78 unit & integration tests)
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
python -m src.ml.train
python -m src.ml.predict
```

### Running Phase 4 (AI Recommendation & Decision Engine)
```bash
python -m src.recommendations
```

Sample output:
```text
============================================================
VYAPARMITRA PHASE 4 RECOMMENDATION SUMMARY
============================================================
Inventory Actions: 14 Restock Orders Recommended
Pricing Actions: 8 Dynamic Discounts / Bundle Offers
Customer Actions: 22 At-Risk Customer Interventions
Cross-Sell Bundles: 12 High-Affinity Product Pairs
Prioritized Actions: Top 5 Actions Ranked for Merchant M001
Daily Action Plan: data/recommendations/daily_action_plan.md
Status: SUCCESS
============================================================
```

---

## 4. 6-Part Transparent Evidence Framework

Every recommendation generated by VyaparMitra is backed by a verifiable 6-part evidence trail:

1. **Current Metric**: Real-time KPI from Phase 2 BI (e.g., current stock: 3 units).
2. **Context**: Operational context (e.g., festival in 4 days, lead time: 3 days).
3. **Prediction**: Phase 3 ML forecast (e.g., predicted 7-day demand: 28 units).
4. **Business Impact**: Quantified financial outcome (e.g., prevent ₹4,200 revenue loss).
5. **Confidence Score**: Calibrated probability (e.g., 91% model confidence).
6. **Action Plan**: Exact operational steps (e.g., order 25 units from Supplier S01 today).

---

## 5. Testing & Verification

The repository includes a comprehensive 78-test suite covering Phases 1, 2, 3, and 4:

```bash
python -m pytest -v
```

```text
tests/test_analytics_integration.py ............ PASSED
tests/test_category_analytics.py ............... PASSED
tests/test_cleaning.py ......................... PASSED
tests/test_conflicts.py ........................ PASSED
tests/test_context_analytics.py ................ PASSED
tests/test_cross_sell.py ....................... PASSED
tests/test_customer_actions.py ................. PASSED
tests/test_customer_analytics.py ............... PASSED
tests/test_deduplication.py .................... PASSED
tests/test_explanations.py ..................... PASSED
tests/test_features.py ......................... PASSED
tests/test_inventory.py ........................ PASSED
tests/test_ml_evaluation.py .................... PASSED
tests/test_ml_features.py ...................... PASSED
tests/test_ml_integration.py ................... PASSED
tests/test_ml_leakage.py ....................... PASSED
tests/test_ml_models.py ........................ PASSED
tests/test_ml_split.py ......................... PASSED
tests/test_payment_analytics.py ................ PASSED
tests/test_pipeline_integration.py ............. PASSED
tests/test_pricing.py .......................... PASSED
tests/test_priority.py ......................... PASSED
tests/test_product_actions.py .................. PASSED
tests/test_product_analytics.py ................ PASSED
tests/test_recommendation_integration.py ....... PASSED
tests/test_recommendation_schemas.py ........... PASSED
tests/test_sales_analytics.py .................. PASSED
tests/test_time_analytics.py ................... PASSED
tests/test_trend_analytics.py .................. PASSED
tests/test_validation.py ....................... PASSED

===================== 78 passed, 0 failed in 13.37s =====================
```

---

## 6. Roadmap

* **Phase 1 (Complete)**: Data Foundation & Merchant Feature Store
* **Phase 2 (Complete)**: Business Intelligence & Analytics Engine
* **Phase 3 (Complete)**: Predictive AI Engine
* **Phase 4 (Complete)**: AI Recommendation & Decision Support System
* **Phase 5 (Next)**: Multilingual Hindi/Hinglish Business Copilot
* **Phase 6**: Merchant Command Center & Dashboard Web Application
