"""
Customer Retention and Engagement Recommendation Engine.
Ingests Phase 3 customer churn risk assessments and Phase 1/2 RFM profiles
to produce targeted, evidence-backed retention and re-engagement recommendations.
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


class CustomerActionEngine:
    """Generates customer-level retention, re-engagement, and personalization recommendations."""

    def __init__(self, config_path: str = "configs/recommendations.yaml") -> None:
        self.config = load_recommendation_config(config_path)
        self.cust_cfg = self.config.get("customer", {})
        self.scoring_cfg = self.config.get("scoring", {})
        self.prio_thresholds = self.config.get("priority_thresholds", {})

    def generate_recommendations(
        self,
        customer_risk_df: pd.DataFrame,
        customer_features_df: pd.DataFrame,
        customer_segments_df: Optional[pd.DataFrame] = None,
        customer_id: Optional[str] = None,
        max_recommendations: int = 100,
    ) -> List[Recommendation]:
        """
        Generates customer retention and re-engagement recommendations.
        """
        recommendations: List[Recommendation] = []
        if customer_risk_df.empty or customer_features_df.empty:
            logger.warning("Empty risk or feature dataframe provided to customer action engine.")
            return recommendations

        # Merge risk scores with customer profiles
        merged = pd.merge(customer_risk_df, customer_features_df, on="customer_id", how="inner")
        if customer_segments_df is not None and not customer_segments_df.empty and "customer_recency" in customer_segments_df.columns:
            rec_map = customer_segments_df.set_index("customer_id")["customer_recency"].to_dict()
            merged["recency_days"] = merged["customer_id"].map(rec_map).fillna(30.0)
        else:
            merged["recency_days"] = 30.0

        if customer_id:
            merged = merged[merged["customer_id"] == customer_id]

        # Spend threshold for high value (top 25% or configured percentile)
        spend_pctl = float(self.cust_cfg.get("high_value_spend_percentile", 75.0))
        high_value_spend = float(np.percentile(merged["customer_total_spend"], spend_pctl))

        high_risk_thresh = float(self.cust_cfg.get("churn_high_risk", 0.60))
        med_risk_thresh = float(self.cust_cfg.get("churn_medium_risk", 0.30))
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        for _, row in merged.iterrows():
            cid = str(row["customer_id"])
            cname = str(row.get("customer_name", cid))
            p_risk = float(row.get("risk_probability", 0.50))
            tot_spend = float(row.get("customer_total_spend", 0.0))
            orders_cnt = int(row.get("customer_order_count", 1))
            aov = float(row.get("customer_average_order_value", tot_spend / max(1, orders_cnt)))
            recency = float(row.get("recency_days", 30.0))

            is_high_value = tot_spend >= high_value_spend
            is_high_risk = p_risk >= high_risk_thresh
            is_med_risk = (p_risk >= med_risk_thresh) and (not is_high_risk)

            # Segment & Action Assignment
            if is_high_value and is_high_risk:
                rec_type = RecommendationType.RETENTION
                title = f"High-Value Customer Retention: {cname} ({cid})"
                action = f"Initiate proactive personal outreach or exclusive loyalty perk to re-activate customer."
                reason = (
                    f"Customer is in the top 25% of spenders (Total: ₹{tot_spend:,.2f}, {orders_cnt} orders), "
                    f"but has been inactive for {recency:.0f} days with an estimated churn/inactivity risk of {p_risk*100:.1f}%."
                )
                urgency = float(np.clip(0.60 + 0.35 * p_risk, 0.60, 0.95))
                cust_val = 0.90
            elif is_high_value and not is_high_risk:
                rec_type = RecommendationType.PERSONALIZED_OFFER
                title = f"Reward Loyal Top Customer: {cname} ({cid})"
                action = f"Offer curated premium bundle or VIP preview to foster ongoing loyalty."
                reason = (
                    f"Customer exhibits strong engagement (Risk: {p_risk*100:.1f}%) and high lifetime value "
                    f"(Spend: ₹{tot_spend:,.2f}, AOV: ₹{aov:,.2f})."
                )
                urgency = 0.50
                cust_val = 0.85
            elif (not is_high_value) and is_high_risk:
                rec_type = RecommendationType.RE_ENGAGEMENT
                title = f"Re-engage At-Risk Customer: {cname} ({cid})"
                action = f"Send automated seasonal catalog reminder or welcome-back communication."
                reason = (
                    f"Customer inactivity has reached {recency:.0f} days with a risk probability of {p_risk*100:.1f}%. "
                    f"Automated re-engagement can prompt a repeat purchase."
                )
                urgency = float(np.clip(0.40 + 0.30 * p_risk, 0.40, 0.80))
                cust_val = 0.40
            elif is_med_risk and orders_cnt <= 2:
                rec_type = RecommendationType.PRODUCT_REMINDER
                title = f"Second-Purchase Follow-up: {cname} ({cid})"
                action = f"Nudge with complementary product recommendations related to recent purchases."
                reason = (
                    f"Newer customer ({orders_cnt} historical orders) entering inactivity threshold. "
                    f"A timely reminder encourages habit formation."
                )
                urgency = 0.45
                cust_val = 0.45
            else:
                continue

            impact_score = compute_impact(
                revenue_opportunity=float(np.clip(aov / 3000.0, 0.20, 0.90)),
                margin_opportunity=0.50,
                customer_value=cust_val,
                urgency=urgency,
                scale=0.50,
                weights=self.scoring_cfg.get("impact_weights"),
            )

            confidence_score = compute_confidence(
                prediction_confidence=float(np.clip(0.60 + 0.35 * (abs(p_risk - 0.5) * 2), 0.60, 0.92)),
                evidence_strength=0.85,
                historical_consistency=0.80,
                data_quality=0.90,
                weights=self.scoring_cfg.get("confidence_weights"),
            )

            priority_score = compute_priority(impact_score, confidence_score, urgency)
            priority_band = assign_priority_band(priority_score, self.prio_thresholds)

            evidence_items = [
                build_evidence("churn_risk_probability", round(p_risk, 4), "Phase 3 Churn Model", f"Inactivity likelihood within next 30 days ({p_risk*100:.1f}%)"),
                build_evidence("customer_recency_days", round(recency, 1), "Phase 2 Customer Analytics", "Elapsed days since last recorded purchase"),
                build_evidence("customer_total_spend", round(tot_spend, 2), "Phase 1 Feature Store", "Lifetime gross spend"),
                build_evidence("customer_order_count", orders_cnt, "Phase 1 Feature Store", "Total historical transactions placed"),
                build_evidence("average_order_value", round(aov, 2), "Phase 1 Feature Store", "Average transaction basket value"),
            ]

            rec = Recommendation(
                recommendation_id=f"REC_CUST_{cid}",
                merchant_id=None,
                type=rec_type,
                priority=priority_score,
                priority_band=priority_band,
                confidence=confidence_score,
                urgency=urgency,
                expected_impact=impact_score,
                entity_type="customer",
                entity_id=cid,
                title=title,
                action=action,
                reason=reason,
                evidence=evidence_items,
                conflict_category=ConflictCategory.RISK if is_high_risk else ConflictCategory.REVENUE_GROWTH,
                created_at=now_str,
                status=LifecycleState.GENERATED,
            )
            recommendations.append(rec)

        recommendations.sort(key=lambda r: r.priority, reverse=True)
        # Cap to top max_recommendations for focused daily action
        final_recs = recommendations[:max_recommendations]
        logger.info("Generated %d customer recommendations (top %d retained).", len(recommendations), len(final_recs))
        return final_recs
