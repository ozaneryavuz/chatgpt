from __future__ import annotations

import base64
import hashlib
import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise RuntimeError(f"{name} tam sayı olmalıdır.") from exc


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError as exc:
        raise RuntimeError(f"{name} ondalık sayı olmalıdır.") from exc


def _csv(name: str, default: str = "") -> tuple[str, ...]:
    return tuple(item.strip() for item in os.getenv(name, default).split(",") if item.strip())


def _secret(name: str, default: str | None = None) -> str | None:
    direct = os.getenv(name)
    file_name = os.getenv(f"{name}_FILE")
    if direct and file_name:
        raise RuntimeError(f"{name} ve {name}_FILE aynı anda tanımlanamaz.")
    if file_name:
        path = Path(file_name)
        try:
            return path.read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise RuntimeError(f"{name}_FILE okunamadı: {path}") from exc
    return direct if direct is not None else default


def _derived_fernet_key(secret: str) -> str:
    return base64.urlsafe_b64encode(hashlib.sha256(secret.encode("utf-8")).digest()).decode("ascii")


def normalize_database_url(value: str) -> str:
    """Render/Heroku-style PostgreSQL URLs use the default driver name.

    The project intentionally installs psycopg3, so production URLs are normalized
    to SQLAlchemy's explicit ``postgresql+psycopg`` dialect. SQLite and already
    explicit SQLAlchemy URLs are returned unchanged.
    """

    if value.startswith("postgres://"):
        return "postgresql+psycopg://" + value[len("postgres://") :]
    if value.startswith("postgresql://"):
        return "postgresql+psycopg://" + value[len("postgresql://") :]
    return value


@dataclass(frozen=True)
class Settings:
    environment: str
    database_url: str
    token_secret: str
    data_encryption_key: str
    token_ttl_seconds: int
    email_token_ttl_seconds: int
    password_reset_ttl_seconds: int
    invitation_ttl_seconds: int
    allowed_origins: tuple[str, ...]
    allowed_hosts: tuple[str, ...]
    public_base_url: str
    auto_create_schema: bool
    email_verification_required: bool
    expose_test_tokens: bool
    email_backend: str
    smtp_host: str | None
    smtp_port: int
    smtp_username: str | None
    smtp_password: str | None
    smtp_from_email: str
    smtp_use_tls: bool
    global_rate_limit: int
    auth_rate_limit: int
    rate_limit_window_seconds: int
    max_request_bytes: int
    trust_proxy_headers: bool
    account_lock_threshold: int
    account_lock_seconds: int
    deletion_grace_days: int
    audit_retention_days: int
    outbox_retention_days: int
    metrics_token: str | None
    sentry_dsn: str | None
    sentry_traces_sample_rate: float
    release: str | None

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


def load_settings() -> Settings:
    environment = os.getenv("ALO186_ENV", "development").strip().lower()
    token_secret = _secret(
        "ALO186_TOKEN_SECRET",
        "development-only-secret-change-before-production",
    ) or ""
    explicit_encryption_key = _secret("ALO186_DATA_ENCRYPTION_KEY")
    data_encryption_key = explicit_encryption_key or _derived_fernet_key(token_secret)

    settings = Settings(
        environment=environment,
        database_url=normalize_database_url(
            _secret("ALO186_DATABASE_URL", "sqlite:///./alo186_continuity.db") or ""
        ),
        token_secret=token_secret,
        data_encryption_key=data_encryption_key,
        token_ttl_seconds=_env_int("ALO186_TOKEN_TTL_SECONDS", 28_800),
        email_token_ttl_seconds=_env_int("ALO186_EMAIL_TOKEN_TTL_SECONDS", 86_400),
        password_reset_ttl_seconds=_env_int("ALO186_PASSWORD_RESET_TTL_SECONDS", 3_600),
        invitation_ttl_seconds=_env_int("ALO186_INVITATION_TTL_SECONDS", 604_800),
        allowed_origins=_csv("ALO186_ALLOWED_ORIGINS", "http://localhost:8000"),
        allowed_hosts=_csv("ALO186_ALLOWED_HOSTS", "localhost,127.0.0.1,testserver"),
        public_base_url=os.getenv("ALO186_PUBLIC_BASE_URL", "http://localhost:8000").rstrip("/"),
        auto_create_schema=_env_bool("ALO186_AUTO_CREATE_SCHEMA", environment != "production"),
        email_verification_required=_env_bool(
            "ALO186_EMAIL_VERIFICATION_REQUIRED",
            environment == "production",
        ),
        expose_test_tokens=_env_bool("ALO186_EXPOSE_TEST_TOKENS", environment == "test"),
        email_backend=os.getenv("ALO186_EMAIL_BACKEND", "console").strip().lower(),
        smtp_host=os.getenv("ALO186_SMTP_HOST") or None,
        smtp_port=_env_int("ALO186_SMTP_PORT", 587),
        smtp_username=os.getenv("ALO186_SMTP_USERNAME") or None,
        smtp_password=_secret("ALO186_SMTP_PASSWORD"),
        smtp_from_email=os.getenv("ALO186_SMTP_FROM_EMAIL", "noreply@alo186.com"),
        smtp_use_tls=_env_bool("ALO186_SMTP_USE_TLS", True),
        global_rate_limit=_env_int("ALO186_GLOBAL_RATE_LIMIT", 240),
        auth_rate_limit=_env_int("ALO186_AUTH_RATE_LIMIT", 10),
        rate_limit_window_seconds=_env_int("ALO186_RATE_LIMIT_WINDOW_SECONDS", 900),
        max_request_bytes=_env_int("ALO186_MAX_REQUEST_BYTES", 1_048_576),
        trust_proxy_headers=_env_bool("ALO186_TRUST_PROXY_HEADERS", False),
        account_lock_threshold=_env_int("ALO186_ACCOUNT_LOCK_THRESHOLD", 5),
        account_lock_seconds=_env_int("ALO186_ACCOUNT_LOCK_SECONDS", 900),
        deletion_grace_days=_env_int("ALO186_DELETION_GRACE_DAYS", 30),
        audit_retention_days=_env_int("ALO186_AUDIT_RETENTION_DAYS", 730),
        outbox_retention_days=_env_int("ALO186_OUTBOX_RETENTION_DAYS", 30),
        metrics_token=_secret("ALO186_METRICS_TOKEN"),
        sentry_dsn=_secret("ALO186_SENTRY_DSN"),
        sentry_traces_sample_rate=_env_float("ALO186_SENTRY_TRACES_SAMPLE_RATE", 0.0),
        release=os.getenv("ALO186_RELEASE") or None,
    )
    validate_settings(settings, explicit_encryption_key=explicit_encryption_key)
    return settings


def validate_settings(value: Settings, *, explicit_encryption_key: str | None) -> None:
    if value.environment not in {"development", "test", "staging", "production"}:
        raise RuntimeError("ALO186_ENV development, test, staging veya production olmalıdır.")
    if len(value.token_secret) < 32:
        raise RuntimeError("ALO186_TOKEN_SECRET en az 32 karakter olmalıdır.")
    try:
        raw_key = base64.urlsafe_b64decode(value.data_encryption_key.encode("ascii"))
    except Exception as exc:  # pragma: no cover - savunmacı doğrulama
        raise RuntimeError("ALO186_DATA_ENCRYPTION_KEY geçerli urlsafe base64 olmalıdır.") from exc
    if len(raw_key) != 32:
        raise RuntimeError("ALO186_DATA_ENCRYPTION_KEY çözülünce 32 byte olmalıdır.")
    if (
        value.token_ttl_seconds <= 0
        or value.email_token_ttl_seconds <= 0
        or value.password_reset_ttl_seconds <= 0
        or value.invitation_ttl_seconds <= 0
    ):
        raise RuntimeError("Token süreleri sıfırdan büyük olmalıdır.")
    if value.global_rate_limit <= 0 or value.auth_rate_limit <= 0:
        raise RuntimeError("Rate limit değerleri sıfırdan büyük olmalıdır.")
    if value.max_request_bytes < 16_384:
        raise RuntimeError("ALO186_MAX_REQUEST_BYTES en az 16384 olmalıdır.")
    if not 0.0 <= value.sentry_traces_sample_rate <= 1.0:
        raise RuntimeError("ALO186_SENTRY_TRACES_SAMPLE_RATE 0 ile 1 arasında olmalıdır.")

    if value.is_production:
        if value.database_url.startswith("sqlite"):
            raise RuntimeError("Production ortamında SQLite kullanılamaz.")
        if value.token_secret == "development-only-secret-change-before-production":
            raise RuntimeError("Production ortamında varsayılan token secret kullanılamaz.")
        if explicit_encryption_key is None:
            raise RuntimeError("Production ortamında ALO186_DATA_ENCRYPTION_KEY veya _FILE zorunludur.")
        if value.auto_create_schema:
            raise RuntimeError("Production ortamında create_all kapalı olmalı; Alembic kullanılmalıdır.")
        if not value.allowed_origins or "*" in value.allowed_origins:
            raise RuntimeError("Production CORS origin listesi açıkça tanımlanmalıdır.")
        if not value.allowed_hosts or "*" in value.allowed_hosts:
            raise RuntimeError("Production allowed host listesi açıkça tanımlanmalıdır.")
        parsed = urlparse(value.public_base_url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise RuntimeError("Production public base URL HTTPS olmalıdır.")
        if value.email_backend != "smtp":
            raise RuntimeError("Production ortamında ALO186_EMAIL_BACKEND=smtp zorunludur.")
        if not value.smtp_host or not value.smtp_from_email:
            raise RuntimeError("Production SMTP host ve from e-postası zorunludur.")


settings = load_settings()
