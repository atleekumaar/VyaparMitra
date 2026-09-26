"""
CLI Entrypoint for Model Training in VyaparMitra Phase 3.
Usage:
    python -m src.ml.train --all
    python -m src.ml.train --model sales
    python -m src.ml.train --model demand
    python -m src.ml.train --model churn
    python -m src.ml.train --model trend
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
logger = logging.getLogger("src.ml.train")


def main() -> None:
    parser = argparse.ArgumentParser(description="VyaparMitra ML Training Engine")
    parser.add_argument("--config", default="configs/config.yaml", help="Path to config file")
    parser.add_argument("--all", action="store_true", help="Train all models")
    parser.add_argument(
        "--model",
        choices=["sales", "demand", "churn", "trend"],
        help="Specify single model to train",
    )

    args = parser.parse_args()
    engine = MLEngine(config_path=args.config)

    if args.all or (not args.model):
        logger.info("Executing full ML training pipeline across all predictive systems...")
        results = engine.train_all()
        print("\n================ ML TRAINING COMPLETE ================")
        for mod, res in results.items():
            print(f"[{mod.upper()}] Selected: {res.get('selected_model')} | {res.get('reason')}")
        print("======================================================\n")
    elif args.model == "sales":
        res = engine.train_sales()
        print(f"\n[SALES] Selected: {res.get('selected_model')} | {res.get('reason')}")
    elif args.model == "demand":
        res = engine.train_demand()
        print(f"\n[DEMAND] Selected: {res.get('selected_model')} | {res.get('reason')}")
    elif args.model == "churn":
        res = engine.train_churn()
        print(f"\n[CHURN] Selected: {res.get('selected_model')} | {res.get('reason')}")
    elif args.model == "trend":
        res = engine.train_trend()
        print(f"\n[TREND] Selected: {res.get('selected_model')} | {res.get('reason')}")


if __name__ == "__main__":
    main()
