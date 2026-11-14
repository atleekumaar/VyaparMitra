"""Services package for VyaparMitra Phase 6 API."""

_SERVICE_MAP = {
    "DashboardService": "src.api.services.dashboard_service",
    "AnalyticsService": "src.api.services.analytics_service",
    "ProductService": "src.api.services.product_service",
    "CustomerService": "src.api.services.customer_service",
    "ForecastService": "src.api.services.forecast_service",
    "RecommendationService": "src.api.services.recommendation_service",
    "CopilotServiceAdapter": "src.api.services.copilot_service_adapter",
    "BrevoEmailService": "src.api.services.email_service",
    "get_email_service": "src.api.services.email_service",
}


def __getattr__(name: str):
    if name in _SERVICE_MAP:
        import importlib
        mod = importlib.import_module(_SERVICE_MAP[name])
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = list(_SERVICE_MAP.keys())


