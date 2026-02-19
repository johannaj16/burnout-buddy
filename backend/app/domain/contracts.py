"""API/domain data contracts for evening command flow.

Contains request/response schemas exchanged between mobile clients and backend.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.domain.state_machine import Command, EveningState, ExtensionReasonClass, MachineContext


class EveningSnapshot(BaseModel):
    """Canonical state returned to clients after each command."""

    evening_id: str
    user_id: str
    status: EveningState
    context: MachineContext
    scroll_block_active: bool = False
    updated_at: datetime
    allowed_actions: list[Command] = Field(default_factory=list)


class CommandRequest(BaseModel):
    """Incoming command payload from the client."""

    user_id: str
    command: Command
    extension_reason: ExtensionReasonClass | None = None
    idempotency_key: str | None = None


class EventRecord(BaseModel):
    """Serialized event emitted by a successful command transition."""

    type: str
    payload: dict[str, Any] = Field(default_factory=dict)


class JobRecord(BaseModel):
    """Serialized background job queued as a side effect."""

    type: str
    payload: dict[str, Any] = Field(default_factory=dict)


class CommandResponse(BaseModel):
    """Command result, including updated snapshot and side effects."""

    accepted: bool
    error_code: str | None = None
    snapshot: EveningSnapshot
    emitted_events: list[EventRecord] = Field(default_factory=list)
    queued_jobs: list[JobRecord] = Field(default_factory=list)
