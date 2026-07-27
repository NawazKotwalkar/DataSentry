"""SQLAlchemy ORM models: AuditRun, ColumnStat, Issue, RuleConfig, Source."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Source(Base):
    """A dataset source: an uploaded file, or a live DB table connection."""
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    source_type = Column(String(20), nullable=False)  # "csv_upload" | "db_table"
    location = Column(Text, nullable=True)  # file name, or "schema.table" for DB sources
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    audit_runs = relationship("AuditRun", back_populates="source", cascade="all, delete-orphan")


class AuditRun(Base):
    """One execution of run_audit() against a Source, with its top-line results."""
    __tablename__ = "audit_runs"

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    run_at = Column(DateTime(timezone=True), default=_utcnow)
    row_count = Column(Integer, nullable=False)
    column_count = Column(Integer, nullable=False)
    health_score = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)

    source = relationship("Source", back_populates="audit_runs")
    column_stats = relationship("ColumnStat", back_populates="audit_run", cascade="all, delete-orphan")
    issues = relationship("Issue", back_populates="audit_run", cascade="all, delete-orphan")


class ColumnStat(Base):
    """Per-column profiling stats for a given audit run."""
    __tablename__ = "column_stats"

    id = Column(Integer, primary_key=True)
    audit_run_id = Column(Integer, ForeignKey("audit_runs.id"), nullable=False)
    column_name = Column(String(255), nullable=False)
    dtype = Column(String(50), nullable=True)
    null_count = Column(Integer, nullable=False, default=0)
    null_pct = Column(Float, nullable=False, default=0.0)
    unique_count = Column(Integer, nullable=False, default=0)

    audit_run = relationship("AuditRun", back_populates="column_stats")


class Issue(Base):
    """A single flagged issue (null, duplicate, format, outlier, or rule violation)."""
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True)
    audit_run_id = Column(Integer, ForeignKey("audit_runs.id"), nullable=False)
    issue_type = Column(String(50), nullable=False)
    column_name = Column(String(255), nullable=True)
    detail = Column(Text, nullable=False)

    audit_run = relationship("AuditRun", back_populates="issues")


class RuleConfig(Base):
    """A saved, named set of validation rules (JSON blob), reusable across audits."""
    __tablename__ = "rule_configs"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    rules_json = Column(Text, nullable=False)  # JSON-encoded list of rule dicts
    created_at = Column(DateTime(timezone=True), default=_utcnow)
