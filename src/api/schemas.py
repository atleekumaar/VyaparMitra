"""
Typed Pydantic schemas for VyaparMitra Phase 6 REST API.
Enforces request validation, structured responses, and consistent error envelopes.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# -------------------------------------------------------------
# Common / Error Schemas
# -------------------------------------------------------------

class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: Optional[str] = None
    details: Optional[Any] = None


class APIErrorResponse(BaseModel):
    error: ErrorDetail


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    app_env: str = "development"
    demo_mode: bool = True
    active_copilot_sessions: int = 0
    artifacts_ready: bool = True
    checked_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# -------------------------------------------------------------
# Dashboard Schemas
# -------------------------------------------------------------

class MetricCard(BaseModel):
    label: str
    value: float | int | str
    formatted_value: str
    change_pct: Optional[float] = None
    trend: Optional[str] = None  # UP, DOWN, STABLE
    subtext: Optional[str] = None


class DashboardSummaryResponse(BaseModel):
    merchant_id: str
    merchant_name: str
    date_range: str
    kpis: Dict[str, MetricCard]
    sales_trend_direction: str
    forecast_7d_total_revenue: float
    total_actions_pending: int
    critical_actions_count: int
    demo_mode: bool = True


class ActionItem(BaseModel):
    recommendation_id: str
    type: str
    priority_band: str
    priority_score: float
    title: str
    action: str
    reason: str
    expected_impact: float
    entity_id: Optional[str] = None
    status: str = "GENERATED"
    evidence_snippet: Optional[str] = None


class DashboardActionsResponse(BaseModel):
    merchant_id: str
    total_actions: int
    actions: List[ActionItem]


# -------------------------------------------------------------
# Analytics Schemas
# -------------------------------------------------------------

class DailySalesPoint(BaseModel):
    date: str
    revenue: float
    orders: int
    units: Optional[int] = None
    average_order_value: Optional[float] = None


class SalesAnalyticsResponse(BaseModel):
    total_revenue: float
    total_orders: int
    average_order_value: float
    discount_rate: float
    daily_series: List[DailySalesPoint]


class CustomerSegmentSummary(BaseModel):
    segment_name: str
    customer_count: int
    total_revenue: float
    revenue_share: float


class CustomerAnalyticsResponse(BaseModel):
    total_customers: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    segments: List[CustomerSegmentSummary]


class ProductRankItem(BaseModel):
    product_id: str
    product_name: str
    category: str
    revenue: float
    units: int
    rank: int


class ProductAnalyticsResponse(BaseModel):
    total_products_tracked: int
    top_performers: List[ProductRankItem]
    pareto_80_20_ratio: Optional[float] = None


class CategoryShareItem(BaseModel):
    category: str
    revenue: float
    orders: int
    revenue_share: float


class CategoryAnalyticsResponse(BaseModel):
    categories: List[CategoryShareItem]


class PaymentMethodItem(BaseModel):
    payment_method: str
    transaction_count: int
    total_revenue: float
    revenue_share: float


class PaymentAnalyticsResponse(BaseModel):
    payment_methods: List[PaymentMethodItem]
    primary_payment_method: str


class CashSaleRequest(BaseModel):
    amount: float
    product_name: Optional[str] = "General Item"
    category: Optional[str] = "General"
    customer_id: Optional[str] = "WALK_IN"
    payment_method: Optional[str] = "CASH"


class CashSaleResponse(BaseModel):
    status: str
    message: str
    amount: float
    transaction_id: str
    updated_cash_total: float
    updated_cash_orders: int
    timestamp: str


class TrendAnalyticsResponse(BaseModel):
    predicted_trend: str
    confidence: float
    horizon_days: int
    historical_revenue_change_pct: float


class AnomalyItem(BaseModel):
    date: str
    metric: str
    observed_value: float
    expected_value: float
    deviation_score: float
    is_anomaly: bool


class AnomalyResponse(BaseModel):
    total_anomalies_detected: int
    anomalies: List[AnomalyItem]


# -------------------------------------------------------------
# Product & Customer Detail Schemas
# -------------------------------------------------------------

class ProductListItem(BaseModel):
    product_id: str
    product_name: str
    category: str
    selling_price: float
    total_revenue: float
    total_units: int
    forecast_7d_units: int
    status: str  # STAR, FOCUS, MONITOR


class ProductDetailResponse(BaseModel):
    product_id: str
    product_name: str
    category: str
    selling_price: float
    unit_cost: float
    margin: float
    total_revenue: float
    total_units_sold: int
    forecast_7d_units: int
    cross_sell_recommendations: List[Dict[str, Any]]
    active_recommendations: List[ActionItem]


class CustomerListItem(BaseModel):
    customer_id: str
    segment: str
    lifetime_spend: float
    total_orders: int
    recency_days: float
    churn_risk_tier: str
    churn_probability: float


class CustomerDetailResponse(BaseModel):
    customer_id: str
    segment: str
    lifetime_spend: float
    total_orders: int
    recency_days: float
    churn_risk_tier: str
    churn_probability: float
    suggested_retention_action: Optional[str] = None
    evidence: List[Dict[str, Any]] = Field(default_factory=list)


# -------------------------------------------------------------
# Forecast Schemas
# -------------------------------------------------------------

class DailySalesForecastItem(BaseModel):
    forecast_date: str
    predicted_revenue: float


class SalesForecastResponse(BaseModel):
    forecast_7d_total_revenue: float
    forecast_horizon_days: int = 7
    model_name: str
    daily_forecasts: List[DailySalesForecastItem]
    trend_direction: str


class SKUForecastItem(BaseModel):
    product_id: str
    product_name: str
    category: str
    predicted_7d_units: int


class DemandForecastResponse(BaseModel):
    horizon_days: int = 7
    top_demand_skus: List[SKUForecastItem]


# -------------------------------------------------------------
# Recommendation & Action Schemas
# -------------------------------------------------------------

class EvidenceDetail(BaseModel):
    metric: str
    value: str | float
    source: str
    description: Optional[str] = None


class RecommendationDetailResponse(BaseModel):
    recommendation_id: str
    type: str
    priority_band: str
    priority_score: float
    title: str
    action: str
    reason: str
    expected_impact: float
    entity_id: Optional[str] = None
    status: str
    evidence: List[EvidenceDetail]
    generated_at: str


class RecommendationListResponse(BaseModel):
    total_count: int
    recommendations: List[RecommendationDetailResponse]


class ActionStatusUpdateRequest(BaseModel):
    status: str  # GENERATED, VIEWED, ACCEPTED, REJECTED, EXECUTED


class ActionStatusUpdateResponse(BaseModel):
    recommendation_id: str
    previous_status: str
    new_status: str
    updated_at: str
    message: str


# -------------------------------------------------------------
# Copilot Schemas (Passthrough to Phase 5)
# -------------------------------------------------------------

class CopilotAskRequest(BaseModel):
    query: str
    session_id: Optional[str] = "default_session"
    merchant_id: Optional[str] = "M001"
    language: Optional[str] = None  # hindi, hinglish, english


class CopilotAskResponse(BaseModel):
    answer: str
    intent: str
    language: str
    sources: List[Dict[str, Any]]
    evidence: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    confidence: Optional[float] = None
    validation_status: str
    generated_at: str


class CopilotDailyBriefResponse(BaseModel):
    brief: CopilotAskResponse


# -------------------------------------------------------------
# Benchmarking Schemas
# -------------------------------------------------------------

class BenchmarkMetricItem(BaseModel):
    name: str
    label: str
    label_hi: Optional[str] = None
    unit: str
    you: float
    peer_median: float
    peer_min: float
    peer_max: float
    percentile: int
    status: str  # green, yellow, red
    status_text: str  # Achha, Ausat, Sudhar sakte hain
    status_text_hi: Optional[str] = None
    higher_is_better: bool
    action: str
    action_hi: Optional[str] = None


class BenchmarkResponse(BaseModel):
    merchant_id: str
    merchant_name: str
    business_type: str
    city: str
    state: str
    peer_group: str
    peer_count: int
    is_fallback_group: bool = False
    fallback_reason: Optional[str] = None
    rank: int
    overall_score: int
    metrics: List[BenchmarkMetricItem]
    top_performer_practices: List[str] = []
    whatsapp_digest: Optional[str] = None


class MerchantInfoItem(BaseModel):
    merchant_id: str
    merchant_name: str
    business_type: str
    city: str
    state: str


class MerchantListResponse(BaseModel):
    total: int
    merchants: List[MerchantInfoItem]

