from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import load_settings
from app.middleware import SlidingWindowLimiter, route_label
from app.production import app


def test_liveness_readiness_security_headers_and_metrics():
    with TestClient(app) as client:
        response = client.get("/live", headers={"X-Request-ID": "test-request-1234"})
        assert response.status_code == 200
        assert response.headers["x-request-id"] == "test-request-1234"
        assert response.headers["x-content-type-options"] == "nosniff"
        assert response.headers["x-frame-options"] == "DENY"
        assert response.headers["referrer-policy"] == "no-referrer"
        assert "frame-ancestors 'none'" in response.headers["content-security-policy"]

        ready = client.get("/ready")
        assert ready.status_code == 200, ready.text
        assert ready.json()["database"] == "ok"

        metrics = client.get("/metrics")
        assert metrics.status_code == 200
        assert "alo186_http_requests_total" in metrics.text
        assert "alo186_http_request_duration_seconds_sum" in metrics.text


def test_trusted_host_and_request_body_limit():
    with TestClient(app) as client:
        rejected_host = client.get("/live", headers={"host": "evil.example"})
        assert rejected_host.status_code == 400

        oversized = b'{"email":"' + (b"a" * 1_100_000) + b'"}'
        response = client.post(
            "/api/v1/auth/register",
            content=oversized,
            headers={"content-type": "application/json"},
        )
        assert response.status_code == 413
        assert "boyutu" in response.json()["detail"]


def test_sliding_window_rate_limit_is_deterministic():
    limiter = SlidingWindowLimiter()
    allowed, retry_after = limiter.check("auth:198.51.100.10", 2, now=100.0)
    assert allowed is True and retry_after == 0
    allowed, retry_after = limiter.check("auth:198.51.100.10", 2, now=101.0)
    assert allowed is True and retry_after == 0
    allowed, retry_after = limiter.check("auth:198.51.100.10", 2, now=102.0)
    assert allowed is False and retry_after >= 1
    allowed, retry_after = limiter.check("auth:198.51.100.10", 2, now=161.0)
    assert allowed is True and retry_after == 0


def test_route_labels_reduce_uuid_cardinality():
    path = "/api/v1/incidents/123e4567-e89b-12d3-a456-426614174000/close"
    assert route_label(path) == "/api/v1/incidents/:id/close"


def test_secret_file_and_production_validation(tmp_path: Path):
    secret_file = tmp_path / "token_secret"
    secret_file.write_text("x" * 48, encoding="utf-8")
    settings = load_settings(
        {
            "ALO186_ENV": "production",
            "ALO186_DATABASE_URL": "postgresql+psycopg://user:pass@db/alo186",
            "ALO186_TOKEN_SECRET_FILE": str(secret_file),
            "ALO186_ALLOWED_ORIGINS": "https://www.alo186.com",
            "ALO186_ALLOWED_HOSTS": "api.alo186.com",
            "ALO186_AUTO_CREATE_SCHEMA": "false",
        }
    )
    assert settings.token_secret == "x" * 48
    assert settings.is_production is True
    assert settings.auto_create_schema is False

    with pytest.raises(RuntimeError, match="TOKEN_SECRET"):
        load_settings(
            {
                "ALO186_ENV": "production",
                "ALO186_DATABASE_URL": "postgresql+psycopg://user:pass@db/alo186",
                "ALO186_TOKEN_SECRET": "short",
                "ALO186_ALLOWED_ORIGINS": "https://www.alo186.com",
                "ALO186_ALLOWED_HOSTS": "api.alo186.com",
                "ALO186_AUTO_CREATE_SCHEMA": "false",
            }
        )

    with pytest.raises(RuntimeError, match="SQLite"):
        load_settings(
            {
                "ALO186_ENV": "production",
                "ALO186_DATABASE_URL": "sqlite:///production.db",
                "ALO186_TOKEN_SECRET": "y" * 48,
                "ALO186_ALLOWED_ORIGINS": "https://www.alo186.com",
                "ALO186_ALLOWED_HOSTS": "api.alo186.com",
                "ALO186_AUTO_CREATE_SCHEMA": "false",
            }
        )
