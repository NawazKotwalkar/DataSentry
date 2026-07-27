"""Routes for retrieving stored audit results."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models import crud
from models.database import get_db

from ..schemas import AuditRunDetailOut, SourceOut

router = APIRouter(tags=["reports"])


@router.get("/sources", response_model=list[SourceOut])
def list_sources(db: Session = Depends(get_db)):
    return crud.list_sources(db)


@router.get("/audit-runs/{audit_run_id}", response_model=AuditRunDetailOut)
def get_audit_run(audit_run_id: int, db: Session = Depends(get_db)):
    audit_run = crud.get_audit_run(db, audit_run_id)
    if audit_run is None:
        raise HTTPException(status_code=404, detail="Audit run not found")
    return audit_run
