import sqlite3
import pytest
from unittest.mock import MagicMock
from src.api.db import get_db_connection, init_db
from src.api.routes.auth import signup, login, verify_otp, SignupRequest, LoginRequest
from src.api.routes.inventory import create_inventory_item, InventoryCreateRequest
from src.api.services.product_service import ProductService
from src.api.services.dashboard_service import DashboardService
from src.api.services.analytics_service import AnalyticsService
from src.api.auth import decode_access_token, CurrentUser


@pytest.fixture(autouse=True)
def setup_test_db():
    init_db()


def test_create_product_without_unit_cost_succeeds_and_updates_stock():
    conn = get_db_connection()
    req_mock = MagicMock()
    req_mock.client.host = "127.0.0.1"

    # Signup a merchant
    test_email = f"merchant_stock_test_{pytest.__version__.replace('.', '')}@example.com"
    conn.execute("DELETE FROM users WHERE email = ?", (test_email,))
    conn.commit()

    signup_res = signup(
        SignupRequest(email=test_email, password="password123", full_name="Stock Owner"),
        req_mock,
        conn,
    )
    biz_id = signup_res.user.business_id
    token = signup_res.access_token

    payload = decode_access_token(token)
    user = CurrentUser(
        id=payload["sub"],
        business_id=payload["business_id"],
        branch_id=payload["branch_id"],
        username=payload["username"],
        email=payload["email"],
        full_name="Stock Owner",
        role=payload["role"],
        permissions=[],
    )

    # 1. Add product with unit_cost=None (the exact scenario that caused 500 error previously)
    req1 = InventoryCreateRequest(
        product_id="SKU_SALT_01",
        product_name="Tata Salt 1kg",
        category="Groceries",
        selling_price=28.0,
        unit_cost=None,
        current_stock=75,
    )
    res1 = create_inventory_item(req1, req_mock, user, conn)
    conn.commit()

    assert res1.product_id == "SKU_SALT_01"
    assert res1.current_stock == 75
    assert res1.unit_cost == 22.4  # Auto-calculated 80% of selling price
    assert res1.stock_value_cost == round(75 * 22.4, 2)

    # 2. Add product with explicit unit cost
    req2 = InventoryCreateRequest(
        product_id="SKU_BUTTER_01",
        product_name="Amul Butter 500g",
        category="Dairy",
        selling_price=275.0,
        unit_cost=240.0,
        current_stock=40,
    )
    res2 = create_inventory_item(req2, req_mock, user, conn)
    conn.commit()

    assert res2.current_stock == 40
    assert res2.unit_cost == 240.0

    # 3. Verify ProductService.list_products returns real current_stock
    prod_svc = ProductService()
    products = prod_svc.list_products(merchant_id=biz_id)
    assert len(products) == 2

    p_map = {p.product_id: p for p in products}
    assert p_map["SKU_SALT_01"].current_stock == 75
    assert p_map["SKU_BUTTER_01"].current_stock == 40

    # 4. Verify DashboardService live inventory KPI
    dash_svc = DashboardService()
    summary = dash_svc.get_summary(merchant_id=biz_id)
    assert "inventory" in summary.kpis
    assert summary.kpis["inventory"].value == 115  # 75 + 40
    assert "2 SKUs" in summary.kpis["inventory"].subtext

    # 5. Verify AnalyticsService includes current_stock in performers
    ana_svc = AnalyticsService()
    prod_ana = ana_svc.get_product_analytics(merchant_id=biz_id)
    assert prod_ana.total_products_tracked == 2
    performer_map = {p.product_id: p for p in prod_ana.top_performers}
    assert performer_map["SKU_SALT_01"].current_stock == 75
    assert performer_map["SKU_BUTTER_01"].current_stock == 40

    # 6. Verify Login Again preserves merchant business_id and data
    login_res = login(
        LoginRequest(username_or_email=test_email, password="password123"),
        req_mock,
        conn,
    )
    assert login_res.user.business_id == biz_id
    assert login_res.user.business_name == f"Stock Owner's Store"

    reloaded_products = prod_svc.list_products(merchant_id=login_res.user.business_id)
    assert len(reloaded_products) == 2
    assert {p.current_stock for p in reloaded_products} == {75, 40}
