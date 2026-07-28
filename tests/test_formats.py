import pandas as pd

from engine.formats import check_email_column, check_phone_column, check_date_column_consistency


def test_email_format_check():
    s = pd.Series(["a@b.com", "not-an-email", "c@d.org"], name="email")
    issue = check_email_column(s)
    assert issue.invalid_count == 1
    assert "not-an-email" in issue.examples


def test_phone_format_check():
    s = pd.Series(["+1 416-555-0100", "abc", "555-0100"], name="phone")
    issue = check_phone_column(s)
    assert issue.invalid_count == 1


def test_date_consistency_check_mixed_formats():
    s = pd.Series(["2024-01-01", "01/02/2024", "2024-03-01"], name="date")
    issue = check_date_column_consistency(s)
    assert issue.invalid_count > 0


def test_date_consistency_check_uniform_format():
    s = pd.Series(["2024-01-01", "2024-02-01", "2024-03-01"], name="date")
    issue = check_date_column_consistency(s)
    assert issue.invalid_count == 0
