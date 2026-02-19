"""Core state machine guardrail tests for the MVP."""

from app.domain.state_machine import Command, EveningState, ExtensionReasonClass, MachineContext, transition


def test_reject_start_rest_before_plan_lock() -> None:
    context = MachineContext(plan_locked=False)
    result = transition(EveningState.PLAN_LOCKED, Command.START_REST, context)
    assert result.accepted is False
    assert result.error_code == "plan_not_locked"


def test_first_rest_extension_is_allowed() -> None:
    context = MachineContext(rest_extended_once=False, plan_locked=True, rest_active=True)
    result = transition(EveningState.REST_ACTIVE, Command.REQUEST_REST_EXTENSION, context)
    assert result.accepted is True
    assert result.context.rest_extended_once is True


def test_second_rest_extension_requires_reason() -> None:
    context = MachineContext(rest_extended_once=True, plan_locked=True, rest_active=True)
    result = transition(EveningState.REST_ACTIVE, Command.REQUEST_REST_EXTENSION, context)
    assert result.accepted is False
    assert result.error_code == "extension_reason_required"


def test_second_rest_extension_denies_avoidance() -> None:
    context = MachineContext(rest_extended_once=True, plan_locked=True, rest_active=True)
    result = transition(
        EveningState.REST_ACTIVE,
        Command.REQUEST_REST_EXTENSION,
        context,
        extension_reason=ExtensionReasonClass.AVOIDANCE,
    )
    assert result.accepted is False
    assert result.error_code == "avoidance_extension_denied"


def test_sleep_cutoff_preempts_active_state() -> None:
    context = MachineContext(rest_extended_once=False, plan_locked=True, rest_active=True)
    result = transition(EveningState.REST_ACTIVE, Command.APPLY_SLEEP_CUTOFF, context)
    assert result.accepted is True
    assert result.state == EveningState.SLEEP_CUTOFF
