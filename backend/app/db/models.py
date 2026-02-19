"""ORM models for persisted backend state."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class EveningModel(Base):
    """Persisted snapshot for one user's evening session."""

    __tablename__ = "evenings"
    __table_args__ = (UniqueConstraint("evening_id", "user_id", name="uq_evening_user"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    evening_id: Mapped[str] = mapped_column(String(128), nullable=False)
    user_id: Mapped[str] = mapped_column(String(128), nullable=False)
    state: Mapped[str] = mapped_column(String(64), nullable=False)

    # Flattened machine context fields for simple querying and updates.
    rest_extended_once: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    plan_locked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    rest_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    scroll_block_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
