"""Routes for tracking data quality trends over time, per source."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models import crud
from models.database import get_db

from ..schemas import AuditRunOut

router = APIRouter(prefix="/trends", tags=["trends"])


@router.get("/{source_id}", response_model=list[AuditRunOut])
def get_trend(source_id: int, limit: int = 50, db: Session = Depends(get_db)):
    """Returns audit run history for a source, most recent first, for charting score-over-time."""
    history = crud.get_history(db, source_id, limit=limit)
    if not history:
        raise HTTPException(status_code=404, detail="No audit history found for this source")
    return history
