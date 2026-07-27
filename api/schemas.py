"""Pydantic request/response models for the FastAPI layer."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class RuleDef(BaseModel):
    name: str
    column: str
    type: str
    value: float | None = None
    values: list[Any] | None = None
    pattern: str | None = None


class AuditOptions(BaseModel):
    """Optional parameters controlling how an audit is run."""
    key_columns: list[str] | None = None
    format_checks: dict[str, str] | None = None
    rules: list[RuleDef] | None = None
    cost_config: dict[str, float] | None = None


class DbTableAuditRequest(BaseModel):
    """Request body for auditing a live database table."""
    connection_string: str
    table_name: str
    options: AuditOptions | None = None


class ColumnStatOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    column_name: str
    dtype: str | None
    null_count: int
    null_pct: float
    unique_count: int


class IssueOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    issue_type: str
    column_name: str | None
    detail: str


class AuditRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_id: int
    run_at: datetime
    row_count: int
    column_count: int
    health_score: float
    total_cost: float


class AuditRunDetailOut(AuditRunOut):
    column_stats: list[ColumnStatOut] = []
    issues: list[IssueOut] = []


class SourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    source_type: str
    location: str | None
    created_at: datetime
