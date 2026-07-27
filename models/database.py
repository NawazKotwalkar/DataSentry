"""SQLAlchemy engine and session factory.

Reads DATABASE_URL from the environment, falling back to a local Postgres
default that matches docker-compose.yml. Import get_db() as a FastAPI
dependency; import Base from schema.py for model definitions.
"""
from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://datasentry:datasentry@localhost:5432/datasentry",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
