# VyaparMitra — Phase 4: AI Recommendation & Decision Engine Documentation

## 1. System Architecture

The **Phase 4 Recommendation & Decision Engine** bridges predictive AI models and real-world merchant action. It ingests Phase 1 feature tables, Phase 2 analytics data marts, and Phase 3 predictive outputs, passing them through deterministic domain rules, multi-criteria scoring, conflict resolution, and deduplication.

```text
┌───────────────────────────┐    ┌───────────────────────────┐    ┌───────────────────────────┐
│     Phase 1 Features      │    │     Phase 2 Analytics     │    │   Phase 3 ML Predictions  │
│ (Products, Customers, Tx) │    │ (Segments, RFM, Rankings) │    │  (Sales, Demand, Churn)   │
└─────────────┬─────────────┘    └─────────────┬─────────────┘    └─────────────┬─────────────┘
              │                                │                                │
              └────────────────────────┬───────┴────────────────────────────────┘
                                       ▼
                     ┌───────────────────────────────────┐
                     │   Phase 4 Subsystem Evaluators    │
                     │  • Inventory & Restock Engine     │
                     │  • Sales Opportunities Engine     │
                     │  • Customer Retention Engine      │
                     │  • Cross-Sell Association Engine  │
                     │  • Pricing & Margin Engine        │
                     └─────────────────┬─────────────────┘
                                       ▼
                     ┌───────────────────────────────────┐
                     │  Multi-Criteria Scoring Engine    │
                     │  • Impact (Rev, Margin, Scale)    │
                     │  • Confidence (Data, Pred, Evid)  │
                     │  • Urgency & Priority Bands       │
                     └─────────────────┬─────────────────┘
                                       ▼
                     ┌───────────────────────────────────┐
                     │  Conflict Resolution & Dedupe     │
                     │  Data Qual > Risk > Margin > Rev  │
                     └─────────────────┬─────────────────┘
                                       ▼
                     ┌───────────────────────────────────┐
                     │ Actionable Decision Artifacts     │
                     │  • Top Daily Merchant Action Plan │
                     │  • Parquet Data Marts + Markdown  │
                     └───────────────────────────────────┘
```

---

## 2. Recommendation Subsystems

### System 1: Inventory & Restock Engine
- **Objective**: Identify which product SKUs require reordering to prevent costly stockouts.
- **Safety Stock Formula**:
  $$SS = Z \times \sigma_D \times \sqrt{L}$$
  where $Z = 1.645$ (95% service level), $L = 3$ days supplier lead time, and $\sigma_D$ is daily demand standard deviation.
- **Reorder Point (ROP)**:
  $$ROP = (V_D \times L) + SS$$
- **Inventory Estimation Mode**: Live warehouse telemetry is absent. The system explicitly declares `inventory_estimation_mode = True`, grounding advice on forward 7-day predicted demand and sales velocity without fabricating inventory counts.

### System 2: Sales Opportunity Engine
- **Objective**: Pinpoint where merchants can capture additional revenue.
- **SKU Tiers**:
  - `STAR`: Top-quartile revenue with high forward demand $\to$ `FOCUS` action.
  - `HIGH_MARGIN_SLEEPER`: Top-half profit margins with moderate velocity $\to$ `PROMOTE` action.
  - `UNDERPERFORMER`: Low revenue with slow velocity $\to$ `BUNDLE` (if margin allows) or `MONITOR`.

### System 3: Customer Retention Engine
- **Objective**: Prevent merchant churn and re-engage dormant high-value customers.
- **Decision Logic**:
  - `HIGH_VALUE_HIGH_RISK`: Churn risk $\ge 60\%$ in top 25% lifetime spend $\to$ `RETENTION` (urgent personalized outreach).
  - `HIGH_VALUE_LOW_RISK`: Active loyal VIPs $\to$ `PERSONALIZED_OFFER`.
  - `LOW_VALUE_HIGH_RISK`: At-risk lower-frequency accounts $\to$ `RE_ENGAGEMENT`.
  - `NEW_CUSTOMER`: Inactive after 1-2 orders $\to$ `PRODUCT_REMINDER`.

### System 4: Market Basket & Cross-Sell Engine
- **Objective**: Discover high-lift product affinities to expand average transaction size.
- **Association Metrics**:
  - $\text{Support}(A \to B) = \frac{\text{Baskets}(A \cap B)}{N_{\text{total}}}$
  - $\text{Confidence}(A \to B) = \frac{\text{Baskets}(A \cap B)}{\text{Baskets}(A)}$
  - $\text{Lift}(A \to B) = \frac{\text{Support}(A \to B)}{\text{Support}(A) \times \text{Support}(B)}$
- **Filtering**: Minimum support $0.005$, minimum confidence $0.08$, minimum lift $1.15$.
- **Safeguard**: Affinities denote observational co-occurrence patterns, avoiding false causal guarantees.

### System 5: Pricing & Margin Defense Engine
- **Objective**: Protect gross margin and prevent discount dilution.
- **Decision Matrix**:
  - High Demand + High Margin $\to$ `MAINTAIN_PRICE` (protect pricing power).
  - High Demand + Low Margin $\to$ `REVIEW_MARGIN` (negotiate supplier costs or adjust shelf price).
  - Low Demand + High Margin $\to$ `PROMOTE` (test modest incentive).
  - Low Demand + Low Margin $\to$ `CLEARANCE` (liquidate dead capital).
  - Excessive Historical Discounting ($> 15\%$) $\to$ `LIMIT_DISCOUNT`.

---

## 3. Prioritization & Scoring Methodology

1. **Business Impact ($[0.0, 1.0]$)**:
   $$\text{Impact} = 0.30 \cdot \text{RevOpp} + 0.25 \cdot \text{MarginOpp} + 0.20 \cdot \text{CustVal} + 0.15 \cdot \text{Urgency} + 0.10 \cdot \text{Scale}$$
2. **Confidence ($[0.0, 1.0]$)**:
   $$\text{Confidence} = 0.35 \cdot \text{PredConf} + 0.25 \cdot \text{EvidStr} + 0.20 \cdot \text{HistCons} + 0.20 \cdot \text{DataQual}$$
3. **Composite Priority Score ($[0.0, 1.0]$)**:
   $$\text{Priority} = (\text{Impact} \times \text{Confidence} \times \text{Urgency})^{1/3}$$
4. **Categorical Priority Bands**:
   - $[0.79, 1.00] \to \text{CRITICAL}$
   - $[0.70, 0.79) \to \text{HIGH}$
   - $[0.55, 0.70) \to \text{MEDIUM}$
   - $[0.00, 0.55) \to \text{LOW}$

---

## 4. Conflict Resolution & Deduplication

- **Conflict Hierarchy**:
  $$\text{DATA\_QUALITY} > \text{RISK} > \text{MARGIN\_PROTECTION} > \text{REVENUE\_GROWTH} > \text{EXPERIMENTAL\_ACTION}$$
  Example: If a product receives both `PROMOTE` (Revenue Growth) and `REVIEW_MARGIN` (Margin Protection), the margin defense action wins deterministically.
- **Deduplication**: Recommendations targeting the identical `(entity_type, entity_id, type)` collapse into a single unified record, merging distinct evidence metrics and preserving peak priority.

---

## 5. Standardized 6-Part Explanation Structure

Every recommendation conforms to the explainability contract:
```text
WHAT: Restock Leather Wallet (Accessories) (RESTOCK)
WHY: Projected 7-day demand is 6 units with daily velocity of 0.8 units/day. Initiating a reorder of 8 units protects against stockouts. (Inventory data unavailable — recommendation based on forecast demand and historical sales velocity).
EVIDENCE:
  • forecast_7d_units = 5.7 (Expected 7-day customer unit demand) [Source: Phase 3 Demand Model]
  • daily_demand_velocity = 0.82 (Forecasted units per day) [Source: Phase 3 Demand Model]
  • safety_stock_units = 2.45 (Z=1.645 safety buffer for 95% service level) [Source: Statistical Formula]
  • reorder_point_units = 4.91 (Trigger threshold across 3 days lead time) [Source: Statistical Formula]
  • unit_margin = 1400.0 (Unit profit ₹1400.00 (30% margin)) [Source: Product Catalog]
  • inventory_estimation_mode = True (Recommendation based on forecast demand and historical velocity) [Source: System Configuration]
CONFIDENCE: 0.84
URGENCY: 0.75
EXPECTED IMPACT: 0.71
PRIORITY: 0.76 [HIGH]
```

---

## 6. Python API & CLI Reference

### Python API
```python
from src.recommendations.recommendation_engine import RecommendationEngine

engine = RecommendationEngine()

# Complete execution & export
summary = engine.generate_all(export=True)

# Subsystem queries
inv_recs = engine.inventory_recommendations(product_id="PRD_ACC_01")
sales_recs = engine.sales_opportunities()
cust_recs = engine.customer_recommendations(customer_id="C00001")
cross_recs = engine.cross_sell_recommendations()
price_recs = engine.pricing_recommendations()
action_plan = engine.daily_action_plan(limit=10)
```

### CLI
```powershell
# Full execution and export
python -m src.recommendations --all

# Subsystems
python -m src.recommendations --inventory
python -m src.recommendations --customers
python -m src.recommendations --products
python -m src.recommendations --cross-sell
python -m src.recommendations --pricing
python -m src.recommendations --action-plan
```
