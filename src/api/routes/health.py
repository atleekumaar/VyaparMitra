"""
Health and readiness route for VyaparMitra Phase 6 API.
"""

from __future__ import annotations

from fastapi import APIRouter
from src.api.config import get_api_config
from src.api.schemas import HealthResponse
from src.api.services.copilot_service_adapter import CopilotServiceAdapter

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Returns system status, active environment, artifacts availability, and copilot sessions."""
    config = get_api_config()
    adapter = CopilotServiceAdapter(config)
    copilot_health = adapter.get_health()

    artifacts_ready = (
        (config.data_dir / "analytics" / "sales" / "sales_summary.parquet").exists()
        and (config.data_dir / "ml" / "forecasts" / "sales_forecast_7d.parquet").exists()
        and (config.data_dir / "recommendations" / "all_recommendations.parquet").exists()
    )

    return HealthResponse(
        status="healthy",
        version="1.0.0",
        app_env=config.app_env,
        demo_mode=config.demo_mode,
        active_copilot_sessions=copilot_health.get("active_sessions", 0),
        artifacts_ready=artifacts_ready,
    )
