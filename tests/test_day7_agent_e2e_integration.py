"""
Day 7: End-to-End Integration & Security Regression Suite.
Validates live request binding, cross-tenant isolation, and tool execution boundaries.
"""
import pytest
from src.copilot.agents.orchestrator import MerchantOSAgentOrchestrator, AgentState
from src.copilot.agents.security import Role, UnauthorizedAgentActionError, TenantIsolationError
from src.copilot.agents.inventory_tools import InventoryAgentTools
from src.copilot.agents.finance_tools import FinanceAgentTools

@pytest.fixture
def orchestrator():
    return MerchantOSAgentOrchestrator()

def test_e2e_tenant_isolation_boundary_enforcement(orchestrator):
    # Missing tenant must fail immediately
    invalid_state: AgentState = {
        "tenant_id": "",
        "user_id": "usr_test",
        "role": Role.OWNER.value,
        "branch_id": "b1",
        "query": "Check financial summary",
        "intent": None,
        "messages": [],
        "draft_actions": [],
        "final_response": None
    }
    with pytest.raises(TenantIsolationError):
        FinanceAgentTools.get_financial_health_summary(context={"role": "OWNER"})

def test_e2e_cross_tenant_branch_scoping(orchestrator):
    from datetime import datetime, timezone
    from src.api.db import init_db, get_db_connection
    init_db()
    conn = get_db_connection()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute("INSERT OR IGNORE INTO businesses (id, name, created_at) VALUES ('merchant_lucknow_01', 'Lucknow Store', ?)", (now,))
    conn.execute("INSERT OR IGNORE INTO branches (id, business_id, name, created_at) VALUES ('hazratganj_hub', 'merchant_lucknow_01', 'Hazratganj', ?)", (now,))
    conn.execute(
        """INSERT OR REPLACE INTO inventory (id, business_id, branch_id, product_id, product_name, category, current_stock, min_stock_threshold, unit_cost, selling_price, updated_at)
           VALUES ('inv_lko_01', 'merchant_lucknow_01', 'hazratganj_hub', 'SKU-LKO-01', 'Basmati Rice 5kg', 'Grains', 2, 10, 350.0, 420.0, ?)""",
        (now,),
    )
    conn.commit()
    conn.close()

    state_branch_a: AgentState = {
        "tenant_id": "merchant_lucknow_01",
        "user_id": "sup_01",
        "role": Role.SUPERVISOR.value,
        "branch_id": "hazratganj_hub",
        "query": "Check current stock",
        "intent": None,
        "messages": [],
        "draft_actions": [],
        "final_response": None
    }
    res = orchestrator.route_and_execute(state_branch_a)
    assert res["intent"] == "INVENTORY_QUERY"
    assert "Low stock alert" in res["final_response"]
    assert "Basmati Rice 5kg" in res["final_response"]

def test_e2e_l3_approval_gating_audit_trail(orchestrator):
    # Ensure draft orders capture full audit context
    state: AgentState = {
        "tenant_id": "merchant_lucknow_01",
        "user_id": "sup_01",
        "role": Role.SUPERVISOR.value,
        "branch_id": "hazratganj_hub",
        "query": "Please reorder mustard oil immediately",
        "intent": None,
        "messages": [],
        "draft_actions": [],
        "final_response": None
    }
    updated = orchestrator.route_and_execute(state)
    assert len(updated["draft_actions"]) == 1
    draft = updated["draft_actions"][0]
    assert draft["status"] == "PENDING_APPROVAL"
    assert draft["approval_required_by"] == Role.OWNER.value
    assert draft["audit_trail"]["stage"] == "L2_DRAFT_STAGE"
    assert draft["audit_trail"]["initiated_by"] == "sup_01"

def test_e2e_security_privilege_escalation_block(orchestrator):
    # Staff attempting to draft purchase orders
    state: AgentState = {
        "tenant_id": "merchant_lucknow_01",
        "user_id": "staff_01",
        "role": Role.STAFF.value,
        "branch_id": "hazratganj_hub",
        "query": "Order 20 units of oil",
        "intent": None,
        "messages": [],
        "draft_actions": [],
        "final_response": None
    }
    updated = orchestrator.route_and_execute(state)
    assert updated["intent"] == "RESTRICTED"
    assert len(updated["draft_actions"]) == 0
    assert "Access Restricted" in updated["final_response"]
