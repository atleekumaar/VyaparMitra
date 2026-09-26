"""Services package for VyaparMitra Phase 6 API."""

from src.api.services.analytics_service import AnalyticsService
from src.api.services.copilot_service_adapter import CopilotServiceAdapter
from src.api.services.customer_service import CustomerService
from src.api.services.dashboard_service import DashboardService
from src.api.services.forecast_service import ForecastService
from src.api.services.product_service import ProductService
from src.api.services.recommendation_service import RecommendationService

__all__ = [
    "DashboardService",
    "AnalyticsService",
    "ProductService",
    "CustomerService",
    "ForecastService",
    "RecommendationService",
    "CopilotServiceAdapter",
]
