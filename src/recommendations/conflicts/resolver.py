"""
Deterministic Conflict Resolution Engine for VyaparMitra Recommendations.
Resolves opposing business recommendations for the same entity using strict priority hierarchy:
DATA_QUALITY > RISK > MARGIN_PROTECTION > REVENUE_GROWTH > EXPERIMENTAL_ACTION.
"""

from __future__ import annotations

from collections import defaultdict
import logging
from typing import Dict, List, Optional
from src.recommendations.config import load_recommendation_config
from src.recommendations.schemas import ConflictCategory, Recommendation, RecommendationType

logger = logging.getLogger(__name__)

# Mutually conflicting pairs of action types
OPPOSING_ACTION_PAIRS = {
    (RecommendationType.PROMOTE, RecommendationType.MAINTAIN_PRICE),
    (RecommendationType.MAINTAIN_PRICE, RecommendationType.PROMOTE),
    (RecommendationType.PROMOTE, RecommendationType.REVIEW_MARGIN),
    (RecommendationType.REVIEW_MARGIN, RecommendationType.PROMOTE),
    (RecommendationType.CLEARANCE, RecommendationType.RESTOCK),
    (RecommendationType.RESTOCK, RecommendationType.CLEARANCE),
    (RecommendationType.CLEARANCE, RecommendationType.MAINTAIN_PRICE),
    (RecommendationType.MAINTAIN_PRICE, RecommendationType.CLEARANCE),
    (RecommendationType.RETENTION, RecommendationType.NO_ACTION),
    (RecommendationType.NO_ACTION, RecommendationType.RETENTION),
}


class ConflictResolver:
    """Detects and resolves contradictory recommendations on the same business entity."""

    def __init__(self, config_path: str = "configs/recommendations.yaml") -> None:
        self.config = load_recommendation_config(config_path)
        self.order: List[str] = self.config.get(
            "conflict_resolution_order",
            ["DATA_QUALITY", "RISK", "MARGIN_PROTECTION", "REVENUE_GROWTH", "EXPERIMENTAL_ACTION"],
        )
        self.rank_map: Dict[str, int] = {cat: idx for idx, cat in enumerate(self.order)}

    def resolve(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        """
        Resolves conflicts across recommendations.
        Groups by (entity_type, entity_id), detects incompatible pairs, and keeps the champion.
        """
        if not recommendations:
            return []

        # Group by entity
        grouped = defaultdict(list)
        for rec in recommendations:
            grouped[(rec.entity_type, rec.entity_id)].append(rec)

        resolved_list: List[Recommendation] = []
        for (etype, eid), recs in grouped.items():
            if len(recs) <= 1:
                resolved_list.extend(recs)
                continue

            # Check if any pair conflicts
            has_conflict = False
            for i in range(len(recs)):
                for j in range(i + 1, len(recs)):
                    if (recs[i].type, recs[j].type) in OPPOSING_ACTION_PAIRS:
                        has_conflict = True
                        break
                if has_conflict:
                    break

            if not has_conflict:
                resolved_list.extend(recs)
                continue

            # Deterministic conflict resolution:
            # 1. Lower rank index in resolution order (e.g. RISK < REVENUE_GROWTH)
            # 2. If tie in category, higher priority score
            def sort_key(r: Recommendation):
                cat_str = r.conflict_category.value if hasattr(r.conflict_category, "value") else str(r.conflict_category)
                rank = self.rank_map.get(cat_str, 99)
                return (rank, -r.priority)

            champion = min(recs, key=sort_key)
            logger.debug(
                "Conflict detected on %s:%s. Selected %s over other candidates.",
                etype, eid, champion.type.value
            )
            # Add surviving champion plus any non-opposing recommendations
            survivors = [champion]
            for r in recs:
                if r.recommendation_id == champion.recommendation_id:
                    continue
                # If r does NOT conflict with the champion, keep it
                if (champion.type, r.type) not in OPPOSING_ACTION_PAIRS:
                    survivors.append(r)

            resolved_list.extend(survivors)

        return resolved_list
