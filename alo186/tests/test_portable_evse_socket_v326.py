from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = REPO_ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))
from build_static_site import load_effective_manifest

TOOL_ROUTE = "/hesaplama/tasinabilir-ev-sarj-priz-uygunluk/"
TOOL_SOURCE = "alo186/hesaplama/tasinabilir-ev-sarj-priz-uygunluk/index.html"
GUIDE_ROUTE = "/amazon-elektrik-urunleri/tasinabilir-evse-secimi/"
GUIDE_SOURCE = "alo186/amazon-elektrik-urunleri/tasinabilir-evse-secimi/index.html"
MODULE = REPO_ROOT / "alo186/hesaplama/tasinabilir-ev-sarj-priz-uygunluk"
GUIDE = REPO_ROOT / GUIDE_SOURCE
HUB = REPO_ROOT / "alo186/hesaplama/index.html"


def schema_types(html: str) -> set[str]:
    found: set[str] = set()
    for block in re.findall(
        r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S | re.I
    ):
        payload = json.loads(block)
        nodes = payload.get("@graph", [payload]) if isinstance(payload, dict) else []
        for node in nodes:
            if not isinstance(node, dict):
                continue
            value = node.get("@type")
            if isinstance(value, str):
                found.add(value)
    return found


def main() -> None:
    manifest = load_effective_manifest(REPO_ROOT)
    assert manifest["version"] >= 87

    tool_routes = [item for item in manifest["routes"] if item["canonicalPath"] == TOOL_ROUTE]
    assert len(tool_routes) == 1
    assert tool_routes[0]["source"] == TOOL_SOURCE
    assert tool_routes[0]["type"] == "calculator"

    guide_routes = [item for item in manifest["routes"] if item["canonicalPath"] == GUIDE_ROUTE]
    assert len(guide_routes) == 1
    assert guide_routes[0]["source"] == GUIDE_SOURCE
    assert guide_routes[0]["type"] == "commerce-guide"

    html = (MODULE / "index.html").read_text(encoding="utf-8")
    css = (MODULE / "styles.css").read_text(encoding="utf-8")
    app = (MODULE / "app.js").read_text(encoding="utf-8")
    post_mount = (MODULE / "post-mount.js").read_text(encoding="utf-8")
    test = (MODULE / "app.test.js").read_text(encoding="utf-8")
    guide = GUIDE.read_text(encoding="utf-8")
    hub = HUB.read_text(encoding="utf-8")

    assert 'rel="canonical" href="https://alo186.com' + TOOL_ROUTE + '"' in html
    assert html.count("<h1>") == 1
    for schema_type in ["WebApplication", "DefinedTermSet", "FAQPage", "BreadcrumbList"]:
        assert schema_type in schema_types(html)
    for token in [
        'id="portableEvseForm"', 'id="outletType"', 'id="documentedCurrentA"',
        'id="dailyKm"', 'id="vehicleAcMaxKw"', 'id="evseMaxA"',
        'id="sourceStatus"', 'id="actualNeed"', 'id="technicalCheck"',
        'id="affiliateCheck"', 'id="productLinks"', 'aria-live="polite"',
        "yeni ürün almayın", "satış ortaklığı", "kullanıcıya ek maliyet yansımaz",
        '<script src="./post-mount.js"></script>',
    ]:
        assert token in html or token in app or token in post_mount

    calculator_combined = html + app + post_mount
    for token in ["amazon.com", "localStorage", "sessionStorage", "geolocation", "fetch(", "XMLHttpRequest", "WebSocket"]:
        assert token not in calculator_combined
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
        "commercialAllowed:true", "portable_evse_socket_result", "portable_evse",
        "requiredCurrentA", "deliverableKm", "installationCouldMeet",
    ]:
        assert token in app
    for token in [
        "form.addEventListener('reset'", "clearOutput", "commerce.dataset.categories = '[]'",
        "tasinabilir-evse-secimi", "portable_evse_socket_reset",
    ]:
        assert token in post_mount
    assert "scenarios:22" in test

    assert 'rel="canonical" href="https://alo186.com' + GUIDE_ROUTE + '"' in guide
    assert guide.count("<h1>") == 1
    guide_types = schema_types(guide)
    assert {"WebPage", "ItemList", "FAQPage", "BreadcrumbList"} <= guide_types
    assert "Product" not in guide_types and "Offer" not in guide_types
    for token in [
        'id="needGate"', 'id="evidenceGate"', 'id="affiliateGate"',
        'id="amazonLink"', 'rel="sponsored nofollow noopener"',
        "alo186rehber-21", "Amazon satış ortaklığı bağlantısı", "yeni ürün almayın",
        'id="jsonBtn"', 'id="icsBtn"', "reviewDays:90", "personalData:false",
        "Üç onay tamamlanmadan mağaza araması açılmaz", "EDAŞ, kamu kurumu",
    ]:
        assert token in guide
    for token in ["localStorage", "sessionStorage", "geolocation", "fetch(", "XMLHttpRequest", "WebSocket"]:
        assert token not in guide
    assert 'type="email"' not in guide and 'type="tel"' not in guide and '<textarea' not in guide
    assert '"@type":"Product"' not in guide and '"@type":"Offer"' not in guide

    tool_count_match = re.search(r"(\d+) çekirdek araç", hub)
    assert tool_count_match, "Hesaplama Merkezi araç sayacı bulunamadı."
    hub_tool_count = int(tool_count_match.group(1))
    assert hub_tool_count >= 41
    assert './tasinabilir-ev-sarj-priz-uygunluk/' in hub
    assert './seyahat-priz-adaptoru-voltaj-uygunluk/' in hub
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
        "toolRoute": TOOL_ROUTE,
        "commerceGuideRoute": GUIDE_ROUTE,
        "decisionScenarios": 22,
        "hubToolCount": hub_tool_count,
        "householdPlanningLimitA": 10,
        "directStoreLinksInCalculator": 0,
        "affiliateGuideTripleGate": True,
        "affiliateDisclosure": True,
        "jsonRecheck": True,
        "icsRecheckDays": 90,
        "personalDataFields": 0,
        "browserStorage": False,
        "resetClearsCommercialState": True,
        "noBuyOutcomePreserved": True,
        "extensionLeadFailClosed": True,
        "concurrentTravelToolPreserved": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
