from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UX_MARKER = 'data-alo186-sitewide-ux="true"'
TECHNICAL_HTML_EXCEPTIONS = {"404.html"}
CRITICAL_USER_ROUTES = {
    "index.html",
    "elektrik-portali/index.html",
    "elektrik-durum-merkezi/index.html",
    "edas-bul/index.html",
    "arama/index.html",
    "acil-numaralar/index.html",
    "en/index.html",
    "en/electricity-outage-turkey/index.html",
    "en/electricity-distribution-company-finder/index.html",
    "en/emergency-numbers-turkey/index.html",
}


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def unresolved_root_literals(text: str, known_top_levels: set[str]) -> list[str]:
    pattern = re.compile(r'(?P<quote>["\'`])/(?!/)(?P<rest>[^"\'`\s<>]*)')
    unresolved: list[str] = []
    for match in pattern.finditer(text):
        rest = match.group("rest")
        first = rest.split("/", 1)[0].split("?", 1)[0].split("#", 1)[0]
        if rest == "" or first in known_top_levels:
            unresolved.append("/" + rest)
    return unresolved


ux_js = (ROOT / "alo186/assets/alo186-ux.js").read_text(encoding="utf-8")
ux_css = (ROOT / "alo186/assets/alo186-ux.css").read_text(encoding="utf-8")
for token in (
    "const isIndexable = !robots.includes('noindex')",
    "const isTurkish",
    "const isEnglish",
    "markCurrent(nav)",
    "String.fromCharCode(47)",
    "const basePath = scriptUrl.pathname.endsWith(assetSuffix)",
    "body.dataset.alo186UxCompact = 'true'",
    "body.dataset.alo186UxNativeDock = 'true'",
    "Skip to content",
    "Back to top",
    "alo-ux-toc",
    "Bu sayfada neler var?",
    "alo186AltFallback",
    "alo186LabelFallback",
    "alo186LinkFallback",
    "ResizeObserver",
    "wrapper.tabIndex = overflowing ? 0 : -1",
    "header,.hero,[data-critical-media]",
    "alo186ConsentSettingsVisible",
    "requestAnimationFrame(updateTop)",
    "electricity-distribution-company-finder",
    "emergency-numbers-turkey",
    "journeyData",
    "alo186NextSteps",
    "aloAffiliateBadge",
    "linkObserver",
    "sponsored",
    "nofollow",
    "Mevcut ürünün yeterli olup olmadığını önce kontrol edin",
):
    assert token in ux_js, token

for token in (
    'body:not([data-alo186-ux-compact="true"])',
    '.alo-table-scroll[data-overflow="true"]',
    '.alo-ux-toc',
    '.alo-ux-next',
    '.alo-ux-next-grid',
    'a[data-alo-affiliate-badge="true"]::after',
    '.alo-ux-mobilebar a:focus-visible',
    'alo186-consent-settings',
    'prefers-contrast: more',
    'forced-colors: active',
):
    assert token in ux_css, token
assert "body{padding-bottom" not in ux_css.replace(" ", "")
assert "grid-template-columns: repeat(2" in ux_css
assert not re.search(r"outline\s*:\s*(?:0|none)\b", ux_css, re.I), "Klavye odağı bastırılamaz"
assert not unresolved_root_literals(
    ux_js,
    {"assets", "edas-bul", "arama", "acil-numaralar", "en"},
), "Site geneli JS project-path dışında kök rota taşımamalı"

with tempfile.TemporaryDirectory(prefix="alo186-ux-v120-") as folder:
    canonical = Path(folder) / "canonical"
    custom = Path(folder) / "custom"
    project = Path(folder) / "project"
    run([
        sys.executable,
        "alo186/deployment/build_static_site.py",
        "--output",
        str(canonical),
        "--commit",
        "ux-v120-test",
    ])

    results = []
    for target, base_path in ((custom, ""), (project, "/chatgpt")):
        subprocess.run(["cp", "-a", str(canonical), str(target)], check=True)
        run([
            sys.executable,
            "alo186/deployment/prepare_github_pages.py",
            "--site",
            str(target),
            "--base-path",
            base_path,
            "--repository",
            "ozaneryavuz/chatgpt",
            "--commit",
            "ux-v120-test",
        ])
        run([
            sys.executable,
            "alo186/deployment/smoke_github_pages.py",
            "--site",
            str(target),
            "--base-path",
            base_path,
        ])

        html_files = sorted(target.rglob("*.html"))
        assert html_files, target
        relative_files = {page.relative_to(target).as_posix() for page in html_files}
        assert CRITICAL_USER_ROUTES <= relative_files, sorted(CRITICAL_USER_ROUTES - relative_files)

        missing_ux: list[str] = []
        missing_metadata: list[str] = []
        missing_h1: list[str] = []
        for page in html_files:
            text = page.read_text(encoding="utf-8")
            relative = page.relative_to(target).as_posix()
            if text.count(UX_MARKER) != 2:
                missing_ux.append(relative)
            required = ('<meta name="viewport"', "<title>", 'rel="canonical"', "<html")
            if relative not in TECHNICAL_HTML_EXCEPTIONS and any(token not in text for token in required):
                missing_metadata.append(relative)
            if not re.search(r"<h1\b", text, re.I):
                missing_h1.append(relative)

        assert not missing_ux, missing_ux[:20]
        assert not missing_metadata, missing_metadata[:20]
        assert not (CRITICAL_USER_ROUTES & set(missing_h1)), {
            "criticalRoutesWithoutH1": sorted(CRITICAL_USER_ROUTES & set(missing_h1)),
        }
        h1_ratio = (len(html_files) - len(missing_h1)) / len(html_files)
        assert h1_ratio >= 0.97, {"ratio": h1_ratio, "missing": missing_h1[:20]}
        assert (target / "assets/alo186-ux.css").is_file()
        assert (target / "assets/alo186-ux.js").is_file()

        generated_js = (target / "assets/alo186-ux.js").read_text(encoding="utf-8")
        known_top_levels = {path.name for path in target.iterdir()}
        if base_path:
            assert not unresolved_root_literals(generated_js, known_top_levels)

        release = json.loads((target / "pages-release.json").read_text(encoding="utf-8"))
        assert release["sitewideUx"]["injectedPages"] + release["sitewideUx"]["alreadyInjectedPages"] == len(html_files)
        results.append({
            "target": "custom" if not base_path else "project",
            "pages": len(html_files),
            "h1Coverage": round(h1_ratio, 4),
            "criticalRoutes": len(CRITICAL_USER_ROUTES),
            "projectPathSmoke": True,
            "englishMobileNavigation": True,
            "contextualNextSteps": True,
            "dynamicAffiliateHardening": True,
            "uxInjected": True,
        })

run(["node", "--check", "alo186/assets/alo186-ux.js"])
print(json.dumps({
    "ok": True,
    "targets": results,
    "technicalExceptions": sorted(TECHNICAL_HTML_EXCEPTIONS),
    "criticalRoutes": sorted(CRITICAL_USER_ROUTES),
    "mobileUtilityBar": "indexable-tr-and-en-with-native-dock-deduplication",
    "projectPathAware": True,
    "localizedUtilities": True,
    "activePageState": True,
    "tableOverflowGuard": "focus-only-when-overflowing",
    "tableContextLabels": True,
    "formControlFallbackLabels": True,
    "dynamicLinkFallbackNames": True,
    "keyboardFocusVisible": True,
    "externalLinkHardening": True,
    "dynamicAffiliateHardening": True,
    "affiliateDisclosureBadge": True,
    "criticalImagesProtected": True,
    "imageAltFallback": True,
    "longPageToc": True,
    "contextualNextSteps": True,
    "consentDockCollisionGuard": True,
    "backToTop": "request-animation-frame-throttled",
    "minimumTouchTarget": 44,
}, ensure_ascii=False))
