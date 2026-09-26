"""
Typed Pydantic schemas and dataclasses for VyaparMitra Phase 3 Predictive AI Engine.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SplitInfo(BaseModel):
    """Chronological dataset split boundaries."""
    train_start: str
    train_end: str
    train_count: int
    validation_start: str
    validation_end: str
    validation_count: int
    test_start: str
    test_end: str
    test_count: int


class ForecastRecord(BaseModel):
    """Daily revenue forecast record."""
    forecast_date: str
    predicted_revenue: float = Field(..., ge=0.0)
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    model_name: str
    model_version: str
    generated_at: str


class ProductDemandForecastRecord(BaseModel):
    """Product SKU demand prediction."""
    forecast_date: str
    product_id: str
    product_category: str
    predicted_units: float = Field(..., ge=0.0)
    model_name: str
    model_version: str


class CustomerRiskRecord(BaseModel):
    """Customer churn/inactivity risk assessment."""
    customer_id: str
    snapshot_date: str
    risk_probability: float = Field(..., ge=0.0, le=1.0)
    risk_band: str  # low, medium, high
    model_name: str
    model_version: str


class BusinessTrendPredictionRecord(BaseModel):
    """Short-term operational revenue direction prediction."""
    prediction_date: str
    horizon_days: int
    predicted_trend: str  # INCREASING, STABLE, DECREASING
    confidence: float = Field(..., ge=0.0, le=1.0)
    model_name: str
    model_version: str


class ModelMetadata(BaseModel):
    """Versioned model metadata artifact stored alongside joblib weights."""
    model_name: str
    model_version: str
    training_date: str
    training_data_range: Dict[str, Any]
    feature_list: List[str]
    target: str
    hyperparameters: Dict[str, Any]
    validation_metrics: Dict[str, Any]
    test_metrics: Dict[str, Any]
    baseline_comparison: Dict[str, Any]
    selection_reason: str

