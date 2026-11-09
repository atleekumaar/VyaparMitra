"""
Unit & Integration Tests for MerchantOS Agents & RAG (Days 1 to 6).
Verifies RBAC enforcement, tenant isolation, and approval gating.
"""
import pytest
from src.copilot.agents.security import Role, UnauthorizedAgentActionError, TenantIsolationError
from src.copilot.agents.inventory_tools import InventoryAgentTools
from src.copilot.agents.finance_tools import FinanceAgentTools
from src.copilot.agents.orchestrator import MerchantOSAgentOrchestrator, AgentState

def test_tenant_isolation_enforcement():
    with pytest.raises(TenantIsolationError):
        FinanceAgentTools.get_financial_health_summary(context={"role": "OWNER"})

def test_staff_finance_denial():
    ctx = {"tenant_id": "tenant_123", "role": "STAFF", "user_id": "staff_u1"}
    with pytest.raises(UnauthorizedAgentActionError):
        FinanceAgentTools.get_financial_health_summary(context=ctx)

def test_owner_finance_access():
    ctx = {"tenant_id": "tenant_123", "role": "OWNER", "user_id": "owner_u1"}
    res = FinanceAgentTools.get_financial_health_summary(context=ctx)
    assert res["working_capital_status"] == "HEALTHY"
    assert res["total_receivables_udhaar"] == 18900.00

def test_inventory_draft_l3_approval():
    ctx = {"tenant_id": "tenant_123", "role": "SUPERVISOR", "user_id": "sup_u1"}
    res = InventoryAgentTools.draft_purchase_reorder(sku="SKU-OIL-1L", quantity=10, context=ctx)
    assert res["status"] == "PENDING_APPROVAL"
    assert res["approval_required_by"] == "OWNER"

def test_orchestrator_routing_finance_staff_restricted():
    orch = MerchantOSAgentOrchestrator()
    state: AgentState = {
        "tenant_id": "tenant_123", "user_id": "staff_1", "role": "STAFF",
        "branch_id": "b1", "query": "Kitna cash aur udhaar bacha hai?",
        "intent": None, "messages": [], "draft_actions": [], "final_response": None
    }
    updated = orch.route_and_execute(state)
    assert "Access Restricted" in updated["final_response"]
    assert updated["intent"] == "RESTRICTED"

def test_orchestrator_reorder_draft_flow():
    orch = MerchantOSAgentOrchestrator()
    state: AgentState = {
        "tenant_id": "tenant_123", "user_id": "sup_1", "role": "SUPERVISOR",
        "branch_id": "b1", "query": "Mustard oil ka reorder create karo",
        "intent": None, "messages": [], "draft_actions": [], "final_response": None
    }
    updated = orch.route_and_execute(state)
    assert len(updated["draft_actions"]) == 1
    assert updated["draft_actions"][0]["status"] == "PENDING_APPROVAL"
