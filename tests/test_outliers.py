import pandas as pd

from engine.outliers import detect_outliers_iqr, detect_outliers_zscore, detect_outliers_isolation_forest


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
