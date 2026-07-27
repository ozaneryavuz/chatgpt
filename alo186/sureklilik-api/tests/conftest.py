from __future__ import annotations

import os
from pathlib import Path

TEST_DB = Path(__file__).with_name("test_continuity.db")
if TEST_DB.exists():
    TEST_DB.unlink()

os.environ["ALO186_DATABASE_URL"] = f"sqlite:///{TEST_DB}"
os.environ["ALO186_TOKEN_SECRET"] = "test-secret-at-least-32-characters-long"
os.environ["ALO186_ALLOWED_ORIGINS"] = "http://testserver"

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session", autouse=True)
def cleanup():
    yield
    if TEST_DB.exists():
        TEST_DB.unlink()
