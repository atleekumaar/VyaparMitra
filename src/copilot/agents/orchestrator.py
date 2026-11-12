"""
MerchantOS Multi-Agent Orchestrator & State Dispatcher.
Routes merchant queries to Inventory, Finance, or Business Briefing agents using live DB data
and enforces RBAC + L3 approval gates.
"""
import re
from typing import Any, Dict, List, Optional, TypedDict
from src.copilot.agents.security import Role, UnauthorizedAgentActionError, TenantIsolationError, normalize_role
from src.copilot.agents.inventory_tools import InventoryAgentTools
from src.copilot.agents.finance_tools import FinanceAgentTools


class AgentState(TypedDict):
    tenant_id: str
    user_id: str
    role: str
    branch_id: Optional[str]
    query: str
    intent: Optional[str]
    messages: List[Dict[str, str]]
    draft_actions: List[Dict[str, Any]]
    final_response: Optional[str]


class MerchantOSAgentOrchestrator:
    """Routes merchant queries across live DB-backed agents with RBAC enforcement."""

    def __init__(self):
        self.inventory_tools = InventoryAgentTools()
        self.finance_tools = FinanceAgentTools()

    def _extract_reorder_params(self, query: str, low_stock_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extracts SKU/product and quantity from query, falling back to top low-stock item."""
        qty_match = re.search(r"(\d+)\s*(?:units?|pcs?|packets?|bottles?|kg|liters?|qty)?", query.lower())
        qty = int(qty_match.group(1)) if qty_match else None

        # Match against actual low-stock inventory items first
        q_lower = query.lower()
        for item in low_stock_items:
            if item["sku"].lower() in q_lower or any(w in q_lower for w in item["name"].lower().split() if len(w) > 3):
                return {
                    "sku": item["sku"],
                    "quantity": qty or item["recommended_reorder_qty"],
                }

        # Explicit fallback for mustard oil or first low-stock alert
        if "mustard" in q_lower or "oil" in q_lower:
            return {"sku": "SKU-OIL-001", "quantity": qty or 50}
        if low_stock_items:
            top = low_stock_items[0]
            return {"sku": top["sku"], "quantity": qty or top["recommended_reorder_qty"]}
        return {"sku": "SKU-GEN-001", "quantity": qty or 25}

    def route_and_execute(self, state: AgentState) -> AgentState:
        tenant_id = state.get("tenant_id")
        if not tenant_id:
            raise TenantIsolationError("Execution blocked: 'tenant_id' is mandatory in AgentState.")

        caller_role = normalize_role(state.get("role"))
        context = {
            "tenant_id": tenant_id,
            "user_id": state.get("user_id", "unknown"),
            "role": caller_role.value,
            "branch_id": state.get("branch_id"),
        }

        query_lower = state.get("query", "").lower()

        try:
            # 1. Reorder / Purchase Action -> L3 Approval Gating
            if any(w in query_lower for w in ["reorder", "order", "purchase", "buy stock", "restock"]):
                state["intent"] = "PURCHASE_REORDER_DRAFT"
                low_stock = self.inventory_tools.check_low_stock(context=context)
                params = self._extract_reorder_params(state.get("query", ""), low_stock)
                draft = self.inventory_tools.draft_purchase_reorder(
                    sku=params["sku"],
                    quantity=params["quantity"],
                    context=context,
                )
                state["draft_actions"].append(draft)
                state["final_response"] = (
                    f"Created Purchase Request Draft ({draft['approval_id']}) for {draft['product_name']} "
                    f"[{draft['sku']}] (Qty: {draft['quantity']}, Est. Cost: ₹{draft['estimated_cost']}). "
                    f"Awaiting Owner Approval."
                )

            # 2. Inventory / Stock Query
            elif any(w in query_lower for w in ["stock", "inventory", "low", "item", "alert"]):
                state["intent"] = "INVENTORY_QUERY"
                low_items = self.inventory_tools.check_low_stock(context=context)
                if not low_items:
                    state["final_response"] = "Inventory check complete: All items are above minimum stock thresholds."
                else:
                    summary_lines = [
                        f"{i['name']} ({i['sku']}): {i['stock']} left (Min: {i['threshold']}, Suggested Reorder: {i['recommended_reorder_qty']})"
                        for i in low_items[:5]
                    ]
                    state["final_response"] = f"Low stock alert ({len(low_items)} items): " + "; ".join(summary_lines)

            # 3. Finance / Profit / Udhaar Query
            elif any(w in query_lower for w in ["profit", "finance", "cash", "udhaar", "khata", "revenue", "expense"]):
                state["intent"] = "FINANCE_QUERY"
                fin = self.finance_tools.get_financial_health_summary(context=context)
                state["final_response"] = (
                    f"Financial Health Summary: Revenue ₹{fin['total_revenue']:,.2f}, "
                    f"Net Profit ₹{fin['net_profit']:,.2f} ({fin['net_margin_pct']}% margin), "
                    f"Pending Udhaar ₹{fin['pending_udhaar_receivables']:,.2f}, "
                    f"Supplier Payables ₹{fin['supplier_payables']:,.2f}."
                )

            # 4. General Business Briefing (Live DB aggregation)
            else:
                state["intent"] = "GENERAL_BRIEFING"
                low_items = self.inventory_tools.check_low_stock(context=context)
                if caller_role in (Role.OWNER, Role.SUPERVISOR):
                    fin = self.finance_tools.get_financial_health_summary(context=context)
                    pending_aprs = self.inventory_tools.list_approval_requests(status_filter="PENDING_APPROVAL", context=context)
                    state["final_response"] = (
                        f"MerchantOS Briefing for {tenant_id}: Revenue ₹{fin['total_revenue']:,.2f}, "
                        f"Net Profit ₹{fin['net_profit']:,.2f}, Pending Udhaar ₹{fin['pending_udhaar_receivables']:,.2f} | "
                        f"Low Stock Alerts: {len(low_items)} items | Pending Approvals: {len(pending_aprs)}."
                    )
                else:
                    state["final_response"] = (
                        f"MerchantOS Staff Briefing for {tenant_id}: {len(low_items)} low-stock items require attention today."
                    )

        except UnauthorizedAgentActionError as sec_err:
            state["intent"] = "RESTRICTED"
            state["final_response"] = f"Access Restricted: {str(sec_err)}"

        return state
