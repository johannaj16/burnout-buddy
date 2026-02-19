"""API integration tests for evening command flow and side effects."""

from __future__ import annotations


def test_full_evening_flow_emits_rest_side_effects(client) -> None:
    """Verify happy-path transitions and rest/execution side effects over HTTP."""

    evening_id = "eve-1"
    user_id = "user-1"

    commands = [
        "record_mood",
        "recommend_rest",
        "select_rest_duration",
        "lock_plan",
        "start_rest",
    ]

    last_body = None
    for cmd in commands:
        response = client.post(
            f"/v1/evening/{evening_id}/commands",
            json={"user_id": user_id, "command": cmd},
        )
        assert response.status_code == 200
        last_body = response.json()
        assert last_body["accepted"] is True

    assert last_body is not None
    assert last_body["snapshot"]["status"] == "REST_ACTIVE"
    assert last_body["snapshot"]["scroll_block_active"] is False

    emitted_event_types = [event["type"] for event in last_body["emitted_events"]]
    assert "rest.started" in emitted_event_types
    assert "apps.unblocked" in emitted_event_types

    queued_job_types = [job["type"] for job in last_body["queued_jobs"]]
    assert "end_rest_window" in queued_job_types



def test_rest_to_execution_blocks_apps(client) -> None:
    """Ensure ending rest moves to execution mode and re-enables app blocking."""

    evening_id = "eve-2"
    user_id = "user-2"

    setup_commands = [
        "record_mood",
        "recommend_rest",
        "lock_plan",
        "start_rest",
    ]

    for cmd in setup_commands:
        response = client.post(
            f"/v1/evening/{evening_id}/commands",
            json={"user_id": user_id, "command": cmd},
        )
        assert response.status_code == 200
        assert response.json()["accepted"] is True

    response = client.post(
        f"/v1/evening/{evening_id}/commands",
        json={"user_id": user_id, "command": "end_rest"},
    )
    assert response.status_code == 200

    body = response.json()
    assert body["accepted"] is True
    assert body["snapshot"]["status"] == "EXECUTION_ACTIVE"
    assert body["snapshot"]["scroll_block_active"] is True

    emitted_event_types = [event["type"] for event in body["emitted_events"]]
    assert "rest.ended" in emitted_event_types
    assert "execution.started" in emitted_event_types
    assert "apps.blocked" in emitted_event_types



def test_sleep_cutoff_from_active_state_enqueues_enforcer_job(client) -> None:
    """Sleep cutoff should preempt active flow and queue enforcement work."""

    evening_id = "eve-3"
    user_id = "user-3"

    for cmd in ["record_mood", "recommend_rest"]:
        response = client.post(
            f"/v1/evening/{evening_id}/commands",
            json={"user_id": user_id, "command": cmd},
        )
        assert response.status_code == 200

    response = client.post(
        f"/v1/evening/{evening_id}/commands",
        json={"user_id": user_id, "command": "apply_sleep_cutoff"},
    )
    assert response.status_code == 200

    body = response.json()
    assert body["accepted"] is True
    assert body["snapshot"]["status"] == "SLEEP_CUTOFF"
    assert body["snapshot"]["scroll_block_active"] is True

    emitted_event_types = [event["type"] for event in body["emitted_events"]]
    assert "sleep.cutoff.reached" in emitted_event_types
    assert "apps.blocked" in emitted_event_types

    queued_job_types = [job["type"] for job in body["queued_jobs"]]
    assert "sleep_cutoff_enforcer" in queued_job_types
