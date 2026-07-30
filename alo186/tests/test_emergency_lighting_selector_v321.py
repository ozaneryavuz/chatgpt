from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = REPO_ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))
from build_static_site import load_effective_manifest

ROUTE = "/hesaplama/acil-aydinlatma-sure-lumen-uygunluk/"
MODULE = REPO_ROOT / "alo186/hesaplama/acil-aydinlatma-sure-lumen-uygunluk"


def main() -> None:
    manifest = load_effective_manifest(REPO_ROOT)
    assert manifest["version"] >= 82
    routes = [route for route in manifest["routes"] if route["canonicalPath"] == ROUTE]
    assert routes == [{
        "source": "alo186/hesaplama/acil-aydinlatma-sure-lumen-uygunluk/index.html",
        "canonicalPath": ROUTE,
        "type": "calculator",
    }]

    for name in ("index.html", "styles.css", "app.js", "app.test.js"):
        assert (MODULE / name).is_file(), name

    html = (MODULE / "index.html").read_text(encoding="utf-8")
    css = (MODULE / "styles.css").read_text(encoding="utf-8")
    app = (MODULE / "app.js").read_text(encoding="utf-8")
    common = (REPO_ROOT / "alo186/hesaplama/common.js").read_text(encoding="utf-8")

    assert 'rel="canonical" href="https://alo186.com/hesaplama/acil-aydinlatma-sure-lumen-uygunluk/"' in html
    for token in ("WebApplication", "DefinedTermSet", "FAQPage", "BreadcrumbList"):
        assert token in html
    assert html.count("<h1>") == 1
    assert 'id="lightingForm"' in html
    assert 'aria-live="polite"' in html
    assert 'Satış ortaklığı açıklaması' in html
    assert 'doğrudan mağaza bağlantısı açmaz' in html
    assert 'ürün satıcısı değildir' in html
    assert 'mevzuata tabi bina kaçış yolu' in html.casefold()
    assert 'amazon.com' not in html.casefold()

    for token in ("@media(max-width:820px)", "@media(max-width:560px)", "prefers-reduced-motion", "min-inline-size:0"):
        assert token in css

    for forbidden in ("localStorage", "sessionStorage", "fetch(", "XMLHttpRequest", "navigator.geolocation"):
        assert forbidden not in app
    for personal in ("name=\"email\"", "name=\"phone\"", "name=\"address\"", "type=\"email\"", "type=\"tel\""):
        assert personal not in html

    for token in (
        "PRESET_LUX", "EFFICIENCY=0.85", "USABLE_FRACTION=0.80", "LIGHT_RESERVE=1.30",
        "emergency_light", "powerbank", "power_station", "conditional_purchase", "no_buy",
        "actualNeed", "technicalCheck", "affiliateCheck",
    ):
        assert token in app
    assert "amazon." not in app.casefold()
    assert "../../akilli-urun-secimi?kategori=" in app

    assert "/hesaplama/acil-aydinlatma-sure-lumen-uygunluk/" in common
    assert "data-alo186-emergency-lighting-card" in common
    assert "37 çekirdek araç" in common

    result = subprocess.run(
        ["node", str(MODULE / "app.test.js")],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["scenarios"] == 11
    assert payload["route"] == ROUTE

    print(json.dumps({
        "ok": True,
        "routingVersion": manifest["version"],
        "route": ROUTE,
        "decisionScenarios": payload["scenarios"],
        "personalDataFields": 0,
        "directStoreLinks": 0,
        "toolCount": 37,
        "affiliateGateChecks": 3,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
