"""
Customer Service for VyaparMitra Phase 6 API.
Manages customer segmentation, RFM metrics, churn probabilities, and retention actions.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import pandas as pd
from src.api.db import fetch_table_df

from src.api.config import APIConfig, get_api_config
from src.api.schemas import CustomerDetailResponse, CustomerListItem


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
    ) -> List[CustomerListItem]:
        feat_path = self.features_dir / "customer_features.parquet"
        seg_path = self.analytics_dir / "customers" / "customer_segments.parquet"
        risk_path = self.ml_dir / "customer_risk" / "customer_risk_scores.parquet"

        cust_map: Dict[str, Dict[str, Any]] = {}

        if True:
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

        if True:
            df_seg = fetch_table_df("customer_segments")
            seg_col = "rfm_segment" if "rfm_segment" in df_seg.columns else ("segment" if "segment" in df_seg.columns else "customer_type")
            for _, r in df_seg.iterrows():
                cid = str(r["customer_id"])
                if cid in cust_map and seg_col in r:
                    cust_map[cid]["segment"] = str(r[seg_col])


        if True:
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

    def get_customer(self, customer_id: str) -> Optional[CustomerDetailResponse]:
        feat_path = self.features_dir / "customer_features.parquet"
        seg_path = self.analytics_dir / "customers" / "customer_segments.parquet"
        risk_path = self.ml_dir / "customer_risk" / "customer_risk_scores.parquet"
        rec_path = self.rec_dir / "customer_recommendations.parquet"
        ev_path = self.rec_dir / "recommendation_evidence.parquet"

        if not True:
            return None

        df_feat = fetch_table_df("customer_features")
        matched = df_feat[df_feat["customer_id"].str.contains(customer_id, case=False, na=False)]
        if matched.empty:
            return None

        c_row = matched.iloc[0]
        actual_cid = str(c_row["customer_id"])
        spend = round(float(c_row.get("total_spend", c_row.get("customer_total_spend", 0.0))), 2)
        orders = int(c_row.get("total_orders", c_row.get("customer_total_orders", 1)))
        recency = round(float(c_row.get("recency_days", c_row.get("days_since_last_order", 20.0))), 1)

        segment = "Regular"
        if True:
            df_seg = fetch_table_df("customer_segments")
            s_m = df_seg[df_seg["customer_id"] == actual_cid]
            seg_col = "rfm_segment" if "rfm_segment" in df_seg.columns else ("segment" if "segment" in df_seg.columns else "customer_type")
            if not s_m.empty and seg_col in s_m.columns:
                segment = str(s_m.iloc[0][seg_col])


        tier = "Low"
        prob = 0.15
        if True:
            df_risk = fetch_table_df("customer_risk_scores")
            r_m = df_risk[df_risk["customer_id"] == actual_cid]
            if not r_m.empty:
                risk_band_col = "risk_band" if "risk_band" in df_risk.columns else "churn_tier"
                score_col = "risk_probability" if "risk_probability" in df_risk.columns else "churn_probability"
                tier = str(r_m.iloc[0].get(risk_band_col, "Low")).title()
                prob = round(float(r_m.iloc[0].get(score_col, 0.2)), 4)

        action_desc = "Standard customer follow-up via WhatsApp or phone call."
        if True:
            df_rec = fetch_table_df("customer_recommendations")
            rec_m = df_rec[df_rec["entity_id"] == actual_cid]
            if not rec_m.empty:
                action_desc = str(rec_m.iloc[0].get("action", action_desc))

        evidence_list: List[Dict[str, Any]] = []
        if True:
            df_ev = fetch_table_df("recommendation_evidence")
            ev_m = df_ev[df_ev["entity_id"] == actual_cid]
            evidence_list = ev_m.head(4).to_dict(orient="records")

        return CustomerDetailResponse(
            customer_id=actual_cid,
            segment=segment,
            lifetime_spend=spend,
            total_orders=orders,
            recency_days=recency,
            churn_risk_tier=tier,
            churn_probability=prob,
            suggested_retention_action=action_desc,
            evidence=evidence_list,
        )
