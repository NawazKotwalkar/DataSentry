"""Estimates the dollar business cost of data quality issues, per user-defined multipliers."""
from __future__ import annotations

from dataclasses import dataclass

DEFAULT_COST_CONFIG = {
    "cost_per_null": 0.50,
    "cost_per_duplicate_row": 2.00,
    "cost_per_format_error": 1.00,
    "cost_per_outlier": 1.50,
    "cost_per_rule_violation": 1.00,
}


@dataclass
class CostEstimate:
    total_cost: float
    breakdown: dict[str, float]


def estimate_cost(
    total_nulls: int,
    total_duplicate_rows: int,
    total_format_errors: int,
    total_outliers: int,
    total_rule_violations: int,
    cost_config: dict[str, float] | None = None,
) -> CostEstimate:
    cfg = cost_config or DEFAULT_COST_CONFIG

    breakdown = {
        "null_cost": round(total_nulls * cfg.get("cost_per_null", 0), 2),
        "duplicate_cost": round(total_duplicate_rows * cfg.get("cost_per_duplicate_row", 0), 2),
        "format_cost": round(total_format_errors * cfg.get("cost_per_format_error", 0), 2),
        "outlier_cost": round(total_outliers * cfg.get("cost_per_outlier", 0), 2),
        "rule_violation_cost": round(total_rule_violations * cfg.get("cost_per_rule_violation", 0), 2),
    }

    return CostEstimate(total_cost=round(sum(breakdown.values()), 2), breakdown=breakdown)
