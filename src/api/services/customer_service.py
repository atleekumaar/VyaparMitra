"""
Customer Service for VyaparMitra Phase 6 API.
Manages customer segmentation, RFM metrics, churn probabilities, and retention actions.
Supports multi-tenant isolation via operational tables for non-demo merchants.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import pandas as pd
from src.api.db import fetch_table_df, get_db_connection

from src.api.config import APIConfig, get_api_config
from src.api.schemas import ActionItem, CustomerDetailResponse, CustomerListItem


class CustomerService:
    def __init__(self, config: APIConfig | None = None) -> None:
        self.config = config or get_api_config()
        self.features_dir = self.config.data_dir / "features"
        self.analytics_dir = self.config.data_dir / "analytics"
        self.ml_dir = self.config.data_dir / "ml"
        self.rec_dir = self.config.data_dir / "recommendations"

    def list_customers(
        self,
        segment: Optional[str] = None,
        risk_tier: Optional[str] = None,
        limit: int = 100,
        merchant_id: Optional[str] = None,
    ) -> List[CustomerListItem]:
        is_explicit_non_demo = merchant_id is not None and merchant_id not in ("M001", "M015")

        if is_explicit_non_demo:
            conn = get_db_connection()
            try:
                query = "SELECT id, name, city, current_balance, credit_limit FROM customers WHERE business_id = ?"
                params: List[Any] = [merchant_id]
                if segment:
                    query += " AND 1=1"
                query += " LIMIT ?"
                params.append(limit)

                rows = conn.execute(query, params).fetchall()
                items = [
                    CustomerListItem(
                        customer_id=r["id"],
                        segment="Regular",
                        lifetime_spend=float(r["current_balance"]),
                        total_orders=1,
                        recency_days=5.0,
                        churn_risk_tier="Low",
                        churn_probability=0.10,
                    )
                    for r in rows
                ]
                return items
            finally:
                conn.close()

        cust_map: Dict[str, Dict[str, Any]] = {}

        df_feat = fetch_table_df("customer_features")
        for _, r in df_feat.iterrows():
            cid = str(r["customer_id"])
            cust_map[cid] = {
                "customer_id": cid,
                "segment": "Regular",
                "lifetime_spend": round(float(r.get("total_spend", r.get("customer_total_spend", 0.0))), 2),
                "total_orders": int(r.get("total_orders", r.get("customer_total_orders", 1))),
                "recency_days": round(float(r.get("recency_days", r.get("days_since_last_order", 15.0))), 1),
                "churn_risk_tier": "Low",
                "churn_probability": 0.15,
            }

        df_seg = fetch_table_df("customer_segments")
        seg_col = "rfm_segment" if "rfm_segment" in df_seg.columns else ("segment" if "segment" in df_seg.columns else "customer_type")
        for _, r in df_seg.iterrows():
            cid = str(r["customer_id"])
            if cid in cust_map and seg_col in r:
                cust_map[cid]["segment"] = str(r[seg_col])

        df_risk = fetch_table_df("customer_risk_scores")
        risk_band_col = "risk_band" if "risk_band" in df_risk.columns else "churn_tier"
        score_col = "risk_probability" if "risk_probability" in df_risk.columns else "churn_probability"
        for _, r in df_risk.iterrows():
            cid = str(r["customer_id"])
            if cid in cust_map:
                cust_map[cid]["churn_risk_tier"] = str(r.get(risk_band_col, "Low")).title()
                cust_map[cid]["churn_probability"] = round(float(r.get(score_col, 0.2)), 4)

        items = list(cust_map.values())

        if segment:
            s_lower = segment.lower()
            items = [c for c in items if s_lower in c["segment"].lower()]

        if risk_tier:
            r_lower = risk_tier.lower()
            items = [c for c in items if r_lower in c["churn_risk_tier"].lower()]

        items.sort(key=lambda x: x["lifetime_spend"], reverse=True)

        return [
            CustomerListItem(
                customer_id=c["customer_id"],
                segment=c["segment"],
                lifetime_spend=c["lifetime_spend"],
                total_orders=c["total_orders"],
                recency_days=c["recency_days"],
                churn_risk_tier=c["churn_risk_tier"],
                churn_probability=c["churn_probability"],
            )
            for c in items[:limit]
        ]

    def get_customer(self, customer_id: str, merchant_id: Optional[str] = None) -> Optional[CustomerDetailResponse]:
        is_explicit_non_demo = merchant_id is not None and merchant_id not in ("M001", "M015")

        if is_explicit_non_demo:
            conn = get_db_connection()
            try:
                row = conn.execute("SELECT * FROM customers WHERE id = ? AND business_id = ?", (customer_id, merchant_id)).fetchone()
                if row:
                    return CustomerDetailResponse(
                        customer_id=row["id"],
                        segment="Regular",
                        lifetime_spend=float(row["current_balance"]),
                        total_orders=1,
                        recency_days=5.0,
                        churn_risk_tier="Low",
                        churn_probability=0.10,
                        recommended_action=None,
                    )
            finally:
                conn.close()

        df_feat = fetch_table_df("customer_features")
        matched = df_feat[df_feat["customer_id"].str.contains(customer_id, case=False, na=False)]
        if matched.empty:
            return None

        c_row = matched.iloc[0]
        actual_cid = str(c_row["customer_id"])
        tot_spend = round(float(c_row.get("total_spend", c_row.get("customer_total_spend", 0.0))), 2)
        tot_orders = int(c_row.get("total_orders", c_row.get("customer_total_orders", 1)))
        recency = round(float(c_row.get("recency_days", c_row.get("days_since_last_order", 15.0))), 1)

        segment = "Regular"
        df_seg = fetch_table_df("customer_segments")
        seg_matched = df_seg[df_seg["customer_id"] == actual_cid]
        if not seg_matched.empty:
            seg_col = "rfm_segment" if "rfm_segment" in df_seg.columns else ("segment" if "segment" in df_seg.columns else "customer_type")
            if seg_col in seg_matched.columns:
                segment = str(seg_matched.iloc[0][seg_col])

        risk_tier = "Low"
        churn_prob = 0.15
        df_risk = fetch_table_df("customer_risk_scores")
        risk_matched = df_risk[df_risk["customer_id"] == actual_cid]
        if not risk_matched.empty:
            risk_band_col = "risk_band" if "risk_band" in df_risk.columns else "churn_tier"
            score_col = "risk_probability" if "risk_probability" in df_risk.columns else "churn_probability"
            risk_tier = str(risk_matched.iloc[0].get(risk_band_col, "Low")).title()
            churn_prob = round(float(risk_matched.iloc[0].get(score_col, 0.15)), 4)

        rec_action = None
        df_act = fetch_table_df("merchant_action_plan")
        if not df_act.empty and "entity_id" in df_act.columns:
            a_matched = df_act[df_act["entity_id"] == actual_cid]
            if not a_matched.empty:
                r = a_matched.iloc[0]
                rec_action = ActionItem(
                    recommendation_id=str(r.get("recommendation_id", "")),
                    type=str(r.get("type", "CUSTOMER")),
                    priority_band=str(r.get("priority_band", "HIGH")).upper(),
                    priority_score=float(r.get("priority", 0.8)),
                    title=str(r.get("title", "")),
                    action=str(r.get("action", "")),
                    reason=str(r.get("reason", "")),
                    expected_impact=float(r.get("expected_impact", 1000.0)),
                    entity_id=actual_cid,
                    status=str(r.get("lifecycle_state", "GENERATED")).upper(),
                )

        return CustomerDetailResponse(
            customer_id=actual_cid,
            segment=segment,
            lifetime_spend=tot_spend,
            total_orders=tot_orders,
            recency_days=recency,
            churn_risk_tier=risk_tier,
            churn_probability=churn_prob,
            recommended_action=rec_action,
        )
