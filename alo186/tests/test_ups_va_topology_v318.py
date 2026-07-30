from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = REPO_ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

from build_static_site import load_effective_manifest  # noqa: E402

ROUTE = "/hesaplama/ups-va-topoloji-uygunluk/"
SOURCE = "alo186/hesaplama/ups-va-topoloji-uygunluk/index.html"


def schema_types(html: str) -> set[str]:
    found: set[str] = set()
    for block in re.findall(r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S | re.I):
        payload = json.loads(block)
        nodes = payload.get("@graph", [payload]) if isinstance(payload, dict) else []
        for node in nodes:
            value = node.get("@type") if isinstance(node, dict) else None
            if isinstance(value, str):
                found.add(value)
            elif isinstance(value, list):
                found.update(str(item) for item in value)
    return found


def main() -> None:
    manifest = load_effective_manifest(REPO_ROOT)
    assert manifest["version"] >= 77
    routes = [item for item in manifest["routes"] if item["canonicalPath"] == ROUTE]
    assert len(routes) == 1
    assert routes[0]["source"] == SOURCE
    assert routes[0]["type"] == "calculator"

    page_path = REPO_ROOT / SOURCE
    app_path = page_path.with_name("app.js")
    css_path = page_path.with_name("styles.css")
    assert page_path.is_file() and app_path.is_file() and css_path.is_file()

    html = page_path.read_text(encoding="utf-8")
    app = app_path.read_text(encoding="utf-8")
    css = css_path.read_text(encoding="utf-8")
    hub = (REPO_ROOT / "alo186/hesaplama/index.html").read_text(encoding="utf-8")

    assert html.count("<h1") == 1
    assert 'rel="canonical" href="https://www.alo186.com/hesaplama/ups-va-topoloji-uygunluk/"' in html
    assert {"WebApplication", "FAQPage", "BreadcrumbList"} <= schema_types(html)
    assert 'aria-live="polite"' in html and 'tabindex="-1"' in html
    assert 'rel="sponsored nofollow noopener"' in html
    assert "alo186rehber-21" in app
    assert "amazon.com.tr/s?k=" in app
    assert "Fiyat, stok, puan" in html
    assert "ALO186 ürün satıcısı veya resmî kurum değildir" in html

    lower = html.casefold()
    for forbidden in ['type="email"', 'type="tel"', 'name="email"', 'name="phone"', 'name="address"']:
        assert forbidden not in lower
    assert "localStorage" not in app and "sessionStorage" not in app
    assert "fetch(" not in app and "XMLHttpRequest" not in app

    for token in ["input.watts * 1.25", "input.peak * 1.10", "0.85 * 0.80", "roundUp", "inferredPf"]:
        assert token in app
    assert "medical" in app and "motor" in app and "professional" in app
    assert "commerceAllowed" in app
    assert "!result.hazard" in app
    assert "result.runtime <= 30" in app
    assert "result.watts <= 1500" in app
    assert "Duman, kıvılcım" in html
    assert "Ticari rota kapalı" in app
    assert "112’yi arayın" in app

    assert "ups-va-topoloji-uygunluk" in hub
    count_match = re.search(r"(\d+) çekirdek araç", hub)
    assert count_match and int(count_match.group(1)) >= 33
    assert "UPS VA ve Topoloji Uygunluğu" in hub

    assert "@media(max-width:820px)" in css
    assert "@media(max-width:480px)" in css
    assert "prefers-reduced-motion" in css
    assert "focus-visible" in css

    print(json.dumps({
        "ok": True,
        "routingVersion": manifest["version"],
        "route": ROUTE,
        "hubToolCountLabel": int(count_match.group(1)),
        "personalDataFields": 0,
        "browserStorage": False,
        "affiliateDisclosure": True,
        "emergencyCommerceClosed": True,
        "professionalGate": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
