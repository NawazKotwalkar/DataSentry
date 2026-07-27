"""FastAPI application entry point.

Run with:
    uvicorn api.main:app --reload
"""
from __future__ import annotations

from fastapi import FastAPI

from models.database import engine
from models.schema import Base

from .routes import audit, reports, trends

app = FastAPI(
    title="DataSentry API",
    description="Data quality auditing engine — upload CSVs or point at a live DB table.",
    version="0.2.0",
)


@app.on_event("startup")
def on_startup() -> None:
    # Creates tables if they don't exist yet. For anything beyond local dev,
    # replace this with Alembic migrations.
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(audit.router)
app.include_router(reports.router)
app.include_router(trends.router)
