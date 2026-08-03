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

Some legacy product-selector runtimes are bundled into final HTML after
``prepare_github_pages`` has already rewritten structural ``href``/``src``
attributes. For the ``/chatgpt`` artifact, route string literals inside those
inline scripts must receive the same public prefix. This module performs that
narrow final-artifact rewrite only for string literals whose first path segment
exists in the generated site, then recomputes the release checksums. Canonical
URLs and logical data-* route identifiers are not changed.
"""

import json
import re
from pathlib import Path

import inject_ai_commerce_aeo_v250 as _ai_commerce
import inject_intent_tools_run135 as _base

_POSITIVE_CONDITION = (
    "const valid=rawHours!==''&&Number.isFinite(hours)&&hours>=0&&hours<=8760;"
)
_NEGATIVE_CONDITION = (
    "const invalid=rawHours===''||!Number.isFinite(hours)||hours<0||hours>8760;"
)
_ROOT_LITERAL = re.compile(r'(?P<quote>["\'`])/(?!/)(?P<rest>[^"\'`\s<>]*)')
_EXECUTABLE_BLOCKS = (
    re.compile(r'(?P<open><script\b[^>]*>)(?P<body>.*?)(?P<close></script>)', re.I | re.S),
    re.compile(r'(?P<open><style\b[^>]*>)(?P<body>.*?)(?P<close></style>)', re.I | re.S),
)
_ORIGINAL_HARDEN = _base.harden_outage_input
_ORIGINAL_INJECT = _base.inject


def normalize_base_path(value: str) -> str:
    cleaned = (value or "").strip()
    if not cleaned or cleaned == "/":
        return ""
    return "/" + cleaned.strip("/")


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


def _rewrite_executable_body(
    body: str,
    base_path: str,
    known_top_levels: set[str],
) -> tuple[str, int]:
    changes = 0
    base_segment = base_path.strip("/")

    def replace(match: re.Match[str]) -> str:
        nonlocal changes
        quote = match.group("quote")
        rest = match.group("rest")
        first = rest.split("/", 1)[0].split("?", 1)[0].split("#", 1)[0]
        if first == base_segment or rest.startswith(base_segment + "/"):
            return match.group(0)
        if rest != "" and first not in known_top_levels:
            return match.group(0)
        changes += 1
        suffix = "/" + rest if rest else "/"
        return f"{quote}{base_path}{suffix}"

    return _ROOT_LITERAL.sub(replace, body), changes


def rewrite_project_path_executables(site: Path, base_path: str) -> int:
    """Prefix browser route literals in final inline executable content.

    The rewrite runs only for a non-empty project path and only when the first
    path segment physically exists in the final artifact. This keeps regex
    literals, protocol-relative URLs, canonical absolute URLs and logical data
    identifiers untouched while making real navigation strings project-safe.
    """

    base_path = normalize_base_path(base_path)
    if not base_path:
        return 0
    known_top_levels = {path.name for path in site.iterdir()}
    total = 0
    for html_path in sorted(site.rglob("*.html")):
        original = html_path.read_text(encoding="utf-8", errors="strict")
        updated = original
        for pattern in _EXECUTABLE_BLOCKS:
            def block_repl(match: re.Match[str]) -> str:
                nonlocal total
                body, count = _rewrite_executable_body(
                    match.group("body"),
                    base_path,
                    known_top_levels,
                )
                total += count
                return match.group("open") + body + match.group("close")

            updated = pattern.sub(block_repl, updated)
        if updated != original:
            html_path.write_text(updated, encoding="utf-8")
    return total


def unresolved_project_path_executables(site: Path, base_path: str) -> list[str]:
    base_path = normalize_base_path(base_path)
    if not base_path:
        return []
    known_top_levels = {path.name for path in site.iterdir()}
    base_segment = base_path.strip("/")
    failures: list[str] = []
    for html_path in sorted(site.rglob("*.html")):
        text = html_path.read_text(encoding="utf-8", errors="ignore")
        bodies: list[str] = []
        for pattern in _EXECUTABLE_BLOCKS:
            bodies.extend(match.group("body") for match in pattern.finditer(text))
        for match in _ROOT_LITERAL.finditer("\n".join(bodies)):
            rest = match.group("rest")
            first = rest.split("/", 1)[0].split("?", 1)[0].split("#", 1)[0]
            if first == base_segment or rest.startswith(base_segment + "/"):
                continue
            if rest == "" or first in known_top_levels:
                failures.append(
                    f"{html_path.relative_to(site).as_posix()} → /{rest}"
                )
                break
    return failures


def record_project_path_rewrite(site: Path, count: int) -> None:
    report_path = site / _ai_commerce.REPORT_NAME
    if report_path.is_file():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        report["projectPathExecutableRewrites"] = count
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    release_path = site / "pages-release.json"
    if release_path.is_file():
        release = json.loads(release_path.read_text(encoding="utf-8"))
        contract = release.get("aiCommerceAeo")
        if isinstance(contract, dict):
            contract["projectPathExecutableRewrites"] = count
            release_path.write_text(
                json.dumps(release, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )


def inject(site: Path, base_path: str) -> dict:
    """Run route/search discovery first, then attach the AI commerce semantics."""
    resolved = site.resolve()
    run135_result = _ORIGINAL_INJECT(resolved, base_path)
    ai_result = _ai_commerce.run(resolved, base_path)
    rewrite_count = rewrite_project_path_executables(resolved, base_path)
    remaining = unresolved_project_path_executables(resolved, base_path)
    if remaining:
        raise RuntimeError(
            "Project-path executable URL rewrite başarısız:\n" + "\n".join(remaining[:20])
        )
    record_project_path_rewrite(resolved, rewrite_count)
    _ai_commerce.recompute_checksums(resolved)
    ai_result["projectPathExecutableRewrites"] = rewrite_count
    return {
        **run135_result,
        "aiCommerceAeoV250": ai_result,
    }


def validate(site: Path, base_path: str) -> dict:
    resolved = site.resolve()
    run135_result = _base.validate(resolved, base_path)
    ai_result = _ai_commerce.validate(resolved, base_path)
    remaining = unresolved_project_path_executables(resolved, base_path)
    if remaining:
        raise RuntimeError(
            "Project-path executable URL sızıntısı:\n" + "\n".join(remaining[:20])
        )
    return {
        **run135_result,
        "aiCommerceAeoV250": ai_result,
    }


_base.harden_outage_input = harden_outage_input
_ai_commerce.inject_ssr_baseline = inject_ssr_baseline_without_inline_css

VERSION = max(_base.VERSION, _ai_commerce.VERSION)
ROUTES = _base.ROUTES
main = _base.main
