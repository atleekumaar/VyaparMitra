"""
Audit logging service for tracking security, operational changes, and business transactions.
"""

from __future__ import annotations

import json
import logging
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

logger = logging.getLogger("vyaparmitra.api.audit")


def record_audit_log(
    db: sqlite3.Connection,
    business_id: str,
    user_id: str,
    user_name: str,
    user_role: str,
    action: str,
    resource: str,
    resource_id: Optional[str] = None,
    branch_id: Optional[str] = None,
    details: Optional[Dict[str, Any] | str] = None,
    ip_address: Optional[str] = None,
) -> str:
    """
    Records an immutable audit trail entry into the SQLite audit_logs table.
    Ensures accountability for critical sales, inventory, pricing, user, and financial actions.
    """
    log_id = f"AUD_{uuid.uuid4().hex[:12].upper()}"
    timestamp = datetime.now(timezone.utc).isoformat()

    details_str = ""
    if isinstance(details, dict):
        try:
            details_str = json.dumps(details)
        except Exception:
            details_str = str(details)
    elif details is not None:
        details_str = str(details)

    try:
        db.execute("""
            INSERT INTO audit_logs (
                id, business_id, branch_id, user_id, user_name, user_role,
                action, resource, resource_id, details, ip_address, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            log_id,
            business_id,
            branch_id,
            user_id,
            user_name,
            user_role,
            action,
            resource,
            resource_id,
            details_str,
            ip_address or "127.0.0.1",
            timestamp,
        ))
        db.commit()
    except Exception as exc:
        logger.error(f"Failed to record audit log {log_id}: {exc}", exc_info=True)

    return log_id
