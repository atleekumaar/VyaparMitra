# VyaparMitra Analytics Architecture (Phase 2)

This document details the architectural layout, data flow, immutability constraints, and design patterns governing **Phase 2: Business Intelligence & Analytics Engine**.

---

## 1. High-Level System Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                 PHASE 1: FEATURE STORE                      │
│                   (Immutable Inputs)                        │
├─────────────────────────────────────────────────────────────┤
│ • transaction_features.parquet (9,995 rows)                 │
│ • merchant_features.parquet    (50 rows)                    │
│ • customer_features.parquet    (3,308 rows)                 │
│ • product_features.parquet     (64 rows)                    │
│ • daily_features.parquet       (358 rows)                   │
└──────────────────────────────┬──────────────────────────────┘
                               │ (Read-Only)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│               PHASE 2: ANALYTICS ENGINE                     │
│               (Descriptive & Diagnostic)                    │
├──────────────────────────────┬──────────────────────────────┤
│ Core Analytics Modules:      │ Reporting & Insights:        │
│ • SalesAnalytics             │ • SummaryGenerator (JSON)    │
│ • CustomerAnalytics (RFM)    │ • ReportGenerator (Markdown) │
│ • ProductAnalytics (Pareto)  │                              │
│ • CategoryAnalytics          │ Orchestration:               │
│ • TimeAnalytics (Peaks)      │ • AnalyticsEngine Facade     │
│ • PaymentAnalytics           │ • Strict Output Validation   │
│ • MerchantAnalytics (Peer)   │ • Exact Phase 1 Reconcile    │
│ • ContextAnalytics           │                              │
│ • TrendAnalytics (IQR Outlier│                              │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 ANALYTICS DATA MART                         │
│                  (data/analytics/)                          │
├─────────────────────────────────────────────────────────────┤
│ Sales:      sales_summary, sales_daily, weekly, monthly     │
│ Customers:  customer_summary, customer_segments, cohorts    │
│ Products:   product_summary, product_rankings               │
│ Categories: category_summary, category_monthly              │
│ Time:       time_hourly, time_weekday, time_monthly         │
│ Payments:   payment_summary                                 │
│ Merchants:  merchant_summary, merchant_benchmarks           │
│ Context:    festival_analysis, weather_analysis             │
│ Trends:     trend_analysis, anomaly_analysis                │
│ Reports:    business_summary.json, business_summary.md      │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
                Phase 3: Predictive ML Engine
```

---

## 2. Core Architectural Principles

### 1. Strict Immutability of Phase 1 Data
Phase 2 treats all files under `data/raw/`, `data/processed/`, and `data/features/` as strictly read-only. Analytical artifacts are persisted exclusively into `data/analytics/` and its domain-specific subdirectories.

### 2. Descriptive vs. Prescriptive Boundary
Phase 2 answers **"What happened?"** and **"Where/Why did it happen?"**.
* **Permitted**: Observational insights, moving averages, percentile rankings, RFM behavioral scoring, weather/festival correlation analysis.
* **Prohibited**: Prescriptive recommendations ("You should discount SKU X"), demand forecasts, churn predictions, or autonomous agent decision loops (reserved for Phase 3 and Phase 4).

### 3. Strongly Typed Schemas & Zero-Division Safety
All analytical records conform to Pydantic models defined in `src/schemas/analytics_schema.py`. Every ratio and percentage change calculation uses `.clip(lower=1e-9)` or safe denominator checks to ensure mathematical stability under sparse transaction slices.

### 4. Automated Quality Validation & Reconciliation
Every execution of `AnalyticsEngine.run_all_analytics()` automatically verifies:
1. **Reconciliation**: Phase 2 aggregate revenue exactly equals Phase 1 net revenue (₹15,510,039.34), and Phase 2 total order count equals Phase 1 transaction count (9,995).
2. **Quality Validation**: Non-negativity across all financial metrics and consistency of shares (summing to approximately $1.0$).
