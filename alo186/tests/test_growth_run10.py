from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGES = {
    "ev_cable": ROOT / "alo186/amazon-elektrik-urunleri/type-2-ev-sarj-kablosu-secimi/index.html",
    "ups_battery": ROOT / "alo186/amazon-elektrik-urunleri/ups-yedek-akusu-kartus-secimi/index.html",
    "outlet_tester": ROOT / "alo186/amazon-elektrik-urunleri/priz-rcd-test-cihazi-secimi/index.html",
}
ROUTES = {
    "ev_cable": "/amazon-elektrik-urunleri/type-2-ev-sarj-kablosu-secimi",
    "ups_battery": "/amazon-elektrik-urunleri/ups-yedek-akusu-kartus-secimi",
    "outlet_tester": "/amazon-elektrik-urunleri/priz-rcd-test-cihazi-secimi",
}


def read(path: Path) -> str:
    assert path.is_file(), path
    return path.read_text(encoding="utf-8")


def jsonld(html: str) -> list[dict]:
    blocks = re.findall(r'<script\s+type="application/ld\+json">(.*?)</script>', html, re.S | re.I)
    assert blocks
    return [json.loads(block) for block in blocks]


def schema_types(graphs: list[dict]) -> set[str]:
    found: set[str] = set()
    for graph in graphs:
        for node in graph.get("@graph", [graph]):
            value = node.get("@type") if isinstance(node, dict) else None
            if isinstance(value, str):
                found.add(value)
            elif isinstance(value, list):
                found.update(str(item) for item in value)
    return found


def test_common_pages() -> None:
    for key, path in PAGES.items():
        html = read(path)
        lower = html.lower()
        assert html.count("<h1") == 1, key
        assert f'https://www.alo186.com{ROUTES[key]}' in html, key
        assert {"Article", "FAQPage", "BreadcrumbList"} <= schema_types(jsonld(html)), key
        assert '"@type":"Product"'.lower() not in lower, key
        assert '"@type":"Offer"'.lower() not in lower, key
        assert "amazon.com" not in lower and "amzn." not in lower, key
        assert "fiyat, stok" in lower, key
        assert "satın almama" in lower or "satın alma" in lower, key
        assert "alo186" in lower and ("resmî" in lower or "resmi" in lower), key
        assert "29 temmuz 2026" in lower, key
        assert html.count("<details>") >= 4, key


def test_ev_cable_funnel() -> None:
    html = read(PAGES["ev_cable"])
    lower = html.lower()
    for token in [
        'data-category="ev_cable"',
        "/hesaplama/ev-sarj-kablosu-uygunluk/",
        "/akilli-urun-secimi?kategori=ev_cable",
        "amazon satış ortaklığı",
        "iec 62196-2:2025",
        "webstore.iec.ch/en/publication/86317",
        "onboard charger",
        "16 a / 32 a",
    ]:
        assert token.lower() in lower, token
    assert "doğrudan ürün önermiyor" in lower


def test_professional_only_funnels() -> None:
    ups = read(PAGES["ups_battery"]).lower()
    outlet = read(PAGES["outlet_tester"]).lower()
    for token in [
        'data-category="ups_battery"',
        "/hesaplama/yedek-guc-runtime-saglik-gunlugu/",
        "/akilli-urun-secimi?kategori=ups_battery",
        "doğrudan amazon veya mağaza bağlantısı içermez",
        "eski-yeni",
        "fa156530",
        "fa317828",
    ]:
        assert token in ups, token
    for token in [
        'data-category="outlet_tester"',
        "/haberler/kacak-akim-rolesi-acma-suresi-rampa-testi-nasil-olculur",
        "/akilli-urun-secimi?kategori=outlet_tester",
        "profesyonel-only",
        "doğrudan amazon veya mağaza bağlantısı içermez",
        "iec 61557-6:2019",
        "megger.com/tr/urun/rcd-ve-cevrim-testi",
        "fluke.com/en/product/electrical-testing/installation-testers/fluke-1662",
    ]:
        assert token in outlet, token


def test_pipeline_contract() -> None:
    injector = read(ROOT / "alo186/deployment/inject_growth_run10.py")
    orchestrator = read(ROOT / "alo186/deployment/inject_shortlist_growth.py")
    overlay = json.loads(read(ROOT / "alo186/deployment/routing-overlays/growth-commercial-intent-run10.json"))
    assert overlay["version"] == 53
    assert {item["canonicalPath"] for item in overlay["routes"]} == set(ROUTES.values())
    assert overlay["trust"]["directAffiliateLinksAdded"] == 0
    assert overlay["trust"]["professionalOnlyCategories"] == ["ups_battery", "outlet_tester"]
    for token in [
        '"directAffiliateLinksAdded": 0',
        '"qualifiedAffiliateCategories": ["ev_cable"]',
        '"professionalOnlyCategories": ["ups_battery", "outlet_tester"]',
        '"unverifiedCommercialFieldsUsed": []',
        '"noBuyOutcomePreserved": True',
        '"officialApprovalClaimed": False',
        "10 özel rehber",
        "append_search",
        "append_sitemap",
    ]:
        assert token in injector, token
    assert "from inject_growth_run10 import run as run_growth_run10" in orchestrator
    assert "growth_run10 = run_growth_run10(site, base_path)" in orchestrator
    assert '"growthRun10": growth_run10' in orchestrator


if __name__ == "__main__":
    test_common_pages()
    test_ev_cable_funnel()
    test_professional_only_funnels()
    test_pipeline_contract()
    print("ALO186 growth run10 commercial intent and trust contracts: OK")
