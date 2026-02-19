"""Store/repository abstraction for evening aggregates.

Uses Postgres when DATABASE_URL is configured, otherwise falls back to in-memory.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

from sqlalchemy import delete, select

from app.db.models import EveningModel
from app.db.session import SessionLocal, is_postgres_enabled
from app.domain.state_machine import EveningState, MachineContext


@dataclass(slots=True)
class EveningAggregate:
    """Current persisted view of a single user's evening session."""

    evening_id: str
    user_id: str
    state: EveningState
    context: MachineContext
    updated_at: datetime
    scroll_block_active: bool = False


class EveningStore(Protocol):
    """Contract for state persistence backends."""

    def get_or_create(self, evening_id: str, user_id: str) -> EveningAggregate: ...

    def save(self, aggregate: EveningAggregate) -> None: ...

    def clear(self) -> None: ...


class InMemoryEveningStore:
    """Simple key-value store keyed by (evening_id, user_id)."""

    def __init__(self) -> None:
        self._by_key: dict[tuple[str, str], EveningAggregate] = {}

    def get_or_create(self, evening_id: str, user_id: str) -> EveningAggregate:
        key = (evening_id, user_id)
        if key not in self._by_key:
            self._by_key[key] = EveningAggregate(
                evening_id=evening_id,
                user_id=user_id,
                state=EveningState.IDLE,
                context=MachineContext(),
                updated_at=datetime.now(UTC),
                scroll_block_active=False,
            )
        return self._by_key[key]

    def save(self, aggregate: EveningAggregate) -> None:
        self._by_key[(aggregate.evening_id, aggregate.user_id)] = aggregate

    def clear(self) -> None:
        """Test helper to reset all stored aggregates."""

        self._by_key.clear()


class PostgresEveningStore:
    """Postgres-backed store for evening aggregate snapshots."""

    def get_or_create(self, evening_id: str, user_id: str) -> EveningAggregate:
        if SessionLocal is None:
            raise RuntimeError("Postgres is not configured")

        with SessionLocal() as session:
            model = session.execute(
                select(EveningModel).where(EveningModel.evening_id == evening_id, EveningModel.user_id == user_id)
            ).scalar_one_or_none()

            if model is None:
                model = EveningModel(
                    evening_id=evening_id,
                    user_id=user_id,
                    state=EveningState.IDLE.value,
                    rest_extended_once=False,
                    plan_locked=False,
                    rest_active=False,
                    scroll_block_active=False,
                    updated_at=datetime.now(UTC),
                )
                session.add(model)
                session.commit()
                session.refresh(model)

            return self._to_aggregate(model)

    def save(self, aggregate: EveningAggregate) -> None:
        if SessionLocal is None:
            raise RuntimeError("Postgres is not configured")

        with SessionLocal() as session:
            model = session.execute(
                select(EveningModel).where(
                    EveningModel.evening_id == aggregate.evening_id,
                    EveningModel.user_id == aggregate.user_id,
                )
            ).scalar_one_or_none()

            if model is None:
                model = EveningModel(evening_id=aggregate.evening_id, user_id=aggregate.user_id, state=EveningState.IDLE.value)
                session.add(model)

            model.state = aggregate.state.value
            model.rest_extended_once = aggregate.context.rest_extended_once
            model.plan_locked = aggregate.context.plan_locked
            model.rest_active = aggregate.context.rest_active
            model.scroll_block_active = aggregate.scroll_block_active
            model.updated_at = aggregate.updated_at

            session.commit()

    def clear(self) -> None:
        """Test helper to delete persisted snapshots."""

        if SessionLocal is None:
            return
        with SessionLocal() as session:
            session.execute(delete(EveningModel))
            session.commit()

    @staticmethod
    def _to_aggregate(model: EveningModel) -> EveningAggregate:
        return EveningAggregate(
            evening_id=model.evening_id,
            user_id=model.user_id,
            state=EveningState(model.state),
            context=MachineContext(
                rest_extended_once=model.rest_extended_once,
                plan_locked=model.plan_locked,
                rest_active=model.rest_active,
            ),
            scroll_block_active=model.scroll_block_active,
            updated_at=model.updated_at,
        )


def _build_store() -> EveningStore:
    if is_postgres_enabled():
        return PostgresEveningStore()
    return InMemoryEveningStore()


store = _build_store()
