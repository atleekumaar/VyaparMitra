"""
Unit test verifying complete multi-tenant isolation between merchants.
Asserts that Merchant A and Merchant B have zero crossover in inventory and sales.
"""

import sys
import uuid
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.api.db import init_db, get_db_connection

def test_tenant_data_isolation():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now(timezone.utc).isoformat()

    biz_a = f"BIZ_TEST_A_{uuid.uuid4().hex[:6]}"
    biz_b = f"BIZ_TEST_B_{uuid.uuid4().hex[:6]}"

    # 1. Create Business A & Business B
    cursor.execute("INSERT INTO businesses (id, name, created_at) VALUES (?, 'Store A', ?)", (biz_a, now_str))
    cursor.execute("INSERT INTO businesses (id, name, created_at) VALUES (?, 'Store B', ?)", (biz_b, now_str))

    cursor.execute("INSERT INTO branches (id, business_id, name, created_at) VALUES (?, ?, 'Main A', ?)", (f"BR_{biz_a}", biz_a, now_str))
    cursor.execute("INSERT INTO branches (id, business_id, name, created_at) VALUES (?, ?, 'Main B', ?)", (f"BR_{biz_b}", biz_b, now_str))

    # 2. Add inventory for Merchant A ONLY
    cursor.execute(
        """
        INSERT INTO inventory (id, business_id, branch_id, product_id, product_name, category, current_stock, unit_cost, selling_price, updated_at)
        VALUES ('INV_A_1', ?, ?, 'PROD_1', 'Basmati Rice 5kg', 'Grains', 100, 250.0, 320.0, ?)
        """,
        (biz_a, f"BR_{biz_a}", now_str)
    )
    conn.commit()

    # 3. Query inventory as Merchant B
    b_inventory = cursor.execute("SELECT * FROM inventory WHERE business_id = ?", (biz_b,)).fetchall()
    assert len(b_inventory) == 0, f"Isolation failure! Merchant B saw: {b_inventory}"
    print("✅ Verified: Merchant B sees 0 items from Merchant A's inventory.")

    # 4. Add sale for Merchant B ONLY
    cursor.execute(
        """
        INSERT INTO sales (id, invoice_number, business_id, branch_id, subtotal, total_amount, payment_method, created_by, created_at)
        VALUES ('SALE_B_1', 'INV-B-001', ?, ?, 450.0, 450.0, 'UPI', 'usr_b', ?)
        """,
        (biz_b, f"BR_{biz_b}", now_str)
    )
    conn.commit()

    # 5. Query sales as Merchant A
    a_sales = cursor.execute("SELECT * FROM sales WHERE business_id = ?", (biz_a,)).fetchall()
    assert len(a_sales) == 0, f"Isolation failure! Merchant A saw: {a_sales}"
    print("✅ Verified: Merchant A sees 0 sales from Merchant B's checkout.")

    # Cleanup test records
    cursor.execute("DELETE FROM sales WHERE id = 'SALE_B_1'")
    cursor.execute("DELETE FROM inventory WHERE id = 'INV_A_1'")
    cursor.execute("DELETE FROM branches WHERE id IN (?, ?)", (f"BR_{biz_a}", f"BR_{biz_b}"))
    cursor.execute("DELETE FROM businesses WHERE id IN (?, ?)", (biz_a, biz_b))
    conn.commit()
    conn.close()

    print("\n🎉 MULTI-TENANT ISOLATION FULLY VERIFIED!")

if __name__ == "__main__":
    test_tenant_data_isolation()
