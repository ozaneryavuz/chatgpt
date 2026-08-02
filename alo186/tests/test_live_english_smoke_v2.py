from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))
MODULE_PATH = DEPLOYMENT / "check_live_english_v2.py"
SPEC = importlib.util.spec_from_file_location("check_live_english_v2", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

ORIGIN = "https://alo186.com"
EXPECTED = "a" * 40


def valid_html(route: str) -> str:
    turkish = MODULE.contract.LANGUAGE_PAIRS[route]
    calls = (
        '<a href="tel:112">112</a><a href="tel:186">186</a>'
        if route in MODULE.contract.CALL_ROUTES
        else ""
    )
    gas = (
        '<a href="tel:187">187</a>'
        if route == "/en/emergency-numbers-turkey/"
        else ""
    )
    finder = (
        '<script src="/edas-bul/companies.js"></script>'
        '<script src="/en/assets/finder.js"></script>'
        "81 provinces 21 electricity distribution regions"
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


def sitemap() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(
            f"<url><loc>{ORIGIN}{route}</loc></url>"
            for route in MODULE.contract.LANGUAGE_PAIRS
        )
        + "</urlset>"
    )


def route_responses() -> dict[str, tuple[int, str, dict[str, str]]]:
    return {
        route: (200, valid_html(route), {"server": "cloudflare"})
        for route in MODULE.contract.LANGUAGE_PAIRS
    }


def evaluate(
    *,
    release: tuple[int, str, dict[str, str]],
    routes: dict[str, tuple[int, str, dict[str, str]]] | None = None,
    sitemap_response: tuple[int, str, dict[str, str]] | None = None,
):
    return MODULE.evaluate_snapshot(
        origin=ORIGIN,
        repository="ozaneryavuz/chatgpt",
        expected_commit=EXPECTED,
        github_token="",
        attempt=1,
        release_response=release,
        route_responses=routes or route_responses(),
        sitemap_response=sitemap_response or (200, sitemap(), {}),
    )


def main() -> None:
    external = evaluate(
        release=(404, "<html>static-snapshot cloudflare</html>", {"server": "cloudflare"})
    )
    assert external.ok is True
    assert external.hosting_mode == "chatgpt-sites"
    assert external.release_marker_available is False
    assert external.live_commit_relation == "unavailable-external-host"
    assert external.route_count == 10
    assert external.expected_route_count == 10
    assert external.sitemap_ok is True
    assert len(external.warnings) == 1
    assert external.errors == []

    broken_routes = route_responses()
    broken_routes["/en/privacy/"] = (404, "not found", {"server": "cloudflare"})
    broken_routes["/en/contact/"] = (
        200,
        valid_html("/en/contact/").replace('lang="en"', 'lang="tr-TR"', 1),
        {},
    )
    broken = evaluate(
        release=(404, "<html>static-snapshot</html>", {"server": "cloudflare"}),
        routes=broken_routes,
    )
    assert broken.ok is False
    assert broken.route_count == 8
    assert len([probe for probe in broken.routes if not probe.ok]) == 2
    assert any("/en/privacy/ HTTP 404" in error for error in broken.errors)
    assert any("/en/contact/ html lang" in error for error in broken.errors)

    missing_sitemap = evaluate(
        release=(404, "external", {}),
        sitemap_response=(404, "", {}),
    )
    assert missing_sitemap.ok is False
    assert missing_sitemap.route_count == 10
    assert missing_sitemap.sitemap_ok is False
    assert "sitemap.xml HTTP 404" in missing_sitemap.errors

    original_compare = MODULE.contract.compare_commits
    MODULE.contract.compare_commits = lambda *_args, **_kwargs: "identical"
    try:
        pages = evaluate(
            release=(200, json.dumps({"commit": EXPECTED}), {"server": "github.com"})
        )
    finally:
        MODULE.contract.compare_commits = original_compare
    assert pages.ok is True
    assert pages.hosting_mode == "github-pages"
    assert pages.release_marker_available is True
    assert pages.live_commit == EXPECTED
    assert pages.live_commit_relation == "identical"

    invalid_release = evaluate(
        release=(200, json.dumps([{"commit": EXPECTED}]), {"server": "github.com"})
    )
    assert invalid_release.ok is False
    assert invalid_release.hosting_mode == "invalid-release-marker"
    assert any("pages-release.json geçersiz" in error for error in invalid_release.errors)

    payload = json.loads(json.dumps(external.to_json(), ensure_ascii=False))
    assert payload["route_count"] == 10
    assert payload["hosting_mode"] == "chatgpt-sites"

    print(
        json.dumps(
            {
                "ok": True,
                "version": 2,
                "routes": len(MODULE.contract.LANGUAGE_PAIRS),
                "externalHostContentCanPassWithoutCommitReceipt": True,
                "allRouteFailuresCollected": True,
                "sitemapRequired": True,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
