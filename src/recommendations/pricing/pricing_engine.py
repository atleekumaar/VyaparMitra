"""
Conservative Pricing and Margin Protection Recommendation Engine.
Evaluates margin elasticity, unit profitability, and demand forecasts
to recommend price defense, margin reviews, discount limits, and clearance actions.
"""

from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from src.recommendations.config import load_recommendation_config
from src.recommendations.explanations.evidence import build_evidence
from src.recommendations.schemas import (
    ConflictCategory,
    LifecycleState,
    PriorityBand,
    Recommendation,
    RecommendationType,
)
from src.recommendations.scoring.priority import (
    assign_priority_band,
    compute_confidence,
    compute_impact,
    compute_priority,
)

logger = logging.getLogger(__name__)


class PricingRecommendationEngine:
    """Produces margin-defending pricing and promotional recommendations."""

    def __init__(self, config_path: str = "configs/recommendations.yaml") -> None:
        self.config = load_recommendation_config(config_path)
        self.pricing_cfg = self.config.get("pricing", {})
        self.scoring_cfg = self.config.get("scoring", {})
        self.prio_thresholds = self.config.get("priority_thresholds", {})

    def generate_recommendations(
        self,
        product_features_df: pd.DataFrame,
        demand_forecast_df: pd.DataFrame,
        transactions_df: Optional[pd.DataFrame] = None,
        product_id: Optional[str] = None,
    ) -> List[Recommendation]:
        """
        Analyzes unit margins and projected demand to generate pricing actions.
        """
        recommendations: List[Recommendation] = []
        if product_features_df.empty or demand_forecast_df.empty:
            return recommendations

        df_prods = product_features_df.copy()
        if product_id:
            df_prods = df_prods[df_prods["product_id"] == product_id]

        forecast_7d = demand_forecast_df.groupby("product_id")["predicted_units"].sum().to_dict()

        # Compute average discount rate per product if transactions are supplied
        disc_rate_map: Dict[str, float] = {}
        if transactions_df is not None and not transactions_df.empty:
            if "discount" in transactions_df.columns and "unit_price" in transactions_df.columns:
                tx = transactions_df.copy()
                tx["gross"] = tx["quantity"] * tx["unit_price"]
                tx["disc_pct"] = tx["discount"] / tx["gross"].clip(lower=1e-9)
                disc_rate_map = tx.groupby("product_id")["disc_pct"].mean().to_dict()

        # Thresholds
        high_m_thresh = float(self.pricing_cfg.get("high_margin_threshold", 0.25))
        low_m_thresh = float(self.pricing_cfg.get("low_margin_threshold", 0.15))
        excessive_disc = float(self.pricing_cfg.get("excessive_discount_rate", 0.15))

        # Demand percentiles across catalog
        f_vals = list(forecast_7d.values())
        high_demand_val = float(np.percentile(f_vals, self.pricing_cfg.get("high_demand_percentile", 70.0))) if f_vals else 5.0
        low_demand_val = float(np.percentile(f_vals, self.pricing_cfg.get("low_demand_percentile", 30.0))) if f_vals else 2.0

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        for _, row in df_prods.iterrows():
            pid = str(row["product_id"])
            pname = str(row.get("product_name", pid))
            pcat = str(row.get("product_category", "General"))
            unit_cost = float(row.get("unit_cost", 50.0))
            selling_price = float(row.get("selling_price", 100.0))
            margin = round(selling_price - unit_cost, 2)
            margin_pct = round(margin / max(1e-9, selling_price), 4)

            f_units = float(forecast_7d.get(pid, 0.0))
            avg_disc = float(disc_rate_map.get(pid, 0.0))

            is_high_demand = f_units >= high_demand_val
            is_low_demand = f_units <= low_demand_val
            is_high_margin = margin_pct >= high_m_thresh
            is_low_margin = margin_pct <= low_m_thresh

            # Check excessive discount guardrail first
            if avg_disc >= excessive_disc:
                rec_type = RecommendationType.LIMIT_DISCOUNT
                title = f"Curtail Discount Erosion: {pname}"
                action = f"Cap transaction discounts at 5% to preserve realized unit margins."
                reason = (
                    f"Product has an average historical discount rate of {avg_disc*100:.1f}%, which erodes the "
                    f"nominal margin of {margin_pct*100:.1f}%. Restricting ad-hoc discounts recovers bottom-line profit."
                )
                urgency = 0.70
                rev_opp = 0.60
                margin_opp = 0.85
                conflict_cat = ConflictCategory.MARGIN_PROTECTION

            # 1. High Demand + High Margin -> MAINTAIN_PRICE
            elif is_high_demand and is_high_margin:
                rec_type = RecommendationType.MAINTAIN_PRICE
                title = f"Protect Pricing Power: {pname}"
                action = f"Avoid promotional price-cutting; preserve current price point of ₹{selling_price:.2f}."
                reason = (
                    f"Strong forward demand ({f_units:.0f} units/week) paired with healthy {margin_pct*100:.1f}% unit margin. "
                    f"Customers exhibit low price sensitivity; discounting is unnecessary and dilutes profit."
                )
                urgency = 0.65
                rev_opp = 0.80
                margin_opp = 0.90
                conflict_cat = ConflictCategory.MARGIN_PROTECTION

            # 2. High Demand + Low Margin -> REVIEW_MARGIN
            elif is_high_demand and is_low_margin:
                rec_type = RecommendationType.REVIEW_MARGIN
                title = f"Margin Review Alert: {pname}"
                action = f"Negotiate volume supplier concessions or test a modest 3-5% price adjustment."
                reason = (
                    f"Robust volume ({f_units:.0f} projected units) generates high operational turnover, but slim "
                    f"margin of {margin_pct*100:.1f}% (₹{margin:.2f}/unit) limits profit capture."
                )
                urgency = 0.75
                rev_opp = 0.70
                margin_opp = 0.80
                conflict_cat = ConflictCategory.MARGIN_PROTECTION

            # 3. Low Demand + High Margin -> PROMOTE
            elif is_low_demand and is_high_margin:
                rec_type = RecommendationType.PROMOTE
                title = f"Promotional Discount Candidate: {pname}"
                action = f"Introduce a 5-10% introductory or seasonal incentive to accelerate sales velocity."
                reason = (
                    f"Product exhibits low projected demand ({f_units:.1f} units) but healthy margin room "
                    f"({margin_pct*100:.1f}%, ₹{margin:.2f}). Modest discounting can stimulate sales without compromising unit viability."
                )
                urgency = 0.50
                rev_opp = 0.60
                margin_opp = 0.65
                conflict_cat = ConflictCategory.REVENUE_GROWTH

            # 4. Low Demand + Low Margin -> CLEARANCE
            elif is_low_demand and is_low_margin:
                rec_type = RecommendationType.CLEARANCE
                title = f"Clearance Evaluation: {pname}"
                action = f"Liquidate remaining stock at break-even and reallocate working capital."
                reason = (
                    f"Both demand ({f_units:.1f} units) and unit margin ({margin_pct*100:.1f}%) are compressed. "
                    f"Holding inventory ties up capital without delivering commercial returns."
                )
                urgency = 0.60
                rev_opp = 0.35
                margin_opp = 0.40
                conflict_cat = ConflictCategory.RISK

            else:
                continue

            impact_score = compute_impact(
                revenue_opportunity=rev_opp,
                margin_opportunity=margin_opp,
                customer_value=0.50,
                urgency=urgency,
                scale=0.55,
                weights=self.scoring_cfg.get("impact_weights"),
            )

            confidence_score = compute_confidence(
                prediction_confidence=0.82,
                evidence_strength=0.85,
                historical_consistency=0.80,
                data_quality=0.90,
                weights=self.scoring_cfg.get("confidence_weights"),
            )

            priority_score = compute_priority(impact_score, confidence_score, urgency)
            priority_band = assign_priority_band(priority_score, self.prio_thresholds)

            evidence_items = [
                build_evidence("forecast_7d_units", round(f_units, 1), "Phase 3 Demand Model", "7-day forward demand forecast"),
                build_evidence("selling_price", selling_price, "Product Catalog", "Current shelf price"),
                build_evidence("unit_cost", unit_cost, "Product Catalog", "Wholesale inventory replacement cost"),
                build_evidence("unit_margin", margin, "Product Catalog", f"Unit margin ₹{margin:.2f} ({margin_pct*100:.1f}%)"),
                build_evidence("historical_avg_discount", round(avg_disc, 4), "Historical Transactions", f"Average observed discount rate ({avg_disc*100:.1f}%)"),
            ]

            rec = Recommendation(
                recommendation_id=f"REC_PRICE_{pid}",
                merchant_id=None,
                type=rec_type,
                priority=priority_score,
                priority_band=priority_band,
                confidence=confidence_score,
                urgency=urgency,
                expected_impact=impact_score,
                entity_type="product",
                entity_id=pid,
                title=title,
                action=action,
                reason=reason,
                evidence=evidence_items,
                conflict_category=conflict_cat,
                created_at=now_str,
                status=LifecycleState.GENERATED,
            )
            recommendations.append(rec)

        recommendations.sort(key=lambda r: r.priority, reverse=True)
        logger.info("Generated %d pricing/promotion recommendations.", len(recommendations))
        return recommendations
