import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from engine.audit import run_audit
from models import crud
from models.schema import Base


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def make_sample_df() -> pd.DataFrame:
    return pd.DataFrame({
        "id": [1, 2, 2, None],
        "amount": [10, -5, 20, 15],
    })


def test_get_or_create_source_is_idempotent(db_session):
    s1 = crud.get_or_create_source(db_session, name="test.csv", source_type="csv_upload")
    s2 = crud.get_or_create_source(db_session, name="test.csv", source_type="csv_upload")
    assert s1.id == s2.id


def test_save_report_persists_run_and_children(db_session):
    df = make_sample_df()
    report = run_audit(df, key_columns=["id"])

    source = crud.get_or_create_source(db_session, name="test.csv", source_type="csv_upload")
    audit_run = crud.save_report(db_session, source, report)

    assert audit_run.id is not None
    assert audit_run.row_count == 4
    assert audit_run.health_score == report.score.dataset_score
    assert len(audit_run.column_stats) == 2
    assert len(audit_run.issues) == len(report.issues)


def test_get_history_orders_most_recent_first(db_session):
    df = make_sample_df()
    source = crud.get_or_create_source(db_session, name="test.csv", source_type="csv_upload")

    report1 = run_audit(df)
    run1 = crud.save_report(db_session, source, report1)
    report2 = run_audit(df)
    run2 = crud.save_report(db_session, source, report2)

    history = crud.get_history(db_session, source.id)
    assert len(history) == 2
    assert history[0].id == run2.id
    assert history[1].id == run1.id


def test_rule_config_save_and_load_roundtrip(db_session):
    rules = [{"name": "id_required", "column": "id", "type": "not_null"}]
    crud.save_rule_config(db_session, "my_rules", rules)
    loaded = crud.load_rule_config(db_session, "my_rules")
    assert loaded == rules


def test_load_missing_rule_config_returns_empty(db_session):
    assert crud.load_rule_config(db_session, "does_not_exist") == []
