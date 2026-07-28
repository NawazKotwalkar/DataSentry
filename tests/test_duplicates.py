import pandas as pd
import pytest

from engine.duplicates import detect_duplicates


def test_exact_duplicates():
    df = pd.DataFrame({"a": [1, 1, 2], "b": ["x", "x", "y"]})
    report = detect_duplicates(df)
    assert report.exact_duplicate_rows == 2
    assert report.exact_duplicate_pct == pytest.approx(66.67, rel=0.01)


def test_key_duplicates():
    df = pd.DataFrame({"id": [1, 1, 2], "value": ["a", "b", "c"]})
    report = detect_duplicates(df, key_columns=["id"])
    assert report.key_duplicate_rows == 2
    assert report.exact_duplicate_rows == 0


def test_missing_key_column_raises():
    df = pd.DataFrame({"a": [1, 2]})
    with pytest.raises(ValueError):
        detect_duplicates(df, key_columns=["missing"])
