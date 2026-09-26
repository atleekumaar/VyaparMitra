"""
Sales Opportunity and Product Action Engine.
Evaluates SKU performance tiers (Star, Growth, Declining, Low Velocity, High Margin)
and generates prioritized commercial growth recommendations.
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


class ProductActionEngine:
    """Generates revenue expansion and product focus recommendations."""

    def __init__(self, config_path: str = "configs/recommendations.yaml") -> None:
        self.config = load_recommendation_config(config_path)
        self.pricing_cfg = self.config.get("pricing", {})
        self.scoring_cfg = self.config.get("scoring", {})
        self.prio_thresholds = self.config.get("priority_thresholds", {})

    def generate_recommendations(
        self,
        product_features_df: pd.DataFrame,
        demand_forecast_df: pd.DataFrame,
        trend_df: Optional[pd.DataFrame] = None,
        product_rankings_df: Optional[pd.DataFrame] = None,
        product_id: Optional[str] = None,
    ) -> List[Recommendation]:
        """
        Generates product-level sales opportunity recommendations.
        """
        recommendations: List[Recommendation] = []
        if product_features_df.empty or demand_forecast_df.empty:
            return recommendations

        df_prods = product_features_df.copy()
        if product_id:
            df_prods = df_prods[df_prods["product_id"] == product_id]

        # 7-day predicted units per product
        forecast_7d = demand_forecast_df.groupby("product_id")["predicted_units"].sum().to_dict()

        # Business trend direction
        trend_direction = "STABLE"
        if trend_df is not None and not trend_df.empty and "predicted_trend" in trend_df.columns:
            trend_direction = str(trend_df["predicted_trend"].iloc[0])

        # Revenue and Margin percentiles
        rev_75 = float(np.percentile(df_prods["product_revenue"], 75.0))
        rev_25 = float(np.percentile(df_prods["product_revenue"], 25.0))

        df_prods["unit_margin"] = (df_prods["selling_price"] - df_prods["unit_cost"]).round(2)
        df_prods["margin_pct"] = (df_prods["unit_margin"] / df_prods["selling_price"].clip(lower=1e-9)).round(4)
        median_margin_pct = float(df_prods["margin_pct"].median())

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        for _, row in df_prods.iterrows():
            pid = str(row["product_id"])
            pname = str(row.get("product_name", pid))
            pcat = str(row.get("product_category", "General"))
            rev = float(row.get("product_revenue", 0.0))
            sales_units = float(row.get("product_sales", 0.0))
            m_pct = float(row["margin_pct"])
            unit_margin = float(row["unit_margin"])
            f_units = float(forecast_7d.get(pid, 0.0))

            is_top_rev = rev >= rev_75
            is_low_rev = rev <= rev_25
            is_high_margin = m_pct >= median_margin_pct
            is_high_demand = f_units >= 5.0

            # 1. STAR PRODUCT: Top revenue + high forward demand -> FOCUS
            if is_top_rev and is_high_demand:
                rec_type = RecommendationType.FOCUS
                title = f"Maximize Star Product Velocity: {pname}"
                action = f"Prioritize prime display placement and ensure zero catalog outages."
                reason = (
                    f"Product is in the top 25% of merchant revenue (Total: ₹{rev:,.2f}) with robust 7-day forecast "
                    f"of {f_units:.0f} units. Maintaining prominent visibility captures core demand."
                )
                urgency = 0.70
                rev_opp = 0.85
                conflict_cat = ConflictCategory.REVENUE_GROWTH

            # 2. GROWTH / HIGH MARGIN SLEEPER: High margin + low/medium revenue -> PROMOTE
            elif is_high_margin and not is_top_rev and f_units >= 2.0:
                rec_type = RecommendationType.PROMOTE
                title = f"Promote High-Margin Opportunity: {pname}"
                action = f"Feature in promotional showcases or digital store banners to lift awareness."
                reason = (
                    f"Product yields an attractive margin of {m_pct*100:.1f}% (₹{unit_margin:.2f}/unit) but currently "
                    f"accounts for moderate historical sales (₹{rev:,.2f}). Targeted promotion will expand profitability."
                )
                urgency = 0.60
                rev_opp = 0.75
                conflict_cat = ConflictCategory.REVENUE_GROWTH

            # 3. UNDERPERFORMING / DECLINING: Low revenue + low demand -> BUNDLE / MONITOR
            elif is_low_rev and f_units < 2.0:
                if is_high_margin:
                    rec_type = RecommendationType.BUNDLE
                    title = f"Bundle Low-Velocity Item: {pname}"
                    action = f"Pair as a bonus or discounted add-on alongside fast-moving {pcat} staples."
                    reason = (
                        f"Product exhibits sluggish sales (₹{rev:,.2f}) with only {f_units:.0f} units projected next week. "
                        f"Healthy unit margin (₹{unit_margin:.2f}) makes it an ideal bundling candidate."
                    )
                    urgency = 0.50
                    rev_opp = 0.45
                    conflict_cat = ConflictCategory.EXPERIMENTAL_ACTION
                else:
                    rec_type = RecommendationType.MONITOR
                    title = f"Monitor Slow-Moving SKU: {pname}"
                    action = f"Track customer impressions and hold off on additional capital allocation."
                    reason = (
                        f"Product contributes low revenue (₹{rev:,.2f}) with low forecast demand ({f_units:.1f} units). "
                        f"Avoid speculative bulk orders until velocity rebounds."
                    )
                    urgency = 0.40
                    rev_opp = 0.30
                    conflict_cat = ConflictCategory.RISK
            else:
                continue

            impact_score = compute_impact(
                revenue_opportunity=rev_opp,
                margin_opportunity=float(np.clip(m_pct * 1.5, 0.20, 0.90)),
                customer_value=0.60,
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
                build_evidence("forecast_7d_units", round(f_units, 1), "Phase 3 Demand Model", "Expected 7-day unit demand"),
                build_evidence("product_revenue", round(rev, 2), "Phase 1 Feature Store", "Historical total revenue"),
                build_evidence("unit_margin", round(unit_margin, 2), "Product Catalog", f"Profit margin ₹{unit_margin:.2f} ({m_pct*100:.1f}%)"),
                build_evidence("business_trend", trend_direction, "Phase 3 Trend Model", "Overall store revenue trajectory"),
            ]

            rec = Recommendation(
                recommendation_id=f"REC_SALES_{pid}",
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
        logger.info("Generated %d sales opportunity recommendations.", len(recommendations))
        return recommendations
