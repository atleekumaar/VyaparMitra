"""
Finance & Cashflow Intelligence Agent Tools for MerchantOS.
Connected to live SQLite/PostgreSQL tables (`sales`, `sale_items`, `expenses`, `customers`, `suppliers`).
Strictly restricted to OWNER & SUPERVISOR/MANAGER roles with tenant isolation.
"""
from typing import Any, Dict, List, Optional
from src.api.db import get_db_connection
from src.copilot.agents.security import Role, require_agent_role


class FinanceAgentTools:
    """Tools executed by the Finance Intelligence Agent against live DB."""

    @staticmethod
    @require_agent_role(Role.OWNER, Role.SUPERVISOR)
    def get_financial_health_summary(context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        ctx = context or {}
        tenant_id = ctx.get("tenant_id") or ctx.get("business_id")
        branch_id = ctx.get("branch_id")

        conn = get_db_connection()
        try:
            # 1. Total Revenue
            sales_sql = "SELECT SUM(total_amount), COUNT(*) FROM sales WHERE business_id = ? AND status = 'COMPLETED'"
            sales_params: List[Any] = [tenant_id]
            if branch_id:
                sales_sql += " AND branch_id = ?"
                sales_params.append(branch_id)
            rev_row = conn.execute(sales_sql, sales_params).fetchone()
            total_revenue = float(rev_row[0] or 0.0)
            sales_count = int(rev_row[1] or 0)

            # 2. COGS
            cogs_sql = """
                SELECT SUM(si.quantity * si.unit_cost)
                FROM sale_items si JOIN sales s ON si.sale_id = s.id
                WHERE s.business_id = ? AND s.status = 'COMPLETED'
            """
            cogs_params: List[Any] = [tenant_id]
            if branch_id:
                cogs_sql += " AND s.branch_id = ?"
                cogs_params.append(branch_id)
            cogs = float(conn.execute(cogs_sql, cogs_params).fetchone()[0] or 0.0)

            # 3. Operating Expenses
            exp_sql = "SELECT SUM(amount) FROM expenses WHERE business_id = ?"
            exp_params: List[Any] = [tenant_id]
            if branch_id:
                exp_sql += " AND branch_id = ?"
                exp_params.append(branch_id)
            total_expenses = float(conn.execute(exp_sql, exp_params).fetchone()[0] or 0.0)

            # 4. Receivables (Khata/Udhaar) & Payables
            pending_udhaar = float(
                conn.execute("SELECT SUM(current_balance) FROM customers WHERE business_id = ?", (tenant_id,)).fetchone()[0] or 0.0
            )
            supplier_payables = float(
                conn.execute("SELECT SUM(current_payable) FROM suppliers WHERE business_id = ?", (tenant_id,)).fetchone()[0] or 0.0
            )

            gross_profit = round(total_revenue - cogs, 2)
            net_profit = round(gross_profit - total_expenses, 2)
            margin_pct = round((net_profit / total_revenue) * 100, 1) if total_revenue > 0 else 0.0

            return {
                "tenant_id": tenant_id,
                "branch_id": branch_id,
                "total_revenue": round(total_revenue, 2),
                "completed_sales_count": sales_count,
                "cogs": round(cogs, 2),
                "gross_profit": gross_profit,
                "total_expenses": round(total_expenses, 2),
                "net_profit": net_profit,
                "net_margin_pct": margin_pct,
                "pending_udhaar_receivables": round(pending_udhaar, 2),
                "total_receivables_udhaar": round(pending_udhaar, 2),
                "supplier_payables": round(supplier_payables, 2),
                "status": "HEALTHY" if net_profit >= 0 else "DEFICIT",
                "working_capital_status": "HEALTHY" if net_profit >= 0 else "DEFICIT"
            }
        finally:
            conn.close()
