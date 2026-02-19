"""Schema initialization helpers for local development."""

from __future__ import annotations

from app.db.base import Base
from app.db.session import engine, is_postgres_enabled

# Ensure model metadata is registered before create_all executes.
from app.db import models  # noqa: F401


def init_db_schema() -> None:
    """Create missing tables when Postgres is configured."""

    if not is_postgres_enabled() or engine is None:
        return
    Base.metadata.create_all(bind=engine)
