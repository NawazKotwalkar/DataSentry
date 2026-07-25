"""Per-column profiling: type, null %, unique count, min/max, top values."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd


@dataclass
class ColumnProfile:
    name: str
    dtype: str
    null_count: int
    null_pct: float
    unique_count: int
    top_values: dict[Any, int] = field(default_factory=dict)
    min_value: Any = None
    max_value: Any = None
    mean_value: float | None = None
    std_value: float | None = None


def profile_column(series: pd.Series) -> ColumnProfile:
    n = len(series)
    null_count = int(series.isna().sum())
    null_pct = round((null_count / n) * 100, 2) if n else 0.0
    unique_count = int(series.nunique(dropna=True))

    top_values = series.value_counts(dropna=True).head(5).to_dict()

    min_value = max_value = mean_value = std_value = None
    if pd.api.types.is_numeric_dtype(series):
        non_null = series.dropna()
        if not non_null.empty:
            min_value = float(non_null.min())
            max_value = float(non_null.max())
            mean_value = float(non_null.mean())
            std_value = float(non_null.std()) if len(non_null) > 1 else 0.0
    elif pd.api.types.is_datetime64_any_dtype(series):
        non_null = series.dropna()
        if not non_null.empty:
            min_value = non_null.min()
            max_value = non_null.max()

    return ColumnProfile(
        name=series.name,
        dtype=str(series.dtype),
        null_count=null_count,
        null_pct=null_pct,
        unique_count=unique_count,
        top_values=top_values,
        min_value=min_value,
        max_value=max_value,
        mean_value=mean_value,
        std_value=std_value,
    )


def profile_dataset(df: pd.DataFrame) -> dict[str, ColumnProfile]:
    return {col: profile_column(df[col]) for col in df.columns}
