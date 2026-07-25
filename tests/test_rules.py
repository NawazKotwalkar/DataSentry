import pandas as pd

from engine.rules import apply_rule, apply_rules


def test_not_null_rule():
    df = pd.DataFrame({"id": [1, None, 3]})
    rule = {"name": "id_required", "column": "id", "type": "not_null"}
    result = apply_rule(df, rule)
    assert result.violation_count == 1


def test_unique_rule():
    df = pd.DataFrame({"id": [1, 1, 2]})
    rule = {"name": "id_unique", "column": "id", "type": "unique"}
    result = apply_rule(df, rule)
    assert result.violation_count == 2


def test_min_value_rule():
    df = pd.DataFrame({"amount": [10, -5, 20]})
    rule = {"name": "positive_amount", "column": "amount", "type": "min_value", "value": 0}
    result = apply_rule(df, rule)
    assert result.violation_count == 1


def test_allowed_values_rule():
    df = pd.DataFrame({"status": ["pending", "shipped", "unknown"]})
    rule = {"name": "status_check", "column": "status", "type": "allowed_values",
            "values": ["pending", "shipped"]}
    result = apply_rule(df, rule)
    assert result.violation_count == 1


def test_missing_column_flagged():
    df = pd.DataFrame({"a": [1, 2]})
    rule = {"name": "ghost", "column": "b", "type": "not_null"}
    result = apply_rule(df, rule)
    assert result.violation_count == len(df)


def test_apply_rules_multiple():
    df = pd.DataFrame({"id": [1, None], "amount": [10, -1]})
    rules = [
        {"name": "id_required", "column": "id", "type": "not_null"},
        {"name": "positive_amount", "column": "amount", "type": "min_value", "value": 0},
    ]
    results = apply_rules(df, rules)
    assert len(results) == 2
