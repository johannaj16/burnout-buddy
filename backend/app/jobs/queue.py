"""In-memory job queue for MVP side effects.

Real deployments should replace this with Redis/Celery/ARQ-backed jobs.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from app.domain.contracts import JobRecord


class JobType(str, Enum):
    """Background job identifiers triggered by state transitions."""

    END_REST_WINDOW = "end_rest_window"
    SLEEP_CUTOFF_ENFORCER = "sleep_cutoff_enforcer"


class JobQueue:
    """Minimal queue abstraction used by the domain service."""

    def __init__(self) -> None:
        self.jobs: list[JobRecord] = []

    def enqueue(self, job_type: JobType, payload: dict[str, Any] | None = None) -> JobRecord:
        """Append a job and return the stored record."""

        job = JobRecord(type=job_type.value, payload=payload or {})
        self.jobs.append(job)
        return job

    def clear(self) -> None:
        """Test helper to clear queued jobs."""

        self.jobs.clear()


queue = JobQueue()
