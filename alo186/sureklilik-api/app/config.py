from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


_DEVELOPMENT_SECRET = "development-only-secret-change-before-production"


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _as_int(value: str | None, default: int, *, minimum: int = 1) -> int:
    if value is None or not value.strip():
        return default
    parsed = int(value)
    if parsed < minimum:
        raise RuntimeError(f"Yapılandırma değeri en az {minimum} olmalıdır.")
    return parsed


def _csv(value: str | None, default: str) -> tuple[str, ...]:
    source = value if value is not None else default
    return tuple(item.strip() for item in source.split(",") if item.strip())


def _read_value(env: Mapping[str, str], name: str, default: str | None = None) -> str:
    file_name = env.get(f"{name}_FILE", "").strip()
    if file_name:
        try:
            value = Path(file_name).read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise RuntimeError(f"{name}_FILE okunamadı: {file_name}") from exc
        if not value:
            raise RuntimeError(f"{name}_FILE boş olamaz: {file_name}")
        return value
    value = env.get(name, default)
    if value is None:
        raise RuntimeError(f"Zorunlu yapılandırma eksik: {name}")
    return value


@dataclass(frozen=True)
class Settings:
    environment: str
    database_url: str
    token_secret: str
    token_ttl_seconds: int
    allowed_origins: tuple[str, ...]
    allowed_hosts: tuple[str, ...]
    max_request_body_bytes: int
    api_rate_limit_per_minute: int
    auth_rate_limit_per_minute: int
    metrics_enabled: bool
    trust_proxy_headers: bool
    auto_create_schema: bool
    log_level: str
    require_email_verification: bool
    email_verification_ttl_seconds: int
    password_reset_ttl_seconds: int
    login_max_failures: int
    login_lock_seconds: int
    public_app_url: str
    email_backend: str
    email_from: str
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    smtp_use_tls: bool

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


def validate_settings(value: Settings) -> Settings:
    if value.environment not in {"development", "test", "staging", "production"}:
        raise RuntimeError("ALO186_ENV development, test, staging veya production olmalıdır.")
    if value.email_backend not in {"console", "smtp"}:
        raise RuntimeError("ALO186_EMAIL_BACKEND console veya smtp olmalıdır.")
    if value.is_production:
        if value.token_secret == _DEVELOPMENT_SECRET or len(value.token_secret) < 32:
            raise RuntimeError(
                "Production ortamında en az 32 karakterlik benzersiz ALO186_TOKEN_SECRET zorunludur."
            )
        if value.database_url.startswith("sqlite"):
            raise RuntimeError("Production ortamında SQLite kullanılamaz; PostgreSQL yapılandırın.")
        if not value.allowed_hosts or "*" in value.allowed_hosts:
            raise RuntimeError("Production ortamında açık bir ALO186_ALLOWED_HOSTS listesi zorunludur.")
        if "*" in value.allowed_origins:
            raise RuntimeError("Production ortamında wildcard CORS origin kullanılamaz.")
        if value.auto_create_schema:
            raise RuntimeError(
                "Production ortamında ALO186_AUTO_CREATE_SCHEMA kapalı olmalı; migration uygulanmalıdır."
            )
        if value.require_email_verification and value.email_backend != "smtp":
            raise RuntimeError(
                "Production e-posta doğrulaması için ALO186_EMAIL_BACKEND=smtp zorunludur."
            )
        if value.email_backend == "smtp" and (not value.smtp_host or not value.email_from):
            raise RuntimeError("SMTP backend için ALO186_SMTP_HOST ve ALO186_EMAIL_FROM zorunludur.")
    return value


def load_settings(environ: Mapping[str, str] | None = None) -> Settings:
    env = environ or os.environ
    environment = env.get("ALO186_ENV", "development").strip().lower()
    production_hosts = "api.alo186.com,www.alo186.com" if environment == "production" else "localhost,127.0.0.1,testserver"
    value = Settings(
        environment=environment,
        database_url=_read_value(env, "ALO186_DATABASE_URL", "sqlite:///./alo186_continuity.db"),
        token_secret=_read_value(env, "ALO186_TOKEN_SECRET", _DEVELOPMENT_SECRET),
        token_ttl_seconds=_as_int(env.get("ALO186_TOKEN_TTL_SECONDS"), 28_800),
        allowed_origins=_csv(env.get("ALO186_ALLOWED_ORIGINS"), "http://localhost:8000"),
        allowed_hosts=_csv(env.get("ALO186_ALLOWED_HOSTS"), production_hosts),
        max_request_body_bytes=_as_int(env.get("ALO186_MAX_REQUEST_BODY_BYTES"), 1_048_576),
        api_rate_limit_per_minute=_as_int(env.get("ALO186_API_RATE_LIMIT_PER_MINUTE"), 120),
        auth_rate_limit_per_minute=_as_int(env.get("ALO186_AUTH_RATE_LIMIT_PER_MINUTE"), 12),
        metrics_enabled=_as_bool(env.get("ALO186_METRICS_ENABLED"), True),
        trust_proxy_headers=_as_bool(env.get("ALO186_TRUST_PROXY_HEADERS"), False),
        auto_create_schema=_as_bool(
            env.get("ALO186_AUTO_CREATE_SCHEMA"),
            default=environment != "production",
        ),
        log_level=env.get("ALO186_LOG_LEVEL", "INFO").strip().upper(),
        require_email_verification=_as_bool(
            env.get("ALO186_REQUIRE_EMAIL_VERIFICATION"),
            default=environment == "production",
        ),
        email_verification_ttl_seconds=_as_int(
            env.get("ALO186_EMAIL_VERIFICATION_TTL_SECONDS"), 86_400
        ),
        password_reset_ttl_seconds=_as_int(
            env.get("ALO186_PASSWORD_RESET_TTL_SECONDS"), 3_600
        ),
        login_max_failures=_as_int(env.get("ALO186_LOGIN_MAX_FAILURES"), 5),
        login_lock_seconds=_as_int(env.get("ALO186_LOGIN_LOCK_SECONDS"), 900),
        public_app_url=env.get("ALO186_PUBLIC_APP_URL", "https://www.alo186.com").rstrip("/"),
        email_backend=env.get("ALO186_EMAIL_BACKEND", "console").strip().lower(),
        email_from=env.get("ALO186_EMAIL_FROM", "ALO186 <noreply@alo186.com>").strip(),
        smtp_host=env.get("ALO186_SMTP_HOST", "").strip(),
        smtp_port=_as_int(env.get("ALO186_SMTP_PORT"), 587),
        smtp_username=env.get("ALO186_SMTP_USERNAME", "").strip(),
        smtp_password=_read_value(env, "ALO186_SMTP_PASSWORD", ""),
        smtp_use_tls=_as_bool(env.get("ALO186_SMTP_USE_TLS"), True),
    )
    return validate_settings(value)


settings = load_settings()
