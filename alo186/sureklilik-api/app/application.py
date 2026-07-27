from __future__ import annotations

from .invitations import router as invitations_router
from .main import app

if not getattr(app.state, "invitations_router_included", False):
    app.include_router(invitations_router)
    app.state.invitations_router_included = True

app.version = "0.4.0"
app.description = (
    "Otel, site ve işletmeler için e-posta doğrulamalı, MFA destekli, "
    "tenant izolasyonlu ve davet tabanlı ekip onboarding'i sağlayan "
    "elektrik sürekliliği SaaS API temeli."
)
