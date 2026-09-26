"""
Recommendation Deduplication Engine for VyaparMitra.
Consolidates duplicate recommendations targeting the same entity and action type,
merging evidence and retaining the highest-confidence scores.
"""

from __future__ import annotations

from collections import defaultdict
import logging
from typing import Dict, List
from src.recommendations.schemas import Evidence, Recommendation

logger = logging.getLogger(__name__)


class RecommendationDeduplicator:
    """Merges multiple overlapping recommendations targeting the same entity and action."""

    def deduplicate(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        """
        Collapses duplicates sharing (entity_type, entity_id, type).
        Combines evidence metrics without duplicates and preserves maximal priority.
        """
        if not recommendations:
            return []

        grouped = defaultdict(list)
        for rec in recommendations:
            key = (rec.entity_type, rec.entity_id, rec.type)
            grouped[key].append(rec)

        deduped: List[Recommendation] = []
        for key, recs in grouped.items():
            if len(recs) == 1:
                deduped.append(recs[0])
                continue

            # Pick highest priority as base
            primary = max(recs, key=lambda r: r.priority)

            # Merge unique evidence metrics
            seen_metrics = set()
            merged_evidence: List[Evidence] = []
            for r in recs:
                for ev in r.evidence:
                    if ev.metric not in seen_metrics:
                        seen_metrics.add(ev.metric)
                        merged_evidence.append(ev)

            # Construct consolidated recommendation
            consolidated = primary.model_copy(
                update={"evidence": merged_evidence}
            )
            deduped.append(consolidated)

        logger.debug("Deduplicated %d raw recommendations into %d consolidated recommendations.", len(recommendations), len(deduped))
        return deduped
