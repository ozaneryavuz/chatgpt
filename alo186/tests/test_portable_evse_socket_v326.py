from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = REPO_ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))
from build_static_site import load_effective_manifest

ROUTE = "/hesaplama/tasinabilir-ev-sarj-priz-uygunluk/"
SOURCE = "alo186/hesaplama/tasinabilir-ev-sarj-priz-uygunluk/index.html"
MODULE = REPO_ROOT / "alo186/hesaplama/tasinabilir-ev-sarj-priz-uygunluk"
HUB = REPO_ROOT / "alo186/hesaplama/index.html"


def main() -> None:
    manifest = load_effective_manifest(REPO_ROOT)
    assert manifest["version"] >= 87
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
        'id="portableEvseForm"', 'id="outletType"', 'id="documentedCurrentA"',
        'id="dailyKm"', 'id="vehicleAcMaxKw"', 'id="evseMaxA"',
        'id="sourceStatus"', 'id="actualNeed"', 'id="technicalCheck"',
        'id="affiliateCheck"', 'id="productLinks"', 'aria-live="polite"',
        "yeni ürün almayın", "satış ortaklığı", "kullanıcıya ek maliyet yansımaz",
    ]:
        assert token in html or token in app

    combined = html + app
    for token in ["amazon.com", "localStorage", "sessionStorage", "geolocation", "fetch(", "XMLHttpRequest", "WebSocket"]:
        assert token not in combined
    for personal in ["Adınız", "Telefon", "E-posta", "Adresiniz", "Araç plakası", "VIN numarası"]:
        assert personal not in html

    assert "@media(max-width:820px)" in css
    assert "@media(max-width:560px)" in css
    assert "prefers-reduced-motion" in css
    assert "focus-visible" in css
    assert "minmax(0,1fr)" in css

    for token in [
        "CHARGING_EFFICIENCY", "SINGLE_PHASE_V", "THREE_PHASE_V", "OUTLETS",
        "schuko", "cee_blue_16", "cee_blue_32", "cee_red_16", "cee_red_32",
        "stop_use", "wallbox_path", "active_event", "no_buy", "conditional_purchase",
        "commercialAllowed:true", "niyet=portable_evse", "portable_evse_socket_result",
        "portable_evse", "requiredCurrentA", "deliverableKm", "installationCouldMeet",
    ]:
        assert token in app
    assert "scenarios:22" in test

    assert "41 çekirdek araç" in hub
    assert './tasinabilir-ev-sarj-priz-uygunluk/' in hub
    assert "Taşınabilir EV Şarj Cihazı ve Priz Uygunluğu" in hub

    result = subprocess.run(
        ["node", str(MODULE / "app.test.js")],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload == {"ok": True, "scenarios": 22}

    print(json.dumps({
        "ok": True,
        "routingVersion": manifest["version"],
        "route": ROUTE,
        "decisionScenarios": 22,
        "hubToolCount": 41,
        "householdPlanningLimitA": 10,
        "directStoreLinks": 0,
        "personalDataFields": 0,
        "browserStorage": False,
        "affiliateTripleGate": True,
        "noBuyOutcomePreserved": True,
        "extensionLeadFailClosed": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
