from __future__ import annotations

"""Compatibility layer for the run135 outage-input hardening step.

The current outage-compensation tool already uses a fail-closed positive
validation expression. The original injector only recognised its older
negative-expression spelling and stopped otherwise-safe release artifacts.
This shim normalises the equivalent expression only when the positive flag is
actually consumed. If the page already contains a separate fail-closed
``invalidHours`` condition, the strict base validator can accept it directly.
No input bound or commercial guard is weakened.
"""

from pathlib import Path

import inject_intent_tools_run135 as _base

_POSITIVE_CONDITION = (
    "const valid=rawHours!==''&&Number.isFinite(hours)&&hours>=0&&hours<=8760;"
)
_NEGATIVE_CONDITION = (
    "const invalid=rawHours===''||!Number.isFinite(hours)||hours<0||hours>8760;"
)
_SECURE_EXPRESSION = "rawHours===''||!Number.isFinite(hours)||hours<0||hours>8760"
_ORIGINAL_HARDEN = _base.harden_outage_input


def harden_outage_input(site: Path) -> bool:
    """Accept either safe validation spelling and preserve fail-closed bounds."""
    path = site / _base.ROUTES[0].strip("/") / "index.html"
    if not path.is_file():
        raise FileNotFoundError(f"Kesinti tazminatı aracı bulunamadı: {path}")

    text = path.read_text(encoding="utf-8", errors="strict")
    changed = False
    if _POSITIVE_CONDITION in text:
        if "if(!valid){" in text:
            text = text.replace(_POSITIVE_CONDITION, _NEGATIVE_CONDITION, 1)
            text = text.replace("if(!valid){", "if(invalid){", 1)
            path.write_text(text, encoding="utf-8")
            changed = True
        elif _SECURE_EXPRESSION not in text:
            raise RuntimeError(
                "Kesinti süresi pozitif doğrulaması bulundu ancak fail-closed kullanım kalıbı tanınmadı"
            )

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
