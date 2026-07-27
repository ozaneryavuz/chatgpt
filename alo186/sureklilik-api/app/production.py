from __future__ import annotations

import logging

from fastapi import HTTPException
from fastapi.responses import PlainTextResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .config import settings
from .db import database_ready
from .main import app
from .middleware import (
    RateLimitMiddleware,
    RequestBodyLimitMiddleware,
    RequestContextMiddleware,
    metrics,
)


logging.basicConfig(
    level=getattr(logging, settings.log_level, logging.INFO),
    format="%(message)s",
)

app.version = "0.3.0"
app.description = (
    "Otel, site ve işletmeler için tenant izolasyonlu elektrik sürekliliği API'si. "
    "Bu production entrypoint request ID, güvenlik başlıkları, body/rate limit, "
    "readiness ve Prometheus text metrikleri ekler."
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=list(settings.allowed_hosts),
)
app.add_middleware(
    RateLimitMiddleware,
    settings=settings,
)
app.add_middleware(
    RequestBodyLimitMiddleware,
    max_bytes=settings.max_request_body_bytes,
)
app.add_middleware(
    RequestContextMiddleware,
    settings=settings,
)


@app.get("/live", include_in_schema=False)
def liveness() -> dict[str, str]:
    return {"status": "ok", "version": app.version}


@app.get("/ready", include_in_schema=False)
def readiness() -> dict[str, str]:
    if not database_ready():
        raise HTTPException(status_code=503, detail="Veri tabanı hazır değil.")
    return {"status": "ready", "database": "ok", "version": app.version}


@app.get("/metrics", response_class=PlainTextResponse, include_in_schema=False)
def prometheus_metrics() -> PlainTextResponse:
    if not settings.metrics_enabled:
        raise HTTPException(status_code=404, detail="Metrikler kapalı.")
    return PlainTextResponse(metrics.render(), media_type="text/plain; version=0.0.4")
