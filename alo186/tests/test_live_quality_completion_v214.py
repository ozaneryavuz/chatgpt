from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "alo186/deployment"
TESTS = ROOT / "alo186/tests"
sys.path.insert(0, str(DEPLOYMENT))
sys.path.insert(0, str(TESTS))

from audit_lighthouse_v214 import run as audit_lighthouse  # noqa: E402
from inject_live_quality_completion_v214 import CSS_MARKER, CRITICAL_ROUTES, run  # noqa: E402
from test_live_quality_hardening import seed  # noqa: E402
from verify_live_copy_v214 import validate_html  # noqa: E402


def basic_page(title: str, canonical: str, root_href: str) -> str:
    return f'''<!doctype html><html lang="tr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{title} için güvenli ve bağımsız teknik içerik.">
<meta name="robots" content="index,follow"><link rel="canonical" href="{canonical}">
<title>{title}</title></head><body><main><h1>{title}</h1><p>ALO186 bağımsız bilgi platformudur; resmî kurum değildir ve kişisel veri istemez.</p><a href="{root_href}">Ana sayfaya dön</a></main></body></html>'''


def complete_seed(site: Path, base_path: str) -> None:
    seed(site, base_path)
    root = site / "index.html"
    root_text = root.read_text(encoding="utf-8")
    root_text = root_text.replace(
        "</head>",
        '<meta name="description" content="ALO186 güvenli elektrik yönlendirme ana sayfası."></head>',
        1,
    ).replace(
        "<h1>ALO186</h1>",
        "<h1>Sorun sayfası aramayın. Doğru eylem yolunu seçin.</h1>",
    )
    root.write_text(root_text, encoding="utf-8")
    portal = site / "elektrik-portali/index.html"
    portal_text = portal.read_text(encoding="utf-8")
    portal_text = portal_text.replace(
        "</head>",
        '<meta name="description" content="ALO186 bağımsız elektrik portalı."></head>',
        1,
    ).replace(
        "</main>",
        "<p>Zararın ortaya çıktığı tarihten itibaren 30 gün içinde EDAŞ kaydı açın.</p>"
        "<p>89 rehber · 25 rehber · 12 kaynaklı makale</p></main>",
    )
    portal.write_text(portal_text, encoding="utf-8")

    extra_routes = [route for route in CRITICAL_ROUTES if route not in {"/", "/elektrik-portali/"}]
    support_routes = ["/karar-motoru/", "/kesintiye-hazirlik-atolyesi/", *extra_routes]
    for route in support_routes:
        target = site / route.strip("/")
        target.mkdir(parents=True, exist_ok=True)
        title = route.strip("/").replace("-", " ").replace("/", " — ").title()
        canonical = "https://alo186.com" + (route.rstrip("/") if route != "/" else "/")
        root_href = f"{base_path}/" if base_path else "/"
        (target / "index.html").write_text(basic_page(title, canonical, root_href), encoding="utf-8")

    locs = []
    for route in CRITICAL_ROUTES:
        public = route.rstrip("/") if route != "/" else "/"
        locs.append(f"<url><loc>https://alo186.com{public}</loc></url>")
    (site / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(locs)
        + "</urlset>",
        encoding="utf-8",
    )
    release_path = site / "alo186-release.json"
    release = json.loads(release_path.read_text(encoding="utf-8"))
    release["routes"] = [
        {"canonicalPath": route.rstrip("/") or "/", "source": "test", "type": "tool"}
        for route in CRITICAL_ROUTES if route != "/"
    ]
    release_path.write_text(json.dumps(release), encoding="utf-8")


def fake_lighthouse(path: Path, *, mode: str, performance: float = 0.95) -> None:
    payload = {
        "requestedUrl": "http://127.0.0.1:4173/",
        "finalUrl": "http://127.0.0.1:4173/",
        "lighthouseVersion": "12.8.2",
        "configSettings": {"formFactor": mode},
        "categories": {
            "performance": {"score": performance},
            "accessibility": {"score": 0.98},
            "best-practices": {"score": 0.96},
            "seo": {"score": 0.99},
        },
        "audits": {
            "largest-contentful-paint": {"numericValue": 1800 if mode == "desktop" else 2600},
            "cumulative-layout-shift": {"numericValue": 0.02},
            "total-blocking-time": {"numericValue": 90},
            "first-contentful-paint": {"numericValue": 900},
            "speed-index": {"numericValue": 1500},
        },
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_custom_domain_completion() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        complete_seed(site, "")
        result = run(site, "")
        assert result["ok"] is True
        assert result["version"] == 214
        assert result["copyNormalization"]["replacementCount"] >= 5
        assert result["criticalPages"]["criticalPageCount"] == len(CRITICAL_ROUTES)
        assert result["internalLinks"]["brokenInternalLinks"] == 0
        assert result["searchDiscovery"]["sitemapCanonicalMismatches"] == 0
        assert result["searchDiscovery"]["sitemapDuplicateUrls"] == 0
        assert result["personalDataCollectionAdded"] is False
        root = (site / "index.html").read_text(encoding="utf-8")
        portal = (site / "elektrik-portali/index.html").read_text(encoding="utf-8")
        assert "Sorun sayfası aramayın" not in root
        assert "Elektrik sorununu güvenli biçimde sınıflandırın" in root
        assert "30 gün içinde EDAŞ kaydı açın" not in portal
        assert "30 gün içinde ilgili dağıtım şirketinin resmî kanalına başvurun" in portal
        assert "89 rehber" not in portal and "12 kaynaklı makale" not in portal
        assert 'class="skip-link"' in root and 'id="main-content"' in root
        assert CSS_MARKER in (site / "alo186-live-quality.css").read_text(encoding="utf-8")
        receipt = json.loads((site / "live-quality-v214.json").read_text(encoding="utf-8"))
        assert receipt["ok"] is True
        for release_name in ("alo186-release.json", "pages-release.json"):
            release = json.loads((site / release_name).read_text(encoding="utf-8"))
            assert release["liveQualityCompletionV214"]["version"] == 214
            assert release["liveQualityCompletionV214"]["brokenInternalLinks"] == 0


def test_project_path_completion() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        complete_seed(site, "/chatgpt")
        result = run(site, "/chatgpt")
        assert result["basePath"] == "/chatgpt"
        assert result["internalLinks"]["brokenInternalLinks"] == 0
        assert result["criticalPages"]["criticalPageCount"] == len(CRITICAL_ROUTES)


def test_live_copy_validator() -> None:
    home = '''<!doctype html><html lang="tr"><head><link rel="canonical" href="https://alo186.com/"></head><body><main><h1>60 saniyede doğru elektrik rotası</h1><p>ALO186 bağımsız bilgi platformudur.</p></main></body></html>'''.encode("utf-8")
    portal = '''<!doctype html><html lang="tr"><head><link rel="canonical" href="https://alo186.com/elektrik-portali"></head><body><main><h1>Portal</h1><p>ALO186 bağımsız bilgi platformudur. Zararın ortaya çıktığı tarihten itibaren 30 gün içinde ilgili dağıtım şirketinin resmî kanalına başvurun.</p></main></body></html>'''.encode("utf-8")
    assert validate_html("home", home, "https://alo186.com/", "/")["forbiddenCopyCount"] == 0
    assert validate_html("portal", portal, "https://alo186.com/elektrik-portali", "/elektrik-portali")["forbiddenCopyCount"] == 0
    bad = home.replace(
        "60 saniyede doğru elektrik rotası".encode("utf-8"),
        "Sorun sayfası aramayın. Doğru eylem yolunu seçin.".encode("utf-8"),
    )
    try:
        validate_html("home", bad, "https://alo186.com/", "/")
    except AssertionError:
        pass
    else:
        raise AssertionError("Eski canlı ana sayfa kopyası reddedilmedi")


def test_lighthouse_budget_parser() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        mobile = root / "mobile.json"
        desktop = root / "desktop.json"
        fake_lighthouse(mobile, mode="mobile", performance=0.90)
        fake_lighthouse(desktop, mode="desktop", performance=0.96)
        result = audit_lighthouse([("mobile-root", mobile), ("desktop-root", desktop)])
        assert result["ok"] is True
        assert {report["mode"] for report in result["reports"]} == {"mobile", "desktop"}
        assert result["fieldCoreWebVitalsClaimed"] is False


if __name__ == "__main__":
    test_custom_domain_completion()
    test_project_path_completion()
    test_live_copy_validator()
    test_lighthouse_budget_parser()
    print(json.dumps({
        "ok": True,
        "version": 214,
        "criticalRoutes": len(CRITICAL_ROUTES),
        "obsoleteHomepageCopyRejected": True,
        "misleadingEdasCopyRejected": True,
        "brokenInternalLinks": 0,
        "sitemapCanonicalMismatches": 0,
        "mobileAndDesktopLighthouseBudget": True,
        "personalDataCollectionAdded": False,
        "officialInstitutionClaimed": False,
    }, ensure_ascii=False, indent=2))
