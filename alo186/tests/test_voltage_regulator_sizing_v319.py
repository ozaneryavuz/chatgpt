from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = REPO_ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

from build_static_site import load_effective_manifest  # noqa: E402

ROUTE = "/hesaplama/voltaj-regulatoru-kva-uygunluk/"
SOURCE = "alo186/hesaplama/voltaj-regulatoru-kva-uygunluk/index.html"


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
    assert manifest["version"] >= 78
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
    assert 'rel="canonical" href="https://www.alo186.com/hesaplama/voltaj-regulatoru-kva-uygunluk/"' in html
    assert {"WebApplication", "FAQPage", "BreadcrumbList"} <= schema_types(html)
    assert 'aria-live="polite"' in html and 'tabindex="-1"' in html
    assert 'rel="sponsored nofollow noopener"' in html
    assert "ALO186 ürün satıcısı veya resmî kurum değildir" in html
    assert "Fiyat, stok, puan" in html
    assert "Satın almama sonucu var" in html

    lower = html.casefold()
    for forbidden in ['type="email"', 'type="tel"', 'name="email"', 'name="phone"', 'name="address"']:
        assert forbidden not in lower
    assert "localStorage" not in app and "sessionStorage" not in app
    assert "fetch(" not in app and "XMLHttpRequest" not in app

    for token in [
        "input.loadKw / pf", "input.motorKw * input.startFactor", "nextStandard",
        "lowRatio < 0.7", "runningKva", "startKva", "derating"
    ]:
        assert token in app
    for token in ["plug_avr", "no_buy", "root_cause", "spd", "ups", "professional"]:
        assert token in app
    assert "input.phase === 'mono'" in app
    assert "$('phase').value === 'three'" in app
    assert "input.loadKw <= 1.5" in app
    assert "selectedKva <= 3" in app
    assert "Ticari rota kapalı" in html or "Ticari rota kapalı" in app
    assert "112’yi arayın" in app
    assert "amazon.com.tr/s?k=" in app and "alo186rehber-21" in app
    assert "aria-disabled" in app and "setGate" in app
    assert app.index("if (input.hazard)") < app.index("if (!(input.vmin >= 80")

    assert "voltaj-regulatoru-kva-uygunluk" in hub
    assert "34 çekirdek araç" in hub
    assert "Voltaj Regülatörü kVA ve Faz Uygunluğu" in hub

    assert "@media(max-width:820px)" in css
    assert "@media(max-width:480px)" in css
    assert "prefers-reduced-motion" in css
    assert "focus-visible" in css

    print(json.dumps({
        "ok": True,
        "routingVersion": manifest["version"],
        "route": ROUTE,
        "hubToolCountLabel": 34,
        "personalDataFields": 0,
        "browserStorage": False,
        "affiliateDisclosure": True,
        "emergencyCommerceClosed": True,
        "hazardBeforeNumericValidation": True,
        "professionalGate": True,
        "noBuyOutcome": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
