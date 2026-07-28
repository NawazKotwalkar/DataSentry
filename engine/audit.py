"""Orchestrator: run_audit(df, rules, cost_config) -> AuditReport.

This is the single entry point into the pure engine core. It has no knowledge
of FastAPI, SQLAlchemy, or Streamlit — it takes a DataFrame in and returns a
plain dataclass out.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd

from . import cost as cost_module
from . import duplicates as duplicates_module
from . import formats as formats_module
from . import outliers as outliers_module
from . import profiler as profiler_module
from . import rules as rules_module
from . import scoring as scoring_module


@dataclass
class AuditReport:
    run_at: str
    row_count: int
    column_count: int
    column_profiles: dict[str, profiler_module.ColumnProfile]
    duplicate_report: duplicates_module.DuplicateReport
    format_issues: list[formats_module.FormatIssue]
    outlier_reports: list[outliers_module.OutlierReport]
    rule_violations: list[rules_module.RuleViolation]
    score: scoring_module.ScoreBreakdown
    cost_estimate: cost_module.CostEstimate
    issues: list[dict[str, Any]] = field(default_factory=list)


def _avg(values: list[float]) -> float:
    return round(sum(values) / len(values), 2) if values else 0.0


def run_audit(
    df: pd.DataFrame,
    key_columns: list[str] | None = None,
    format_checks: dict[str, str] | None = None,
    rule_defs: list[dict[str, Any]] | None = None,
    cost_config: dict[str, float] | None = None,
    score_weights: dict[str, float] | None = None,
    numeric_columns: list[str] | None = None,
) -> AuditReport:
    row_count, column_count = len(df), len(df.columns)

    # 1. Profile every column
    column_profiles = profiler_module.profile_dataset(df)

    # 2. Duplicates
    dup_report = duplicates_module.detect_duplicates(df, key_columns)

    # 3. Format checks (only run if the caller supplied a mapping)
    format_issues = formats_module.run_format_checks(df, format_checks or {})

    # 4. Outliers (only on numeric columns)
    if numeric_columns is None:
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    outlier_reports = outliers_module.run_outlier_checks(df, numeric_columns)

    # 5. Custom rules
    rule_violations = rules_module.apply_rules(df, rule_defs or [])

    # --- roll everything up into score inputs ---
    avg_null_pct = _avg([p.null_pct for p in column_profiles.values()])
    avg_format_invalid_pct = _avg([f.invalid_pct for f in format_issues])
    avg_outlier_pct = _avg([o.outlier_pct for o in outlier_reports if o.method != "isolation_forest"])
    avg_rule_violation_pct = _avg([r.violation_pct for r in rule_violations])

    score = scoring_module.compute_score(
        avg_null_pct=avg_null_pct,
        duplicate_pct=dup_report.exact_duplicate_pct,
        avg_format_invalid_pct=avg_format_invalid_pct,
        avg_outlier_pct=avg_outlier_pct,
        avg_rule_violation_pct=avg_rule_violation_pct,
        weights=score_weights,
    )

    total_nulls = sum(p.null_count for p in column_profiles.values())
    total_format_errors = sum(f.invalid_count for f in format_issues)
    total_outliers = sum(o.outlier_count for o in outlier_reports if o.method != "isolation_forest")
    total_rule_violations = sum(r.violation_count for r in rule_violations)

    cost_estimate = cost_module.estimate_cost(
        total_nulls=total_nulls,
        total_duplicate_rows=dup_report.exact_duplicate_rows,
        total_format_errors=total_format_errors,
        total_outliers=total_outliers,
        total_rule_violations=total_rule_violations,
        cost_config=cost_config,
    )

    # Flatten a human-readable issues list for reporting/UI convenience
    issues: list[dict[str, Any]] = []
    for name, profile in column_profiles.items():
        if profile.null_pct > 0:
            issues.append({"type": "null", "column": name, "detail": f"{profile.null_pct}% null"})
    if dup_report.exact_duplicate_rows > 0:
        issues.append({"type": "duplicate", "column": None,
                        "detail": f"{dup_report.exact_duplicate_rows} exact duplicate rows"})
    for f in format_issues:
        if f.invalid_count > 0:
            issues.append({"type": "format", "column": f.column,
                            "detail": f"{f.invalid_count} {f.check} violations ({f.invalid_pct}%)"})
    for o in outlier_reports:
        if o.outlier_count > 0:
            issues.append({"type": "outlier", "column": o.column,
                            "detail": f"{o.outlier_count} outliers via {o.method} ({o.outlier_pct}%)"})
    for r in rule_violations:
        if r.violation_count > 0:
            issues.append({"type": "rule_violation", "column": r.column,
                            "detail": f"rule '{r.rule_name}' violated {r.violation_count} times ({r.violation_pct}%)"})

    return AuditReport(
        run_at=datetime.now(timezone.utc).isoformat(),
        row_count=row_count,
        column_count=column_count,
        column_profiles=column_profiles,
        duplicate_report=dup_report,
        format_issues=format_issues,
        outlier_reports=outlier_reports,
        rule_violations=rule_violations,
        score=score,
        cost_estimate=cost_estimate,
        issues=issues,
    )
