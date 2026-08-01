from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "alo186/deployment/check_live_english.py"
SPEC = importlib.util.spec_from_file_location("check_live_english", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

ORIGIN = "https://alo186.com"


def valid_html(route: str) -> str:
    turkish = MODULE.LANGUAGE_PAIRS[route]
    calls = '<a href="tel:112">112</a><a href="tel:186">186</a>' if route in MODULE.CALL_ROUTES else ""
    gas = '<a href="tel:187">187</a>' if route == "/en/emergency-numbers-turkey/" else ""
    finder = (
    '<script src="/edas-bul/companies.js"></script>'
    '<script src="/en/assets/finder.js"></script>'
    '81 provinces 21 electricity distribution regions'
    if route.endswith("company-finder/")
    else ""
)
    return f'''<!doctype html>
<html lang="en"><head>
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{ORIGIN}{route}">
<link rel="alternate" hreflang="tr-TR" href="{ORIGIN}{turkish}">
<link rel="alternate" hreflang="en" href="{ORIGIN}{route}">
<link rel="alternate" hreflang="x-default" href="{ORIGIN}{turkish}">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebPage","inLanguage":"en"}}</script>
</head><body><h1>English title</h1><div>Direct answer:</div>{calls}{gas}{finder}</body></html>'''


def expect_error(callback, fragment: str) -> None:
    try:
        callback()
    except MODULE.LiveValidationError as exc:
        assert fragment in str(exc), (fragment, str(exc))
    else:
        raise AssertionError(f"Beklenen LiveValidationError oluşmadı: {fragment}")


def main() -> None:
    for route in MODULE.LANGUAGE_PAIRS:
        result = MODULE.validate_english_page(route, valid_html(route), ORIGIN)
        assert result.route == route
        assert result.status == 200
        assert result.canonical == ORIGIN + route
        assert result.html_lang == "en"
        assert "self-canonical" in result.checks
        assert "reciprocal-hreflang" in result.checks
        assert "valid-json-ld" in result.checks

    route = "/en/electricity-outage-turkey/"
    expect_error(
        lambda: MODULE.validate_english_page(route, valid_html(route).replace('lang="en"', 'lang="tr-TR"'), ORIGIN),
        "html lang",
    )
    expect_error(
        lambda: MODULE.validate_english_page(route, valid_html(route).replace(ORIGIN + route, ORIGIN + "/wrong/", 1), ORIGIN),
        "canonical",
    )
    expect_error(
        lambda: MODULE.validate_english_page(route, valid_html(route).replace("Direct answer:", ""), ORIGIN),
        "doğrudan cevap",
    )
    expect_error(
        lambda: MODULE.validate_english_page(route, valid_html(route).replace("</body>", '<a rel="sponsored" href="https://amazon.com.tr/">Buy now</a></body>'), ORIGIN),
        "ticari token",
    )
    expect_error(
        lambda: MODULE.validate_english_page(route, valid_html(route).replace('"inLanguage":"en"', '"inLanguage":"tr-TR"'), ORIGIN),
        "inLanguage=en",
    )

    sitemap = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">" + "".join(
        f"<url><loc>{ORIGIN}{route}</loc></url>" for route in MODULE.LANGUAGE_PAIRS
    ) + "</urlset>"
    urls = MODULE.validate_sitemap(sitemap, ORIGIN)
    assert len(urls) == len(MODULE.LANGUAGE_PAIRS)
    missing = sitemap.replace(f"<url><loc>{ORIGIN}/en/privacy/</loc></url>", "")
    expect_error(lambda: MODULE.validate_sitemap(missing, ORIGIN), "Sitemap İngilizce rota eksik")

    payload = MODULE.SmokeReport(
        ok=True,
        checked_at="2026-07-30T00:00:00+00:00",
        origin=ORIGIN,
        expected_commit="a" * 40,
        live_commit="b" * 40,
        live_commit_relation="ahead",
        attempts=2,
        route_count=10,
        sitemap_url_count=200,
    ).to_json()
    assert json.loads(json.dumps(payload))["route_count"] == 10

    print(
        json.dumps(
            {
                "ok": True,
                "routes": len(MODULE.LANGUAGE_PAIRS),
                "safetyCommerceClosedRoutes": len(MODULE.SAFETY_COMMERCE_CLOSED_ROUTES),
                "liveOrigin": ORIGIN,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
