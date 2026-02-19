"""Shared pytest fixtures for API integration tests."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.domain.store import store
from app.events.writer import writer
from app.jobs.queue import queue
from app.main import app


@pytest.fixture(autouse=True)
def reset_in_memory_state() -> None:
    """Keep tests isolated by resetting in-memory state before each test."""

    store.clear()
    writer.clear()
    queue.clear()


@pytest.fixture()
def client() -> TestClient:
    """HTTP client for exercising FastAPI endpoints."""

    return TestClient(app)
