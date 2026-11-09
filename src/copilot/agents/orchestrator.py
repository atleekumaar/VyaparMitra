"""
LangGraph StateGraph & Multi-Agent Dispatcher for MerchantOS V1.
Orchestrates Business Briefing, Smart Inventory, and Finance Agent Tools.
"""
from typing import TypedDict, Optional, Dict, Any, List
from src.copilot.agents.security import Role, UnauthorizedAgentActionError
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
    def __init__(self):
        self.inv_tools = InventoryAgentTools()
        self.fin_tools = FinanceAgentTools()

    def route_and_execute(self, state: AgentState) -> AgentState:
        query_lower = state["query"].lower()
        context = {
            "tenant_id": state["tenant_id"],
            "user_id": state["user_id"],
            "role": state["role"],
            "branch_id": state.get("branch_id")
        }

        # 1. Finance Intent
        if any(w in query_lower for w in ["finance", "cash", "udhaar", "profit", "margin", "paisa"]):
            try:
                data = self.fin_tools.get_financial_health_summary(context=context)
                state["final_response"] = (
                    f"Financial Summary: Cash in hand Rs {data['cash_in_hand']}, Bank: Rs {data['bank_balance']}, "
                    f"Pending Udhaar: Rs {data['total_receivables_udhaar']}."
                )
                state["intent"] = "FINANCE_QUERY"
            except UnauthorizedAgentActionError:
                state["final_response"] = "Access Restricted: Only business Owners can view financial health and udhaar data."
                state["intent"] = "RESTRICTED"

        # 2. Inventory Intent
        elif any(w in query_lower for w in ["stock", "inventory", "maal", "item", "order"]):
            low_items = self.inv_tools.check_low_stock(context=context)
            if "order" in query_lower or "reorder" in query_lower:
                if state["role"] in [Role.OWNER.value, Role.SUPERVISOR.value]:
                    draft = self.inv_tools.draft_purchase_reorder(sku="SKU-OIL-1L", quantity=15, context=context)
                    state["draft_actions"].append(draft)
                    state["final_response"] = f"Created Purchase Request Draft for {draft['sku']} (Qty: {draft['quantity']}). Awaiting Owner Approval."
                    state["intent"] = "INVENTORY_REORDER_DRAFT"
                else:
                    state["final_response"] = "Access Restricted: Staff cannot create purchase reorder drafts."
                    state["intent"] = "RESTRICTED"
            else:
                names = ", ".join([f"{i['name']} ({i['stock']} left)" for i in low_items])
                state["final_response"] = f"Low stock alert: {names}."
                state["intent"] = "INVENTORY_QUERY"

        # 3. Daily Briefing / General
        else:
            state["final_response"] = f"MerchantOS Briefing: All business systems operational for tenant {state['tenant_id']}."
            state["intent"] = "BUSINESS_BRIEFING"

        return state
