from __future__ import annotations

from datetime import UTC, datetime

from app.domain.contracts import CommandResponse, EveningSnapshot
from app.domain.policies import allowed_actions
from app.domain.state_machine import Command, EveningState, ExtensionReasonClass, transition
from app.domain.store import EveningAggregate
from app.events.types import EventType
from app.events.writer import writer
from app.jobs.queue import JobType, queue


def apply_command(
    aggregate: EveningAggregate,
    command: Command,
    extension_reason: ExtensionReasonClass | None = None,
) -> CommandResponse:
    previous_state = aggregate.state
    transition_result = transition(
        state=aggregate.state,
        command=command,
        context=aggregate.context,
        extension_reason=extension_reason,
    )

    aggregate.state = transition_result.state
    aggregate.context = transition_result.context
    aggregate.updated_at = datetime.now(UTC)

    emitted_events = []
    queued_jobs = []

    if transition_result.accepted:
        emitted_events.extend(_emit_state_events(previous_state, aggregate.state, command, extension_reason))
        emitted_events.extend(_emit_side_effect_events(previous_state, aggregate.state, aggregate.evening_id, aggregate.user_id))
        queued_jobs.extend(_enqueue_jobs(previous_state, aggregate.state, aggregate.evening_id, aggregate.user_id))
        _sync_block_state(aggregate, previous_state, aggregate.state)

    snapshot = EveningSnapshot(
        evening_id=aggregate.evening_id,
        user_id=aggregate.user_id,
        status=aggregate.state,
        context=aggregate.context,
        scroll_block_active=aggregate.scroll_block_active,
        updated_at=aggregate.updated_at,
        allowed_actions=allowed_actions(aggregate.state),
    )

    return CommandResponse(
        accepted=transition_result.accepted,
        error_code=transition_result.error_code,
        snapshot=snapshot,
        emitted_events=emitted_events,
        queued_jobs=queued_jobs,
    )


def _emit_state_events(
    previous_state: EveningState,
    current_state: EveningState,
    command: Command,
    extension_reason: ExtensionReasonClass | None,
):
    events = []
    if command == Command.RECORD_MOOD:
        events.append(writer.emit(EventType.MOOD_RECORDED))
    elif command == Command.RECOMMEND_REST:
        events.append(writer.emit(EventType.REST_RECOMMENDED))
    elif command == Command.SELECT_REST_DURATION:
        events.append(writer.emit(EventType.REST_SELECTED))
    elif command == Command.LOCK_PLAN:
        events.append(writer.emit(EventType.PLAN_LOCKED))
    elif command == Command.REQUEST_REST_EXTENSION:
        events.append(writer.emit(EventType.REST_EXTENDED))
        if extension_reason is not None:
            events.append(writer.emit(EventType.REST_EXTENSION_REQUESTED_WITH_REASON, {"reason": extension_reason.value}))
    elif command == Command.COMPLETE_EVENING:
        events.append(writer.emit(EventType.EVENING_COMPLETED))
    elif command == Command.APPLY_SLEEP_CUTOFF and previous_state != current_state:
        events.append(writer.emit(EventType.SLEEP_CUTOFF_REACHED))
    return events


def _emit_side_effect_events(previous_state: EveningState, current_state: EveningState, evening_id: str, user_id: str):
    events = []
    if previous_state == EveningState.PLAN_LOCKED and current_state == EveningState.REST_ACTIVE:
        events.append(writer.emit(EventType.REST_STARTED, {"evening_id": evening_id, "user_id": user_id}))
        events.append(writer.emit(EventType.APPS_UNBLOCKED, {"evening_id": evening_id, "user_id": user_id}))
    if previous_state == EveningState.REST_ACTIVE and current_state == EveningState.EXECUTION_ACTIVE:
        events.append(writer.emit(EventType.REST_ENDED, {"evening_id": evening_id, "user_id": user_id}))
        events.append(writer.emit(EventType.EXECUTION_STARTED, {"evening_id": evening_id, "user_id": user_id}))
        events.append(writer.emit(EventType.APPS_BLOCKED, {"evening_id": evening_id, "user_id": user_id}))
    if current_state == EveningState.SLEEP_CUTOFF:
        events.append(writer.emit(EventType.APPS_BLOCKED, {"evening_id": evening_id, "user_id": user_id}))
    return events


def _enqueue_jobs(previous_state: EveningState, current_state: EveningState, evening_id: str, user_id: str):
    jobs = []
    if previous_state == EveningState.PLAN_LOCKED and current_state == EveningState.REST_ACTIVE:
        jobs.append(queue.enqueue(JobType.END_REST_WINDOW, {"evening_id": evening_id, "user_id": user_id}))
    if current_state == EveningState.SLEEP_CUTOFF:
        jobs.append(queue.enqueue(JobType.SLEEP_CUTOFF_ENFORCER, {"evening_id": evening_id, "user_id": user_id}))
    return jobs


def _sync_block_state(aggregate: EveningAggregate, previous_state: EveningState, current_state: EveningState) -> None:
    if previous_state == EveningState.PLAN_LOCKED and current_state == EveningState.REST_ACTIVE:
        aggregate.scroll_block_active = False
    elif previous_state == EveningState.REST_ACTIVE and current_state == EveningState.EXECUTION_ACTIVE:
        aggregate.scroll_block_active = True
    elif current_state == EveningState.SLEEP_CUTOFF:
        aggregate.scroll_block_active = True
