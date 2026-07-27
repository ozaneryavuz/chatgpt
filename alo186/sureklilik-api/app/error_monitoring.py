from __future__ import annotations

import logging

from .config import settings

logger = logging.getLogger(__name__)


def configure_error_monitoring() -> bool:
    """Configure Sentry only when a DSN is supplied.

    The integration deliberately disables default PII collection. Tenant IDs,
    e-mail addresses and tokens must not be added as tags or breadcrumbs by
    application code.
    """

    if not settings.sentry_dsn:
        return False

    try:
        import sentry_sdk
    except ImportError:  # pragma: no cover - dependency is installed in production image
        logger.warning("sentry_sdk_missing")
        return False

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        release=settings.release,
        send_default_pii=False,
        traces_sample_rate=settings.sentry_traces_sample_rate,
        profiles_sample_rate=0.0,
        enable_tracing=settings.sentry_traces_sample_rate > 0,
        max_breadcrumbs=50,
        request_bodies="never",
    )
    logger.info(
        "sentry_configured",
        extra={
            "environment": settings.environment,
            "traces_sample_rate": settings.sentry_traces_sample_rate,
        },
    )
    return True
