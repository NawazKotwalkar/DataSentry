"""CRUD helpers bridging the pure engine.AuditReport to the Postgres schema."""
from __future__ import annotations

import json

from sqlalchemy.orm import Session

from engine.audit import AuditReport
from . import schema


def get_or_create_source(db: Session, name: str, source_type: str, location: str | None = None) -> schema.Source:
    source = (
        db.query(schema.Source)
        .filter(schema.Source.name == name, schema.Source.source_type == source_type)
        .first()
    )
    if source:
        return source
    source = schema.Source(name=name, source_type=source_type, location=location)
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


def save_report(db: Session, source: schema.Source, report: AuditReport) -> schema.AuditRun:
    audit_run = schema.AuditRun(
        source_id=source.id,
        row_count=report.row_count,
        column_count=report.column_count,
        health_score=report.score.dataset_score,
        total_cost=report.cost_estimate.total_cost,
    )
    db.add(audit_run)
    db.flush()  # get audit_run.id before adding children

    for name, profile in report.column_profiles.items():
        db.add(schema.ColumnStat(
            audit_run_id=audit_run.id,
            column_name=name,
            dtype=profile.dtype,
            null_count=profile.null_count,
            null_pct=profile.null_pct,
            unique_count=profile.unique_count,
        ))

    for issue in report.issues:
        db.add(schema.Issue(
            audit_run_id=audit_run.id,
            issue_type=issue["type"],
            column_name=issue["column"],
            detail=issue["detail"],
        ))

    db.commit()
    db.refresh(audit_run)
    return audit_run


def get_audit_run(db: Session, audit_run_id: int) -> schema.AuditRun | None:
    return db.query(schema.AuditRun).filter(schema.AuditRun.id == audit_run_id).first()


def get_history(db: Session, source_id: int, limit: int = 50) -> list[schema.AuditRun]:
    return (
        db.query(schema.AuditRun)
        .filter(schema.AuditRun.source_id == source_id)
        .order_by(schema.AuditRun.run_at.desc())
        .limit(limit)
        .all()
    )


def list_sources(db: Session) -> list[schema.Source]:
    return db.query(schema.Source).order_by(schema.Source.created_at.desc()).all()


def save_rule_config(db: Session, name: str, rules: list[dict]) -> schema.RuleConfig:
    existing = db.query(schema.RuleConfig).filter(schema.RuleConfig.name == name).first()
    rules_json = json.dumps(rules)
    if existing:
        existing.rules_json = rules_json
        db.commit()
        db.refresh(existing)
        return existing
    rule_config = schema.RuleConfig(name=name, rules_json=rules_json)
    db.add(rule_config)
    db.commit()
    db.refresh(rule_config)
    return rule_config


def load_rule_config(db: Session, name: str) -> list[dict]:
    rule_config = db.query(schema.RuleConfig).filter(schema.RuleConfig.name == name).first()
    if not rule_config:
        return []
    return json.loads(rule_config.rules_json)
