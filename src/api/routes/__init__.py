"""
API Routes registration for VyaparMitra Phase 6 API & Core Backend Architecture.
"""

from fastapi import APIRouter
from src.api.routes.analytics import router as analytics_router
from src.api.routes.audit_logs import router as audit_logs_router
from src.api.routes.auth import router as auth_router
from src.api.routes.branches import router as branches_router
from src.api.routes.copilot import router as copilot_router
from src.api.routes.customer_ops import router as customer_ops_router
from src.api.routes.customers import router as customers_router
from src.api.routes.dashboard import router as dashboard_router
from src.api.routes.finance import router as finance_router
from src.api.routes.forecasts import router as forecasts_router
from src.api.routes.health import router as health_router
from src.api.routes.import_data import router as import_router
from src.api.routes.inventory import router as inventory_router
from src.api.routes.merchants import router as merchants_router
from src.api.routes.notifications import router as notifications_router
from src.api.routes.products import router as products_router
from src.api.routes.recommendations import router as recommendations_router
from src.api.routes.sales import router as sales_router
from src.api.routes.suppliers import router as suppliers_router

api_router = APIRouter(prefix="/api")

# Core Architecture & Operational Routes (Phase 6 Atul)
api_router.include_router(auth_router)
api_router.include_router(branches_router)
api_router.include_router(sales_router)
api_router.include_router(inventory_router)
api_router.include_router(customer_ops_router)
api_router.include_router(suppliers_router)
api_router.include_router(finance_router)
api_router.include_router(audit_logs_router)
api_router.include_router(import_router)

# Analytics, Copilot & Intelligence Routes
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
