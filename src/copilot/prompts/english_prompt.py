"""
English prompt formatter for VyaparMitra Copilot.
Formats prompt instruction asking for clear English response grounded in BusinessContext.
"""

from __future__ import annotations

import json
from src.copilot.schemas import BusinessContext


def format_english_prompt(query: str, context: BusinessContext) -> str:
    """Formats prompt requiring professional yet accessible merchant English output grounded in context."""
    facts_str = "\n".join([f"- {f.key}: {f.value} (Source: {f.source})" for f in context.facts])
    metrics_str = json.dumps(context.metrics, indent=2, ensure_ascii=False)
    recs_str = json.dumps(context.recommendations, indent=2, ensure_ascii=False)
    knowledge_str = "\n".join([f"- {k}" for k in context.knowledge_snippets])

    return f"""
[Merchant Question]:
{query}

[Verified Business Context]:
-- Facts --
{facts_str or "No direct facts recorded."}

-- Metrics --
{metrics_str}

-- Recommendations --
{recs_str}

-- Knowledge Snippets --
{knowledge_str or "None."}

[Instruction]:
Respond in clear, practical, merchant-friendly English.
Ensure all figures, amounts, product SKUs, and advice strictly match the figures in the context above.
Do not hallucinate or invent any figures.
""".strip()
