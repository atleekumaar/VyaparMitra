"""
Strongly typed domain models and schemas for VyaparMitra Phase 4 Recommendation Engine.
Enforces validation across recommendation types, priority scoring, lifecycle tracking, and evidence.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RecommendationType(str, Enum):
    RESTOCK = "RESTOCK"
    PROMOTE = "PROMOTE"
    CROSS_SELL = "CROSS_SELL"
    UPSELL = "UPSELL"
    RETENTION = "RETENTION"
    RE_ENGAGEMENT = "RE_ENGAGEMENT"
    MAINTAIN_PRICE = "MAINTAIN_PRICE"
    REVIEW_MARGIN = "REVIEW_MARGIN"
    CLEARANCE = "CLEARANCE"
    MONITOR = "MONITOR"
    BUNDLE = "BUNDLE"
    REORDER = "REORDER"
    FOCUS = "FOCUS"
    LIMIT_DISCOUNT = "LIMIT_DISCOUNT"
    PERSONALIZED_OFFER = "PERSONALIZED_OFFER"
    PRODUCT_REMINDER = "PRODUCT_REMINDER"
    NO_ACTION = "NO_ACTION"


class PriorityBand(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class LifecycleState(str, Enum):
    GENERATED = "GENERATED"
    VIEWED = "VIEWED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXECUTED = "EXECUTED"
    EXPIRED = "EXPIRED"


class ConflictCategory(str, Enum):
    DATA_QUALITY = "DATA_QUALITY"
    RISK = "RISK"
    MARGIN_PROTECTION = "MARGIN_PROTECTION"
    REVENUE_GROWTH = "REVENUE_GROWTH"
    EXPERIMENTAL_ACTION = "EXPERIMENTAL_ACTION"


class Evidence(BaseModel):
    """Machine-readable evidence supporting a recommendation."""
    metric: str
    value: Any
    source: str
    description: Optional[str] = None


class Recommendation(BaseModel):
    """Core domain object representing an actionable business recommendation."""
    recommendation_id: str
    merchant_id: Optional[str] = None
    type: RecommendationType
    priority: float = Field(..., ge=0.0, le=1.0)
    priority_band: PriorityBand
    confidence: float = Field(..., ge=0.0, le=1.0)
    urgency: float = Field(..., ge=0.0, le=1.0)
    expected_impact: float = Field(..., ge=0.0, le=1.0)
    entity_type: str  # 'product', 'customer', 'product_pair', 'merchant'
    entity_id: str
    title: str
    action: str
    reason: str
    evidence: List[Evidence] = Field(default_factory=list)
    conflict_category: ConflictCategory = ConflictCategory.REVENUE_GROWTH
    created_at: str
    status: LifecycleState = LifecycleState.GENERATED


class FeedbackRecord(BaseModel):
    """Historical feedback container for future reinforcement learning and bandits."""
    recommendation_id: str
    action: str
    generated_at: str
    accepted: Optional[bool] = None
    executed: Optional[bool] = None
    outcome: Optional[str] = None
    actual_revenue_change: Optional[float] = None
    actual_units_change: Optional[float] = None
    actual_customer_response: Optional[str] = None
