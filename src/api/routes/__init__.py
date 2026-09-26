"""
API Routes registration for VyaparMitra Phase 6 API.
"""

from fastapi import APIRouter
from src.api.routes.analytics import router as analytics_router
from src.api.routes.copilot import router as copilot_router
from src.api.routes.customers import router as customers_router
from src.api.routes.dashboard import router as dashboard_router
from src.api.routes.forecasts import router as forecasts_router
from src.api.routes.health import router as health_router
from src.api.routes.merchants import router as merchants_router
from src.api.routes.notifications import router as notifications_router
from src.api.routes.products import router as products_router
from src.api.routes.recommendations import router as recommendations_router

api_router = APIRouter(prefix="/api")

api_router.include_router(health_router)
api_router.include_router(dashboard_router)
api_router.include_router(analytics_router)
api_router.include_router(merchants_router)
api_router.include_router(notifications_router)
api_router.include_router(products_router)
api_router.include_router(customers_router)
api_router.include_router(forecasts_router)
api_router.include_router(recommendations_router)
api_router.include_router(copilot_router)

__all__ = ["api_router"]
