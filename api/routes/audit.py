"""Routes for triggering audits: CSV upload and live DB table."""
from __future__ import annotations

import io

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import create_engine as sa_create_engine
from sqlalchemy.orm import Session

from engine.audit import run_audit
from models import crud
from models.database import get_db

from ..schemas import AuditRunOut, DbTableAuditRequest

router = APIRouter(prefix="/audit", tags=["audit"])


def _rules_to_dicts(rules) -> list[dict]:
    if not rules:
        return []
    return [r.model_dump(exclude_none=True) for r in rules]


@router.post("/upload", response_model=AuditRunOut)
async def audit_csv_upload(
    file: UploadFile = File(...),
    key_columns: str | None = None,
    db: Session = Depends(get_db),
):
    """Audit an uploaded CSV file. key_columns is a comma-separated string."""
    raw = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(raw))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not parse CSV: {exc}") from exc

    key_cols = key_columns.split(",") if key_columns else None

    report = run_audit(df, key_columns=key_cols)

    source = crud.get_or_create_source(db, name=file.filename, source_type="csv_upload", location=file.filename)
    audit_run = crud.save_report(db, source, report)
    return audit_run


@router.post("/db-table", response_model=AuditRunOut)
def audit_db_table(request: DbTableAuditRequest, db: Session = Depends(get_db)):
    """Audit a table from a live, externally supplied database connection."""
    try:
        target_engine = sa_create_engine(request.connection_string)
        with target_engine.connect() as conn:
            df = pd.read_sql_table(request.table_name, conn)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not read table: {exc}") from exc

    options = request.options
    key_columns = options.key_columns if options else None
    format_checks = options.format_checks if options else None
    rule_defs = _rules_to_dicts(options.rules) if options else []
    cost_config = options.cost_config if options else None

    report = run_audit(
        df,
        key_columns=key_columns,
        format_checks=format_checks,
        rule_defs=rule_defs,
        cost_config=cost_config,
    )

    source = crud.get_or_create_source(
        db, name=request.table_name, source_type="db_table", location=request.table_name
    )
    audit_run = crud.save_report(db, source, report)
    return audit_run
