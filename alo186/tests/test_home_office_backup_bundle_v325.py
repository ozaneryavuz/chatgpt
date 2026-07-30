from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = REPO_ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))
from build_static_site import load_effective_manifest

ROUTE = "/hesaplama/evden-calisma-laptop-modem-yedek-guc-seti/"
SOURCE = "alo186/hesaplama/evden-calisma-laptop-modem-yedek-guc-seti/index.html"
MODULE = REPO_ROOT / "alo186/hesaplama/evden-calisma-laptop-modem-yedek-guc-seti"
HUB = REPO_ROOT / "alo186/hesaplama/index.html"


def main() -> None:
    manifest = load_effective_manifest(REPO_ROOT)
    assert manifest["version"] >= 86
    routes = [item for item in manifest["routes"] if item["canonicalPath"] == ROUTE]
    assert len(routes) == 1
    assert routes[0]["source"] == SOURCE
    assert routes[0]["type"] == "calculator"

    html = (MODULE / "index.html").read_text(encoding="utf-8")
    css = (MODULE / "styles.css").read_text(encoding="utf-8")
    app = (MODULE / "app.js").read_text(encoding="utf-8")
    test = (MODULE / "app.test.js").read_text(encoding="utf-8")
    hub = HUB.read_text(encoding="utf-8")

    assert 'rel="canonical" href="https://alo186.com' + ROUTE + '"' in html
    assert html.count("<h1>") == 1
    for schema_type in ["WebApplication", "DefinedTermSet", "FAQPage", "BreadcrumbList"]:
        assert schema_type in html
    for token in [
        'id="homeOfficeForm"', 'id="computerType"', 'id="laptopW"',
        'id="modemW"', 'id="ontW"', 'id="targetHours"',
        'id="sourceStatus"', 'id="actualNeed"', 'id="technicalCheck"',
        'id="affiliateCheck"', 'id="bundleLinks"', 'aria-live="polite"',
        "yeni ürün almayın", "satış ortaklığı", "kullanıcıya ek maliyet yansımaz",
    ]:
        assert token in html or token in app

    combined = html + app
    for token in ["amazon.com", "localStorage", "sessionStorage", "geolocation", "fetch(", "XMLHttpRequest", "WebSocket"]:
        assert token not in combined
    for personal in ["Adınız", "Telefon", "E-posta", "Adresiniz", "TC kimlik", "İşveren adı"]:
        assert personal not in html

    assert "@media(max-width:820px)" in css
    assert "@media(max-width:560px)" in css
    assert "prefers-reduced-motion" in css
    assert "focus-visible" in css
    assert "minmax(0,1fr)" in css

    for token in [
        "requiredPowerbankWh", "requiredMiniUpsWh", "requiredPowerStationWh",
        "split_dc", "network_only", "powerbank_only", "power_station",
        "ups_path", "active_event", "no_buy", "conditional_purchase",
        "commercialAllowed:true", "../../akilli-urun-secimi?kategori=",
        "home_office_backup_result", "usb_c_charger", "usb_c_cable",
    ]:
        assert token in app
    assert "scenarios:21" in test

    assert "40 çekirdek araç" in hub
    assert './evden-calisma-laptop-modem-yedek-guc-seti/' in hub
    assert "Evden Çalışma Laptop ve Modem Yedek Güç Seti" in hub

    result = subprocess.run(
        ["node", str(MODULE / "app.test.js")],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload == {"ok": True, "scenarios": 21}

    print(json.dumps({
        "ok": True,
        "routingVersion": manifest["version"],
        "route": ROUTE,
        "decisionScenarios": 21,
        "hubToolCount": 40,
        "directStoreLinks": 0,
        "personalDataFields": 0,
        "browserStorage": False,
        "affiliateTripleGate": True,
        "multiCategoryBundle": True,
        "noBuyOutcomePreserved": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
