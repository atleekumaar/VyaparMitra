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
        if merchant_id:
            conn = get_db_connection()
            try:
                cust_count = conn.execute("SELECT COUNT(*) FROM customers WHERE business_id = ?", (merchant_id,)).fetchone()[0]
                if cust_count > 0:
                    query = """
                        SELECT c.id, c.name, c.city, c.current_balance, c.credit_limit,
                               COALESCE(SUM(s.total_amount), 0.0) as actual_spend,
                               COUNT(s.id) as actual_orders
                        FROM customers c
                        LEFT JOIN sales s ON s.customer_id = c.id AND s.status != 'CANCELLED'
                        WHERE c.business_id = ?
                        GROUP BY c.id
                        ORDER BY actual_spend DESC, c.name ASC
                        LIMIT ?
                    """
                    rows = conn.execute(query, (merchant_id, limit)).fetchall()
                    items = [
                        CustomerListItem(
                            customer_id=f"{r['name']} ({r['id']})" if r["name"] else r["id"],
                            segment="Loyal" if float(r["actual_spend"]) > 5000 else ("Regular" if float(r["actual_spend"]) > 0 else "New Lead"),
                            lifetime_spend=round(float(r["actual_spend"]), 2),
                            total_orders=int(r["actual_orders"]),
                            recency_days=3.0 if float(r["actual_spend"]) > 0 else 0.0,
                            churn_risk_tier="Low",
                            churn_probability=0.10,
                        )
                        for r in rows
                    ]
                    return items
                elif merchant_id not in ("M001", "M015"):
                    return []
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
        if merchant_id:
            conn = get_db_connection()
            try:
                clean_id = customer_id.split("(")[-1].rstrip(")") if "(" in customer_id else customer_id
                row = conn.execute(
                    "SELECT * FROM customers WHERE (id = ? OR id = ? OR LOWER(name) = LOWER(?)) AND business_id = ?",
                    (customer_id, clean_id, customer_id, merchant_id)
                ).fetchone()
                if row:
                    spend_row = conn.execute(
                        "SELECT COALESCE(SUM(total_amount), 0.0) as actual_spend, COUNT(id) as actual_orders FROM sales WHERE customer_id = ? AND status != 'CANCELLED'",
                        (row["id"],)
                    ).fetchone()
                    tot_spend = round(float(spend_row["actual_spend"]), 2) if spend_row else 0.0
                    tot_orders = int(spend_row["actual_orders"]) if spend_row else 0
                    return CustomerDetailResponse(
                        customer_id=row["id"],
                        segment="Loyal" if tot_spend > 5000 else ("Regular" if tot_spend > 0 else "New"),
                        lifetime_spend=tot_spend,
                        total_orders=tot_orders,
                        recency_days=3.0 if tot_spend > 0 else 0.0,
                        churn_risk_tier="Low",
                        churn_probability=0.10,
                        suggested_retention_action="Offer personalized discounts on frequent items.",
                        evidence=[
                            {"metric": "Credit Limit", "value": f"₹{float(row['credit_limit']):,.2f}", "source": "customers.credit_limit"},
                            {"metric": "Current Khata Balance", "value": f"₹{float(row['current_balance']):,.2f}", "source": "customers.current_balance"},
                            {"metric": "Contact", "value": str(row["phone"] or "Not provided"), "source": "customers.phone"},
                        ],
                    )
                elif merchant_id not in ("M001", "M015"):
                    return None
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
