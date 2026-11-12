"""
Smart Inventory Agent Tools for MerchantOS.
Connected to live SQLite/PostgreSQL database tables (`inventory`, `agent_approvals`, `audit_logs`)
with strict tenant/branch isolation and L3 approval gating.
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

from src.api.db import get_db_connection, init_db
from src.copilot.agents.security import Role, require_agent_role


def _ensure_tables(conn) -> None:
    """Ensures agent_approvals table exists even on existing DB files."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS agent_approvals (
            id TEXT PRIMARY KEY,
            business_id TEXT NOT NULL,
            branch_id TEXT,
            action_type TEXT NOT NULL DEFAULT 'PURCHASE_REORDER',
            sku TEXT NOT NULL,
            product_name TEXT,
            quantity INTEGER NOT NULL,
            unit_cost REAL NOT NULL DEFAULT 0.0,
            estimated_cost REAL NOT NULL DEFAULT 0.0,
            vendor TEXT DEFAULT 'Standard Supplier',
            status TEXT NOT NULL DEFAULT 'PENDING_APPROVAL',
            requested_by TEXT NOT NULL,
            requested_by_role TEXT NOT NULL,
            reviewed_by TEXT,
            review_notes TEXT,
            created_at TEXT NOT NULL,
            reviewed_at TEXT
        )
    """)


class InventoryAgentTools:
    """Tools executed by the Smart Inventory Agent against live DB."""

    @staticmethod
    @require_agent_role(Role.OWNER, Role.SUPERVISOR, Role.STAFF)
    def check_low_stock(threshold: Optional[int] = None, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        ctx = context or {}
        tenant_id = ctx.get("tenant_id") or ctx.get("business_id")
        branch_id = ctx.get("branch_id")

        conn = get_db_connection()
        try:
            sql = "SELECT * FROM inventory WHERE business_id = ?"
            params: List[Any] = [tenant_id]
            if branch_id:
                sql += " AND branch_id = ?"
                params.append(branch_id)

            if threshold is not None:
                sql += " AND current_stock <= ?"
                params.append(threshold)
            else:
                sql += " AND current_stock <= min_stock_threshold"

            sql += " ORDER BY current_stock ASC"
            rows = conn.execute(sql, params).fetchall()

            results: List[Dict[str, Any]] = []
            for r in rows:
                c_stock = int(r["current_stock"])
                m_thresh = int(r["min_stock_threshold"])
                recommended_qty = max(m_thresh * 2 - c_stock, 10)
                results.append({
                    "id": r["id"],
                    "sku": r["product_id"],
                    "name": r["product_name"],
                    "category": r["category"],
                    "branch_id": r["branch_id"],
                    "stock": c_stock,
                    "threshold": m_thresh,
                    "unit_cost": float(r["unit_cost"]),
                    "recommended_reorder_qty": recommended_qty,
                })
            return results
        finally:
            conn.close()

    @staticmethod
    @require_agent_role(Role.OWNER, Role.SUPERVISOR)
    def draft_purchase_reorder(
        sku: str,
        quantity: int,
        vendor: str = "Standard Supplier",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generates and persists an L3 Purchase Reorder Draft awaiting Owner approval."""
        ctx = context or {}
        tenant_id = ctx.get("tenant_id") or ctx.get("business_id")
        branch_id = ctx.get("branch_id")
        user_id = ctx.get("user_id", "unknown_user")
        role = str(ctx.get("role", "SUPERVISOR")).upper()
        now = datetime.now(timezone.utc).isoformat()
        approval_id = f"apr_{uuid.uuid4().hex[:10]}"

        conn = get_db_connection()
        try:
            _ensure_tables(conn)
            # Lookup product details from live inventory if available
            item_row = None
            if branch_id:
                item_row = conn.execute(
                    "SELECT product_name, unit_cost, branch_id FROM inventory WHERE business_id = ? AND branch_id = ? AND (LOWER(product_id) = ? OR LOWER(product_name) LIKE ?)",
                    (tenant_id, branch_id, sku.lower().strip(), f"%{sku.lower().strip()}%"),
                ).fetchone()
            if not item_row:
                item_row = conn.execute(
                    "SELECT product_name, unit_cost, branch_id FROM inventory WHERE business_id = ? AND (LOWER(product_id) = ? OR LOWER(product_name) LIKE ?)",
                    (tenant_id, sku.lower().strip(), f"%{sku.lower().strip()}%"),
                ).fetchone()

            product_name = item_row["product_name"] if item_row else sku
            unit_cost = float(item_row["unit_cost"]) if item_row else 0.0
            resolved_branch = branch_id or (item_row["branch_id"] if item_row else None)
            estimated_cost = round(unit_cost * quantity, 2)

            # Persist draft if tenant exists in businesses table
            biz_exists = conn.execute("SELECT 1 FROM businesses WHERE id = ?", (tenant_id,)).fetchone()
            if biz_exists:
                conn.execute(
                    """
                    INSERT INTO agent_approvals (
                        id, business_id, branch_id, action_type, sku, product_name,
                        quantity, unit_cost, estimated_cost, vendor, status,
                        requested_by, requested_by_role, created_at
                    ) VALUES (?, ?, ?, 'PURCHASE_REORDER', ?, ?, ?, ?, ?, ?, 'PENDING_APPROVAL', ?, ?, ?)
                    """,
                    (
                        approval_id, tenant_id, resolved_branch, sku, product_name,
                        quantity, unit_cost, estimated_cost, vendor,
                        user_id, role, now
                    ),
                )
                conn.commit()

            return {
                "approval_id": approval_id,
                "action_type": "PURCHASE_REORDER",
                "tenant_id": tenant_id,
                "branch_id": resolved_branch,
                "sku": sku,
                "product_name": product_name,
                "quantity": quantity,
                "unit_cost": unit_cost,
                "estimated_cost": estimated_cost,
                "vendor": vendor,
                "status": "PENDING_APPROVAL",
                "approval_required_by": Role.OWNER.value,
                "persisted": bool(biz_exists),
                "audit_trail": {
                    "initiated_by": user_id,
                    "role": role,
                    "timestamp": now,
                    "stage": "L2_DRAFT_STAGE"
                }
            }
        finally:
            conn.close()

    @staticmethod
    @require_agent_role(Role.OWNER)
    def approve_reorder_request(
        approval_id: str,
        review_notes: str = "Approved by Owner",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Owner-only L3 Execution: Approves draft, updates live inventory stock, and logs audit trail."""
        ctx = context or {}
        tenant_id = ctx.get("tenant_id") or ctx.get("business_id")
        reviewer_id = ctx.get("user_id", "owner")
        reviewer_name = ctx.get("user_name", reviewer_id)
        now = datetime.now(timezone.utc).isoformat()

        conn = get_db_connection()
        try:
            _ensure_tables(conn)
            row = conn.execute(
                "SELECT * FROM agent_approvals WHERE id = ? AND business_id = ?",
                (approval_id, tenant_id),
            ).fetchone()
            if not row:
                raise ValueError(f"Approval request '{approval_id}' not found for tenant '{tenant_id}'.")
            if row["status"] != "PENDING_APPROVAL":
                raise ValueError(f"Approval request '{approval_id}' is already {row['status']}.")

            qty = int(row["quantity"])
            sku = row["sku"]
            branch_id = row["branch_id"]

            # 1. Update approval record
            conn.execute(
                """
                UPDATE agent_approvals
                SET status = 'APPROVED', reviewed_by = ?, review_notes = ?, reviewed_at = ?
                WHERE id = ? AND business_id = ?
                """,
                (reviewer_id, review_notes, now, approval_id, tenant_id),
            )

            # 2. Execute live stock replenishment in inventory table
            inv_row = None
            if branch_id:
                inv_row = conn.execute(
                    "SELECT id, current_stock FROM inventory WHERE business_id = ? AND branch_id = ? AND (LOWER(product_id) = ? OR LOWER(product_name) LIKE ?)",
                    (tenant_id, branch_id, sku.lower().strip(), f"%{sku.lower().strip()}%"),
                ).fetchone()
            if not inv_row:
                inv_row = conn.execute(
                    "SELECT id, current_stock FROM inventory WHERE business_id = ? AND (LOWER(product_id) = ? OR LOWER(product_name) LIKE ?)",
                    (tenant_id, sku.lower().strip(), f"%{sku.lower().strip()}%"),
                ).fetchone()

            new_stock = None
            if inv_row:
                new_stock = int(inv_row["current_stock"]) + qty
                conn.execute(
                    "UPDATE inventory SET current_stock = ?, updated_at = ? WHERE id = ?",
                    (new_stock, now, inv_row["id"]),
                )

            # 3. Record security audit log
            conn.execute(
                """
                INSERT INTO audit_logs (
                    id, business_id, branch_id, user_id, user_name, user_role,
                    action, resource, resource_id, details, timestamp
                ) VALUES (?, ?, ?, ?, ?, 'owner', 'AGENT_APPROVAL_EXECUTED', 'agent_approvals', ?, ?, ?)
                """,
                (
                    f"aud_{uuid.uuid4().hex[:10]}", tenant_id, branch_id, reviewer_id, reviewer_name,
                    approval_id, f"Approved reorder of {qty} units for {sku}. New stock: {new_stock}. Notes: {review_notes}", now
                ),
            )
            conn.commit()

            return {
                "approval_id": approval_id,
                "status": "APPROVED",
                "sku": sku,
                "quantity_added": qty,
                "updated_stock": new_stock,
                "reviewed_by": reviewer_id,
                "reviewed_at": now,
            }
        finally:
            conn.close()

    @staticmethod
    @require_agent_role(Role.OWNER)
    def reject_reorder_request(
        approval_id: str,
        review_notes: str = "Rejected by Owner",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Owner-only rejection of an agent purchase reorder draft."""
        ctx = context or {}
        tenant_id = ctx.get("tenant_id") or ctx.get("business_id")
        reviewer_id = ctx.get("user_id", "owner")
        reviewer_name = ctx.get("user_name", reviewer_id)
        now = datetime.now(timezone.utc).isoformat()

        conn = get_db_connection()
        try:
            _ensure_tables(conn)
            row = conn.execute(
                "SELECT * FROM agent_approvals WHERE id = ? AND business_id = ?",
                (approval_id, tenant_id),
            ).fetchone()
            if not row:
                raise ValueError(f"Approval request '{approval_id}' not found for tenant '{tenant_id}'.")
            if row["status"] != "PENDING_APPROVAL":
                raise ValueError(f"Approval request '{approval_id}' is already {row['status']}.")

            conn.execute(
                """
                UPDATE agent_approvals
                SET status = 'REJECTED', reviewed_by = ?, review_notes = ?, reviewed_at = ?
                WHERE id = ? AND business_id = ?
                """,
                (reviewer_id, review_notes, now, approval_id, tenant_id),
            )
            conn.execute(
                """
                INSERT INTO audit_logs (
                    id, business_id, branch_id, user_id, user_name, user_role,
                    action, resource, resource_id, details, timestamp
                ) VALUES (?, ?, ?, ?, ?, 'owner', 'AGENT_APPROVAL_REJECTED', 'agent_approvals', ?, ?, ?)
                """,
                (
                    f"aud_{uuid.uuid4().hex[:10]}", tenant_id, row["branch_id"], reviewer_id, reviewer_name,
                    approval_id, f"Rejected reorder for {row['sku']}. Notes: {review_notes}", now
                ),
            )
            conn.commit()
            return {
                "approval_id": approval_id,
                "status": "REJECTED",
                "sku": row["sku"],
                "reviewed_by": reviewer_id,
                "reviewed_at": now,
            }
        finally:
            conn.close()

    @staticmethod
    @require_agent_role(Role.OWNER, Role.SUPERVISOR)
    def list_approval_requests(
        status_filter: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Lists persisted agent approval requests for the tenant."""
        ctx = context or {}
        tenant_id = ctx.get("tenant_id") or ctx.get("business_id")
        conn = get_db_connection()
        try:
            _ensure_tables(conn)
            sql = "SELECT * FROM agent_approvals WHERE business_id = ?"
            params: List[Any] = [tenant_id]
            if status_filter:
                sql += " AND status = ?"
                params.append(status_filter.upper())
            sql += " ORDER BY created_at DESC"
            rows = conn.execute(sql, params).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()
