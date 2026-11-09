"""
Smart Inventory Agent Tools for MerchantOS V1.
Implements L3 Trust Ladder: Observe -> Recommend -> Draft -> Approve.
"""
from typing import Dict, Any, List, Optional
from src.copilot.agents.security import require_agent_role, Role

class InventoryAgentTools:
    @staticmethod
    def check_low_stock(threshold: int = 10, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Queries SKUs below replenishment threshold (Accessible by all roles)."""
        ctx = context or {}
        branch_id = ctx.get("branch_id", "main_branch")
        return [
            {"sku": "SKU-OIL-1L", "name": "Mustard Oil 1L", "stock": 4, "reorder_level": 15, "branch": branch_id, "status": "CRITICAL"},
            {"sku": "SKU-ATA-5K", "name": "Chakki Atta 5kg", "stock": 2, "reorder_level": 10, "branch": branch_id, "status": "CRITICAL"}
        ]

    @staticmethod
    @require_agent_role(Role.OWNER, Role.SUPERVISOR)
    def draft_purchase_reorder(sku: str, quantity: int, vendor: str = "Standard Supplier", context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Drafts an approval-gated purchase order request (L3 Gate)."""
        ctx = context or {}
        return {
            "action": "CREATE_PURCHASE_REQUEST",
            "sku": sku,
            "quantity": quantity,
            "vendor": vendor,
            "status": "PENDING_APPROVAL",
            "approval_required_by": Role.OWNER.value,
            "tenant_id": ctx.get("tenant_id"),
            "branch_id": ctx.get("branch_id", "main_branch"),
            "audit_trail": {
                "initiated_by": ctx.get("user_id", "unknown_user"),
                "role": ctx.get("role"),
                "stage": "L2_DRAFT_STAGE"
            }
        }
