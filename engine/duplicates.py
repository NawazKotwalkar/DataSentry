"""Row-level and key-based duplicate detection."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class DuplicateReport:
    exact_duplicate_rows: int
    exact_duplicate_pct: float
    key_duplicate_rows: int = 0
    key_columns: tuple[str, ...] = ()


def find_exact_duplicates(df: pd.DataFrame) -> pd.Index:
    return df[df.duplicated(keep=False)].index


def find_key_duplicates(df: pd.DataFrame, key_columns: list[str]) -> pd.Index:
    missing = [c for c in key_columns if c not in df.columns]
    if missing:
        raise ValueError(f"Key column(s) not found in dataset: {missing}")
    return df[df.duplicated(subset=key_columns, keep=False)].index


def detect_duplicates(df: pd.DataFrame, key_columns: list[str] | None = None) -> DuplicateReport:
    n = len(df)
    exact_idx = find_exact_duplicates(df)
    exact_count = len(exact_idx)
    exact_pct = round((exact_count / n) * 100, 2) if n else 0.0

    key_count = 0
    if key_columns:
        key_count = len(find_key_duplicates(df, key_columns))

    return DuplicateReport(
        exact_duplicate_rows=exact_count,
        exact_duplicate_pct=exact_pct,
        key_duplicate_rows=key_count,
        key_columns=tuple(key_columns or ()),
    )
