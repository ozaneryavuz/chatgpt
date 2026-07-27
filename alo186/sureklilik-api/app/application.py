from __future__ import annotations

import hmac

from fastapi import HTTPException, Request
from fastapi.responses import PlainTextResponse

from .config import settings
from .sentry_integration import initialize_sentry

initialize_sentry()

from .invitations import router as invitations_router  # noqa: E402
from .main import app  # noqa: E402
from .observability import metrics  # noqa: E402

if not getattr(app.state, "invitations_router_included", False):
    app.include_router(invitations_router)
    app.state.invitations_router_included = True

# Prometheus istemcileri standart Authorization: Bearer kullanabilir. Eski
# X-Metrics-Token desteği geriye uyumluluk için korunur.
if not getattr(app.state, "portable_metrics_route_included", False):
    app.router.routes = [
        route for route in app.router.routes if getattr(route, "path", None) != "/metrics"
    ]

    @app.get("/metrics", response_class=PlainTextResponse, include_in_schema=False)
    def production_metrics(request: Request) -> str:
        if settings.metrics_token:
            supplied = request.headers.get("x-metrics-token", "")
            authorization = request.headers.get("authorization", "")
            bearer = authorization[7:].strip() if authorization.lower().startswith("bearer ") else ""
            if not (
                hmac.compare_digest(supplied, settings.metrics_token)
                or hmac.compare_digest(bearer, settings.metrics_token)
            ):
                raise HTTPException(status_code=403, detail="Metrics erişimi reddedildi.")
        return metrics.render_prometheus()

    app.state.portable_metrics_route_included = True

app.version = "0.4.2"
app.description = (
    "Otel, site ve işletmeler için e-posta doğrulamalı, MFA destekli, "
    "tenant izolasyonlu, davet tabanlı ekip onboarding'i ve üretim "
    "gözlemlenebilirliği sağlayan elektrik sürekliliği SaaS API temeli."
)
