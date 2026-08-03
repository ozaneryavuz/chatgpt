from __future__ import annotations

"""Compatibility layer for run135 plus the final AI-commerce AEO stage.

The outage-compensation tool already uses a fail-closed positive validation
expression. The original injector only recognised an older negative spelling.
This shim normalises that equivalent expression, delegates to the strict base
injector, then applies the v250 AI-commerce layer after the private search index
and final route discovery exist.

The final Pages smoke test intentionally rejects root-relative values found in
inline executable/style content. The v250 SSR choices do not require bespoke
CSS to remain visible or crawlable, so this compatibility layer emits the
semantic server-rendered HTML without adding an inline style block. Existing
site CSS and native block layout provide the presentation while preserving the
stricter project-path guard.
"""

from pathlib import Path

import inject_ai_commerce_aeo_v250 as _ai_commerce
import inject_intent_tools_run135 as _base

_POSITIVE_CONDITION = (
    "const valid=rawHours!==''&&Number.isFinite(hours)&&hours>=0&&hours<=8760;"
)
_NEGATIVE_CONDITION = (
    "const invalid=rawHours===''||!Number.isFinite(hours)||hours<0||hours>8760;"
)
_ORIGINAL_HARDEN = _base.harden_outage_input
_ORIGINAL_INJECT = _base.inject


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


def inject_ssr_baseline_without_inline_css(html: str, base_path: str) -> tuple[str, bool]:
    """Emit crawlable SSR choice cards without an inline CSS false positive."""
    if 'data-alo186-ssr-products-v250="true"' in html:
        return html, False
    if "</main>" not in html:
        raise RuntimeError("SSR baseline için </main> yok")
    return html.replace(
        "</main>",
        _ai_commerce.ssr_baseline(base_path) + "</main>",
        1,
    ), True


def inject(site: Path, base_path: str) -> dict:
    """Run route/search discovery first, then attach the AI commerce semantics."""
    run135_result = _ORIGINAL_INJECT(site, base_path)
    ai_result = _ai_commerce.run(site, base_path)
    return {
        **run135_result,
        "aiCommerceAeoV250": ai_result,
    }


def validate(site: Path, base_path: str) -> dict:
    run135_result = _base.validate(site, base_path)
    ai_result = _ai_commerce.validate(site, base_path)
    return {
        **run135_result,
        "aiCommerceAeoV250": ai_result,
    }


_base.harden_outage_input = harden_outage_input
_ai_commerce.inject_ssr_baseline = inject_ssr_baseline_without_inline_css

VERSION = max(_base.VERSION, _ai_commerce.VERSION)
ROUTES = _base.ROUTES
main = _base.main
