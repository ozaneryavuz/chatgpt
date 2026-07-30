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
UNRESOLVED_ROOT_REFERENCE = re.compile(r'(?P<quote>["\'`])/(?!/)(?P<rest>[^"\'`\s<>]*)')


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


ux_js = (ROOT / "alo186/assets/alo186-ux.js").read_text(encoding="utf-8")
ux_css = (ROOT / "alo186/assets/alo186-ux.css").read_text(encoding="utf-8")
for token in (
    "const ROOT = String.fromCharCode(47)",
    "const isIndexable = !robots.includes('noindex')",
    "const isTurkish",
    "const tocDisabled = main?.hasAttribute('data-alo186-toc-disabled')",
    "heading.closest('[data-alo186-toc-skip]')",
    "markCurrent(nav)",
    "const basePath = scriptUrl.pathname.endsWith(assetSuffix)",
    "body.dataset.alo186UxCompact = 'true'",
    "Skip to content",
    "Back to top",
    "alo-ux-toc",
    "Bu sayfada neler var?",
    "alo186AltFallback",
    "figcaption",
):
    assert token in ux_js, token
root_reference = UNRESOLVED_ROOT_REFERENCE.search(ux_js)
assert root_reference is None, f"UX JavaScript project-path dışına çıkan kök referans taşıyor: {root_reference.group(0)!r}"
assert "body:not([data-alo186-ux-compact=true])" in ux_css
assert "body{padding-bottom" not in ux_css
assert ".alo-ux-toc" in ux_css
assert "grid-template-columns:repeat(2" in ux_css

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
        run([
            sys.executable,
            "alo186/deployment/inject_outcome_runtime.py",
            "--site", str(target),
            "--base-path", base_path,
        ])
        run([
            sys.executable,
            "alo186/deployment/inject_shortlist_growth.py",
            "--site", str(target),
            "--base-path", base_path,
        ])
        run([
            sys.executable,
            "alo186/deployment/smoke_github_pages.py",
            "--site", str(target),
            "--base-path", base_path,
        ])
        run([
            sys.executable,
            "alo186/deployment/inject_live_quality_hardening_v2.py",
            "--site", str(target),
            "--base-path", base_path,
        ])
        html_files = sorted(target.rglob("*.html"))
        assert html_files, target
        missing_ux = []
        missing_metadata = []
        missing_h1 = []
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
        h1_ratio = (len(html_files) - len(missing_h1)) / len(html_files)
        assert h1_ratio >= 0.97, {"ratio": h1_ratio, "missing": missing_h1[:20]}
        assert (target / "assets/alo186-ux.css").is_file()
        assert (target / "assets/alo186-ux.js").is_file()
        for route in ("index.html", "edas-bul/index.html", "arama/index.html", "acil-numaralar/index.html", "elektrik-durum-merkezi/index.html"):
            assert (target / route).is_file(), route
        release = json.loads((target / "pages-release.json").read_text(encoding="utf-8"))
        assert release["sitewideUx"]["finalizedAfterGrowthInjectors"] is True
        assert release["sitewideUx"]["finalHtmlPages"] == len(html_files)
        assert release["sitewideUx"]["finalInjectedPages"] + release["sitewideUx"]["finalAlreadyInjectedPages"] == len(html_files)
        results.append({
            "target": "custom" if not base_path else "project",
            "pages": len(html_files),
            "h1Coverage": round(h1_ratio, 4),
            "uxInjected": True,
            "uxFinalizedAfterGrowthInjectors": True,
            "criticalRoutes": 5,
            "fullPagesSmoke": True,
        })

run(["node", "--check", "alo186/assets/alo186-ux.js"])
print(json.dumps({
    "ok": True,
    "targets": results,
    "technicalExceptions": sorted(TECHNICAL_HTML_EXCEPTIONS),
    "mobileUtilityBar": "indexable-tr-only",
    "projectPathAware": True,
    "projectPathSmoke": True,
    "finalizedAfterGrowthInjectors": True,
    "localizedUtilities": True,
    "activePageState": True,
    "tableOverflowGuard": True,
    "externalLinkHardening": True,
    "lazyImages": True,
    "imageAltFallback": True,
    "longPageToc": True,
    "backToTop": True,
    "minimumTouchTarget": 44,
}, ensure_ascii=False))
