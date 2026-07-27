from __future__ import annotations

import base64
from pathlib import Path

import pytest

from app.config import load_settings
from app.rate_limit import SlidingWindowLimiter


def test_sliding_window_limiter_enforces_and_expires():
    limiter = SlidingWindowLimiter()
    first = limiter.check("client", limit=2, window_seconds=10, now=100.0)
    second = limiter.check("client", limit=2, window_seconds=10, now=101.0)
    blocked = limiter.check("client", limit=2, window_seconds=10, now=102.0)
    assert first.allowed and first.remaining == 1
    assert second.allowed and second.remaining == 0
    assert not blocked.allowed and blocked.retry_after >= 1
    released = limiter.check("client", limit=2, window_seconds=10, now=111.1)
    assert released.allowed


def _production_env(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("ALO186_ENV", "production")
    monkeypatch.setenv("ALO186_DATABASE_URL", "postgresql+psycopg://user:pass@db:5432/alo186")
    monkeypatch.setenv("ALO186_TOKEN_SECRET", "production-token-secret-at-least-32-characters")
    monkeypatch.setenv(
        "ALO186_DATA_ENCRYPTION_KEY",
        base64.urlsafe_b64encode(b"1" * 32).decode("ascii"),
    )
    monkeypatch.setenv("ALO186_ALLOWED_ORIGINS", "https://www.alo186.com")
    monkeypatch.setenv("ALO186_ALLOWED_HOSTS", "api.alo186.com")
    monkeypatch.setenv("ALO186_PUBLIC_BASE_URL", "https://www.alo186.com")
    monkeypatch.setenv("ALO186_AUTO_CREATE_SCHEMA", "false")
    monkeypatch.setenv("ALO186_EMAIL_BACKEND", "smtp")
    monkeypatch.setenv("ALO186_SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("ALO186_SMTP_FROM_EMAIL", "noreply@alo186.com")
    monkeypatch.delenv("ALO186_DATABASE_URL_FILE", raising=False)
    monkeypatch.delenv("ALO186_TOKEN_SECRET_FILE", raising=False)
    monkeypatch.delenv("ALO186_DATA_ENCRYPTION_KEY_FILE", raising=False)


def test_valid_production_settings_and_secret_file_support(monkeypatch, tmp_path):
    _production_env(monkeypatch, tmp_path)
    settings = load_settings()
    assert settings.is_production
    assert settings.database_url.startswith("postgresql")
    assert settings.email_backend == "smtp"
    assert settings.auto_create_schema is False

    db_file = tmp_path / "database-url"
    db_file.write_text("postgresql+psycopg://file:secret@db:5432/alo186", encoding="utf-8")
    monkeypatch.delenv("ALO186_DATABASE_URL")
    monkeypatch.setenv("ALO186_DATABASE_URL_FILE", str(db_file))
    settings_from_file = load_settings()
    assert "file:secret" in settings_from_file.database_url


def test_production_rejects_insecure_defaults(monkeypatch, tmp_path):
    _production_env(monkeypatch, tmp_path)
    monkeypatch.setenv("ALO186_DATABASE_URL", "sqlite:///unsafe.db")
    with pytest.raises(RuntimeError, match="SQLite"):
        load_settings()

    _production_env(monkeypatch, tmp_path)
    monkeypatch.setenv("ALO186_ALLOWED_ORIGINS", "*")
    with pytest.raises(RuntimeError, match="CORS"):
        load_settings()

    _production_env(monkeypatch, tmp_path)
    monkeypatch.setenv("ALO186_PUBLIC_BASE_URL", "http://alo186.com")
    with pytest.raises(RuntimeError, match="HTTPS"):
        load_settings()


def test_secret_env_and_file_cannot_be_set_together(monkeypatch, tmp_path):
    secret_file = tmp_path / "token-secret"
    secret_file.write_text("another-production-token-secret-at-least-32", encoding="utf-8")
    monkeypatch.setenv("ALO186_TOKEN_SECRET", "direct-production-token-secret-at-least-32")
    monkeypatch.setenv("ALO186_TOKEN_SECRET_FILE", str(secret_file))
    with pytest.raises(RuntimeError, match="aynı anda"):
        load_settings()
