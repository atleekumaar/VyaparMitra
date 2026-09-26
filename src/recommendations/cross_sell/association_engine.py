"""
Market Basket and Cross-Sell Association Engine for VyaparMitra.
Computes statistically valid association rules (Support, Confidence, Lift)
across customer co-purchasing histories to suggest high-conversion cross-sells.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from itertools import combinations
import logging
from typing import Any, Dict, List, Optional, Tuple
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


class CrossSellAssociationEngine:
    """Discovers high-lift product affinity pairs and generates cross-sell recommendations."""

    def __init__(self, config_path: str = "configs/recommendations.yaml") -> None:
        self.config = load_recommendation_config(config_path)
        self.cross_cfg = self.config.get("cross_sell", {})
        self.scoring_cfg = self.config.get("scoring", {})
        self.prio_thresholds = self.config.get("priority_thresholds", {})

    def extract_association_rules(
        self,
        transactions_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Mines association rules across customer transaction histories.
        Returns DataFrame with columns:
        [antecedent_product, consequent_product, support, confidence, lift, transaction_count]
        """
        if transactions_df.empty:
            return pd.DataFrame()

        # Group distinct products purchased per customer basket
        cust_baskets = transactions_df.groupby("customer_id")["product_id"].apply(lambda s: sorted(set(s))).tolist()
        n_baskets = len(cust_baskets)
        if n_baskets == 0:
            return pd.DataFrame()

        # Single item frequencies
        item_counts = defaultdict(int)
        for basket in cust_baskets:
            for item in basket:
                item_counts[item] += 1

        # Pair frequencies
        pair_counts = defaultdict(int)
        for basket in cust_baskets:
            if len(basket) >= 2:
                for a, b in combinations(basket, 2):
                    pair_counts[(a, b)] += 1

        min_supp = float(self.cross_cfg.get("min_support", 0.005))
        min_conf = float(self.cross_cfg.get("min_confidence", 0.08))
        min_lift = float(self.cross_cfg.get("min_lift", 1.15))

        rules = []
        for (a, b), count in pair_counts.items():
            supp_ab = count / n_baskets
            if supp_ab < min_supp:
                continue

            supp_a = item_counts[a] / n_baskets
            supp_b = item_counts[b] / n_baskets

            # Direction 1: A -> B
            conf_a_b = count / item_counts[a]
            lift_a_b = supp_ab / (supp_a * supp_b)
            if conf_a_b >= min_conf and lift_a_b >= min_lift:
                rules.append({
                    "antecedent_product": a,
                    "consequent_product": b,
                    "support": round(supp_ab, 4),
                    "confidence": round(conf_a_b, 4),
                    "lift": round(lift_a_b, 3),
                    "transaction_count": count,
                })

            # Direction 2: B -> A
            conf_b_a = count / item_counts[b]
            lift_b_a = supp_ab / (supp_a * supp_b)
            if conf_b_a >= min_conf and lift_b_a >= min_lift:
                rules.append({
                    "antecedent_product": b,
                    "consequent_product": a,
                    "support": round(supp_ab, 4),
                    "confidence": round(conf_b_a, 4),
                    "lift": round(lift_b_a, 3),
                    "transaction_count": count,
                })

        rules_df = pd.DataFrame(rules)
        if not rules_df.empty:
            rules_df = rules_df.sort_values(by=["lift", "confidence"], ascending=[False, False]).reset_index(drop=True)
        return rules_df

    def generate_recommendations(
        self,
        transactions_df: pd.DataFrame,
        product_features_df: pd.DataFrame,
        product_id: Optional[str] = None,
    ) -> List[Recommendation]:
        """
        Generates cross-sell recommendations from mined association rules.
        """
        recommendations: List[Recommendation] = []
        rules_df = self.extract_association_rules(transactions_df)
        if rules_df.empty or product_features_df.empty:
            return recommendations

        if product_id:
            rules_df = rules_df[rules_df["antecedent_product"] == product_id]

        prod_meta = product_features_df.set_index("product_id").to_dict(orient="index")
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        max_rules = int(self.cross_cfg.get("max_rules_per_product", 3))
        # Keep top rules per antecedent
        rules_df = rules_df.groupby("antecedent_product").head(max_rules).reset_index(drop=True)

        for _, row in rules_df.iterrows():
            a_id = str(row["antecedent_product"])
            b_id = str(row["consequent_product"])
            lift = float(row["lift"])
            conf = float(row["confidence"])
            supp = float(row["support"])
            tx_count = int(row["transaction_count"])

            a_meta = prod_meta.get(a_id, {})
            b_meta = prod_meta.get(b_id, {})

            a_name = a_meta.get("product_name", a_id)
            b_name = b_meta.get("product_name", b_id)
            b_price = float(b_meta.get("selling_price", 100.0))

            urgency = 0.55
            # Impact: driven by cross-sell lift, confidence, and target basket value
            impact_score = compute_impact(
                revenue_opportunity=float(np.clip(conf * (b_price / 1000.0), 0.20, 0.85)),
                margin_opportunity=0.55,
                customer_value=0.50,
                urgency=urgency,
                scale=float(np.clip(tx_count / 100.0, 0.20, 0.85)),
                weights=self.scoring_cfg.get("impact_weights"),
            )

            confidence_score = compute_confidence(
                prediction_confidence=float(np.clip(conf, 0.40, 0.90)),
                evidence_strength=float(np.clip(lift / 2.0, 0.50, 0.95)),
                historical_consistency=0.85,
                data_quality=0.90,
                weights=self.scoring_cfg.get("confidence_weights"),
            )

            priority_score = compute_priority(impact_score, confidence_score, urgency)
            priority_band = assign_priority_band(priority_score, self.prio_thresholds)

            evidence_items = [
                build_evidence("association_lift", lift, "Association Rule Mining", f"Purchasing {a_name} multiplies odds of purchasing {b_name} by {lift:.2f}x"),
                build_evidence("rule_confidence", conf, "Association Rule Mining", f"{conf*100:.1f}% of {a_name} buyers also ordered {b_name}"),
                build_evidence("rule_support", supp, "Association Rule Mining", f"Observed across {supp*100:.2f}% of customer shopping journeys"),
                build_evidence("shared_transaction_count", tx_count, "Historical Transactions", f"Co-purchased by {tx_count} verified customers"),
            ]

            title = f"Cross-Sell Pair: {a_name} -> {b_name}"
            action = f"Display {b_name} as an automatic checkout add-on whenever {a_name} is added to the cart."
            reason = (
                f"Historical transaction affinity shows that customers purchasing {a_name} have a "
                f"{conf*100:.1f}% probability of buying {b_name} (Lift = {lift:.2f}x across {tx_count} customers). "
                f"Note: This is an observed co-occurrence pattern, not a causal guarantee."
            )

            rec = Recommendation(
                recommendation_id=f"REC_CROSS_{a_id}_{b_id}",
                merchant_id=None,
                type=RecommendationType.CROSS_SELL,
                priority=priority_score,
                priority_band=priority_band,
                confidence=confidence_score,
                urgency=urgency,
                expected_impact=impact_score,
                entity_type="product_pair",
                entity_id=f"{a_id}->{b_id}",
                title=title,
                action=action,
                reason=reason,
                evidence=evidence_items,
                conflict_category=ConflictCategory.REVENUE_GROWTH,
                created_at=now_str,
                status=LifecycleState.GENERATED,
            )
            recommendations.append(rec)

        recommendations.sort(key=lambda r: r.priority, reverse=True)
        logger.info("Generated %d cross-sell recommendations.", len(recommendations))
        return recommendations
