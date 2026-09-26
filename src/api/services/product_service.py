"""
Product Service for VyaparMitra Phase 6 API.
Manages catalog listings, SKU margins, 7-day demand forecasts, and cross-sell pairings.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import pandas as pd

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
    ) -> List[ProductListItem]:
        feat_path = self.features_dir / "product_features.parquet"
        rank_path = self.analytics_dir / "products" / "product_rankings.parquet"
        forecast_path = self.ml_dir / "forecasts" / "product_demand_forecast_7d.parquet"

        products_map: Dict[str, Dict[str, Any]] = {}

        if feat_path.exists():
            df_feat = pd.read_parquet(feat_path)
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

        if rank_path.exists():
            df_rank = pd.read_parquet(rank_path)
            for idx, r in df_rank.iterrows():
                pid = str(r["product_id"])
                if pid in products_map:
                    products_map[pid]["total_revenue"] = round(float(r.get("revenue", 0.0)), 2)
                    products_map[pid]["total_units"] = int(r.get("units", 0))
                    products_map[pid]["status"] = "STAR" if idx < 10 else ("FOCUS" if idx < 30 else "MONITOR")

        if forecast_path.exists():
            df_f = pd.read_parquet(forecast_path)
            grouped = df_f.groupby("product_id")["predicted_units"].sum().to_dict()
            for pid, f_units in grouped.items():
                if pid in products_map:
                    products_map[pid]["forecast_7d_units"] = int(round(float(f_units)))

        items = list(products_map.values())

        # Filtering
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

    def get_product(self, product_id: str) -> Optional[ProductDetailResponse]:
        feat_path = self.features_dir / "product_features.parquet"
        rank_path = self.analytics_dir / "products" / "product_rankings.parquet"
        forecast_path = self.ml_dir / "forecasts" / "product_demand_forecast_7d.parquet"
        cross_path = self.rec_dir / "cross_sell_recommendations.parquet"
        action_path = self.rec_dir / "merchant_action_plan.parquet"

        if not feat_path.exists():
            return None

        df_feat = pd.read_parquet(feat_path)
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
        if rank_path.exists():
            df_rank = pd.read_parquet(rank_path)
            r_matched = df_rank[df_rank["product_id"] == actual_pid]
            if not r_matched.empty:
                tot_rev = round(float(r_matched.iloc[0].get("revenue", 0.0)), 2)
                tot_units = int(r_matched.iloc[0].get("units", 0))

        f_units = 0
        if forecast_path.exists():
            df_f = pd.read_parquet(forecast_path)
            f_matched = df_f[df_f["product_id"] == actual_pid]
            if not f_matched.empty:
                f_units = int(round(float(f_matched["predicted_units"].sum())))

        # Cross-sell pairings
        cross_sells: List[Dict[str, Any]] = []
        if cross_path.exists():
            df_cross = pd.read_parquet(cross_path)
            c_matched = df_cross[df_cross["entity_id"] == actual_pid]
            for _, r in c_matched.head(5).iterrows():
                cross_sells.append({
                    "paired_sku": str(r.get("recommended_entity_id", r.get("cross_product", ""))),
                    "confidence": round(float(r.get("confidence", 0.7)), 2),
                    "action": "Bundle Offer Counter Display",
                })

        # Related actions
        actions: List[ActionItem] = []
        if action_path.exists():
            df_act = pd.read_parquet(action_path)
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
