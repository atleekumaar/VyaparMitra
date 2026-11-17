"""
Health and readiness route for VyaparMitra Phase 6 API.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
import sqlite3
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from src.api.auth import CurrentUser, get_current_user, require_roles
from src.api.backup import create_database_backup
from src.api.config import get_api_config
from src.api.db import get_db
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


@router.post("/health/backup")
def trigger_database_backup(
    request: Request,
    x_backup_secret: Optional[str] = Header(default=None),
    db: sqlite3.Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Triggers an atomic online SQLite database backup snapshot.
    Accessible by authenticated Owner/Admin or via secure X-Backup-Secret matching JWT_SECRET_KEY.
    """
    config = get_api_config()
    is_authorized_secret = bool(x_backup_secret and x_backup_secret == config.jwt_secret_key)
    
    is_authorized_role = False
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            from src.api.auth import decode_access_token
            token = auth_header.split(" ")[1].strip()
            payload = decode_access_token(token)
            user_id = payload.get("sub")
            if user_id:
                row = db.execute("SELECT role FROM users WHERE id = ?", (user_id,)).fetchone()
                if row and row["role"] in ("owner", "admin"):
                    is_authorized_role = True
        except Exception:
            pass

    if not (is_authorized_secret or is_authorized_role or config.demo_mode):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized: Backup trigger requires Owner/Admin role or valid X-Backup-Secret.",
        )

    try:
        result = create_database_backup(retain_count=10)
        return result
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate database backup: {exc}",
        )
