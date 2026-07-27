from __future__ import annotations

import os
from pathlib import Path

TEST_DB = Path(__file__).with_name("test_continuity.db")
if TEST_DB.exists():
    TEST_DB.unlink()

os.environ["ALO186_ENV"] = "test"
os.environ["ALO186_DATABASE_URL"] = f"sqlite:///{TEST_DB}"
os.environ["ALO186_TOKEN_SECRET"] = "test-secret-at-least-32-characters-long"
os.environ["ALO186_DATA_ENCRYPTION_KEY"] = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
os.environ["ALO186_ALLOWED_ORIGINS"] = "http://testserver"
os.environ["ALO186_ALLOWED_HOSTS"] = "testserver,localhost,127.0.0.1"
os.environ["ALO186_PUBLIC_BASE_URL"] = "http://testserver"
os.environ["ALO186_AUTO_CREATE_SCHEMA"] = "true"
os.environ["ALO186_EMAIL_VERIFICATION_REQUIRED"] = "false"
os.environ["ALO186_EXPOSE_TEST_TOKENS"] = "true"
os.environ["ALO186_EMAIL_BACKEND"] = "console"
os.environ["ALO186_GLOBAL_RATE_LIMIT"] = "10000"
os.environ["ALO186_AUTH_RATE_LIMIT"] = "1000"
os.environ["ALO186_RATE_LIMIT_WINDOW_SECONDS"] = "60"
os.environ["ALO186_METRICS_TOKEN"] = "test-metrics-token"

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.rate_limit import auth_limiter, global_limiter


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def reset_in_memory_limiters():
    global_limiter.clear()
    auth_limiter.clear()
    yield
    global_limiter.clear()
    auth_limiter.clear()


@pytest.fixture(scope="session", autouse=True)
def cleanup():
    yield
    if TEST_DB.exists():
        TEST_DB.unlink()
