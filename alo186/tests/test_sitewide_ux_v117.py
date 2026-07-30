from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UX_MARKER = 'data-alo186-sitewide-ux="true"'
AUDIT_MARKER = 'data-alo186-user-experience="true"'
TECHNICAL_HTML_EXCEPTIONS = {"404.html"}
CRITICAL_USER_ROUTES = {
    "index.html",
    "elektrik-portali/index.html",
    "elektrik-durum-merkezi/index.html",
    "edas-bul/index.html",
    "arama/index.html",
    "acil-numaralar/index.html",
}
ALIASES = {
    "bilgi-guncelligi/index.html": "/kaynaklar/",
    "edas/index.html": "/elektrik-dagitim-sirketleri/",
    "isletmeler/index.html": "/isletme-surekliligi/",
    "urun-eslestirme/index.html": "/akilli-urun-secimi/",
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
audit_source = (ROOT / "alo186/deployment/finalize_user_experience.py").read_text(encoding="utf-8")
for token in (
    "const isIndexable = !robots.includes('noindex')",
    "const isTurkish",
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
):
    assert token in ux_js, token
for token in (
    "brokenInternalLinks",
    "unlabelledControls",
    "unsafeBlankTargets",
    "userFacingMonetizationCopy",
    "aliasPagesCreated",
    "metaDescriptionsPresent",
    "gerçek ihtiyacı gelire dönüştüren",
    "data-alo186-pages-sw",
):
    assert token in audit_source, token

assert 'body:not([data-alo186-ux-compact="true"])' in ux_css
assert "body{padding-bottom" not in ux_css.replace(" ", "")
assert '.alo-table-scroll[data-overflow="true"]' in ux_css
assert ".alo-ux-toc" in ux_css
assert "grid-template-columns: repeat(2" in ux_css
assert ".alo-ux-mobilebar a:focus-visible" in ux_css
assert "alo186-consent-settings" in ux_css
assert not re.search(r"outline\s*:\s*(?:0|none)\b", ux_css, re.I), "Klavye odağı bastırılamaz"
assert not unresolved_root_literals(
    ux_js,
    {"assets", "edas-bul", "arama", "acil-numaralar"},
), "Site geneli JS project-path dışında kök rota taşımamalı"

with tempfile.TemporaryDirectory(prefix="alo186-ux-v119-") as folder:
    canonical = Path(folder) / "canonical"
    custom = Path(folder) / "custom"
    project = Path(folder) / "project"
    run([
        sys.executable,
        "alo186/deployment/build_static_site.py",
        "--output",
        str(canonical),
        "--commit",
        "ux-v119-test",
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
            "ux-v119-test",
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
        missing_audit: list[str] = []
        missing_metadata: list[str] = []
        missing_h1: list[str] = []
        internal_copy: list[str] = []
        for page in html_files:
            text = page.read_text(encoding="utf-8")
            relative = page.relative_to(target).as_posix()
            if text.count(UX_MARKER) != 2:
                missing_ux.append(relative)
            if AUDIT_MARKER not in text:
                missing_audit.append(relative)
            required = ('<meta name="viewport"', '<meta name="description"', "<title>", 'rel="canonical"', "<html")
            if relative not in TECHNICAL_HTML_EXCEPTIONS and any(token not in text for token in required):
                missing_metadata.append(relative)
            if not re.search(r"<h1\b", text, re.I):
                missing_h1.append(relative)
            if "gerçek ihtiyacı gelire dönüştüren" in text:
                internal_copy.append(relative)

        assert not missing_ux, missing_ux[:20]
        assert not missing_audit, missing_audit[:20]
        assert not missing_metadata, missing_metadata[:20]
        assert not internal_copy, internal_copy[:20]
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

        for alias, destination in ALIASES.items():
            alias_page = target / alias
            assert alias_page.is_file(), alias
            alias_html = alias_page.read_text(encoding="utf-8")
            assert f"https://alo186.com{destination}" in alias_html
            assert 'data-alo186-pages-sw' in alias_html

        release = json.loads((target / "pages-release.json").read_text(encoding="utf-8"))
        assert release["sitewideUx"]["injectedPages"] + release["sitewideUx"]["alreadyInjectedPages"] == len(html_files)
        audit = release["sitewideUserExperienceAudit"]
        assert audit["htmlPagesScanned"] == len(html_files)
        assert audit["brokenInternalLinks"] == 0
        assert audit["unlabelledControls"] == 0
        assert audit["unsafeBlankTargets"] == 0
        assert audit["userFacingMonetizationCopy"] == 0
        assert audit["metaDescriptionsPresent"] == len(html_files)

        results.append({
            "target": "custom" if not base_path else "project",
            "pages": len(html_files),
            "h1Coverage": round(h1_ratio, 4),
            "criticalRoutes": len(CRITICAL_USER_ROUTES),
            "projectPathSmoke": True,
            "uxInjected": True,
            "aliases": len(ALIASES),
            "brokenLinks": 0,
            "unlabelledControls": 0,
        })

run(["node", "--check", "alo186/assets/alo186-ux.js"])
run([sys.executable, "-m", "py_compile", "alo186/deployment/finalize_user_experience.py"])
print(json.dumps({
    "ok": True,
    "targets": results,
    "technicalExceptions": sorted(TECHNICAL_HTML_EXCEPTIONS),
    "criticalRoutes": sorted(CRITICAL_USER_ROUTES),
    "mobileUtilityBar": "indexable-tr-only-with-native-dock-deduplication",
    "projectPathAware": True,
    "localizedUtilities": True,
    "activePageState": True,
    "tableOverflowGuard": "focus-only-when-overflowing",
    "tableContextLabels": True,
    "formControlFallbackLabels": True,
    "dynamicLinkFallbackNames": True,
    "keyboardFocusVisible": True,
    "externalLinkHardening": True,
    "criticalImagesProtected": True,
    "imageAltFallback": True,
    "longPageToc": True,
    "consentDockCollisionGuard": True,
    "backToTop": "request-animation-frame-throttled",
    "minimumTouchTarget": 44,
    "allPageAudit": True,
    "knownRouteAliases": len(ALIASES),
    "personalDataFieldsAdded": 0,
}, ensure_ascii=False))
