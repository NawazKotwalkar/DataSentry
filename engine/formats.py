"""Regex-based format checks: emails, phone numbers, mixed date formats."""
from __future__ import annotations

import re
from dataclasses import dataclass

import pandas as pd

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^\+?[\d\s\-().]{7,15}$")

# Common date patterns; used to detect a column mixing multiple formats.
DATE_PATTERNS = {
    "YYYY-MM-DD": re.compile(r"^\d{4}-\d{2}-\d{2}$"),
    "MM/DD/YYYY": re.compile(r"^\d{1,2}/\d{1,2}/\d{4}$"),
    "DD-MM-YYYY": re.compile(r"^\d{1,2}-\d{1,2}-\d{4}$"),
    "DD Mon YYYY": re.compile(r"^\d{1,2} [A-Za-z]{3,9} \d{4}$"),
}


@dataclass
class FormatIssue:
    column: str
    check: str
    invalid_count: int
    invalid_pct: float
    examples: list[str]


def _pct(count: int, total: int) -> float:
    return round((count / total) * 100, 2) if total else 0.0


def check_email_column(series: pd.Series) -> FormatIssue:
    non_null = series.dropna().astype(str)
    invalid_mask = ~non_null.str.match(EMAIL_RE)
    invalid = non_null[invalid_mask]
    return FormatIssue(
        column=series.name,
        check="email_format",
        invalid_count=len(invalid),
        invalid_pct=_pct(len(invalid), len(non_null)),
        examples=invalid.head(3).tolist(),
    )


def check_phone_column(series: pd.Series) -> FormatIssue:
    non_null = series.dropna().astype(str)
    invalid_mask = ~non_null.str.match(PHONE_RE)
    invalid = non_null[invalid_mask]
    return FormatIssue(
        column=series.name,
        check="phone_format",
        invalid_count=len(invalid),
        invalid_pct=_pct(len(invalid), len(non_null)),
        examples=invalid.head(3).tolist(),
    )


def check_date_column_consistency(series: pd.Series) -> FormatIssue:
    """Flags a column as inconsistent if values match more than one known date pattern."""
    non_null = series.dropna().astype(str)
    pattern_hits = {name: 0 for name in DATE_PATTERNS}
    unmatched = []

    for value in non_null:
        matched_any = False
        for name, pattern in DATE_PATTERNS.items():
            if pattern.match(value):
                pattern_hits[name] += 1
                matched_any = True
                break
        if not matched_any:
            unmatched.append(value)

    formats_used = [name for name, count in pattern_hits.items() if count > 0]
    mixed = len(formats_used) > 1
    invalid_count = len(unmatched) + (0 if not mixed else sum(pattern_hits.values()) - max(pattern_hits.values()))

    return FormatIssue(
        column=series.name,
        check="date_consistency",
        invalid_count=invalid_count,
        invalid_pct=_pct(invalid_count, len(non_null)),
        examples=unmatched[:3] if unmatched else [],
    )


CHECK_REGISTRY = {
    "email": check_email_column,
    "phone": check_phone_column,
    "date": check_date_column_consistency,
}


def run_format_checks(df: pd.DataFrame, column_checks: dict[str, str]) -> list[FormatIssue]:
    """column_checks maps a column name to a check type: 'email', 'phone', or 'date'."""
    issues = []
    for column, check_type in column_checks.items():
        if column not in df.columns:
            continue
        check_fn = CHECK_REGISTRY.get(check_type)
        if check_fn is None:
            raise ValueError(f"Unknown format check type: {check_type}")
        issues.append(check_fn(df[column]))
    return issues
