"""
Pydantic schemas and data models for VyaparMitra Phase 2 Business Intelligence Engine.
Ensures strong typing, input validation, and structured serialization across all analytical layers.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MetricRecord(BaseModel):
    """Canonical data model for any individual analytical metric."""
    metric_name: str
    metric_value: float
    period: Optional[str] = None
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    merchant_id: Optional[str] = None
    dimension: Optional[str] = None
    dimension_value: Optional[str] = None


class SalesKPISet(BaseModel):
    """Core aggregate sales performance metrics."""
    total_revenue: float = Field(..., ge=0.0)
    total_orders: int = Field(..., ge=0)
    total_units: int = Field(..., ge=0)
    average_order_value: float = Field(..., ge=0.0)
    average_units_per_order: float = Field(..., ge=0.0)
    discount_total: float = Field(..., ge=0.0)
    discount_rate: float = Field(..., ge=0.0)
    revenue_per_active_day: float = Field(..., ge=0.0)


class PeriodComparisonRecord(BaseModel):
    """Periodic performance metrics with sequential comparison."""
    period: str
    period_key: str
    period_start: str
    period_end: str
    revenue: float = Field(..., ge=0.0)
    orders: int = Field(..., ge=0)
    units: int = Field(..., ge=0)
    aov: float = Field(..., ge=0.0)
    discount: float = Field(..., ge=0.0)
    revenue_change: Optional[float] = None
    revenue_growth_pct: Optional[float] = None
    orders_change: Optional[int] = None
    orders_growth_pct: Optional[float] = None


class CustomerKPISet(BaseModel):
    """Customer base volume and engagement KPIs."""
    total_customers: int = Field(..., ge=0)
    active_customers: int = Field(..., ge=0)
    repeat_customers: int = Field(..., ge=0)
    one_time_customers: int = Field(..., ge=0)
    average_customer_spend: float = Field(..., ge=0.0)
    average_orders_per_customer: float = Field(..., ge=0.0)


class RFMSegmentRecord(BaseModel):
    """Customer-level RFM score and segment."""
    customer_id: str
    recency: float
    order_count: int
    total_spend: float
    r_score: int = Field(..., ge=1, le=5)
    f_score: int = Field(..., ge=1, le=5)
    m_score: int = Field(..., ge=1, le=5)
    rfm_score: str
    rfm_segment: str


class ProductPerformanceRecord(BaseModel):
    """Product SKU performance and portfolio contribution."""
    product_id: str
    product_name: str
    product_category: str
    revenue: float = Field(..., ge=0.0)
    units: int = Field(..., ge=0)
    orders: int = Field(..., ge=0)
    unique_customers: int = Field(..., ge=0)
    average_price: float = Field(..., ge=0.0)
    revenue_share: float = Field(..., ge=0.0)
    unit_share: float = Field(..., ge=0.0)


class CategoryPerformanceRecord(BaseModel):
    """Product category performance and market basket share."""
    product_category: str
    revenue: float = Field(..., ge=0.0)
    units: int = Field(..., ge=0)
    orders: int = Field(..., ge=0)
    unique_customers: int = Field(..., ge=0)
    average_order_value: float = Field(..., ge=0.0)
    revenue_share: float = Field(..., ge=0.0)


class TimeKPIRecord(BaseModel):
    """Temporal slice performance (hourly, weekday, monthly)."""
    dimension: str
    time_key: str
    revenue: float = Field(..., ge=0.0)
    orders: int = Field(..., ge=0)
    units: int = Field(..., ge=0)
    aov: float = Field(..., ge=0.0)


class PaymentKPIRecord(BaseModel):
    """Payment method adoption and volume metrics."""
    payment_method: str
    orders: int = Field(..., ge=0)
    revenue: float = Field(..., ge=0.0)
    orders_share: float = Field(..., ge=0.0)
    revenue_share: float = Field(..., ge=0.0)
    aov: float = Field(..., ge=0.0)


class MerchantBenchmarkRecord(BaseModel):
    """Descriptive peer comparison against merchant cohort."""
    merchant_id: str
    merchant_name: str
    business_type: str
    city: str
    revenue: float = Field(..., ge=0.0)
    peer_mean_revenue: float = Field(..., ge=0.0)
    revenue_vs_peer_pct: float
    aov: float = Field(..., ge=0.0)
    peer_mean_aov: float = Field(..., ge=0.0)
    aov_vs_peer_pct: float
    orders: int = Field(..., ge=0)
    peer_mean_orders: float = Field(..., ge=0.0)
    orders_vs_peer_pct: float
    revenue_percentile: float = Field(..., ge=0.0, le=100.0)


class ContextComparisonRecord(BaseModel):
    """Contextual event comparisons (festival, meteorological)."""
    context_type: str
    condition: str
    segment_value: str
    revenue: float = Field(..., ge=0.0)
    orders: int = Field(..., ge=0)
    aov: float = Field(..., ge=0.0)
    sample_size: int = Field(..., ge=0)
    relative_difference_pct: Optional[float] = None


class TrendRecord(BaseModel):
    """Descriptive directional classification."""
    period: str
    period_key: str
    metric: str
    value: float
    moving_average: float
    absolute_change: float
    percentage_change: float
    trend_classification: str


class AnomalyRecord(BaseModel):
    """Statistical outlier observation record."""
    date: str
    metric: str
    value: float
    baseline: float
    deviation: float
    method: str
    status: str


class BusinessSummary(BaseModel):
    """Structured machine-readable snapshot of business performance."""
    period: str
    total_revenue: float
    total_orders: int
    total_units: int
    average_order_value: float
    revenue_growth_pct: Optional[float] = None
    active_customers: int
    top_revenue_category: str
    top_revenue_product: str
    peak_weekday: str
    peak_hour: int
    dominant_payment_method: str
    festival_day_revenue_uplift_pct: Optional[float] = None
    rainy_day_revenue_uplift_pct: Optional[float] = None
    key_insights: List[str] = Field(default_factory=list)
