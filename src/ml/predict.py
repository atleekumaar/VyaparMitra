"""
CLI Entrypoint for Model Inference in VyaparMitra Phase 3.
Usage:
    python -m src.ml.predict --all
    python -m src.ml.predict --model sales --horizon 7
    python -m src.ml.predict --model demand --horizon 7
    python -m src.ml.predict --model churn
    python -m src.ml.predict --model trend
"""

from __future__ import annotations

import argparse
import logging
import sys
from src.ml.ml_engine import MLEngine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("src.ml.predict")


def main() -> None:
    parser = argparse.ArgumentParser(description="VyaparMitra ML Inference Engine")
    parser.add_argument("--config", default="configs/config.yaml", help="Path to config file")
    parser.add_argument("--all", action="store_true", help="Run inference across all models")
    parser.add_argument(
        "--model",
        choices=["sales", "demand", "churn", "trend"],
        help="Specify single model to run inference for",
    )
    parser.add_argument("--horizon", type=int, default=7, help="Forecasting horizon days (default: 7)")

    args = parser.parse_args()
    engine = MLEngine(config_path=args.config)

    if args.all or (not args.model):
        logger.info("Executing unified batch inference across all models...")
        sales_pred = engine.forecast_sales(horizon_days=args.horizon)
        demand_pred = engine.forecast_product_demand(horizon_days=args.horizon)
        churn_pred = engine.score_customer_risk()
        trend_pred = engine.predict_business_trend()

        print("\n================ ML PREDICTION SUMMARY ================")
        print(f"Sales Forecast ({args.horizon} days):")
        print(sales_pred.head(args.horizon).to_string(index=False))
        print("\nProduct Demand Forecast (Sample top 5):")
        print(demand_pred.head(5).to_string(index=False))
        print("\nCustomer Risk Assessment (Sample top 5):")
        print(churn_pred.head(5).to_string(index=False))
        print("\nBusiness Trend Forecast:")
        print(trend_pred.to_string(index=False))
        print("=======================================================\n")
    elif args.model == "sales":
        res = engine.forecast_sales(horizon_days=args.horizon)
        print(res.to_string(index=False))
    elif args.model == "demand":
        res = engine.forecast_product_demand(horizon_days=args.horizon)
        print(res.head(20).to_string(index=False))
    elif args.model == "churn":
        res = engine.score_customer_risk()
        print(res.head(20).to_string(index=False))
    elif args.model == "trend":
        res = engine.predict_business_trend()
        print(res.to_string(index=False))


if __name__ == "__main__":
    main()
