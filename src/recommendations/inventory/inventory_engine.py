"""
Inventory Recommendation Engine for VyaparMitra.
Generates RESTOCK and reorder recommendations based on Phase 3 demand forecasts,
statistical safety stock, lead times, and sales velocity without fabricating inventory levels.
"""

from __future__ import annotations

from datetime import datetime, timezone
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from src.recommendations.config import load_recommendation_config
from src.recommendations.explanations.evidence import build_evidence
from src.recommendations.inventory.reorder_logic import (
    calculate_reorder_point,
    calculate_reorder_quantity,
    calculate_safety_stock,
)
from src.recommendations.schemas import (
    ConflictCategory,
    Evidence,
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


class InventoryRecommendationEngine:
    """Produces prioritized restock recommendations with statistical safety stock."""

    def __init__(self, config_path: str = "configs/recommendations.yaml") -> None:
        self.config = load_recommendation_config(config_path)
        self.inv_cfg = self.config.get("inventory", {})
        self.scoring_cfg = self.config.get("scoring", {})
        self.prio_thresholds = self.config.get("priority_thresholds", {})

    def generate_recommendations(
        self,
        demand_forecast_df: pd.DataFrame,
        product_features_df: pd.DataFrame,
        transactions_df: pd.DataFrame,
        product_id: Optional[str] = None,
    ) -> List[Recommendation]:
        """
        Analyzes product-level forward demand, velocity, and variance to produce restock recommendations.
        """
        recommendations: List[Recommendation] = []
        if demand_forecast_df.empty or product_features_df.empty:
            logger.warning("Empty forecast or product features provided to inventory engine.")
            return recommendations

        # Precompute historical daily demand std and daily velocity per product
        tx = transactions_df.copy()
        if "date" not in tx.columns and "timestamp" in tx.columns:
            tx["date"] = pd.to_datetime(tx["timestamp"]).dt.strftime("%Y-%m-%d")

        daily_units = tx.groupby(["product_id", "date"])["quantity"].sum().reset_index()
        hist_std_map = daily_units.groupby("product_id")["quantity"].std().fillna(1.0).to_dict()
        hist_mean_map = daily_units.groupby("product_id")["quantity"].mean().fillna(1.0).to_dict()

        # Sum 7-day predicted units per product
        forecast_7d = demand_forecast_df.groupby("product_id")["predicted_units"].sum().to_dict()

        # Catalog metadata
        prod_meta = product_features_df.set_index("product_id").to_dict(orient="index")

        target_products = [product_id] if product_id else list(product_features_df["product_id"].unique())
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        lead_time = int(self.inv_cfg.get("lead_time_days", 3))
        z_score = float(self.inv_cfg.get("z_score", 1.645))
        min_reorder = int(self.inv_cfg.get("min_reorder_units", 5))

        for pid in target_products:
            if pid not in prod_meta:
                continue

            meta = prod_meta[pid]
            pname = meta.get("product_name", pid)
            category = meta.get("product_category", "General")
            unit_cost = float(meta.get("unit_cost", 50.0))
            selling_price = float(meta.get("selling_price", 100.0))
            margin = max(0.0, round(selling_price - unit_cost, 2))
            margin_pct = round(margin / max(1e-9, selling_price), 2)

            f_units = float(forecast_7d.get(pid, 0.0))
            h_std = float(hist_std_map.get(pid, 1.0))
            h_velocity = float(hist_mean_map.get(pid, 1.0))

            safety_stock = calculate_safety_stock(h_std, lead_time_days=lead_time, z_score=z_score)
            daily_forecast_velocity = max(0.1, f_units / 7.0)
            reorder_point = calculate_reorder_point(daily_forecast_velocity, lead_time_days=lead_time, safety_stock=safety_stock)
            rec_quantity = calculate_reorder_quantity(f_units, safety_stock, min_units=min_reorder)

            # Filter out SKUs with negligible demand
            if f_units < 1.0 and h_velocity < 0.5:
                continue

            # Urgency: proportional to forecast vs historical velocity and lead time coverage
            velocity_ratio = daily_forecast_velocity / max(0.1, h_velocity)
            urgency = float(np.clip(0.40 + 0.30 * min(velocity_ratio, 2.0) + 0.15 * (margin_pct), 0.20, 0.95))

            # Impact: scale by revenue and margin contribution
            estimated_revenue = f_units * selling_price
            rev_opp = float(np.clip(estimated_revenue / 15000.0, 0.20, 0.95))
            margin_opp = float(np.clip(margin_pct * 1.5, 0.20, 0.90))
            impact_score = compute_impact(
                revenue_opportunity=rev_opp,
                margin_opportunity=margin_opp,
                customer_value=0.50,
                urgency=urgency,
                scale=float(np.clip(f_units / 50.0, 0.20, 0.90)),
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
                build_evidence("forecast_7d_units", round(f_units, 1), "Phase 3 Demand Model", "Expected 7-day customer unit demand"),
                build_evidence("daily_demand_velocity", round(daily_forecast_velocity, 2), "Phase 3 Demand Model", "Forecasted units per day"),
                build_evidence("safety_stock_units", safety_stock, "Statistical Formula", f"Z={z_score} safety buffer for 95% service level"),
                build_evidence("reorder_point_units", reorder_point, "Statistical Formula", f"Trigger threshold across {lead_time} days lead time"),
                build_evidence("unit_margin", margin, "Product Catalog", f"Unit profit ₹{margin:.2f} ({margin_pct*100:.0f}% margin)"),
                build_evidence("inventory_estimation_mode", True, "System Configuration", "Recommendation based on forecast demand and historical velocity"),
            ]

            title = f"Restock {pname} ({category})"
            action = f"Order approximately {rec_quantity} units to cover 7-day forecast demand of {f_units:.0f} units and {safety_stock:.0f} units safety stock."
            reason = (
                f"Projected 7-day demand is {f_units:.0f} units with daily velocity of {daily_forecast_velocity:.1f} units/day. "
                f"With an estimated {lead_time}-day supplier lead time, initiating a reorder of {rec_quantity} units protects against stockouts. "
                f"(Inventory data unavailable — recommendation based on forecast demand and historical sales velocity)."
            )

            rec = Recommendation(
                recommendation_id=f"REC_INV_{pid}",
                merchant_id=None,
                type=RecommendationType.RESTOCK,
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
                conflict_category=ConflictCategory.RISK,
                created_at=now_str,
                status=LifecycleState.GENERATED,
            )
            recommendations.append(rec)

        recommendations.sort(key=lambda r: r.priority, reverse=True)
        logger.info("Generated %d inventory recommendations.", len(recommendations))
        return recommendations
