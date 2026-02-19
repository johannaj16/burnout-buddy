# Burnout Buddy State Machine (MVP)

This document defines the server-owned evening ritual state machine for the iOS-first MVP.

## Goals
- Keep conversation flexible but state transitions deterministic.
- Enforce policy constraints (plan lock, rest extension rules, sleep cutoff).
- Make transitions auditable via append-only events.

## Source of Truth
- Canonical state lives in backend (Postgres + event log).
- Mobile renders from backend snapshot.
- LLM may suggest actions, but backend validates and applies them.

## States
- `IDLE`: No active evening ritual.
- `MOOD_CAPTURED`: User has provided mood input.
- `REST_RECOMMENDED`: Rest duration/options shown; waiting for selection.
- `PLAN_LOCKED`: 1-2 goals locked prior to rest.
- `REST_ACTIVE`: Protected reset window running.
- `EXECUTION_ACTIVE`: Rest ended, locked plan visible and active.
- `COMPLETE`: Evening completed or ended due to cutoff.
- `SLEEP_CUTOFF`: Terminal boundary after sleep-time enforcement.

## Transition Diagram
```text
IDLE
 -> MOOD_CAPTURED
 -> REST_RECOMMENDED
 -> PLAN_LOCKED
 -> REST_ACTIVE
 -> EXECUTION_ACTIVE
 -> COMPLETE

Any active state -> SLEEP_CUTOFF (when local sleep cutoff reached)
```

## Events (MVP)
- `mood.recorded`
- `rest.recommended`
- `rest.selected`
- `plan.locked`
- `rest.started`
- `rest.extended`
- `rest.extension_requested_with_reason`
- `rest.ended`
- `execution.started`
- `task.completed`
- `evening.completed`
- `sleep.cutoff.reached`
- `apps.unblocked`
- `apps.blocked`

## Guardrails
- Plan lock required before entering `REST_ACTIVE`.
- In `REST_ACTIVE`, planning UI edits are blocked.
- One direct extension is allowed (`extended_once=false -> true`).
- Additional extension requires reason classification.
- If classification is avoidance, offer transition alternative instead of extending.
- On `REST_ACTIVE -> EXECUTION_ACTIVE`, selected scroll apps must be blocked.
- At sleep cutoff, enforce blocking and transition to `SLEEP_CUTOFF`.

## Command and Validation Model
Each client action is sent as a command. Backend validates command against current state and policy.

Example commands:
- `RecordMood`
- `RecommendRest`
- `SelectRestDuration`
- `LockPlan`
- `StartRest`
- `RequestRestExtension`
- `EndRest`
- `StartExecution`
- `CompleteEvening`
- `ApplySleepCutoff`

Validation outcomes:
- `accepted`: transition and emit events.
- `rejected`: return machine-readable error code and current snapshot.

## Side Effects by Transition
- `PLAN_LOCKED -> REST_ACTIVE`
  - Emit `rest.started`
  - Unblock selected apps (`apps.unblocked`)
  - Schedule `end_rest_window` job
- `REST_ACTIVE -> EXECUTION_ACTIVE`
  - Emit `rest.ended` and `execution.started`
  - Block selected apps (`apps.blocked`)
- `* -> SLEEP_CUTOFF`
  - Emit `sleep.cutoff.reached`
  - Ensure selected apps remain blocked

## API Notes
- Client should call `GET /v1/evening/{id}/snapshot` after each command.
- Server returns:
  - `status`
  - `allowed_actions`
  - `rest` metadata (`ends_at`, `extended_once`)
  - `boundaries` metadata (`sleep_time_local`, `scroll_block_active`)

## Testing Priorities
- Illegal transition rejection (e.g. start rest before plan lock).
- Rest extension policy, including second extension path.
- Sleep cutoff enforcement from every active state.
- Idempotency for repeated client submits.
- Side-effect ordering (block/unblock events around rest transitions).
