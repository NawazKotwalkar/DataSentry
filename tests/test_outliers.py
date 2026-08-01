import pandas as pd

from engine.outliers import (
    detect_outliers_iqr,
    detect_outliers_zscore,
    detect_outliers_isolation_forest,
    is_likely_identifier,
    run_outlier_checks,
)


def test_iqr_outliers():
    s = pd.Series([10, 11, 12, 11, 10, 200], name="x")
    report = detect_outliers_iqr(s)
    assert report.outlier_count == 1
    assert report.outlier_indices == [5]


def test_zscore_outliers():
    s = pd.Series([10, 11, 12, 11, 10, 500], name="x")
    report = detect_outliers_zscore(s, threshold=2.0)
    assert report.outlier_count >= 1


def test_zscore_handles_zero_std():
    s = pd.Series([5, 5, 5, 5], name="x")
    report = detect_outliers_zscore(s)
    assert report.outlier_count == 0


def test_isolation_forest_small_dataset_returns_empty():
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    report = detect_outliers_isolation_forest(df, ["a", "b"])
    assert report.outlier_count == 0


def test_is_likely_identifier_flags_unique_column():
    s = pd.Series(range(1, 101), name="customer_id")
    assert is_likely_identifier(s) is True


def test_is_likely_identifier_does_not_flag_measurement():
    s = pd.Series([10, 12, 11, 10, 13, 12, 11, 10, 12, 100] * 10, name="order_amount")
    assert is_likely_identifier(s) is False


def test_run_outlier_checks_skips_identifier_columns_by_default():
    # zip-code-like identifier column that would otherwise flag as an outlier
    df = pd.DataFrame({
        "zip_code": list(range(10000, 10099)) + [90210],
        "amount": [50] * 100,
    })
    reports = run_outlier_checks(df)
    checked_columns = {r.column for r in reports}
    assert "zip_code" not in checked_columns


def test_run_outlier_checks_can_include_identifiers_when_disabled():
    df = pd.DataFrame({
        "zip_code": list(range(10000, 10099)) + [90210],
        "amount": [50] * 100,
    })
    reports = run_outlier_checks(df, skip_identifier_columns=False, include_multivariate=False)
    checked_columns = {r.column for r in reports}
    assert "zip_code" in checked_columns
