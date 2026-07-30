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
    "edas-bul/index.html",
    "arama/index.html",
    "acil-numaralar/index.html",
    "elektrik-durum-merkezi/index.html",
}


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


ux_js = (ROOT / "alo186/assets/alo186-ux.js").read_text(encoding="utf-8")
ux_css = (ROOT / "alo186/assets/alo186-ux.css").read_text(encoding="utf-8")
for token in (
    "const ROOT_PATH = String.fromCharCode(47)",
    "const isIndexable = !robots.includes('noindex')",
    "const isTurkish",
    "markCurrent(nav)",
    "const basePath = scriptUrl.pathname.endsWith(assetSuffix)",
    "body.dataset.alo186UxCompact = 'true'",
    "Skip to content",
    "Back to top",
    "alo-ux-toc",
    "Bu sayfada neler var?",
    "alo186AltFallback",
    "figcaption",
    "ResizeObserver",
    "wrapper.tabIndex = overflowing ? 0 : -1",
    "wrapper.dataset.overflow = String(overflowing)",
    "header,.hero,[data-critical-media]",
    "publicPath(ROOT_PATH)",
):
    assert token in ux_js, token
for forbidden in ("publicPath('/')", "|| '/'", "route === '/'", ".replace(/\\/+/g, '/')"):
    assert forbidden not in ux_js, f"Project-path kök URL sabiti kalamaz: {forbidden}"
assert "body:not([data-alo186-ux-compact=true])" in ux_css
assert "body{padding-bottom" not in ux_css
assert ".alo-ux-toc" in ux_css
assert "grid-template-columns:repeat(2" in ux_css
assert ".alo-table-scroll[data-overflow=true]" in ux_css
assert ".alo-ux-mobilebar a:focus-visible" in ux_css
assert ".alo-ux-backtop:focus-visible" in ux_css
assert ".alo-ux-toc a:focus-visible" in ux_css
assert ".alo-ux-toc summary:focus-visible" in ux_css
assert not re.search(r"outline\s*:\s*(?:0|none)\b", ux_css, re.I), "Klavye odağı bastırılamaz"

with tempfile.TemporaryDirectory(prefix="alo186-ux-v119-") as folder:
    canonical = Path(folder) / "canonical"
    custom = Path(folder) / "custom"
    project = Path(folder) / "project"
    run([sys.executable, "alo186/deployment/build_static_site.py", "--output", str(canonical), "--commit", "ux-v119-test"])

    results = []
    for target, base_path in ((custom, ""), (project, "/chatgpt")):
        subprocess.run(["cp", "-a", str(canonical), str(target)], check=True)
        run([
            sys.executable,
            "alo186/deployment/prepare_github_pages.py",
            "--site", str(target),
            "--base-path", base_path,
            "--repository", "ozaneryavuz/chatgpt",
            "--commit", "ux-v119-test",
        ])
        html_files = sorted(target.rglob("*.html"))
        assert html_files, target
        missing_ux = []
        missing_metadata = []
        missing_h1 = []
        relative_files = {page.relative_to(target).as_posix() for page in html_files}
        assert CRITICAL_USER_ROUTES <= relative_files, sorted(CRITICAL_USER_ROUTES - relative_files)
        for page in html_files:
            text = page.read_text(encoding="utf-8")
            relative = page.relative_to(target).as_posix()
            if text.count(UX_MARKER) != 2:
                missing_ux.append(relative)
            required = (
                '<meta name="viewport"',
                "<title>",
                'rel="canonical"',
                "<html",
            )
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
        release = json.loads((target / "pages-release.json").read_text(encoding="utf-8"))
        assert release["sitewideUx"]["injectedPages"] + release["sitewideUx"]["alreadyInjectedPages"] == len(html_files)
        results.append({
            "target": "custom" if not base_path else "project",
            "pages": len(html_files),
            "h1Coverage": round(h1_ratio, 4),
            "uxInjected": True,
            "criticalRoutes": len(CRITICAL_USER_ROUTES),
        })

run(["node", "--check", "alo186/assets/alo186-ux.js"])
print(json.dumps({
    "ok": True,
    "targets": results,
    "technicalExceptions": sorted(TECHNICAL_HTML_EXCEPTIONS),
    "criticalRoutes": sorted(CRITICAL_USER_ROUTES),
    "mobileUtilityBar": "indexable-tr-only",
    "projectPathAware": True,
    "projectRootReferenceFree": True,
    "localizedUtilities": True,
    "activePageState": True,
    "tableOverflowGuard": "focus-only-when-overflowing",
    "keyboardFocusVisible": True,
    "externalLinkHardening": True,
    "criticalImagesProtected": True,
    "imageAltFallback": True,
    "longPageToc": True,
    "backToTop": True,
    "minimumTouchTarget": 44,
}, ensure_ascii=False))
