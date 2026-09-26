"""
CLI Entrypoint for VyaparMitra Phase 4 AI Recommendation & Decision Engine.
Usage:
    python -m src.recommendations --all
    python -m src.recommendations --inventory
    python -m src.recommendations --customers
    python -m src.recommendations --products
    python -m src.recommendations --cross-sell
    python -m src.recommendations --pricing
    python -m src.recommendations --action-plan
"""

from __future__ import annotations

import argparse
import logging
import sys
from src.recommendations.recommendation_engine import RecommendationEngine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("src.recommendations")


def main() -> None:
    parser = argparse.ArgumentParser(description="VyaparMitra AI Recommendation Engine")
    parser.add_argument("--config", default="configs/recommendations.yaml", help="Path to recommendations config")
    parser.add_argument("--all", action="store_true", help="Generate all recommendations and export artifacts")
    parser.add_argument("--inventory", action="store_true", help="Generate inventory restock recommendations")
    parser.add_argument("--customers", action="store_true", help="Generate customer retention recommendations")
    parser.add_argument("--products", action="store_true", help="Generate sales opportunity recommendations")
    parser.add_argument("--cross-sell", action="store_true", help="Generate cross-sell association recommendations")
    parser.add_argument("--pricing", action="store_true", help="Generate pricing and margin recommendations")
    parser.add_argument("--action-plan", action="store_true", help="Display top daily merchant action plan")
    parser.add_argument("--product-id", type=str, default=None, help="Filter for single product SKU")
    parser.add_argument("--customer-id", type=str, default=None, help="Filter for single customer ID")
    parser.add_argument("--merchant-id", type=str, default=None, help="Filter for single merchant ID")
    parser.add_argument("--limit", type=int, default=15, help="Number of recommendations to display in console")

    args = parser.parse_args()
    engine = RecommendationEngine(config_path=args.config)

    # Default to --all if no specific flag is provided
    if args.all or not (
        args.inventory
        or args.customers
        or args.products
        or args.cross_sell
        or args.pricing
        or args.action_plan
    ):
        logger.info("Executing comprehensive Phase 4 recommendation pipeline...")
        summary = engine.generate_all(merchant_id=args.merchant_id, export=True)
        print("\n================ RECOMMENDATION GENERATION COMPLETE ================")
        print(f"Total Consolidated Recommendations: {summary['counts']['total_recommendations']}")
        print(f"Priority Distribution: {summary['priority_distribution']}")
        print(f"Inventory Actions: {summary['counts']['inventory']}")
        print(f"Sales Opportunities: {summary['counts']['sales_opportunities']}")
        print(f"Customer Retention: {summary['counts']['customer_retention']}")
        print(f"Cross-Sell Rules: {summary['counts']['cross_sell']}")
        print(f"Pricing Decisions: {summary['counts']['pricing']}")
        print("====================================================================\n")

    elif args.inventory:
        recs = engine.inventory_recommendations(product_id=args.product_id)
        print(f"\n[INVENTORY RECOMMENDATIONS: {len(recs)} generated]")
        for r in recs[:args.limit]:
            print(f"- [{r.priority_band.value}] ({r.priority:.2f}) {r.title}: {r.action}")

    elif args.customers:
        recs = engine.customer_recommendations(customer_id=args.customer_id)
        print(f"\n[CUSTOMER RETENTION RECOMMENDATIONS: {len(recs)} generated]")
        for r in recs[:args.limit]:
            print(f"- [{r.priority_band.value}] ({r.priority:.2f}) {r.title}: {r.action}")

    elif args.products:
        recs = engine.sales_opportunities(product_id=args.product_id)
        print(f"\n[SALES OPPORTUNITIES: {len(recs)} generated]")
        for r in recs[:args.limit]:
            print(f"- [{r.priority_band.value}] ({r.priority:.2f}) {r.title}: {r.action}")

    elif args.cross_sell:
        recs = engine.cross_sell_recommendations(product_id=args.product_id)
        print(f"\n[CROSS-SELL RECOMMENDATIONS: {len(recs)} generated]")
        for r in recs[:args.limit]:
            print(f"- [{r.priority_band.value}] ({r.priority:.2f}) {r.title}: {r.action}")

    elif args.pricing:
        recs = engine.pricing_recommendations(product_id=args.product_id)
        print(f"\n[PRICING RECOMMENDATIONS: {len(recs)} generated]")
        for r in recs[:args.limit]:
            print(f"- [{r.priority_band.value}] ({r.priority:.2f}) {r.title}: {r.action}")

    elif args.action_plan:
        plan = engine.daily_action_plan(merchant_id=args.merchant_id, limit=args.limit)
        print(f"\n================ DAILY MERCHANT ACTION PLAN (TOP {len(plan)}) ================")
        for idx, r in enumerate(plan, 1):
            print(f"{idx}. [{r.priority_band.value}] {r.title} (Priority: {r.priority:.2f})")
            print(f"   Action: {r.action}")
            print(f"   Why: {r.reason}\n")
        print("============================================================================\n")


if __name__ == "__main__":
    main()
