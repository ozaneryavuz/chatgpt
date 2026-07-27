from __future__ import annotations

import hmac

from fastapi import HTTPException, Request
from fastapi.responses import PlainTextResponse

from .config import settings
from .invitations import router as invitations_router
from .main import app
from .observability import configure_sentry, metrics

configure_sentry()

if not getattr(app.state, "invitations_router_included", False):
    app.include_router(invitations_router)
    app.state.invitations_router_included = True

# Grafana Alloy ve diğer Prometheus istemcileri Authorization: Bearer kullanabildiği
# için eski X-Metrics-Token davranışını koruyarak iki yöntemi de kabul ederiz.
if not getattr(app.state, "portable_metrics_route_included", False):
    app.router.routes = [
        route for route in app.router.routes if getattr(route, "path", None) != "/metrics"
    ]

    @app.get("/metrics", response_class=PlainTextResponse, include_in_schema=False)
    def production_metrics(request: Request) -> str:
        if settings.metrics_token:
            supplied = request.headers.get("x-metrics-token")
            authorization = request.headers.get("authorization", "")
            bearer = authorization[7:].strip() if authorization.lower().startswith("bearer ") else ""
            if not (
                hmac.compare_digest(supplied or "", settings.metrics_token)
                or hmac.compare_digest(bearer, settings.metrics_token)
            ):
                raise HTTPException(status_code=403, detail="Metrics erişimi reddedildi.")
        return metrics.render_prometheus()

    app.state.portable_metrics_route_included = True

app.version = "0.4.1"
app.description = (
    "Otel, site ve işletmeler için e-posta doğrulamalı, MFA destekli, "
    "tenant izolasyonlu, davet tabanlı ekip onboarding'i ve üretim "
    "gözlemlenebilirliği sağlayan elektrik sürekliliği SaaS API temeli."
)
