"""Weighted formula producing per-column and per-dataset health scores (0-100)."""
from __future__ import annotations

from dataclasses import dataclass

DEFAULT_WEIGHTS = {
    "nulls": 0.25,
    "duplicates": 0.20,
    "format_issues": 0.20,
    "outliers": 0.15,
    "rule_violations": 0.20,
}


@dataclass
class ScoreBreakdown:
    dataset_score: float
    component_scores: dict[str, float]
    weights: dict[str, float]


def _component_score(penalty_pct: float) -> float:
    """Converts a 0-100 'percent affected' figure into a 0-100 score (higher is healthier)."""
    return round(max(0.0, 100.0 - penalty_pct), 2)


def compute_score(
    avg_null_pct: float,
    duplicate_pct: float,
    avg_format_invalid_pct: float,
    avg_outlier_pct: float,
    avg_rule_violation_pct: float,
    weights: dict[str, float] | None = None,
) -> ScoreBreakdown:
    weights = weights or DEFAULT_WEIGHTS

    component_scores = {
        "nulls": _component_score(avg_null_pct),
        "duplicates": _component_score(duplicate_pct),
        "format_issues": _component_score(avg_format_invalid_pct),
        "outliers": _component_score(avg_outlier_pct),
        "rule_violations": _component_score(avg_rule_violation_pct),
    }

    dataset_score = sum(component_scores[k] * weights.get(k, 0) for k in component_scores)
    dataset_score = round(dataset_score, 2)

    return ScoreBreakdown(dataset_score=dataset_score, component_scores=component_scores, weights=weights)
