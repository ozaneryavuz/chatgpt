from __future__ import annotations

"""Compatibility layer for the run135 outage-input hardening step.

The outage-compensation tool has used three equivalent fail-closed spellings
across releases:

1. the original ``invalid`` condition,
2. a positive ``valid`` condition consumed by ``if(!valid)``,
3. the current explicit ``invalidHours`` condition, while retaining a positive
   helper value for UI logic.

This shim recognises only those exact safe forms. It normalises the positive-
only form to the original strict contract and otherwise delegates to the base
injector without weakening the 0..8760 hour bound.
"""

from pathlib import Path

import inject_intent_tools_run135 as _base

_POSITIVE_CONDITION = (
    "const valid=rawHours!==''&&Number.isFinite(hours)&&hours>=0&&hours<=8760;"
)
_NEGATIVE_CONDITION = (
    "const invalid=rawHours===''||!Number.isFinite(hours)||hours<0||hours>8760;"
)
_CURRENT_NEGATIVE_CONDITION = (
    "const invalidHours=rawHours===''||!Number.isFinite(hours)||hours<0||hours>8760;"
)
_POSITIVE_USE = "if(!valid){"
_NEGATIVE_USE = "if(invalid){"
_CURRENT_NEGATIVE_USE = "if(invalidHours){"
_ORIGINAL_HARDEN = _base.harden_outage_input


def _has_exact_negative_gate(text: str) -> bool:
    return _NEGATIVE_CONDITION in text and _NEGATIVE_USE in text


def _has_current_negative_gate(text: str) -> bool:
    return (
        _CURRENT_NEGATIVE_CONDITION in text
        and _CURRENT_NEGATIVE_USE in text
    )


def harden_outage_input(site: Path) -> bool:
    """Accept only known fail-closed validation forms, then delegate strictly."""
    path = site / _base.ROUTES[0].strip("/") / "index.html"
    if not path.is_file():
        raise FileNotFoundError(f"Kesinti tazminatı aracı bulunamadı: {path}")

    text = path.read_text(encoding="utf-8", errors="strict")
    changed = False

    if _POSITIVE_CONDITION in text:
        if _has_current_negative_gate(text) or _has_exact_negative_gate(text):
            # The active fail-closed branch is already explicit. The retained
            # positive helper is harmless and may be used by UI/accessibility
            # logic, so preserve the source exactly.
            pass
        elif _POSITIVE_USE in text:
            text = text.replace(_POSITIVE_CONDITION, _NEGATIVE_CONDITION, 1)
            text = text.replace(_POSITIVE_USE, _NEGATIVE_USE, 1)
            path.write_text(text, encoding="utf-8")
            changed = True
        else:
            raise RuntimeError(
                "Kesinti süresi pozitif doğrulaması bulundu ancak güvenli kullanım kalıbı tanınmadı"
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
