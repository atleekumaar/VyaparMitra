"""
Intent classification for Hindi, Hinglish, and English merchant queries.
Uses deterministic pattern matching, intent heuristics, and entity cues.
"""

from __future__ import annotations

import re
from typing import Optional
from src.copilot.language.normalizer import normalize_text
from src.copilot.schemas import Intent

OUT_OF_DOMAIN_PATTERNS = [
    r"\bgdp\b", r"\bcricket\b", r"\bmatch\b", r"\bscore\b", r"\bmovie\b",
    r"\bcinema\b", r"\belection\b", r"\bpolitics\b", r"\brajniti\b",
    r"\bprime minister\b", r"\bpresident\b", r"\bweather in delhi\b",
]

INTENT_RULES = [
    # 0. Benchmark & Peer Comparison
    (
        Intent.BENCHMARK,
        [
            r"(meri dukaan|meri shop|dukaan|shop|business).*(dusron|competition|peers|market).*kaisi",
            r"(benchmark|benchmarks|tulna|compare|comparison)",
            r"(dusron se|peers se|baki dukano se).*(tulna|compare|kaisi|kaisa|rank)",
            r"how do i compare.*(peers|others|competitors|market)",
            r"मेरी दुकान दूसरों से कैसी है",
            r"तुलना.*(दुकान|बेंचमार्क|प्रतिस्पर्धा)",
        ],
    ),
    # 1. Recommendation Explanation
    (
        Intent.RECOMMENDATION_EXPLANATION,
        [
            r"(kyun|kyu|reason|evidence|kyun di|why).*recommendation",
            r"recommendation.*(kyun|kyu|reason|evidence|why)",
            r"ye recommendation kyun",
            r"is recommendation ka (reason|evidence)",
            r"ye prediction kitni reliable",
            r"ye data kaha se aaya",
            r"why.*(recommend|restock|retention)",
        ],
    ),
    # 2. Daily Action Plan & Priorities
    (
        Intent.DAILY_ACTION_PLAN,
        [
            r"aaj mujhe kya (karna|kam).*chahiye",
            r"sabse pehle kya kar",
            r"aaj ke priorities",
            r"today'?s priorities",
            r"daily action plan",
            r"aaj ke top.*actions",
            r"sabse important action kya hai",
            r"mere business ki biggest problem kya hai",
            r"what should i do today",
            r"आज मुझे क्या.*चाहिए",
            r"आज मुझे क्या.*(करना|काम)",
            r"कार्य योजना",

        ],
    ),
    # 3. Inventory & Restock
    (
        Intent.INVENTORY_RECOMMENDATION,
        [
            r"(kya|kaunsa|which|what).*restock",
            r"restock.*(karna|karein|karo|chahiye|guidance)",
            r"stock.*out.*(risk|khatra)",
            r"stock room.*(kitna maal|exactly)",
            r"maal.*(mangwana|reorder|khatam|kam)",
            r"reorder point",
            r"safety stock",
            r"what should i restock",
            r"stock out risk mein hai",
            r"out of stock",
            r"माल.*(खत्म|कम|मंगवाना)",
            r"खत्म होने वाला",
            r"काउंस.*स्टॉक",
            r"रीऑर्डर",
        ],
    ),
    # 4. Cross-Sell & Basket Affinities
    (
        Intent.CROSS_SELL,
        [
            r"(saath|sath).*bech.*(sakta|sakte|hoon)",
            r"(saath|sath).*kharid",
            r"frequently bought together",
            r"cross[- ]?sell",
            r"ke saath kya bech",
            r"what.*sell.*with",
            r"products saath mein kharidte",
            r"साथ में बेचना",
        ],
    ),
    # 5. Pricing & Promotion
    (
        Intent.PRICING_RECOMMENDATION,
        [
            r"(margin|munafa).*(low|kam|review)",
            r"(promotion|promote|discount).*(consider|kahan|limit)",
            r"price.*(maintain|badhana|ghatana|change)",
            r"clearance",
            r"kis product ka margin",
            r"kahan promotion consider",
            r"pricing recommendation",
        ],
    ),
    # 6. Customer Churn & Risk
    (
        Intent.CUSTOMER_RISK,
        [
            r"(customer|customers|grahak).*(risk|risky|churn|chhod|inactive|aana band)",
            r"kaun.*customer.*(chhod|aana band)",
            r"kaunse customers risky hain",
            r"aana band ho gaye",
            r"who.*at[- ]risk",
            r"churn risk",
            r"who are the churn",
            r"ग्राहक.*(जोखिम|रिस्क|छोड़)",
            r"कौनसे ग्राहक रिस्की",
        ],
    ),
    # 7. Customer Retention & Follow-up
    (
        Intent.RETENTION_RECOMMENDATION,
        [
            r"kisko follow[- ]?up karna chahiye",
            r"(follow[- ]?up|call|phone|message).*(customer|grahak)",
            r"retention.*(action|recommendation|priority)",
            r"kis customer ko phone karein",
            r"customer retention",
        ],
    ),
    # 8. Customer Analysis & Segments
    (
        Intent.CUSTOMER_ANALYSIS,
        [
            r"high value customers? kaun",
            r"top customers?",
            r"mere customers? kaise",
            r"customer segments?",
            r"rfm score",
            r"customer base",
        ],
    ),
    # 9. Product Demand Forecast
    (
        Intent.PRODUCT_DEMAND_FORECAST,
        [
            r"(product|sku|item).*(demand|forecast|units)",
            r"demand.*(badhegi|ghategi|forecast)",
            r"kitne piece bikenge",
            r"kaunse products ki demand badhegi",
            r"forecast of sku",
        ],
    ),
    # 10. Historical Sales Summary (Prioritized for past tense questions)
    (
        Intent.SALES_SUMMARY,
        [
            r"(kal|yesterday|pichle|last|aaj|today).*(sales|bikri|revenue|kamai).*(hui|thi|hai|tha)",
            r"(kal|yesterday).*(kitni|total).*(bikri|sales|revenue)",
            r"kal kitni bikri hui thi",
            r"kal kitni sales hui",
            r"what was.*(yesterday|sales|revenue)",
            r"yesterday'?s (sales|revenue)",
            r"pichle hafte ki total revenue",
            r"aaj meri sales kitni (hui|hai)",
            r"aaj sales kitni hui",
            r"march mein sales kaisi thi",
            r"total revenue batao",
            r"sales summary",
            r"आज मेरी बिक्री कितनी हुई",
            r"मेरी कुल बिक्री",
            r"बिक्री कितनी रही",
        ],
    ),
    # 11. Sales Forecast (Future tense and predictions)
    (
        Intent.SALES_FORECAST,
        [
            r"(agle|next|future|aane wale).*(dino|hafte|week|days|months).*(sales|bikri|revenue|forecast|hogi)",
            r"(kal|tomorrow).*(sales|bikri).*(hogi|ho sakti)",
            r"sales prediction",
            r"sales forecast",
            r"next week sales forecast",
            r"next 7 days.*sales.*forecast",
            r"भविष्य में बिक्री",
            r"बिक्री का क्या अनुमान",
            r"अगले हफ्ते का अनुमान",
        ],
    ),
    # 12. Sales Trend & Momentum
    (
        Intent.SALES_TREND,
        [
            r"sales.*(trend|gir|kyun gir|badh|momentum|direction)",
            r"bikri.*(badh|ghat|gir)",
            r"meri sales kyun gir rahi",
            r"sales ka trend kya hai",
            r"trend analysis",
        ],
    ),
    # 13. General Business Summary
    (
        Intent.GENERAL_BUSINESS_SUMMARY,
        [
            r"aaj mere business ka kya haal hai",
            r"business ka kya haal hai",
            r"overall business summary",
            r"daily brief",
            r"business brief",
            r"dukan ka haal kaisa hai",
            r"how is my business doing",
            r"business snapshot",
            r"आज मेरे व्यापार का क्या हाल है",
        ],
    ),
    # 14. Product Performance & Rankings
    (
        Intent.PRODUCT_PERFORMANCE,
        [
            r"(sabse zyada|top|best).*(bikne|selling|bikta|bika|performer|product)",
            r"product performance",
            r"top selling product",
            r"kaunsa product sabse zyada bikta hai",
            r"सबसे ज्यादा बिकने वाला",
        ],
    ),
    # 15. Payment Methods
    (
        Intent.PAYMENT_ANALYSIS,
        [
            r"(payment|upi|cash|card).*(method|breakdown|share)",
            r"upi se kitna",
            r"cash vs upi",
        ],
    ),
    # 16. Category Analysis
    (
        Intent.CATEGORY_ANALYSIS,
        [
            r"(category|categories).*(sales|performance|share)",
            r"electronics.*(sales|revenue)",
            r"grocery.*(sales|revenue)",
            r"kaunsi category top",
        ],
    ),
    # 17. Anomaly Detection
    (
        Intent.ANOMALY,
        [
            r"(anomaly|anomalies|unusual|jhatka|sudden|spike|drop)",
            r"kya koi achanak badlav",
        ],
    ),
]


def classify_intent(
    query: str,
    current_product: Optional[str] = None,
    current_customer: Optional[str] = None,
) -> Intent:
    """Classifies user query into business intent taxonomy."""
    normalized = normalize_text(query)

    # 1. Out of domain check
    for pattern in OUT_OF_DOMAIN_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            return Intent.OUT_OF_DOMAIN

    # 2. Rule-based intent matching
    for intent, patterns in INTENT_RULES:
        for p in patterns:
            if re.search(p, normalized, re.IGNORECASE) or re.search(p, query, re.IGNORECASE):
                return intent

    # 3. Fallback heuristics
    if "forecast" in normalized or "anumaan" in normalized or "अनुमान" in query:
        return Intent.SALES_FORECAST
    if "restock" in normalized or "stock" in normalized or "स्टॉक" in query or "maal" in normalized or "माल" in query:
        return Intent.INVENTORY_RECOMMENDATION
    if "risk" in normalized or "churn" in normalized or "band" in normalized or "जोखिम" in query:
        return Intent.CUSTOMER_RISK
    if "customer" in normalized or "grahak" in normalized or "ग्राहक" in query:
        return Intent.CUSTOMER_ANALYSIS
    if "product" in normalized or "उत्पाद" in query:
        return Intent.PRODUCT_PERFORMANCE
    if "sale" in normalized or "sales" in normalized or "revenue" in normalized or "bikri" in normalized or "बिक्री" in query:
        return Intent.SALES_SUMMARY

    return Intent.GENERAL_BUSINESS_SUMMARY


class IntentClassifier:
    """Class wrapper for intent classification."""

    def classify(
        self,
        query: str,
        current_product: Optional[str] = None,
        current_customer: Optional[str] = None,
    ) -> Intent:
        return classify_intent(query, current_product=current_product, current_customer=current_customer)
