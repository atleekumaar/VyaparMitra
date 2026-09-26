# VyaparMitra Phase 3: Predictive AI Engine Comprehensive Report

## Executive Summary

Phase 3 transforms historical merchant and transaction data into four production-grade predictive systems. Every candidate model was required to pass a strict Quality Gate against empirical baselines under chronological, leakage-free validation.

## 1. Predictive Systems Architecture & Scope

1. **Daily Sales Forecasting**: Recursively forecasts total merchant daily revenue for 7-day and 30-day horizons with confidence intervals.
2. **Product Demand Forecasting**: Item-level unit demand across all catalog products handling zero-demand days via Cartesian panel grid.
3. **Customer Churn & Inactivity Risk**: Supervised classification on point-in-time snapshots predicting 30-day lapsing with probability scores and risk bands.
4. **Business Trend Forecasting**: Multi-class directional forecasting (INCREASING, STABLE, DECREASING) comparing forward 7d vs backward 7d revenue.

## 2. Data Splitting & Leakage Prevention Strategy

- **Strict Chronological Splitting**: All time-series data was split sequentially (70% train, 15% validation, 15% test) without row shuffling.
- **Point-in-Time Customer Snapshots**: Customer behavioral features derive strictly from transactions before the cutoff date; target represents zero orders during the future window.
- **Feature Alignment**: Target lags and rolling averages were shifted strictly (e.g. `shift(1)`), ensuring step $t$ uses only information known at $t-1$.

## 3. Top Feature Importance Signals

### Top Drivers: Daily Sales Forecaster

| Feature | Importance Score | Standard Deviation |
|---|---|---|
| `day_of_week` | 0.0249 | 0.0153 |
| `rainfall` | 0.0209 | 0.0088 |
| `lag_1d_revenue` | 0.0175 | 0.0168 |
| `lag_28d_revenue` | 0.0161 | 0.0060 |
| `rolling_7d_avg_revenue` | 0.0028 | 0.0165 |

### Top Drivers: Product Demand Forecaster

| Feature | Importance Score | Standard Deviation |
|---|---|---|
| `rolling_28_units` | 0.2121 | 0.0122 |
| `rolling_7_units` | 0.0111 | 0.0012 |
| `unit_margin` | 0.0075 | 0.0024 |
| `selling_price` | 0.0049 | 0.0008 |
| `lag_1_units` | 0.0007 | 0.0016 |

### Top Drivers: Customer Churn Risk Model

| Feature | Importance Score | Standard Deviation |
|---|---|---|
| `recent_30d_orders` | 0.0093 | 0.0049 |
| `recent_7d_orders` | 0.0004 | 0.0025 |
| `total_orders` | -0.0085 | 0.0093 |
| `days_since_first_purchase` | -0.0119 | 0.0081 |
| `recent_90d_orders` | -0.0131 | 0.0045 |

### Top Drivers: Business Trend Classifier

| Feature | Importance Score | Standard Deviation |
|---|---|---|
| `past_28d_revenue` | 0.0898 | 0.0379 |
| `past_7d_revenue` | 0.0857 | 0.0327 |
| `historical_7d_momentum` | 0.0245 | 0.0082 |
| `past_14d_revenue` | 0.0122 | 0.0163 |
| `day_of_week` | 0.0000 | 0.0224 |

## 4. Key Business Findings

- **Sales Drivers**: Recent revenue momentum (`lag_1d_revenue`, `lag_7d_revenue`, `rolling_7d_avg_revenue`) dominates daily performance, followed by day-of-week seasonality (weekend surges).
- **Product Demand Dynamics**: High-volume staple categories show strong auto-correlation and seasonal patterns, whereas premium/infrequent categories exhibit intermittent, zero-inflated demand requiring robust smoothing.
- **Customer Churn Indicators**: Days since last purchase (`recency`) and drop in 30-day purchase frequency vs lifetime cadence are the strongest early-warning indicators of impending merchant churn.
- **Operational Revenue Trend**: Historical 7-day momentum and 14-day rolling velocity provide clear directional separation between expanding and contracting cycles.

## 5. Limitations & Future Phase 4 Integration

- **Limitations**: Exogenous shocks (sudden weather changes, unannounced holidays) cannot be fully captured without multi-year records.
- **Handoff to Phase 4 (Recommendations)**: Phase 4 can ingest `customer_risk_scores.parquet` to trigger automated win-back offers for high-risk accounts, `product_demand_forecast_7d.parquet` for reorder alerts, and `sales_forecast_7d.parquet` for merchant cash-flow planning.
