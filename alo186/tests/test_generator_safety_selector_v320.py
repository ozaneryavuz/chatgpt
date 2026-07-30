from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = REPO_ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

from build_static_site import load_effective_manifest  # noqa: E402

ROUTE = "/hesaplama/jenerator-guvenli-kullanim-testi/"
SOURCE = "alo186/hesaplama/jenerator-guvenli-kullanim-testi/index.html"
OVERLAY = REPO_ROOT / "alo186/deployment/routing-overlays/generator-safety-selector-v320.json"


def schema_types(html: str) -> set[str]:
    found: set[str] = set()
    blocks = re.findall(r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S | re.I)
    for block in blocks:
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
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay == {
        "version": 81,
        "generatedAt": "2026-07-30",
        "routes": [{"source": SOURCE, "canonicalPath": ROUTE, "type": "calculator"}],
    }

    manifest = load_effective_manifest(REPO_ROOT)
    assert manifest["version"] >= 81
    routes = [item for item in manifest["routes"] if item["canonicalPath"] == ROUTE]
    assert len(routes) == 1
    assert routes[0]["source"] == SOURCE
    assert routes[0]["type"] == "calculator"

    page = REPO_ROOT / SOURCE
    app_path = page.with_name("app.js")
    styles_path = page.with_name("styles.css")
    app_test = page.with_name("app.test.js")
    assert page.is_file() and app_path.is_file() and styles_path.is_file() and app_test.is_file()

    html = page.read_text(encoding="utf-8")
    app = app_path.read_text(encoding="utf-8")
    styles = styles_path.read_text(encoding="utf-8")
    common = (REPO_ROOT / "alo186/hesaplama/common.js").read_text(encoding="utf-8")

    assert html.count("<h1") == 1
    assert '<link rel="canonical" href="https://alo186.com/hesaplama/jenerator-guvenli-kullanim-testi/">' in html
    assert {"WebApplication", "DefinedTermSet", "FAQPage", "BreadcrumbList"} <= schema_types(html)
    assert 'aria-live="polite"' in html and 'tabindex="-1"' in html
    assert "Satış ortaklığı açıklaması" in html
    assert "ALO186 ürün satıcısı veya resmî kurum değildir" in html
    assert "Satın almama sonucu var" in html
    assert "6,1 m" in html and "20 feet" in html
    for source_domain in ["cdc.gov", "cpsc.gov", "osha.gov"]:
        assert source_domain in html
    assert "amazon.com.tr" not in html.casefold(), "Araç doğrudan mağaza linki açmamalı."
    assert not re.search(r'type=["\'](?:email|tel|text|file|password)["\']', html, re.I)

    for token in [
        "DISTANCE_MIN_M=6.1", "placement==='garage_shed'", "connection==='backfeed'",
        "weather==='wet'", "cord==='damaged'", "refuel==='hot_running'",
        "baseResult('no_buy'", "baseResult('conditional_purchase'", "commerceClosed",
        "co_alarm", "extension_cord", "generator", "112’yi arayın",
    ]:
        assert token in app
    assert app.index("if(input.emergency)") < app.index("const hardStops=[]")
    assert "localStorage" not in app and "sessionStorage" not in app
    assert "fetch(" not in app and "XMLHttpRequest" not in app

    assert "@media(max-width:820px)" in styles
    assert "@media(max-width:520px)" in styles
    assert "prefers-reduced-motion" in styles
    assert "focus-visible" in styles
    assert "min-inline-size:0" in styles

    assert "generatorSafetyCard" in common
    assert "data-alo186-generator-safety-card" in common
    assert "/hesaplama/jenerator-guvenli-kullanim-testi/" in common
    assert "36 çekirdek araç" in common

    print(json.dumps({
        "ok": True,
        "routingVersion": manifest["version"],
        "route": ROUTE,
        "module": "portable_generator_co_placement_connection_test",
        "distanceThresholdM": 6.1,
        "personalDataFields": 0,
        "browserStorage": False,
        "directStoreLinks": 0,
        "affiliateDisclosure": True,
        "emergencyCommerceClosed": True,
        "noBuyOutcome": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
