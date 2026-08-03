from __future__ import annotations

"""Compatibility layer for the run135 outage-input hardening step.

The current outage-compensation tool already uses a fail-closed positive
validation expression. The original injector only recognised its older
negative-expression spelling and stopped otherwise-safe release artifacts.
This shim normalises the equivalent expression before delegating to the
existing, strict injector. It does not weaken any bound or commercial guard.
"""

from pathlib import Path

import inject_intent_tools_run135 as _base

_POSITIVE_CONDITION = (
    "const valid=rawHours!==''&&Number.isFinite(hours)&&hours>=0&&hours<=8760;"
)
_NEGATIVE_CONDITION = (
    "const invalid=rawHours===''||!Number.isFinite(hours)||hours<0||hours>8760;"
)
_ORIGINAL_HARDEN = _base.harden_outage_input


def harden_outage_input(site: Path) -> bool:
    """Accept and normalise the already-safe positive validation spelling."""
    path = site / _base.ROUTES[0].strip("/") / "index.html"
    if not path.is_file():
        raise FileNotFoundError(f"Kesinti tazminatı aracı bulunamadı: {path}")

    text = path.read_text(encoding="utf-8", errors="strict")
    changed = False
    if _POSITIVE_CONDITION in text:
        if "if(!valid){" not in text:
            raise RuntimeError(
                "Kesinti süresi pozitif doğrulaması bulundu ancak kullanım kalıbı tanınmadı"
            )
        text = text.replace(_POSITIVE_CONDITION, _NEGATIVE_CONDITION, 1)
        text = text.replace("if(!valid){", "if(invalid){", 1)
        path.write_text(text, encoding="utf-8")
        changed = True

    return _ORIGINAL_HARDEN(site) or changed


# The imported inject() function resolves harden_outage_input from the base
# module globals at runtime. Patch that single symbol, then expose the strict
# base API unchanged.
_base.harden_outage_input = harden_outage_input

VERSION = _base.VERSION
ROUTES = _base.ROUTES
inject = _base.inject
validate = _base.validate
main = _base.main
