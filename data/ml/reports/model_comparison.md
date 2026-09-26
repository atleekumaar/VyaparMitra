# VyaparMitra Phase 3: Model Benchmark & Comparison Report

This document tracks candidate model performance against mandatory baselines across the 4 predictive ML systems.

## 1. Daily Sales Forecasting (System 1)

| Model | Role | Val MAE | Val RMSE | Val WAPE | Test MAE | Test RMSE | Test WAPE | Status |
|---|---|---|---|---|---|---|---|---|
| naive | Baseline | 17233.09 | 21373.65 | 36.92% | - | - | - | Benchmark |
| seasonal_naive | Baseline | 17483.42 | 21569.80 | 37.46% | - | - | - | Benchmark |
| moving_average | Baseline | 13682.99 | 16899.00 | 29.32% | - | - | - | Benchmark |
| **RandomForestRegressor** | Champion ML | **12717.21** | **16314.79** | **27.25%** | **11867.89** | **13937.77** | **27.01%** | **SELECTED** |

**Selection Justification**: Outperformed best baseline (moving_average WAPE: 29.32%) with validation WAPE: 27.25%

## 2. Product Demand Forecasting (System 2)

| Model | Role | Val WAPE | Val MAE | Val RMSE | Test WAPE | Test MAE | Test RMSE | Status |
|---|---|---|---|---|---|---|---|---|
| Seasonal Naive Demand | Baseline | 166.82% | - | - | - | - | - | Benchmark |
| **HistGradientBoostingRegressor_Demand** | Champion ML | **120.50%** | **0.69** | **0.95** | **120.54%** | **0.68** | **0.95** | **SELECTED** |

**Selection Justification**: Candidate ML model beat baseline WAPE (166.82% vs 120.50%)

## 3. Customer Churn / Inactivity Risk (System 3)

| Model | Role | Val PR-AUC | Val ROC-AUC | Val F1 | Test PR-AUC | Test ROC-AUC | Test F1 | Status |
|---|---|---|---|---|---|---|---|---|
| Rule-Based Recency | Baseline | 0.8066 | 0.4313 | 0.6981 | - | - | - | Benchmark |
| **Rule-Based Recency Baseline** | Champion ML | **0.8066** | **0.4313** | **0.6981** | **0.8445** | **0.5211** | **0.7457** | **SELECTED** |

**Selection Justification**: Candidate ML did not exceed baseline PR-AUC. Selected baseline Rule-Based Recency Baseline.

## 4. Business Trend Direction (System 4)

| Model | Role | Val Balanced Acc | Val Macro F1 | Test Balanced Acc | Test Macro F1 | Status |
|---|---|---|---|---|---|---|
| Majority Class | Baseline | 0.3333 | 0.1863 | - | - | Benchmark |
| **HistGradientBoostingClassifier_Trend** | Champion ML | **0.4516** | **0.4186** | **0.5000** | **0.4657** | **SELECTED** |

**Selection Justification**: Candidate ML model beat or matched baseline Macro F1 (0.4186 vs 0.1863)
