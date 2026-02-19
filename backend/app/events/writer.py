"""In-memory event writer used by the MVP service layer."""

from __future__ import annotations

from typing import Any

from app.domain.contracts import EventRecord
from app.events.types import EventType


class EventWriter:
    """Collects emitted events for API responses and tests."""

    def __init__(self) -> None:
        self.records: list[EventRecord] = []

    def emit(self, event_type: EventType, payload: dict[str, Any] | None = None) -> EventRecord:
        record = EventRecord(type=event_type.value, payload=payload or {})
        self.records.append(record)
        return record

    def clear(self) -> None:
        """Test helper to clear accumulated event records."""

        self.records.clear()


writer = EventWriter()
