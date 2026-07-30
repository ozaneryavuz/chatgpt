from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = REPO_ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))
from build_static_site import load_effective_manifest

ROUTE = "/hesaplama/kamera-nvr-poe-yedek-guc-uygunluk/"
SOURCE = "alo186/hesaplama/kamera-nvr-poe-yedek-guc-uygunluk/index.html"
MODULE = REPO_ROOT / "alo186/hesaplama/kamera-nvr-poe-yedek-guc-uygunluk"


def main() -> None:
    manifest = load_effective_manifest(REPO_ROOT)
    assert manifest["version"] >= 85
    routes = [item for item in manifest["routes"] if item["canonicalPath"] == ROUTE]
    assert len(routes) == 1
    assert routes[0]["source"] == SOURCE
    assert routes[0]["type"] == "calculator"

    html = (MODULE / "index.html").read_text(encoding="utf-8")
    css = (MODULE / "styles.css").read_text(encoding="utf-8")
    app = (MODULE / "app.js").read_text(encoding="utf-8")
    test = (MODULE / "app.test.js").read_text(encoding="utf-8")

    assert 'rel="canonical" href="https://alo186.com' + ROUTE + '"' in html
    assert html.count("<h1>") == 1
    for schema_type in ["WebApplication", "DefinedTermSet", "FAQPage", "BreadcrumbList"]:
        assert schema_type in html
    for token in [
        'id="cameraForm"', 'id="poeBudgetW"', 'id="poePorts"',
        'id="sourceContinuousW"', 'id="sourceWh"', 'aria-live="polite"',
        'id="actualNeed"', 'id="technicalCheck"', 'id="affiliateCheck"',
        "Mevcut kaynak yeterli", "yeni ürün almayın", "satış ortaklığı",
    ]:
        assert token in html or token in app

    forbidden = ["amazon.com", "localStorage", "sessionStorage", "geolocation", "fetch(", "XMLHttpRequest"]
    combined = html + app
    for token in forbidden:
        assert token not in combined
    for personal in ["Adınız", "Telefon", "E-posta", "Adresiniz", "TC kimlik"]:
        assert personal not in html

    assert "@media(max-width:820px)" in css
    assert "@media(max-width:560px)" in css
    assert "prefers-reduced-motion" in css
    assert "focus-visible" in css
    assert "minmax(0,1fr)" in css

    for token in [
        "poeEfficiency=.85", "requiredPoeBudgetW", "requiredContinuousW",
        "requiredWh", "poe_gap", "active_event", "no_buy",
        "conditional_purchase", "commercialAllowed:true",
        "../../akilli-urun-secimi?kategori=", "camera_poe_backup_result",
    ]:
        assert token in app
    assert "scenarios:14" in test

    result = subprocess.run(
        ["node", str(MODULE / "app.test.js")],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload == {"ok": True, "scenarios": 14}

    print(json.dumps({
        "ok": True,
        "routingVersion": manifest["version"],
        "route": ROUTE,
        "decisionScenarios": 14,
        "directStoreLinks": 0,
        "personalDataFields": 0,
        "browserStorage": False,
        "affiliateTripleGate": True,
        "noBuyOutcomePreserved": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
