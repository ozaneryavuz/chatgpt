from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HUB = ROOT / "kesinti-cihaz-surekliligi-karar-merkezi" / "index.html"
COMMERCE = ROOT / "amazon-elektrik-urunleri" / "index.html"
SITEMAP = ROOT / "sitemap-growth-v207.xml"
ROBOTS = ROOT / "robots.txt"
ROUTING = ROOT / "deployment" / "routing-overlays" / "207-discoverability-trust-hub.json"


def read(path: Path) -> str:
    assert path.is_file(), path
    return path.read_text(encoding="utf-8")


def json_ld_documents(html: str) -> list[dict]:
    documents: list[dict] = []
    for body in re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        flags=re.I | re.S,
    ):
        documents.append(json.loads(body))
    return documents


def graph_types(documents: list[dict]) -> set[str]:
    types: set[str] = set()
    for document in documents:
        nodes = document.get("@graph", [document])
        if isinstance(nodes, dict):
            nodes = [nodes]
        for node in nodes:
            value = node.get("@type")
            if isinstance(value, list):
                types.update(value)
            elif isinstance(value, str):
                types.add(value)
    return types


def test_decision_hub_is_apex_canonical_and_structured() -> None:
    html = read(HUB)
    assert '<link rel="canonical" href="https://alo186.com/kesinti-cihaz-surekliligi-karar-merkezi/">' in html
    assert "https://www.alo186.com" not in html
    assert {"CollectionPage", "ItemList", "FAQPage", "BreadcrumbList"}.issubset(
        graph_types(json_ld_documents(html))
    )
    assert '@media(max-width:860px)' in html


def test_decision_hub_is_fail_closed_and_no_buy_first() -> None:
    html = read(HUB)
    required = (
        "Ticari yol kapalı",
        "Mevcut düzen yeterli — yeni ürün almayın.",
        "Ürün yolundan önce kanıtı tamamlayın",
        "continuity_hub_risk_stop",
        "continuity_no_buy",
        "continuity_evidence_needed",
        "continuity_commerce_route_eligible",
        "ALO186; EDAŞ, TEDAŞ, 112",
        "Amazon satış ortaklığı ilişkisi bağlantıdan önce görünür",
    )
    for token in required:
        assert token in html, token
    for forbidden in (
        "https://www.amazon.",
        "tag=alo186rehber-21",
        "localStorage",
        "sessionStorage",
        "navigator.geolocation",
        "Product\"",
        "Offer\"",
        "AggregateRating\"",
    ):
        assert forbidden not in html, forbidden


def test_hub_routes_existing_calculators_selectors_and_repeat_tests() -> None:
    html = read(HUB)
    paths = (
        "/hesaplama/fiber-internet-modem-ont-mini-ups-calisma-suresi/",
        "/amazon-elektrik-urunleri/modem-ont-mini-ups-yedekleme-secici/",
        "/sektor-rehberi/internet-kesintisi-elektrik-mi-operator-mu-test-merkezi/",
        "/hesaplama/guvenlik-kamerasi-nvr-poe-ups-calisma-suresi/",
        "/amazon-elektrik-urunleri/nas-ups-usb-snmp-uygunluk-secici/",
        "/sektor-rehberi/alarm-sistemi-elektrik-kesintisi-30-90-gun-test-merkezi/",
        "/hesaplama/cpap-elektrik-kesintisi-batarya-calisma-suresi/",
        "/amazon-elektrik-urunleri/buzdolabi-dondurucu-kesinti-gida-guvenligi-secici/",
        "/sektor-rehberi/akvaryum-elektrik-kesintisi-30-90-gun-test-merkezi/",
    )
    for path in paths:
        assert path in html, path


def test_commerce_hub_uses_apex_and_discloses_before_visible_routes() -> None:
    html = read(COMMERCE)
    assert '<link rel="canonical" href="https://alo186.com/amazon-elektrik-urunleri/">' in html
    assert "https://www.alo186.com" not in html
    assert "/kesinti-cihaz-surekliligi-karar-merkezi/" in html
    assert "Mevcut sistem yeterliyse satın alma yok" in html
    assert "Aktif tehlikede satış yolu kapalı" in html
    disclosure = html.index('<div class="affiliate-disclosure">')
    visible_priority_section = html.index('<section class="section" aria-labelledby="priorityTitle">')
    assert disclosure < visible_priority_section
    assert {"CollectionPage", "ItemList", "FAQPage", "BreadcrumbList"}.issubset(
        graph_types(json_ld_documents(html))
    )


def test_growth_sitemap_is_valid_unique_and_resolves_to_sources() -> None:
    root = ET.fromstring(read(SITEMAP))
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locations = [node.text for node in root.findall("sm:url/sm:loc", namespace)]
    assert len(locations) >= 30
    assert len(locations) == len(set(locations))
    assert all(location and location.startswith("https://alo186.com/") for location in locations)
    assert "https://alo186.com/kesinti-cihaz-surekliligi-karar-merkezi/" in locations
    assert "https://alo186.com/amazon-elektrik-urunleri/" in locations

    for location in locations:
        relative = location.removeprefix("https://alo186.com/")
        if not relative:
            source = ROOT / "index.html"
        elif relative.endswith(".xml"):
            source = ROOT / relative
        elif relative.endswith("/"):
            source = ROOT / relative / "index.html"
        else:
            source = ROOT / relative / "index.html"
        assert source.is_file(), f"Missing sitemap source for {location}: {source}"


def test_robots_and_routing_publish_the_new_assets() -> None:
    robots = read(ROBOTS)
    assert "Sitemap: https://alo186.com/sitemap-growth-v207.xml" in robots
    routing = json.loads(read(ROUTING))
    assert routing["version"] == 207
    paths = {route["canonicalPath"] for route in routing["routes"]}
    assert {
        "/kesinti-cihaz-surekliligi-karar-merkezi/",
        "/amazon-elektrik-urunleri/",
        "/sitemap-growth-v207.xml",
    }.issubset(paths)
    trust = routing["trust"]
    assert trust["officialImpersonation"] is False
    assert trust["directAffiliateLinkOnDecisionHub"] is False
    assert trust["priceStockRatingWarrantyClaims"] is False
    assert trust["hazardCommerceClosed"] is True
    assert trust["noBuyWhenAdequate"] is True
    assert trust["personalDataCollected"] is False


def run() -> None:
    tests = [value for name, value in globals().items() if name.startswith("test_") and callable(value)]
    for test in sorted(tests, key=lambda item: item.__name__):
        test()
        print(f"PASS {test.__name__}")
    print(f"PASS {len(tests)} discoverability/trust growth checks")


if __name__ == "__main__":
    run()
