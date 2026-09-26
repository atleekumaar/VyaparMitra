# VyaparMitra — Phase 4: AI Recommendation & Decision Engine Implementation Report

## 1. Executive Summary

Phase 4 completes the transformation of **VyaparMitra** from a predictive machine learning system into an **Actionable AI Decision Engine**. By synthesizing Phase 1 feature stores, Phase 2 business intelligence analytics, and Phase 3 machine learning forecasts, Phase 4 answers:

> **"Given what happened and what is predicted to happen, what should the merchant do next?"**

The system does NOT train new speculative models. Instead, it introduces a robust, deterministic decision layer comprising:
1. **Six Interlocking Recommendation Systems** (Inventory, Sales Opportunities, Customer Retention, Cross-Sell Affinities, Pricing & Margin Defense, and a Unified Daily Action Plan).
2. **Multi-Criteria Prioritization Scoring** (combining Revenue Opportunity, Margin Opportunity, Customer Value, Prediction Confidence, Data Quality, and Urgency).
3. **Conflict Resolution Hierarchy** (`DATA_QUALITY > RISK > MARGIN_PROTECTION > REVENUE_GROWTH > EXPERIMENTAL_ACTION`).
4. **Deduplication & Consolidated Evidence Extraction**.
5. **Observational Guardrails** (Explicit inventory estimation layer; non-causal association rule framing).

The system achieved a **100% pass rate across all 78 tests** (60 Phase 1–3 regression tests + 18 new Phase 4 tests) with zero test regressions.

---

## 2. Architecture & Data Flow

```text
PHASE 1: FEATURE STORE
  ├── daily_features.parquet
  ├── product_features.parquet
  ├── customer_features.parquet
  └── clean_transactions.parquet
            │
PHASE 2: BUSINESS INTELLIGENCE
  ├── customer_segments.parquet (RFM & Recency)
  ├── product_rankings.parquet
  └── sales_daily.parquet
            │
PHASE 3: PREDICTIVE AI
  ├── sales_forecast_7d.parquet
  ├── product_demand_forecast_7d.parquet
  ├── customer_risk_scores.parquet
  └── business_trend_predictions.parquet
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│             PHASE 4: DECISION & RECOMMENDATION ENGINE       │
│                                                             │
│   ┌─────────────────────┐       ┌──────────────────────┐    │
│   │ Inventory Restock   │       │ Sales Opportunities  │    │
│   └──────────┬──────────┘       └──────────┬───────────┘    │
│              │                             │                │
│   ┌──────────┴──────────┐       ┌──────────┴───────────┐    │
│   │ Customer Retention  │       │ Cross-Sell Affinities│    │
│   └──────────┬──────────┘       └──────────┬───────────┘    │
│              │                             │                │
│              └──────────────┬──────────────┘                │
│                             ▼                               │
│              ┌─────────────────────────────┐                │
│              │  Pricing & Margin Defense   │                │
│              └──────────────┬──────────────┘                │
│                             ▼                               │
│              ┌─────────────────────────────┐                │
│              │   Multi-Criteria Scoring    │                │
│              │ Impact • Confidence • Urg   │                │
│              └──────────────┬──────────────┘                │
│                             ▼                               │
│              ┌─────────────────────────────┐                │
│              │ Conflict Resolution & Dedupe│                │
│              └──────────────┬──────────────┘                │
│                             ▼                               │
│              ┌─────────────────────────────┐                │
│              │   Prioritized Action Plan   │                │
│              └─────────────────────────────┘                │
└─────────────────────────────┬───────────────────────────────┘
                              ▼
                      OUTPUT ARTIFACTS
       data/recommendations/*.parquet, *.csv, *.md
```

---

## 3. Recommendation Systems Implemented

### System 1: Inventory & Restock Engine
- **Objective**: Identifies catalog products requiring reorder coverage to protect against stockouts.
- **Formulas**:
  - Safety Stock: $SS = Z \times \sigma_D \times \sqrt{L}$ ($Z=1.645$, $L=3$ lead time days).
  - Reorder Point: $ROP = (V_D \times L) + SS$.
  - Batch Quantity: $Q = \max(5, \lceil D_{7d} + SS \rceil)$.
- **Status**: Operates in `inventory_estimation_mode = True`, explicitly reporting that guidance derives from 7-day forecast demand ($D_{7d}$) and historical daily demand variance rather than fabricated warehouse stock counts.

### System 2: Sales Opportunity Engine
- **Objective**: Maximizes revenue capture across commercial SKU tiers.
- **Classification**:
  - `STAR` (Top 25% revenue + high forecast demand) $\to$ `FOCUS` action.
  - `HIGH_MARGIN_SLEEPER` (Above-median margin + moderate velocity) $\to$ `PROMOTE` action.
  - `UNDERPERFORMER` (Bottom 25% revenue + low forecast demand) $\to$ `BUNDLE` (if margin allows) or `MONITOR`.

### System 3: Customer Retention Engine
- **Objective**: Identifies high-value customers exhibiting churn signals and triggers retention outreach.
- **Segmentation**:
  - `HIGH_VALUE_HIGH_RISK` $\to$ `RETENTION` (top 25% spenders with $\ge 60\%$ churn risk).
  - `HIGH_VALUE_LOW_RISK` $\to$ `PERSONALIZED_OFFER`.
  - `LOW_VALUE_HIGH_RISK` $\to$ `RE_ENGAGEMENT`.
  - `NEW_CUSTOMER` $\to$ `PRODUCT_REMINDER`.
- **Safeguard**: Explicitly framed as decision support; avoids claims of guaranteed causal retention.

### System 4: Cross-Sell & Market Basket Engine
- **Objective**: Identifies high-lift product affinities from customer co-purchasing histories.
- **Metrics**: Support $\ge 0.005$, Confidence $\ge 0.08$, Lift $\ge 1.15$.
- **Action**: Generates checkout bundling suggestions with empirical lift multipliers.

### System 5: Pricing & Margin Defense Engine
- **Objective**: Protects profit margins against discount erosion and mispricing.
- **Rules**:
  - High Demand + High Margin $\to$ `MAINTAIN_PRICE` (defend price point).
  - High Demand + Low Margin $\to$ `REVIEW_MARGIN` (supplier cost renegotiation).
  - Low Demand + High Margin $\to$ `PROMOTE` (controlled incentive).
  - Low Demand + Low Margin $\to$ `CLEARANCE` (working capital release).
  - Average Discount $> 15\%$ $\to$ `LIMIT_DISCOUNT`.

### System 6: Merchant Action Prioritizer & Daily Action Plan
- **Objective**: Blends all recommendations into a unified, conflict-free daily action plan ranked by Priority Score.

---

## 4. Recommendation Counts & Subsystem Breakdown

| Subsystem | Primary Action Types | Count Generated |
|---|---|---|
| **Inventory Recommendations** | `RESTOCK` | 64 |
| **Sales Opportunities** | `FOCUS`, `PROMOTE`, `BUNDLE`, `MONITOR` | 29 |
| **Customer Retention** | `RETENTION` (Top High-Value At-Risk) | 100 |
| **Cross-Sell Affinities** | `CROSS_SELL` | 34 |
| **Pricing & Margin Defense** | `MAINTAIN_PRICE`, `REVIEW_MARGIN`, `LIMIT_DISCOUNT`, `CLEARANCE` | 49 |
| **Total Consolidated Recommendations** | **All Subsystems** | **270** |

---

## 5. Priority Distribution

Priority scores are calculated via normalized geometric mean:
$$\text{Priority} = (\text{Impact} \times \text{Confidence} \times \text{Urgency})^{1/3}$$

Assigned to categorical bands using calibrated thresholds:
- **🔴 CRITICAL** ($\ge 0.79$): **23 recommendations** (urgent retention of top spenders and high-velocity restocks).
- **🟠 HIGH** ($0.70 - 0.78$): **132 recommendations** (standard reorders, star product focus, margin defense).
- **🟡 MEDIUM** ($0.55 - 0.69$): **80 recommendations** (cross-sells, promotional candidates, selective re-engagements).
- **🟢 LOW** ($< 0.55$): **35 recommendations** (low-velocity monitoring and clearance candidates).

---

## 6. Subsystem Deep-Dive Statistics

### Cross-Sell Statistics
- **Candidate Product Pairs Evaluated**: 2,016 pairs
- **Valid Association Rules Retained**: 34 rules
- **Minimum Lift**: 1.150
- **Average Lift**: 1.407
- **Maximum Lift**: 1.988
- **Average Confidence**: 17.8%

### Inventory Statistics
- **Product SKUs Analyzed**: 64 products
- **Restock Candidates Generated**: 64 recommendations
- **Average 7-Day Forecast Demand**: 3.6 units/SKU (ranging up to 18.2 units)
- **Average Statistical Safety Stock**: 4.1 units
- **Inventory Estimation Mode Usage**: 100% (clearly labeled without fabricated warehouse counts)

### Customer Retention Statistics
- **Total Customers in Risk Assessment**: 3,146 customers
- **High-Risk Customers Identified ($\ge 60\%$)**: 267 customers
- **Retention Recommendations Generated**: 100 prioritized VIP customers
- **Average Inactivity Period**: 42.8 days
- **Average Lifetime Spend of Target Customers**: ₹12,480.50

---

## 7. Representative Recommendation Examples

### Example 1: Critical Customer Retention
```text
WHAT: High-Value Customer Retention: Customer_C03388 (C03388) (RETENTION)
WHY: Customer is in the top 25% of spenders (Total: ₹24,810.20, 8 orders), but has been inactive for 48 days with an estimated churn/inactivity risk of 95.0%.
EVIDENCE:
  • churn_risk_probability = 0.95 (Inactivity likelihood within next 30 days (95.0%)) [Source: Phase 3 Churn Model]
  • customer_recency_days = 48.0 (Elapsed days since last recorded purchase) [Source: Phase 2 Customer Analytics]
  • customer_total_spend = 24810.2 (Lifetime gross spend) [Source: Phase 1 Feature Store]
  • customer_order_count = 8 (Total historical transactions placed) [Source: Phase 1 Feature Store]
  • average_order_value = 3101.28 (Average transaction basket value) [Source: Phase 1 Feature Store]
CONFIDENCE: 0.89
URGENCY: 0.93
EXPECTED IMPACT: 0.75
PRIORITY: 0.85 [CRITICAL]
```

### Example 2: Inventory Restock with Safety Stock
```text
WHAT: Restock Casual Cotton T-Shirt (Apparel) (RESTOCK)
WHY: Projected 7-day demand is 14 units with daily velocity of 2.0 units/day. With an estimated 3-day supplier lead time, initiating a reorder of 21 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).
EVIDENCE:
  • forecast_7d_units = 14.2 (Expected 7-day customer unit demand) [Source: Phase 3 Demand Model]
  • daily_demand_velocity = 2.03 (Forecasted units per day) [Source: Phase 3 Demand Model]
  • safety_stock_units = 6.42 (Z=1.645 safety buffer for 95% service level) [Source: Statistical Formula]
  • reorder_point_units = 12.51 (Trigger threshold across 3 days lead time) [Source: Statistical Formula]
  • unit_margin = 420.0 (Unit profit ₹420.00 (45% margin)) [Source: Product Catalog]
  • inventory_estimation_mode = True (Recommendation based on forecast demand and historical velocity) [Source: System Configuration]
CONFIDENCE: 0.84
URGENCY: 0.78
EXPECTED IMPACT: 0.72
PRIORITY: 0.78 [HIGH]
```

### Example 3: Cross-Sell Basket Affinity
```text
WHAT: Cross-Sell Pair: PRD_ART_02 -> PRD_SNK_01 (CROSS_SELL)
WHY: Historical transaction affinity shows that customers purchasing PRD_ART_02 have a 24.8% probability of buying PRD_SNK_01 (Lift = 1.39x across 33 customers). Note: This is an observed co-occurrence pattern, not a causal guarantee.
EVIDENCE:
  • association_lift = 1.39 (Purchasing PRD_ART_02 multiplies odds of purchasing PRD_SNK_01 by 1.39x) [Source: Association Rule Mining]
  • rule_confidence = 0.2481 (24.8% of PRD_ART_02 buyers also ordered PRD_SNK_01) [Source: Association Rule Mining]
  • rule_support = 0.0100 (Observed across 1.00% of customer shopping journeys) [Source: Association Rule Mining]
  • shared_transaction_count = 33 (Co-purchased by 33 verified customers) [Source: Historical Transactions]
CONFIDENCE: 0.81
URGENCY: 0.55
EXPECTED IMPACT: 0.62
PRIORITY: 0.65 [MEDIUM]
```

---

## 8. Test Suite Verification

```text
===================== 78 passed, 1328 warnings in 27.33s ======================
```

- **Phase 1 & 2 Regressions**: 37 tests (data validation, cleaning, feature store, sales KPIs, customer cohorts, time patterns, anomaly detection) — **100% PASS**.
- **Phase 3 ML Regressions**: 23 tests (chronological split, no-leakage shifts, forecasting baselines, classifier gates, backtesting, integration) — **100% PASS**.
- **Phase 4 New Tests**: 18 tests (`test_recommendation_schemas.py`, `test_inventory.py`, `test_customer_actions.py`, `test_product_actions.py`, `test_cross_sell.py`, `test_pricing.py`, `test_priority.py`, `test_conflicts.py`, `test_deduplication.py`, `test_explanations.py`, `test_recommendation_integration.py`) — **100% PASS**.
- **Total Test Suite**: **78/78 Passed**.

---

## 9. Performance & Execution Runtime

- **End-to-End Pipeline Execution Time**: ~1.85 seconds
- **Full Test Suite Runtime (78 tests)**: 27.33 seconds
- **Computational Complexity**: All basket co-occurrences and customer grouping algorithms execute via vectorized Pandas aggregations ($O(N \log N)$ or grouped hashing) avoiding costly nested loops.

---

## 10. Known Limitations & Future Phase 5 Handoff

1. **Synthetic Data**: Upstream features and transactions are generated synthetically; underlying behavioral dynamics reflect generated distributions.
2. **Absence of Real Warehouse Telemetry**: Real inventory levels are unobserved in the POS dataset. The system honestly applies `inventory_estimation_mode = True`.
3. **Observational vs Causal**: Cross-sell and pricing recommendations reflect observed historical affinities and heuristics, not controlled A/B experiment outcomes.
4. **Handoff to Phase 5 (Hindi NLP / LLM Copilot)**: Phase 5 can directly consume `data/recommendations/daily_action_plan.md` and `all_recommendations.parquet` to power conversational Hindi explanations, merchant Q&A, and interactive voice walkthroughs.

---

## 11. Command Reference

```powershell
# 1. Run all 78 tests across Phases 1, 2, 3, and 4
python -m pytest -v

# 2. Run Phase 4 recommendation pipeline & export all artifacts
python -m src.recommendations --all

# 3. View Daily Merchant Action Plan
python -m src.recommendations --action-plan

# 4. Target individual subsystems
python -m src.recommendations --inventory
python -m src.recommendations --customers
python -m src.recommendations --products
python -m src.recommendations --cross-sell
python -m src.recommendations --pricing
```
