from __future__ import annotations

from .sentry_integration import initialize_sentry

initialize_sentry()

from .invitations import router as invitations_router  # noqa: E402
from .main import app  # noqa: E402

if not getattr(app.state, "invitations_router_included", False):
    app.include_router(invitations_router)
    app.state.invitations_router_included = True

app.version = "0.4.1"
app.description = (
    "Otel, site ve işletmeler için e-posta doğrulamalı, MFA destekli, "
    "tenant izolasyonlu ve davet tabanlı ekip onboarding'i sağlayan "
    "elektrik sürekliliği SaaS API temeli."
)
