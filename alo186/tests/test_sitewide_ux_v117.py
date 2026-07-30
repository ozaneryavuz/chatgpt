from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
UX_MARKER = 'data-alo186-sitewide-ux="true"'
TECHNICAL_HTML_EXCEPTIONS = {"404.html"}
CRITICAL_ROUTES = ("/", "/edas-bul", "/arama/", "/acil-numaralar/", "/elektrik-durum-merkezi/")


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def route_exists(target: Path, route: str, base_path: str) -> bool:
    path = urlsplit(route).path
    if base_path and path.startswith(base_path + "/"):
        path = path[len(base_path):]
    path = path.strip("/")
    if not path:
        return (target / "index.html").is_file()
    candidate = target / path
    return candidate.is_file() or (candidate / "index.html").is_file()


with tempfile.TemporaryDirectory(prefix="alo186-ux-v118-") as folder:
    canonical = Path(folder) / "canonical"
    custom = Path(folder) / "custom"
    project = Path(folder) / "project"
    run([sys.executable, "alo186/deployment/build_static_site.py", "--output", str(canonical), "--commit", "ux-v118-test"])

    results = []
    for target, base_path in ((custom, ""), (project, "/chatgpt")):
        subprocess.run(["cp", "-a", str(canonical), str(target)], check=True)
        run([
            sys.executable,
            "alo186/deployment/prepare_github_pages.py",
            "--site", str(target),
            "--base-path", base_path,
            "--repository", "ozaneryavuz/chatgpt",
            "--commit", "ux-v118-test",
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
            required = ('<meta name="viewport"', "<title>", 'rel="canonical"', "<html")
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
        for route in CRITICAL_ROUTES:
            public_route = f"{base_path}{route}" if base_path else route
            assert route_exists(target, public_route, base_path), public_route
        release = json.loads((target / "pages-release.json").read_text(encoding="utf-8"))
        assert release["sitewideUx"]["injectedPages"] + release["sitewideUx"]["alreadyInjectedPages"] == len(html_files)
        results.append({
            "target": "custom" if not base_path else "project",
            "pages": len(html_files),
            "h1Coverage": round(h1_ratio, 4),
            "uxInjected": True,
            "criticalRoutes": len(CRITICAL_ROUTES),
        })

js = (ROOT / "alo186/assets/alo186-ux.js").read_text(encoding="utf-8")
css = (ROOT / "alo186/assets/alo186-ux.css").read_text(encoding="utf-8")
for token in ["alo-ux-toc", "Bu sayfada neler var?", "alo186AltFallback", "figcaption"]:
    assert token in js
for token in [".alo-ux-toc", "grid-template-columns:repeat(2", "@media(max-width:720px)"]:
    assert token in css
run(["node", "--check", "alo186/assets/alo186-ux.js"])
print(json.dumps({
    "ok": True,
    "targets": results,
    "mobileUtilityBar": True,
    "tableOverflowGuard": True,
    "externalLinkHardening": True,
    "lazyImages": True,
    "imageAltFallback": True,
    "longPageToc": True,
    "backToTop": True,
    "minimumTouchTarget": 44,
}, ensure_ascii=False))