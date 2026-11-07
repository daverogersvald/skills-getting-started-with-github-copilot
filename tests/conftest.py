"""Shared fixtures for the FastAPI backend tests."""

import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module
from src.app import app


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities database after each test."""
    snapshot = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(snapshot)


@pytest.fixture
def client():
    return TestClient(app)
