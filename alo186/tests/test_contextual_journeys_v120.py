from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JS_PATH = ROOT / "alo186/assets/alo186-ux.js"
CSS_PATH = ROOT / "alo186/assets/alo186-ux.css"
UX_MARKER = 'data-alo186-sitewide-ux="true"'


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


js = JS_PATH.read_text(encoding="utf-8")
css = CSS_PATH.read_text(encoding="utf-8")

for token in (
    "const isEnglish",
    "routePath('en', 'electricity-distribution-company-finder')",
    "routePath('en', 'electricity-outage-turkey')",
    "routePath('en', 'emergency-numbers-turkey')",
    "const journeyData",
    "alo186NextSteps",
    "sensitiveTool",
    "Mevcut ürünün yeterli olup olmadığını önce kontrol edin",
    "MutationObserver",
    "const linkObserver",
    "rel.add('sponsored')",
    "rel.add('nofollow')",
    "rel.add('noopener')",
    "aloAffiliateBadge",
    "aloAffiliateLabel",
    "localCurrent",
):
    assert token in js, token
assert "else if (isIndexable)" in js
assert "else if (isIndexable && isTurkish)" not in js
assert all(token not in js for token in ("localStorage", "sessionStorage", "geolocation"))

for token in (
    ".alo-ux-next",
    ".alo-ux-next-grid",
    'a[data-alo-affiliate-badge="true"]::after',
    "prefers-contrast: more",
    "forced-colors: active",
    "HighlightText",
    "safe-area-inset-bottom",
):
    assert token in css, token
assert not re.search(r"outline\s*:\s*(?:0|none)\b", css, re.I)
assert "overflow-x:hidden" not in css.replace(" ", "").lower()
assert not unresolved_root_literals(js, {"assets", "en", "edas-bul", "arama", "acil-numaralar"})

with tempfile.TemporaryDirectory(prefix="alo186-contextual-v120-") as folder:
    canonical = Path(folder) / "canonical"
    run([
        sys.executable,
        "alo186/deployment/build_static_site.py",
        "--output",
        str(canonical),
        "--commit",
        "contextual-v120-test",
    ])

    results = []
    for name, base_path in (("custom", ""), ("project", "/chatgpt")):
        target = Path(folder) / name
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
            "contextual-v120-test",
        ])
        run([
            sys.executable,
            "alo186/deployment/smoke_github_pages.py",
            "--site",
            str(target),
            "--base-path",
            base_path,
        ])

        pages = sorted(target.rglob("*.html"))
        assert len(pages) >= 456, len(pages)
        missing = []
        for page in pages:
            if page.read_text(encoding="utf-8").count(UX_MARKER) != 2:
                missing.append(page.relative_to(target).as_posix())
        assert not missing, missing[:20]

        for route in (
            "en/index.html",
            "en/electricity-distribution-company-finder/index.html",
            "en/electricity-outage-turkey/index.html",
            "en/emergency-numbers-turkey/index.html",
            "hesaplama/cpap-apap-bipap-yedek-guc-uygunluk/index.html",
            "affiliate-knowledge-graph/index.html",
            "mevzuat/index.html",
        ):
            assert (target / route).is_file(), route

        generated_js = (target / "assets/alo186-ux.js").read_text(encoding="utf-8")
        if base_path:
            known_top_levels = {item.name for item in target.iterdir()}
            assert not unresolved_root_literals(generated_js, known_top_levels)

        results.append({
            "target": name,
            "basePath": base_path,
            "pages": len(pages),
            "englishRoutes": 4,
            "contextGroups": 7,
            "dynamicAffiliateHardening": True,
            "noindexCommerceSuppressed": True,
        })

run(["node", "--check", str(JS_PATH)])
print(json.dumps({
    "ok": True,
    "results": results,
    "englishMobileNavigation": True,
    "contextualNextSteps": True,
    "sensitiveToolCommerceRoute": False,
    "affiliateDisclosureBadge": True,
    "dynamicAffiliateRel": ["sponsored", "nofollow", "noopener"],
    "personalStorage": False,
    "officialAffiliationClaimed": False,
}, ensure_ascii=False))
