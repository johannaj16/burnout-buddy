"""Server-owned evening ritual state machine for Burnout Buddy MVP.

This module defines deterministic state transitions and policy checks.
LLM output can suggest commands, but all transitions are validated here.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class EveningState(str, Enum):
    IDLE = "IDLE"
    MOOD_CAPTURED = "MOOD_CAPTURED"
    REST_RECOMMENDED = "REST_RECOMMENDED"
    PLAN_LOCKED = "PLAN_LOCKED"
    REST_ACTIVE = "REST_ACTIVE"
    EXECUTION_ACTIVE = "EXECUTION_ACTIVE"
    COMPLETE = "COMPLETE"
    SLEEP_CUTOFF = "SLEEP_CUTOFF"


class Command(str, Enum):
    RECORD_MOOD = "record_mood"
    RECOMMEND_REST = "recommend_rest"
    SELECT_REST_DURATION = "select_rest_duration"
    LOCK_PLAN = "lock_plan"
    START_REST = "start_rest"
    REQUEST_REST_EXTENSION = "request_rest_extension"
    END_REST = "end_rest"
    START_EXECUTION = "start_execution"
    COMPLETE_EVENING = "complete_evening"
    APPLY_SLEEP_CUTOFF = "apply_sleep_cutoff"


class ExtensionReasonClass(str, Enum):
    FATIGUE = "fatigue"
    OVERWHELM = "overwhelm"
    AVOIDANCE = "avoidance"
    TRANSITION_DIFFICULTY = "transition_difficulty"


@dataclass(slots=True)
class MachineContext:
    rest_extended_once: bool = False
    plan_locked: bool = False
    rest_active: bool = False


@dataclass(slots=True)
class TransitionResult:
    state: EveningState
    context: MachineContext
    accepted: bool
    error_code: Optional[str] = None


class StateMachineError(ValueError):
    pass


def transition(
    state: EveningState,
    command: Command,
    context: MachineContext,
    extension_reason: Optional[ExtensionReasonClass] = None,
) -> TransitionResult:
    """Apply a single command to the current state.

    Rules implemented:
    - Plan must be locked before rest starts.
    - First rest extension is direct.
    - Additional extension requires non-avoidance classification.
    - Sleep cutoff can preempt any non-terminal state.
    """

    if command == Command.APPLY_SLEEP_CUTOFF:
        if state in {EveningState.COMPLETE, EveningState.SLEEP_CUTOFF}:
            return TransitionResult(state=state, context=context, accepted=False, error_code="already_terminal")
        return TransitionResult(state=EveningState.SLEEP_CUTOFF, context=context, accepted=True)

    if state in {EveningState.COMPLETE, EveningState.SLEEP_CUTOFF}:
        return TransitionResult(state=state, context=context, accepted=False, error_code="terminal_state")

    if state == EveningState.IDLE:
        if command == Command.RECORD_MOOD:
            return TransitionResult(EveningState.MOOD_CAPTURED, context, True)
        return _reject(state, context, "invalid_from_idle")

    if state == EveningState.MOOD_CAPTURED:
        if command == Command.RECOMMEND_REST:
            return TransitionResult(EveningState.REST_RECOMMENDED, context, True)
        return _reject(state, context, "invalid_from_mood_captured")

    if state == EveningState.REST_RECOMMENDED:
        if command == Command.SELECT_REST_DURATION:
            return TransitionResult(EveningState.REST_RECOMMENDED, context, True)
        if command == Command.LOCK_PLAN:
            context.plan_locked = True
            return TransitionResult(EveningState.PLAN_LOCKED, context, True)
        return _reject(state, context, "invalid_from_rest_recommended")

    if state == EveningState.PLAN_LOCKED:
        if command == Command.START_REST:
            if not context.plan_locked:
                return _reject(state, context, "plan_not_locked")
            context.rest_active = True
            return TransitionResult(EveningState.REST_ACTIVE, context, True)
        return _reject(state, context, "invalid_from_plan_locked")

    if state == EveningState.REST_ACTIVE:
        if command == Command.REQUEST_REST_EXTENSION:
            if not context.rest_extended_once:
                context.rest_extended_once = True
                return TransitionResult(EveningState.REST_ACTIVE, context, True)
            if extension_reason is None:
                return _reject(state, context, "extension_reason_required")
            if extension_reason == ExtensionReasonClass.AVOIDANCE:
                return _reject(state, context, "avoidance_extension_denied")
            return TransitionResult(EveningState.REST_ACTIVE, context, True)
        if command in {Command.END_REST, Command.START_EXECUTION}:
            context.rest_active = False
            return TransitionResult(EveningState.EXECUTION_ACTIVE, context, True)
        return _reject(state, context, "invalid_from_rest_active")

    if state == EveningState.EXECUTION_ACTIVE:
        if command == Command.COMPLETE_EVENING:
            return TransitionResult(EveningState.COMPLETE, context, True)
        return _reject(state, context, "invalid_from_execution_active")

    raise StateMachineError(f"Unhandled state '{state}'")


def _reject(state: EveningState, context: MachineContext, error_code: str) -> TransitionResult:
    return TransitionResult(state=state, context=context, accepted=False, error_code=error_code)
