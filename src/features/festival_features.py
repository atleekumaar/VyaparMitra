"""
Festival feature engineering.
Merges festival context with transaction dates, supporting multi-festival dates,
and computes days_to_festival and days_after_festival.
"""

from __future__ import annotations

import logging
from typing import Optional
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def merge_festival_features(
    df: pd.DataFrame,
    festivals: pd.DataFrame,
    date_col: str = "date",
) -> pd.DataFrame:
    """
    Merge festival information with transaction records.
    Generates:
    - is_festival (0/1)
    - festival_name (str or 'None')
    - festival_type (str or 'None')
    - festival_intensity (float)
    - days_to_festival (int)
    - days_after_festival (int)
    """
    logger.info("Merging festival features for %d rows...", len(df))
    out = df.copy()

    if festivals is None or festivals.empty:
        out["is_festival"] = 0
        out["festival_name"] = "None"
        out["festival_type"] = "None"
        out["festival_intensity"] = 0.0
        out["days_to_festival"] = 999
        out["days_after_festival"] = 999
        return out

    # 1. Aggregate multiple festivals on the same date
    fest_agg = (
        festivals.groupby("date")
        .agg({
            "festival_name": lambda s: " / ".join(sorted(set(str(x) for x in s))),
            "festival_type": lambda s: " / ".join(sorted(set(str(x) for x in s))),
            "is_festival": "max",
            "festival_intensity": "max",
        })
        .reset_index()
    )

    # 2. Merge festival info on date
    out = pd.merge(out, fest_agg, on=date_col, how="left")
    out["is_festival"] = out["is_festival"].fillna(0).astype(int)
    out["festival_name"] = out["festival_name"].fillna("None")
    out["festival_type"] = out["festival_type"].fillna("None")
    out["festival_intensity"] = out["festival_intensity"].fillna(0.0).astype(float).round(2)

    # 3. Calculate distance to upcoming and past festivals
    unique_fest_dates = pd.to_datetime(fest_agg["date"]).sort_values().drop_duplicates().values
    
    if len(unique_fest_dates) > 0:
        row_dates = pd.to_datetime(out[date_col]).values
        
        # Upcoming festival (searchsorted right gives index of first festival >= row_date)
        idx_upcoming = np.searchsorted(unique_fest_dates, row_dates, side="left")
        
        days_to_list = []
        days_after_list = []
        n_fests = len(unique_fest_dates)

        for i, idx in enumerate(idx_upcoming):
            r_dt = row_dates[i]
            # Upcoming festival
            if idx < n_fests:
                diff_upcoming = (unique_fest_dates[idx] - r_dt) / np.timedelta64(1, "D")
                days_to_list.append(int(round(diff_upcoming)))
            else:
                days_to_list.append(999)  # No future festival in calendar

            # Past festival (closest festival <= row_date)
            idx_past = idx if (idx < n_fests and unique_fest_dates[idx] == r_dt) else idx - 1
            if idx_past >= 0:
                diff_past = (r_dt - unique_fest_dates[idx_past]) / np.timedelta64(1, "D")
                days_after_list.append(int(round(diff_past)))
            else:
                days_after_list.append(999)  # No past festival in calendar

        out["days_to_festival"] = days_to_list
        out["days_after_festival"] = days_after_list
    else:
        out["days_to_festival"] = 999
        out["days_after_festival"] = 999

    return out
