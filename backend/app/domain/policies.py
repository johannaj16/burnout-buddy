"""State-based policy helpers.

This module defines which commands are currently legal for each state.
"""

from __future__ import annotations

from app.domain.state_machine import Command, EveningState


def allowed_actions(state: EveningState) -> list[Command]:
    """Return the command whitelist for the current evening state."""

    if state == EveningState.IDLE:
        return [Command.RECORD_MOOD, Command.APPLY_SLEEP_CUTOFF]
    if state == EveningState.MOOD_CAPTURED:
        return [Command.RECOMMEND_REST, Command.APPLY_SLEEP_CUTOFF]
    if state == EveningState.REST_RECOMMENDED:
        return [Command.SELECT_REST_DURATION, Command.LOCK_PLAN, Command.APPLY_SLEEP_CUTOFF]
    if state == EveningState.PLAN_LOCKED:
        return [Command.START_REST, Command.APPLY_SLEEP_CUTOFF]
    if state == EveningState.REST_ACTIVE:
        return [Command.REQUEST_REST_EXTENSION, Command.END_REST, Command.START_EXECUTION, Command.APPLY_SLEEP_CUTOFF]
    if state == EveningState.EXECUTION_ACTIVE:
        return [Command.COMPLETE_EVENING, Command.APPLY_SLEEP_CUTOFF]
    return []
