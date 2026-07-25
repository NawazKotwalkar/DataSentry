import pandas as pd

from engine.audit import run_audit


def make_sample_df() -> pd.DataFrame:
    return pd.DataFrame({
        "customer_id": [1, 2, 2, 4, None],
        "email": ["a@b.com", "bad-email", "c@d.com", "e@f.com", "g@h.com"],
        "order_amount": [100, 200, -50, 150, 9999],
        "status": ["pending", "shipped", "delivered", "unknown_status", "shipped"],
    })


def test_run_audit_end_to_end():
    df = make_sample_df()
    rules = [
        {"name": "amount_positive", "column": "order_amount", "type": "min_value", "value": 0},
        {"name": "status_allowed", "column": "status", "type": "allowed_values",
         "values": ["pending", "shipped", "delivered", "cancelled"]},
    ]
    format_checks = {"email": "email"}

    report = run_audit(
        df,
        key_columns=["customer_id"],
        format_checks=format_checks,
        rule_defs=rules,
    )

    assert report.row_count == 5
    assert report.column_count == 4
    assert 0 <= report.score.dataset_score <= 100
    assert report.cost_estimate.total_cost >= 0
    assert len(report.issues) > 0
    assert report.duplicate_report.key_duplicate_rows == 2


def test_run_audit_no_config_still_runs():
    df = make_sample_df()
    report = run_audit(df)
    assert report.row_count == 5
    assert isinstance(report.score.dataset_score, float)
