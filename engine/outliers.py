"""Statistical (IQR/z-score) and ML-based (Isolation Forest) outlier detection."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


@dataclass
class OutlierReport:
    column: str
    method: str
    outlier_count: int
    outlier_pct: float
    outlier_indices: list[int] = field(default_factory=list)


def detect_outliers_iqr(series: pd.Series, multiplier: float = 1.5) -> OutlierReport:
    non_null = series.dropna()
    q1, q3 = non_null.quantile(0.25), non_null.quantile(0.75)
    iqr = q3 - q1
    lower, upper = q1 - multiplier * iqr, q3 + multiplier * iqr
    mask = (non_null < lower) | (non_null > upper)
    idx = non_null[mask].index.tolist()

    return OutlierReport(
        column=series.name,
        method="iqr",
        outlier_count=len(idx),
        outlier_pct=round((len(idx) / len(non_null)) * 100, 2) if len(non_null) else 0.0,
        outlier_indices=idx,
    )


def detect_outliers_zscore(series: pd.Series, threshold: float = 3.0) -> OutlierReport:
    non_null = series.dropna()
    if len(non_null) < 2 or non_null.std() == 0:
        return OutlierReport(column=series.name, method="zscore", outlier_count=0, outlier_pct=0.0)

    z_scores = (non_null - non_null.mean()) / non_null.std()
    mask = z_scores.abs() > threshold
    idx = non_null[mask].index.tolist()

    return OutlierReport(
        column=series.name,
        method="zscore",
        outlier_count=len(idx),
        outlier_pct=round((len(idx) / len(non_null)) * 100, 2),
        outlier_indices=idx,
    )


def detect_outliers_isolation_forest(
    df: pd.DataFrame,
    columns: list[str],
    contamination: float = 0.05,
    random_state: int = 42,
) -> OutlierReport:
    """Multivariate anomaly detection across the given numeric columns."""
    subset = df[columns].dropna()
    if len(subset) < 10:
        return OutlierReport(column=",".join(columns), method="isolation_forest", outlier_count=0, outlier_pct=0.0)

    model = IsolationForest(contamination=contamination, random_state=random_state)
    predictions = model.fit_predict(subset.values)
    outlier_mask = predictions == -1
    idx = subset[outlier_mask].index.tolist()

    return OutlierReport(
        column=",".join(columns),
        method="isolation_forest",
        outlier_count=len(idx),
        outlier_pct=round((len(idx) / len(subset)) * 100, 2),
        outlier_indices=idx,
    )


def is_likely_identifier(series: pd.Series, uniqueness_threshold: float = 0.95) -> bool:
    """Heuristic: a column where almost every non-null value is unique is very
    likely an identifier (customer_id, order_id, a zip/postal code, etc.),
    not a measurable quantity — outlier detection on it is meaningless
    ("90210 is far from 10001" is not a data quality issue)."""
    non_null = series.dropna()
    if len(non_null) < 10:
        return False
    return (non_null.nunique() / len(non_null)) >= uniqueness_threshold


def run_outlier_checks(
    df: pd.DataFrame,
    numeric_columns: list[str] | None = None,
    include_multivariate: bool = True,
    skip_identifier_columns: bool = True,
    identifier_uniqueness_threshold: float = 0.95,
) -> list[OutlierReport]:
    if numeric_columns is None:
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()

    if skip_identifier_columns:
        numeric_columns = [
            col for col in numeric_columns
            if not is_likely_identifier(df[col], identifier_uniqueness_threshold)
        ]

    reports: list[OutlierReport] = []
    for col in numeric_columns:
        reports.append(detect_outliers_iqr(df[col]))
        reports.append(detect_outliers_zscore(df[col]))

    if include_multivariate and len(numeric_columns) >= 2:
        reports.append(detect_outliers_isolation_forest(df, numeric_columns))

    return reports
