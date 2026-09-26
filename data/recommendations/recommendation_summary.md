# VyaparMitra — Recommendation Engine Summary Report

**Execution Timestamp**: 2026-09-26 06:00:02 UTC

## 1. Executive Metrics Overview

- **Total Consolidated Recommendations**: 270
- **🔴 Critical Actions**: 23
- **🟠 High Priority Actions**: 132
- **🟡 Medium Priority Actions**: 80
- **🟢 Low Priority Actions**: 35

## 2. Recommendation Breakdown by System

| Subsystem | Recommendation Type | Count |
|---|---|---|
| **Inventory & Restock** | `RESTOCK` | 64 |
| **Sales Opportunities** | `FOCUS`, `PROMOTE`, `BUNDLE`, `MONITOR` | 29 |
| **Customer Retention** | `RETENTION`, `RE_ENGAGEMENT`, `PERSONALIZED_OFFER` | 100 |
| **Cross-Sell Affinities** | `CROSS_SELL` | 34 |
| **Pricing & Margin Defense** | `MAINTAIN_PRICE`, `REVIEW_MARGIN`, `LIMIT_DISCOUNT`, `CLEARANCE` | 49 |
| **Total Consolidated** | All Systems | **270** |

## 3. Data Integrity & Observational Safeguards

- **Inventory Estimation**: Since live warehouse telemetry is unobserved, inventory guidance operates in `inventory_estimation_mode = True` without fabricating stock counts.
- **Non-Causal Association Rules**: Cross-sell affinities denote observed co-purchase lift, avoiding false causal promises.
- **Margin Protection Priority**: Resolves conflicting advice by giving precedence to data quality, risk mitigation, and margin preservation.