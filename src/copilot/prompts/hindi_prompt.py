"""
Hindi prompt formatter for VyaparMitra Copilot.
Formats prompt instruction asking for Hindi (Devanagari) response grounded in BusinessContext.
"""

from __future__ import annotations

import json
from src.copilot.schemas import BusinessContext


def format_hindi_prompt(query: str, context: BusinessContext) -> str:
    """Formats prompt requiring Devanagari Hindi output strictly grounded in context."""
    facts_str = "\n".join([f"- {f.key}: {f.value} (Source: {f.source})" for f in context.facts])
    metrics_str = json.dumps(context.metrics, indent=2, ensure_ascii=False)
    recs_str = json.dumps(context.recommendations, indent=2, ensure_ascii=False)
    knowledge_str = "\n".join([f"- {k}" for k in context.knowledge_snippets])

    return f"""
[व्यापारी का प्रश्न]:
{query}

[प्रमाणित व्यापार डेटा एवं संदर्भ]:
-- मुख्य तथ्य (Facts) --
{facts_str or "कोई विशेष तथ्य नहीं।"}

-- मेट्रिक्स (Metrics) --
{metrics_str}

-- अनुशंसित कार्य (Recommendations) --
{recs_str}

-- ज्ञान आधार संदर्भ (Knowledge) --
{knowledge_str or "लागू नहीं।"}

[निर्देश]:
कृपया व्यापारी के प्रश्न का उत्तर शुद्ध, आदरसूचक एवं सरल हिंदी (देवनागरी लिपि) में दें।
उत्तर में केवल दिए गए डेटा के आंकड़ों और सुझावों का ही उपयोग करें। किसी नए आंकड़े या उत्पाद का अनुमान न लगाएं।
""".strip()
