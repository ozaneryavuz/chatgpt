from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "alo186/deployment"))

from inject_live_quality_hardening import CANONICAL_ORIGIN, CSS_FILE, CSS_MARKER, run  # noqa: E402


def seed(site: Path, base_path: str) -> None:
    route = site / "elektrik-portali"
    route.mkdir(parents=True)
    css_href = f"{base_path}/{CSS_FILE}" if base_path else f"/{CSS_FILE}"
    html = f'''<!doctype html><html lang="tr"><head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="canonical" href="https://www.alo186.com/elektrik-portali">
<title>Test portalı</title></head><body><main>
<h1>Elektrik portalı</h1>
<p>Elektrik kesintisi cihazımı bozduysa zararın ortaya çıktığı tarihten itibaren 30 gün içinde EDAŞ kaydı açın.</p>
<a href="{base_path}/elektrik-portali" aria-label="Portal">Portal</a>
</main></body></html>'''
    (route / "index.html").write_text(html, encoding="utf-8")
    (site / "index.html").write_text(html.replace("/elektrik-portali", "/"), encoding="utf-8")
    (site / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://www.alo186.com/sitemap.xml\n", encoding="utf-8")
    (site / "sitemap.xml").write_text('<?xml version="1.0"?><urlset><url><loc>https://www.alo186.com/elektrik-portali</loc></url></urlset>', encoding="utf-8")
    (site / ".htaccess").write_text("RewriteCond %{HTTP_HOST} !^www\\.alo186\\.com$ [NC]\nRewriteRule ^ https://www.alo186.com%{REQUEST_URI} [R=301,L]\n", encoding="utf-8")
    release = {
        "canonicalHost": "https://www.alo186.com",
        "routes": [{"canonicalPath": "/elektrik-portali", "source": "alo186/index.html", "type": "collection"}],
    }
    (site / "alo186-release.json").write_text(json.dumps(release), encoding="utf-8")
    (site / "pages-release.json").write_text(json.dumps({"canonicalHost": "https://www.alo186.com", "basePath": base_path}), encoding="utf-8")
    assert css_href not in html


def test_custom_domain() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        seed(site, "")
        result = run(site, "")
        assert result["canonicalOrigin"] == CANONICAL_ORIGIN
        assert result["deviceDamageDeadline"] == "10 iş günü"
        assert result["minimumTouchTargetCssPx"] == 44
        assert result["officialInstitutionClaimed"] is False
        assert result["personalDataCollectionAdded"] is False
        portal = (site / "elektrik-portali/index.html").read_text(encoding="utf-8")
        assert "https://www.alo186.com" not in portal
        assert '<link rel="canonical" href="https://alo186.com/elektrik-portali">' in portal
        assert "10 iş günü içinde ilgili dağıtım şirketinin resmî kanalına başvurun" in portal
        assert CSS_MARKER in portal and f'href="/{CSS_FILE}"' in portal
        assert "Sitemap: https://alo186.com/sitemap.xml" in (site / "robots.txt").read_text(encoding="utf-8")
        assert "!^alo186\\.com$" in (site / ".htaccess").read_text(encoding="utf-8")
        for name in ("alo186-release.json", "pages-release.json"):
            release = json.loads((site / name).read_text(encoding="utf-8"))
            assert release["canonicalHost"] == CANONICAL_ORIGIN
            assert release["liveTechnicalQuality"]["minimumTouchTargetCssPx"] == 44
        css = (site / CSS_FILE).read_text(encoding="utf-8")
        for token in ["min-height:44px", ".amazon-intent-card small", "focus-visible", "overflow-wrap:anywhere"]:
            assert token in css


def test_project_base_path() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        seed(site, "/chatgpt")
        result = run(site, "/chatgpt")
        assert result["basePath"] == "/chatgpt"
        portal = (site / "elektrik-portali/index.html").read_text(encoding="utf-8")
        assert f'href="/chatgpt/{CSS_FILE}"' in portal
        release = json.loads((site / "pages-release.json").read_text(encoding="utf-8"))
        assert release["liveTechnicalQuality"]["stylesheet"] == f"/chatgpt/{CSS_FILE}"


if __name__ == "__main__":
    test_custom_domain()
    test_project_base_path()
    print(json.dumps({
        "ok": True,
        "canonicalOrigin": CANONICAL_ORIGIN,
        "deviceDamageDeadline": "10 iş günü",
        "minimumTouchTargetCssPx": 44,
        "knownContrastSelectors": 4,
        "personalDataCollectionAdded": False,
        "officialInstitutionClaimed": False,
    }, ensure_ascii=False, indent=2))
