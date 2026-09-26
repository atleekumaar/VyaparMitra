"""
Evidence extraction and human-readable explanation formatter.
Transforms machine-readable metrics into clear, explainable business rationale.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from src.recommendations.schemas import Evidence, Recommendation


def build_evidence(
    metric: str,
    value: Any,
    source: str,
    description: Optional[str] = None,
) -> Evidence:
    """Helper to construct strongly-typed Evidence object."""
    return Evidence(
        metric=metric,
        value=value,
        source=source,
        description=description,
    )


def format_explanation(rec: Recommendation) -> str:
    """
    Formats recommendation into standardized 6-part merchant explanation:
    WHAT, WHY, EVIDENCE, CONFIDENCE, URGENCY, EXPECTED IMPACT.
    """
    lines = [
        f"WHAT: {rec.title} ({rec.action})",
        f"WHY: {rec.reason}",
        "EVIDENCE:",
    ]
    for ev in rec.evidence:
        desc = f" ({ev.description})" if ev.description else ""
        lines.append(f"  • {ev.metric} = {ev.value}{desc} [Source: {ev.source}]")

    lines.extend([
        f"CONFIDENCE: {rec.confidence:.2f}",
        f"URGENCY: {rec.urgency:.2f}",
        f"EXPECTED IMPACT: {rec.expected_impact:.2f}",
        f"PRIORITY: {rec.priority:.2f} [{rec.priority_band.value}]",
    ])
    return "\n".join(lines)
