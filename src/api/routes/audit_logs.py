"""
Audit Log Routes for VyaparMitra Backend Security & Accountability.
Provides audit trail inspection restricted to Owner / Admin roles.
"""

from __future__ import annotations

import logging
import sqlite3
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Query

from src.api.auth import CurrentUser, require_roles
from src.api.backend_schemas import AuditLogListResponse, AuditLogOutput
from src.api.db import get_db

logger = logging.getLogger("vyaparmitra.api.audit_logs")
router = APIRouter(prefix="/audit-logs", tags=["Security & Audit Logs"])


@router.get(
    "",
    response_model=AuditLogListResponse,
    summary="Query audit logs for business operations (Owner/Admin only)",
)
def get_audit_logs(
    resource: Optional[str] = Query(None, description="Filter by resource (sales, inventory, auth, finance, suppliers)"),
    action: Optional[str] = Query(None, description="Filter by action name"),
    user_id: Optional[str] = Query(None, description="Filter by actor user ID"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: CurrentUser = Depends(require_roles(["owner", "admin"])),
    db: sqlite3.Connection = Depends(get_db),
) -> AuditLogListResponse:
    """Returns audit log trail for tenant business with multi-criteria filtering."""
    query = "SELECT * FROM audit_logs WHERE business_id = ?"
    params: List[Any] = [current_user.business_id]

    if resource:
        query += " AND resource = ?"
        params.append(resource.strip().lower())

    if action:
        query += " AND action = ?"
        params.append(action.strip().upper())

    if user_id:
        query += " AND user_id = ?"
        params.append(user_id.strip())

    count_query = query.replace("SELECT *", "SELECT COUNT(*)")
    total_count = db.execute(count_query, params).fetchone()[0] or 0

    query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = db.execute(query, params).fetchall()
    logs = [
        AuditLogOutput(
            id=r["id"],
            business_id=r["business_id"],
            branch_id=r["branch_id"],
            user_id=r["user_id"],
            user_name=r["user_name"],
            user_role=r["user_role"],
            action=r["action"],
            resource=r["resource"],
            resource_id=r["resource_id"],
            details=r["details"],
            ip_address=r["ip_address"],
            timestamp=r["timestamp"],
        )
        for r in rows
    ]

    return AuditLogListResponse(total_logs=total_count, logs=logs)
