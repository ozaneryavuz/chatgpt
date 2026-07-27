from __future__ import annotations

import os


def initialize_sentry() -> bool:
    dsn = os.getenv("ALO186_SENTRY_DSN", "").strip()
    if not dsn:
        return False

    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

    environment = os.getenv("ALO186_ENV", "development").strip().lower()
    traces_sample_rate = max(
        0.0,
        min(1.0, float(os.getenv("ALO186_SENTRY_TRACES_SAMPLE_RATE", "0.05"))),
    )
    profiles_sample_rate = max(
        0.0,
        min(1.0, float(os.getenv("ALO186_SENTRY_PROFILES_SAMPLE_RATE", "0.0"))),
    )
    release = os.getenv("RENDER_GIT_COMMIT") or os.getenv("ALO186_RELEASE") or None

    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        release=release,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
            LoggingIntegration(level=None, event_level="ERROR"),
        ],
        traces_sample_rate=traces_sample_rate,
        profiles_sample_rate=profiles_sample_rate,
        send_default_pii=False,
        max_request_body_size="small",
        attach_stacktrace=True,
        enable_tracing=traces_sample_rate > 0,
    )
    return True
