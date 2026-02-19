"""Database engine/session configuration."""

from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "")


def is_postgres_enabled() -> bool:
    """Return true when a Postgres connection URL is configured."""

    return DATABASE_URL.startswith("postgresql")


engine = create_engine(DATABASE_URL, pool_pre_ping=True) if is_postgres_enabled() else None
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False) if engine else None
