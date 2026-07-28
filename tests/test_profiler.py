import pandas as pd

from engine.profiler import profile_column, profile_dataset


def test_profile_column_numeric():
    s = pd.Series([1, 2, 3, None, 5], name="x")
    profile = profile_column(s)
    assert profile.name == "x"
    assert profile.null_count == 1
    assert profile.null_pct == 20.0
    assert profile.unique_count == 4
    assert profile.min_value == 1.0
    assert profile.max_value == 5.0


def test_profile_column_categorical():
    s = pd.Series(["a", "b", "a", "c"], name="cat")
    profile = profile_column(s)
    assert profile.null_count == 0
    assert profile.unique_count == 3
    assert profile.top_values["a"] == 2


def test_profile_dataset():
    df = pd.DataFrame({"a": [1, 2, None], "b": ["x", "y", "z"]})
    profiles = profile_dataset(df)
    assert set(profiles.keys()) == {"a", "b"}
    assert profiles["a"].null_count == 1
