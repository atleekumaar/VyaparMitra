"""
Unified Recommendation & Decision Engine for VyaparMitra Phase 4.
Orchestrates inventory, sales opportunities, customer retention, cross-sell, and pricing engines
into a cohesive, prioritized merchant decision support platform.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd
import yaml

from src.recommendations.config import load_recommendation_config
from src.recommendations.conflicts.resolver import ConflictResolver
from src.recommendations.cross_sell.association_engine import CrossSellAssociationEngine
from src.recommendations.customers.customer_actions import CustomerActionEngine
from src.recommendations.deduplication.deduplicator import RecommendationDeduplicator
from src.recommendations.explanations.evidence import format_explanation
from src.recommendations.inventory.inventory_engine import InventoryRecommendationEngine
from src.recommendations.pricing.pricing_engine import PricingRecommendationEngine
from src.recommendations.products.product_actions import ProductActionEngine
from src.recommendations.schemas import (
    LifecycleState,
    PriorityBand,
    Recommendation,
    RecommendationType,
)

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Unified Facade for VyaparMitra Phase 4 Recommendation Engine."""

    def __init__(
        self,
        config_path: str = "configs/recommendations.yaml",
        main_config_path: str = "configs/config.yaml",
    ) -> None:
        self.config_path = config_path
        self.config = load_recommendation_config(config_path)

        with open(main_config_path, "r", encoding="utf-8") as f:
            main_cfg = yaml.safe_load(f)

        paths = main_cfg.get("paths", {})
        self.features_dir = Path(paths.get("features", "data/features"))
        self.processed_dir = Path(paths.get("processed", "data/processed"))
        self.analytics_dir = Path(paths.get("analytics", "data/analytics"))
        self.ml_dir = Path(paths.get("ml", "data/ml"))
        self.output_dir = Path(paths.get("recommendations", "data/recommendations"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Sub-engines
        self.inventory_engine = InventoryRecommendationEngine(config_path=config_path)
        self.product_engine = ProductActionEngine(config_path=config_path)
        self.customer_engine = CustomerActionEngine(config_path=config_path)
        self.cross_sell_engine = CrossSellAssociationEngine(config_path=config_path)
        self.pricing_engine = PricingRecommendationEngine(config_path=config_path)
        self.conflict_resolver = ConflictResolver(config_path=config_path)
        self.deduplicator = RecommendationDeduplicator()

        # Cached datasets
        self._product_features: Optional[pd.DataFrame] = None
        self._customer_features: Optional[pd.DataFrame] = None
        self._clean_transactions: Optional[pd.DataFrame] = None
        self._demand_forecast: Optional[pd.DataFrame] = None
        self._sales_forecast: Optional[pd.DataFrame] = None
        self._customer_risk: Optional[pd.DataFrame] = None
        self._business_trend: Optional[pd.DataFrame] = None

    # Lazy loaders
    def get_product_features(self) -> pd.DataFrame:
        if self._product_features is None:
            path = self.features_dir / "product_features.parquet"
            self._product_features = pd.read_parquet(path) if path.exists() else pd.DataFrame()
        return self._product_features

    def get_customer_features(self) -> pd.DataFrame:
        if self._customer_features is None:
            path = self.features_dir / "customer_features.parquet"
            self._customer_features = pd.read_parquet(path) if path.exists() else pd.DataFrame()
        return self._customer_features

    def get_clean_transactions(self) -> pd.DataFrame:
        if self._clean_transactions is None:
            path = self.processed_dir / "clean_transactions.parquet"
            if not path.exists():
                path = self.processed_dir / "cleaned_transactions.parquet"
            self._clean_transactions = pd.read_parquet(path) if path.exists() else pd.DataFrame()
        return self._clean_transactions

    def get_demand_forecast(self) -> pd.DataFrame:
        if self._demand_forecast is None:
            path = self.ml_dir / "forecasts" / "product_demand_forecast_7d.parquet"
            self._demand_forecast = pd.read_parquet(path) if path.exists() else pd.DataFrame()
        return self._demand_forecast

    def get_sales_forecast(self) -> pd.DataFrame:
        if self._sales_forecast is None:
            path = self.ml_dir / "forecasts" / "sales_forecast_7d.parquet"
            self._sales_forecast = pd.read_parquet(path) if path.exists() else pd.DataFrame()
        return self._sales_forecast

    def get_customer_risk(self) -> pd.DataFrame:
        if self._customer_risk is None:
            path = self.ml_dir / "customer_risk" / "customer_risk_scores.parquet"
            self._customer_risk = pd.read_parquet(path) if path.exists() else pd.DataFrame()
        return self._customer_risk

    def get_business_trend(self) -> pd.DataFrame:
        if self._business_trend is None:
            path = self.ml_dir / "trends" / "business_trend_predictions.parquet"
            self._business_trend = pd.read_parquet(path) if path.exists() else pd.DataFrame()
        return self._business_trend

    # Subsystem execution
    def inventory_recommendations(self, product_id: Optional[str] = None) -> List[Recommendation]:
        """Generates inventory restock and safety stock recommendations."""
        return self.inventory_engine.generate_recommendations(
            demand_forecast_df=self.get_demand_forecast(),
            product_features_df=self.get_product_features(),
            transactions_df=self.get_clean_transactions(),
            product_id=product_id,
        )

    def sales_opportunities(self, product_id: Optional[str] = None) -> List[Recommendation]:
        """Generates commercial sales and SKU focus recommendations."""
        return self.product_engine.generate_recommendations(
            product_features_df=self.get_product_features(),
            demand_forecast_df=self.get_demand_forecast(),
            trend_df=self.get_business_trend(),
            product_id=product_id,
        )

    def customer_recommendations(self, customer_id: Optional[str] = None) -> List[Recommendation]:
        """Generates customer retention and re-engagement recommendations."""
        seg_path = self.analytics_dir / "customers" / "customer_segments.parquet"
        seg_df = pd.read_parquet(seg_path) if seg_path.exists() else None
        return self.customer_engine.generate_recommendations(
            customer_risk_df=self.get_customer_risk(),
            customer_features_df=self.get_customer_features(),
            customer_segments_df=seg_df,
            customer_id=customer_id,
        )

    def cross_sell_recommendations(self, product_id: Optional[str] = None) -> List[Recommendation]:
        """Generates co-purchase and market basket cross-sell recommendations."""
        return self.cross_sell_engine.generate_recommendations(
            transactions_df=self.get_clean_transactions(),
            product_features_df=self.get_product_features(),
            product_id=product_id,
        )

    def pricing_recommendations(self, product_id: Optional[str] = None) -> List[Recommendation]:
        """Generates margin defense, pricing, and promotional discount recommendations."""
        return self.pricing_engine.generate_recommendations(
            product_features_df=self.get_product_features(),
            demand_forecast_df=self.get_demand_forecast(),
            transactions_df=self.get_clean_transactions(),
            product_id=product_id,
        )

    def product_recommendations(self, product_id: str) -> List[Recommendation]:
        """Collects and deduplicates all recommendations pertaining to a specific product SKU."""
        all_recs = []
        all_recs.extend(self.inventory_recommendations(product_id=product_id))
        all_recs.extend(self.sales_opportunities(product_id=product_id))
        all_recs.extend(self.cross_sell_recommendations(product_id=product_id))
        all_recs.extend(self.pricing_recommendations(product_id=product_id))

        resolved = self.conflict_resolver.resolve(all_recs)
        deduped = self.deduplicator.deduplicate(resolved)
        deduped.sort(key=lambda r: r.priority, reverse=True)
        return deduped

    def daily_action_plan(
        self,
        merchant_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[Recommendation]:
        """
        Produces top ranked merchant action plan across all recommendation types.
        Filters conflicts, deduplicates, and orders strictly by composite Priority.
        """
        all_recs = self.get_all_unified_recommendations(merchant_id=merchant_id)
        return all_recs[:limit]

    def get_all_unified_recommendations(
        self,
        merchant_id: Optional[str] = None,
    ) -> List[Recommendation]:
        """Collects, resolves conflicts, and deduplicates all system recommendations."""
        raw_recs: List[Recommendation] = []
        raw_recs.extend(self.inventory_recommendations())
        raw_recs.extend(self.sales_opportunities())
        raw_recs.extend(self.customer_recommendations())
        raw_recs.extend(self.cross_sell_recommendations())
        raw_recs.extend(self.pricing_recommendations())

        resolved = self.conflict_resolver.resolve(raw_recs)
        deduped = self.deduplicator.deduplicate(resolved)
        deduped.sort(key=lambda r: r.priority, reverse=True)
        return deduped

    def generate_all(
        self,
        merchant_id: Optional[str] = None,
        export: bool = True,
    ) -> Dict[str, Any]:
        """
        Executes end-to-end recommendation generation and exports all artifacts.
        """
        logger.info("Executing Phase 4 recommendation pipeline...")
        inv_recs = self.inventory_recommendations()
        sales_recs = self.sales_opportunities()
        cust_recs = self.customer_recommendations()
        cross_recs = self.cross_sell_recommendations()
        price_recs = self.pricing_recommendations()

        unified_recs = self.get_all_unified_recommendations(merchant_id=merchant_id)
        action_plan = unified_recs[:50]

        counts = {
            "total_recommendations": len(unified_recs),
            "inventory": len(inv_recs),
            "sales_opportunities": len(sales_recs),
            "customer_retention": len(cust_recs),
            "cross_sell": len(cross_recs),
            "pricing": len(price_recs),
        }

        # Priority distribution
        prio_counts = {
            PriorityBand.CRITICAL.value: sum(1 for r in unified_recs if r.priority_band == PriorityBand.CRITICAL),
            PriorityBand.HIGH.value: sum(1 for r in unified_recs if r.priority_band == PriorityBand.HIGH),
            PriorityBand.MEDIUM.value: sum(1 for r in unified_recs if r.priority_band == PriorityBand.MEDIUM),
            PriorityBand.LOW.value: sum(1 for r in unified_recs if r.priority_band == PriorityBand.LOW),
        }

        if export:
            self._export_artifacts(
                inv_recs=inv_recs,
                sales_recs=sales_recs,
                cust_recs=cust_recs,
                cross_recs=cross_recs,
                price_recs=price_recs,
                all_recs=unified_recs,
                action_plan=action_plan,
                prio_counts=prio_counts,
                counts=counts,
            )

        logger.info("Phase 4 recommendation pipeline complete: %d recommendations generated.", len(unified_recs))
        return {
            "counts": counts,
            "priority_distribution": prio_counts,
            "action_plan_count": len(action_plan),
        }

    def _export_artifacts(
        self,
        inv_recs: List[Recommendation],
        sales_recs: List[Recommendation],
        cust_recs: List[Recommendation],
        cross_recs: List[Recommendation],
        price_recs: List[Recommendation],
        all_recs: List[Recommendation],
        action_plan: List[Recommendation],
        prio_counts: Dict[str, int],
        counts: Dict[str, int],
    ) -> None:
        """Exports Parquet, CSV, and Markdown decision artifacts."""

        def to_df(recs: List[Recommendation]) -> pd.DataFrame:
            if not recs:
                return pd.DataFrame()
            rows = []
            for r in recs:
                rows.append({
                    "recommendation_id": r.recommendation_id,
                    "merchant_id": r.merchant_id,
                    "type": r.type.value,
                    "priority": r.priority,
                    "priority_band": r.priority_band.value,
                    "confidence": r.confidence,
                    "urgency": r.urgency,
                    "expected_impact": r.expected_impact,
                    "entity_type": r.entity_type,
                    "entity_id": r.entity_id,
                    "title": r.title,
                    "action": r.action,
                    "reason": r.reason,
                    "created_at": r.created_at,
                    "status": r.status.value,
                })
            return pd.DataFrame(rows)

        def to_evidence_df(recs: List[Recommendation]) -> pd.DataFrame:
            rows = []
            for r in recs:
                for ev in r.evidence:
                    rows.append({
                        "recommendation_id": r.recommendation_id,
                        "entity_id": r.entity_id,
                        "metric": ev.metric,
                        "value": str(ev.value),
                        "source": ev.source,
                        "description": ev.description,
                    })
            return pd.DataFrame(rows)

        # 1. Parquet & CSV exports
        datasets = {
            "inventory_recommendations": to_df(inv_recs),
            "sales_opportunities": to_df(sales_recs),
            "customer_recommendations": to_df(cust_recs),
            "cross_sell_recommendations": to_df(cross_recs),
            "pricing_recommendations": to_df(price_recs),
            "all_recommendations": to_df(all_recs),
            "merchant_action_plan": to_df(action_plan),
            "recommendation_evidence": to_evidence_df(all_recs),
        }

        for name, df in datasets.items():
            if not df.empty:
                df.to_parquet(self.output_dir / f"{name}.parquet", index=False)
                df.to_csv(self.output_dir / f"{name}.csv", index=False)

        # 2. Generate daily_action_plan.md
        self._write_action_plan_md(action_plan)

        # 3. Generate recommendation_summary.md
        self._write_summary_md(counts, prio_counts, all_recs)

    def _write_action_plan_md(self, action_plan: List[Recommendation]) -> None:
        path = self.output_dir / "daily_action_plan.md"
        emoji_map = {
            PriorityBand.CRITICAL: "🔴 CRITICAL",
            PriorityBand.HIGH: "🟠 HIGH",
            PriorityBand.MEDIUM: "🟡 MEDIUM",
            PriorityBand.LOW: "🟢 LOW",
        }

        md = [
            "# VyaparMitra — Daily Merchant Action Plan\n",
            f"**Generated At**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n",
            "This document presents the top prioritized commercial and operational decisions for the merchant.",
            "Each action is backed by empirical evidence from Phase 1 features, Phase 2 analytics, and Phase 3 ML predictions.\n",
            "## Top Prioritized Business Actions\n",
        ]

        for idx, rec in enumerate(action_plan[:30], 1):
            band_str = emoji_map.get(rec.priority_band, rec.priority_band.value)
            md.append(f"### {idx}. [{band_str}] {rec.title}")
            md.append(f"**Action**: {rec.action}\n")
            md.append(f"**Why**: {rec.reason}\n")
            md.append("**Evidence**:")
            for ev in rec.evidence:
                desc = f" ({ev.description})" if ev.description else ""
                md.append(f"- `{ev.metric}`: **{ev.value}**{desc} — *Source: {ev.source}*")
            md.append(f"\n*Priority Score*: `{rec.priority:.4f}` | *Confidence*: `{rec.confidence:.2f}` | *Urgency*: `{rec.urgency:.2f}` | *Expected Impact*: `{rec.expected_impact:.2f}`\n")
            md.append("---\n")

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(md))

    def _write_summary_md(
        self,
        counts: Dict[str, int],
        prio_counts: Dict[str, int],
        all_recs: List[Recommendation],
    ) -> None:
        path = self.output_dir / "recommendation_summary.md"
        md = [
            "# VyaparMitra — Recommendation Engine Summary Report\n",
            f"**Execution Timestamp**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n",
            "## 1. Executive Metrics Overview\n",
            f"- **Total Consolidated Recommendations**: {counts.get('total_recommendations', 0)}",
            f"- **🔴 Critical Actions**: {prio_counts.get(PriorityBand.CRITICAL.value, 0)}",
            f"- **🟠 High Priority Actions**: {prio_counts.get(PriorityBand.HIGH.value, 0)}",
            f"- **🟡 Medium Priority Actions**: {prio_counts.get(PriorityBand.MEDIUM.value, 0)}",
            f"- **🟢 Low Priority Actions**: {prio_counts.get(PriorityBand.LOW.value, 0)}\n",
            "## 2. Recommendation Breakdown by System\n",
            "| Subsystem | Recommendation Type | Count |",
            "|---|---|---|",
            f"| **Inventory & Restock** | `RESTOCK` | {counts.get('inventory', 0)} |",
            f"| **Sales Opportunities** | `FOCUS`, `PROMOTE`, `BUNDLE`, `MONITOR` | {counts.get('sales_opportunities', 0)} |",
            f"| **Customer Retention** | `RETENTION`, `RE_ENGAGEMENT`, `PERSONALIZED_OFFER` | {counts.get('customer_retention', 0)} |",
            f"| **Cross-Sell Affinities** | `CROSS_SELL` | {counts.get('cross_sell', 0)} |",
            f"| **Pricing & Margin Defense** | `MAINTAIN_PRICE`, `REVIEW_MARGIN`, `LIMIT_DISCOUNT`, `CLEARANCE` | {counts.get('pricing', 0)} |",
            f"| **Total Consolidated** | All Systems | **{counts.get('total_recommendations', 0)}** |\n",
            "## 3. Data Integrity & Observational Safeguards\n",
            "- **Inventory Estimation**: Since live warehouse telemetry is unobserved, inventory guidance operates in `inventory_estimation_mode = True` without fabricating stock counts.",
            "- **Non-Causal Association Rules**: Cross-sell affinities denote observed co-purchase lift, avoiding false causal promises.",
            "- **Margin Protection Priority**: Resolves conflicting advice by giving precedence to data quality, risk mitigation, and margin preservation.",
        ]

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(md))
