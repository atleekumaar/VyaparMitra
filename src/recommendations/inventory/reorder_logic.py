"""
Statistical safety stock and reorder point formulas for inventory decision support.
"""

from __future__ import annotations

import math


def calculate_safety_stock(
    demand_std: float,
    lead_time_days: int = 3,
    z_score: float = 1.645,
) -> float:
    """
    Computes statistical safety stock for a target service level.
    Formula: SS = Z * sigma_D * sqrt(lead_time)
    """
    if demand_std <= 0 or lead_time_days <= 0:
        return 1.0
    ss = z_score * float(demand_std) * math.sqrt(float(lead_time_days))
    return round(max(1.0, ss), 2)


def calculate_reorder_point(
    daily_velocity: float,
    lead_time_days: int = 3,
    safety_stock: float = 0.0,
) -> float:
    """
    Computes reorder point (ROP).
    Formula: ROP = (daily_velocity * lead_time) + safety_stock
    """
    lead_time_demand = float(daily_velocity) * float(lead_time_days)
    rop = lead_time_demand + float(safety_stock)
    return round(max(1.0, rop), 2)


def calculate_reorder_quantity(
    forecast_demand_7d: float,
    safety_stock: float,
    min_units: int = 5,
) -> int:
    """
    Computes recommended reorder batch quantity.
    Ensures coverage of 7-day forward demand plus protective safety buffer.
    """
    rec_qty = float(forecast_demand_7d) + float(safety_stock)
    return max(int(min_units), int(math.ceil(rec_qty)))
