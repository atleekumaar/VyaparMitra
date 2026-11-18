"""
Product Service for VyaparMitra Phase 6 API.
Manages catalog listings, SKU margins, 7-day demand forecasts, and cross-sell pairings.
Supports multi-tenant isolation via operational inventory tables for non-demo merchants.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import pandas as pd
from src.api.db import fetch_table_df, get_db_connection

from src.api.config import APIConfig, get_api_config
from src.api.schemas import ActionItem, ProductDetailResponse, ProductListItem


class ProductService:
    def __init__(self, config: APIConfig | None = None) -> None:
        self.config = config or get_api_config()
        self.features_dir = self.config.data_dir / "features"
        self.analytics_dir = self.config.data_dir / "analytics"
        self.ml_dir = self.config.data_dir / "ml"
        self.rec_dir = self.config.data_dir / "recommendations"

    def list_products(
        self,
        category: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 100,
        merchant_id: Optional[str] = None,
    ) -> List[ProductListItem]:
        if merchant_id:
            conn = get_db_connection()
            try:
                inv_count = conn.execute("SELECT COUNT(*) FROM inventory WHERE business_id = ?", (merchant_id,)).fetchone()[0]
                if inv_count > 0:
                    query = "SELECT product_id, product_name, category, selling_price, current_stock FROM inventory WHERE business_id = ?"
                    params: List[Any] = [merchant_id]
                    if category:
                        query += " AND LOWER(category) LIKE ?"
                        params.append(f"%{category.lower()}%")
                    if search:
                        query += " AND (LOWER(product_name) LIKE ? OR LOWER(product_id) LIKE ?)"
                        params.extend([f"%{search.lower()}%", f"%{search.lower()}%"])
                    query += " ORDER BY product_name ASC LIMIT ?"
                    params.append(limit)

                    rows = conn.execute(query, params).fetchall()
                    items = []
                    for r in rows:
                        pid = r["product_id"]
                        rev_row = conn.execute(
                            """
                            SELECT COALESCE(SUM(si.total_price), 0.0) as rev, COALESCE(SUM(si.quantity), 0) as units
                            FROM sale_items si
                            JOIN sales s ON si.sale_id = s.id
                            WHERE s.business_id = ? AND si.product_id = ? AND s.status != 'CANCELLED'
                            """,
                            (merchant_id, pid)
                        ).fetchone()
                        rev = float(rev_row["rev"]) if rev_row else 0.0
                        units = int(rev_row["units"]) if rev_row else 0
                        stock_val = int(r["current_stock"] if r["current_stock"] is not None else 0)
                        items.append(
                            ProductListItem(
                                product_id=pid,
                                product_name=r["product_name"],
                                category=r["category"] or "General",
                                selling_price=float(r["selling_price"]),
                                total_revenue=round(rev, 2),
                                total_units=units,
                                forecast_7d_units=0,
                                status="STAR" if rev > 10000 else ("FOCUS" if stock_val <= 15 else "MONITOR"),
                                current_stock=stock_val,
                            )
                        )
                    return items
                elif merchant_id not in ("M001", "M015"):
                    return []
            finally:
                conn.close()

        # Fallback to pre-computed synthetic data marts for demo mode M001 / M015
        products_map: Dict[str, Dict[str, Any]] = {}

        df_feat = fetch_table_df("product_features")
        for _, r in df_feat.iterrows():
            pid = str(r["product_id"])
            products_map[pid] = {
                "product_id": pid,
                "product_name": str(r.get("product_name", pid)),
                "category": str(r.get("product_category", "General")),
                "selling_price": float(r.get("selling_price", 100.0)),
                "total_revenue": 0.0,
                "total_units": 0,
                "forecast_7d_units": 0,
                "status": "MONITOR",
            }

        df_rank = fetch_table_df("product_rankings")
        for idx, r in df_rank.iterrows():
            pid = str(r["product_id"])
            if pid in products_map:
                products_map[pid]["total_revenue"] = round(float(r.get("revenue", 0.0)), 2)
                products_map[pid]["total_units"] = int(r.get("units", 0))
                products_map[pid]["status"] = "STAR" if idx < 10 else ("FOCUS" if idx < 30 else "MONITOR")

        df_f = fetch_table_df("product_demand_forecast_7d")
        if not df_f.empty and "product_id" in df_f.columns and "predicted_units" in df_f.columns:
            grouped = df_f.groupby("product_id")["predicted_units"].sum().to_dict()
            for pid, f_units in grouped.items():
                if pid in products_map:
                    products_map[pid]["forecast_7d_units"] = int(round(float(f_units)))

        items = list(products_map.values())

        if category:
            cat_lower = category.lower()
            items = [p for p in items if cat_lower in p["category"].lower()]

        if search:
            s_lower = search.lower()
            items = [p for p in items if s_lower in p["product_id"].lower() or s_lower in p["product_name"].lower()]

        items.sort(key=lambda x: x["total_revenue"], reverse=True)

        return [
            ProductListItem(
                product_id=p["product_id"],
                product_name=p["product_name"],
                category=p["category"],
                selling_price=p["selling_price"],
                total_revenue=p["total_revenue"],
                total_units=p["total_units"],
                forecast_7d_units=p["forecast_7d_units"],
                status=p["status"],
            )
            for p in items[:limit]
        ]

    def get_product(self, product_id: str, merchant_id: Optional[str] = None) -> Optional[ProductDetailResponse]:
        if merchant_id:
            conn = get_db_connection()
            try:
                row = conn.execute(
                    "SELECT * FROM inventory WHERE business_id = ? AND (product_id = ? OR id = ?)",
                    (merchant_id, product_id, product_id)
                ).fetchone()

                if row:
                    pid = row["product_id"]
                    sp = float(row["selling_price"])
                    uc = float(row["unit_cost"])
                    rev_row = conn.execute(
                        """
                        SELECT COALESCE(SUM(si.total_price), 0.0) as rev, COALESCE(SUM(si.quantity), 0) as units
                        FROM sale_items si
                        JOIN sales s ON si.sale_id = s.id
                        WHERE s.business_id = ? AND si.product_id = ? AND s.status != 'CANCELLED'
                        """,
                        (merchant_id, pid)
                    ).fetchone()
                    tot_rev = float(rev_row["rev"]) if rev_row else 0.0
                    tot_units = int(rev_row["units"]) if rev_row else 0
                    c_stock = int(row["current_stock"] if row["current_stock"] is not None else 0)

                    return ProductDetailResponse(
                        product_id=pid,
                        product_name=row["product_name"],
                        category=row["category"] or "General",
                        selling_price=sp,
                        unit_cost=uc,
                        margin=round(sp - uc, 2),
                        total_revenue=round(tot_rev, 2),
                        total_units_sold=tot_units,
                        forecast_7d_units=0,
                        cross_sell_recommendations=[],
                        active_recommendations=[],
                        current_stock=c_stock,
                    )
                elif merchant_id not in ("M001", "M015"):
                    return None
            finally:
                conn.close()

        df_feat = fetch_table_df("product_features")
        matched = df_feat[df_feat["product_id"].str.contains(product_id, case=False, na=False)]
        if matched.empty:
            return None

        p_row = matched.iloc[0]
        actual_pid = str(p_row["product_id"])
        p_name = str(p_row.get("product_name", actual_pid))
        cat = str(p_row.get("product_category", "General"))
        sp = float(p_row.get("selling_price", 100.0))
        uc = float(p_row.get("unit_cost", 70.0))
        margin = round(sp - uc, 2)

        tot_rev = 0.0
        tot_units = 0
        df_rank = fetch_table_df("product_rankings")
        r_matched = df_rank[df_rank["product_id"] == actual_pid]
        if not r_matched.empty:
            tot_rev = round(float(r_matched.iloc[0].get("revenue", 0.0)), 2)
            tot_units = int(r_matched.iloc[0].get("units", 0))

        f_units = 0
        df_f = fetch_table_df("product_demand_forecast_7d")
        if not df_f.empty and "product_id" in df_f.columns:
            f_matched = df_f[df_f["product_id"] == actual_pid]
            if not f_matched.empty:
                f_units = int(round(float(f_matched["predicted_units"].sum())))

        cross_sells: List[Dict[str, Any]] = []
        df_cross = fetch_table_df("cross_sell_recommendations")
        if not df_cross.empty and "entity_id" in df_cross.columns:
            c_matched = df_cross[df_cross["entity_id"] == actual_pid]
            for _, r in c_matched.head(5).iterrows():
                cross_sells.append({
                    "paired_sku": str(r.get("recommended_entity_id", r.get("cross_product", ""))),
                    "confidence": round(float(r.get("confidence", 0.7)), 2),
                    "action": "Bundle Offer Counter Display",
                })

        actions: List[ActionItem] = []
        df_act = fetch_table_df("merchant_action_plan")
        if not df_act.empty and "entity_id" in df_act.columns:
            a_matched = df_act[df_act["entity_id"] == actual_pid]
            for _, r in a_matched.head(3).iterrows():
                actions.append(
                    ActionItem(
                        recommendation_id=str(r.get("recommendation_id", "")),
                        type=str(r.get("type", "INVENTORY")),
                        priority_band=str(r.get("priority_band", "HIGH")).upper(),
                        priority_score=float(r.get("priority", 0.8)),
                        title=str(r.get("title", "")),
                        action=str(r.get("action", "")),
                        reason=str(r.get("reason", "")),
                        expected_impact=float(r.get("expected_impact", 1000.0)),
                        entity_id=actual_pid,
                        status=str(r.get("lifecycle_state", "GENERATED")).upper(),
                    )
                )

        return ProductDetailResponse(
            product_id=actual_pid,
            product_name=p_name,
            category=cat,
            selling_price=sp,
            unit_cost=uc,
            margin=margin,
            total_revenue=tot_rev,
            total_units_sold=tot_units,
            forecast_7d_units=f_units,
            cross_sell_recommendations=cross_sells,
            active_recommendations=actions,
        )
