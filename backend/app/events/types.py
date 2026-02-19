from __future__ import annotations

from enum import Enum


class EventType(str, Enum):
    MOOD_RECORDED = "mood.recorded"
    REST_RECOMMENDED = "rest.recommended"
    REST_SELECTED = "rest.selected"
    PLAN_LOCKED = "plan.locked"
    REST_STARTED = "rest.started"
    REST_EXTENDED = "rest.extended"
    REST_EXTENSION_REQUESTED_WITH_REASON = "rest.extension_requested_with_reason"
    REST_ENDED = "rest.ended"
    EXECUTION_STARTED = "execution.started"
    EVENING_COMPLETED = "evening.completed"
    SLEEP_CUTOFF_REACHED = "sleep.cutoff.reached"
    APPS_UNBLOCKED = "apps.unblocked"
    APPS_BLOCKED = "apps.blocked"
