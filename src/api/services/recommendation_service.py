"""
Recommendation & Action Center Service for VyaparMitra Phase 6 API.
Manages recommendation queries, evidence breakdowns, and action lifecycle state transitions.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import HTTPException
import pandas as pd
from src.api.db import fetch_table_df

from src.api.config import APIConfig, get_api_config
from src.api.schemas import (
    ActionStatusUpdateResponse,
    EvidenceDetail,
    RecommendationDetailResponse,
    RecommendationListResponse,
)

logger = logging.getLogger(__name__)

VALID_STATUSES = {"GENERATED", "VIEWED", "ACCEPTED", "REJECTED", "EXECUTED", "EXPIRED"}


class RecommendationService:
    def __init__(self, config: APIConfig | None = None) -> None:
        self.config = config or get_api_config()
        self.rec_dir = self.config.data_dir / "recommendations"
        self.status_file = self.rec_dir / "action_statuses.json"
        self._statuses: Dict[str, str] = self._load_statuses()

    def _load_statuses(self) -> Dict[str, str]:
        if self.status_file.exists():
            try:
                with open(self.status_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load action statuses: {e}")
        return {}

    def _save_statuses(self) -> None:
        try:
            self.rec_dir.mkdir(parents=True, exist_ok=True)
            with open(self.status_file, "w", encoding="utf-8") as f:
                json.dump(self._statuses, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not persist action statuses: {e}")

    def list_recommendations(
        self,
        rec_type: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> RecommendationListResponse:
        all_recs_path = self.rec_dir / "all_recommendations.parquet"
        ev_path = self.rec_dir / "recommendation_evidence.parquet"

        if not True:
            return RecommendationListResponse(total_count=0, recommendations=[])

        df_recs = fetch_table_df("all_recommendations")
        df_ev = fetch_table_df("recommendation_evidence") if True else pd.DataFrame()

        # Build evidence lookup
        ev_by_id: Dict[str, List[EvidenceDetail]] = {}
        if not df_ev.empty:
            for _, r in df_ev.iterrows():
                rid = str(r.get("recommendation_id", ""))
                if rid not in ev_by_id:
                    ev_by_id[rid] = []
                ev_by_id[rid].append(
                    EvidenceDetail(
                        metric=str(r.get("metric", "")),
                        value=str(r.get("value", "")),
                        source=str(r.get("source", "")),
                        description=str(r.get("description", "")) if r.get("description") else None,
                    )
                )

        items: List[RecommendationDetailResponse] = []
        for _, r in df_recs.iterrows():
            rid = str(r.get("recommendation_id", ""))
            curr_status = self._statuses.get(rid, str(r.get("lifecycle_state", "GENERATED")).upper())

            r_type = str(r.get("type", "ACTION")).upper()
            prio_band = str(r.get("priority_band", "MEDIUM")).upper()

            # Apply filters
            if rec_type and rec_type.upper() != "ALL" and rec_type.upper() not in r_type:
                continue
            if priority and priority.upper() != "ALL" and priority.upper() != prio_band:
                continue
            if status and status.upper() != "ALL" and status.upper() != curr_status:
                continue

            items.append(
                RecommendationDetailResponse(
                    recommendation_id=rid,
                    type=r_type,
                    priority_band=prio_band,
                    priority_score=round(float(r.get("priority", r.get("priority_score", 0.5))), 4),
                    title=str(r.get("title", "")),
                    action=str(r.get("action", "")),
                    reason=str(r.get("reason", "")),
                    expected_impact=round(float(r.get("expected_impact", r.get("impact_score", 1000.0))), 2),
                    entity_id=str(r.get("entity_id", "")) if r.get("entity_id") else None,
                    status=curr_status,
                    evidence=ev_by_id.get(rid, []),
                    generated_at=str(r.get("created_at", datetime.now(timezone.utc).isoformat())),
                )
            )

        items.sort(key=lambda x: x.priority_score, reverse=True)

        return RecommendationListResponse(
            total_count=len(items),
            recommendations=items[:limit],
        )

    def get_recommendation(self, recommendation_id: str) -> Optional[RecommendationDetailResponse]:
        all_recs_path = self.rec_dir / "all_recommendations.parquet"
        ev_path = self.rec_dir / "recommendation_evidence.parquet"

        if not True:
            return None

        df_recs = fetch_table_df("all_recommendations")
        matched = df_recs[df_recs["recommendation_id"] == recommendation_id]
        if matched.empty:
            return None

        r = matched.iloc[0]
        rid = str(r["recommendation_id"])
        curr_status = self._statuses.get(rid, str(r.get("lifecycle_state", "GENERATED")).upper())

        ev_list: List[EvidenceDetail] = []
        if True:
            df_ev = fetch_table_df("recommendation_evidence")
            ev_matched = df_ev[df_ev["recommendation_id"] == rid]
            for _, ev_r in ev_matched.iterrows():
                ev_list.append(
                    EvidenceDetail(
                        metric=str(ev_r.get("metric", "")),
                        value=str(ev_r.get("value", "")),
                        source=str(ev_r.get("source", "")),
                        description=str(ev_r.get("description", "")) if ev_r.get("description") else None,
                    )
                )

        return RecommendationDetailResponse(
            recommendation_id=rid,
            type=str(r.get("type", "ACTION")).upper(),
            priority_band=str(r.get("priority_band", "MEDIUM")).upper(),
            priority_score=round(float(r.get("priority", r.get("priority_score", 0.5))), 4),
            title=str(r.get("title", "")),
            action=str(r.get("action", "")),
            reason=str(r.get("reason", "")),
            expected_impact=round(float(r.get("expected_impact", r.get("impact_score", 1000.0))), 2),
            entity_id=str(r.get("entity_id", "")) if r.get("entity_id") else None,
            status=curr_status,
            evidence=ev_list,
            generated_at=str(r.get("created_at", datetime.now(timezone.utc).isoformat())),
        )

    def update_status(self, recommendation_id: str, new_status: str) -> ActionStatusUpdateResponse:
        norm_status = new_status.upper().strip()
        if norm_status not in VALID_STATUSES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid action status '{new_status}'. Allowed values are: {sorted(VALID_STATUSES)}"
            )

        # Check existence
        rec = self.get_recommendation(recommendation_id)
        if not rec:
            raise HTTPException(
                status_code=404,
                detail=f"Recommendation with ID '{recommendation_id}' not found."
            )

        prev_status = rec.status
        self._statuses[recommendation_id] = norm_status
        self._save_statuses()

        now_str = datetime.now(timezone.utc).isoformat()
        return ActionStatusUpdateResponse(
            recommendation_id=recommendation_id,
            previous_status=prev_status,
            new_status=norm_status,
            updated_at=now_str,
            message=f"Action '{recommendation_id}' status successfully updated from {prev_status} to {norm_status}.",
        )
