from __future__ import annotations

from .sentry_integration import initialize_sentry

initialize_sentry()

from .invitations import router as invitations_router  # noqa: E402
from .knowledge_graph import router as knowledge_graph_router  # noqa: E402
from .main import app  # noqa: E402

if not getattr(app.state, "invitations_router_included", False):
    app.include_router(invitations_router)
    app.state.invitations_router_included = True

if not getattr(app.state, "knowledge_graph_router_included", False):
    app.include_router(knowledge_graph_router)
    app.state.knowledge_graph_router_included = True

app.version = "0.5.0"
app.description = (
    "Otel, site ve işletmeler için e-posta doğrulamalı, MFA destekli, "
    "tenant izolasyonlu, davet tabanlı ekip onboarding'i ve provenance-aware "
    "Elektrik Knowledge Graph API'si sağlayan süreklilik SaaS temeli."
)
