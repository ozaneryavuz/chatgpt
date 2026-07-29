from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGES = {
    "ev": ROOT / "alo186/hesaplama/ev-sarj-kablosu-saglik-gunlugu/index.html",
    "pv": ROOT / "alo186/hesaplama/ges-panel-temizlik-karar-gunlugu/index.html",
    "ground": ROOT / "alo186/hesaplama/topraklama-olcum-trend-gunlugu/index.html",
}
APPS = {key: path.with_name("app.js") for key, path in PAGES.items()}
ROUTES = {
    "ev": "/hesaplama/ev-sarj-kablosu-saglik-gunlugu/",
    "pv": "/hesaplama/ges-panel-temizlik-karar-gunlugu/",
    "ground": "/hesaplama/topraklama-olcum-trend-gunlugu/",
}


def read(path: Path) -> str:
    assert path.is_file(), path
    return path.read_text(encoding="utf-8")


def schema_types(html: str) -> set[str]:
    blocks = re.findall(r'<script\s+type="application/ld\+json">(.*?)</script>', html, re.S | re.I)
    assert blocks
    found: set[str] = set()
    for block in blocks:
        payload = json.loads(block)
        for item in payload.get("@graph", [payload]):
            value = item.get("@type") if isinstance(item, dict) else None
            if isinstance(value, str):
                found.add(value)
            elif isinstance(value, list):
                found.update(str(entry) for entry in value)
    return found


def test_pages() -> None:
    for key, path in PAGES.items():
        html = read(path); lower = html.lower()
        assert html.count("<h1") == 1, key
        assert f'https://www.alo186.com{ROUTES[key]}' in html, key
        assert {"WebApplication", "FAQPage", "BreadcrumbList"} <= schema_types(html), key
        assert "amazon.com.tr" not in lower and "amzn." not in lower, key
        assert '"@type":"product"' not in lower and '"@type":"offer"' not in lower, key
        assert APPS[key].is_file(), key
    assert "Reklam / satış ortaklığı açıklaması" in read(PAGES["ev"])
    assert "Reklam / satış ortaklığı" not in read(PAGES["pv"])
    assert "Reklam / satış ortaklığı" not in read(PAGES["ground"])


def test_ev_contract() -> None:
    combined = read(PAGES["ev"]) + read(APPS["ev"])
    for token in [
        "IEC 62196-1:2025", "IEC 62196-2:2025", "Tesla mobil konnektör kontrolü",
        "TTL=540*86400000", "MAX=18", "retentionMode:'per-record'",
        "cableType==='portable'", "purpose==='replacement'", "r.crosscheck",
        "Kullanımı durdur", "kategori=ev_cable", "Mevcut kabloyla devam edin",
    ]:
        assert token in combined, token
    assert "Sabit kablolu EVSE onarımı" in read(PAGES["ev"])


def test_pv_contract() -> None:
    combined = read(PAGES["pv"]) + read(APPS["pv"])
    for token in [
        "IEC 61724-1:2021", "IEA PVPS Soiling Fact Sheet 2025", "NREL yağmur/polen araştırması",
        "TTL=730*86400000", "MAX=24", "retentionMode:'per-record'", "affiliateLinks:0",
        "performance==='repeated'", "soiling==='heavy'", "Temizlik yapmayın",
        "/hesaplama/ges-aylik-uretim-saglik-gunlugu/", "takvim nedeniyle temizlik yapmayın",
    ]:
        assert token in combined, token
    lower = combined.lower()
    assert "fiyat, stok, puan" not in lower
    assert "evrensel temizlik periyodu" in lower


def test_ground_contract() -> None:
    combined = read(PAGES["ground"]) + read(APPS["ground"])
    for token in [
        "IEC 60364-6:2016", "IEC 61557-5:2019", "Fluke kazıksız çevrim yöntemi",
        "TTL=1095*86400000", "MAX=30", "retentionMode:'per-record'", "officialReport:false",
        "method==='stakeless'&&!r.bonded", "Evrensel tek ohm sınırı kullanılmadı",
        "kazıksız sonuç çevrim direncidir", "affiliateLinks:0",
    ]:
        assert token in combined, token
    assert "2026 sayfası 17 Temmuz 2026 itibarıyla ön yayımdır" in read(PAGES["ground"])


def test_overlay_and_pipeline() -> None:
    overlay = json.loads(read(ROOT / "alo186/deployment/routing-overlays/growth-trust-retention-run15.json"))
    assert overlay["version"] == 61
    actual = {item["canonicalPath"]: item["type"] for item in overlay["routes"]}
    assert actual == {ROUTES["ev"]: "calculator", ROUTES["pv"]: "calculator", ROUTES["ground"]: "business-tool"}
    trust = overlay["trust"]
    assert trust["rawPersonalDataCollected"] is False
    assert trust["directAffiliateLinksAdded"] == 0
    assert trust["unverifiedCommercialFieldsUsed"] == []
    assert trust["noBuyOutcomePreserved"] is True
    assert trust["affiliateDisclosureRequired"] is True
    assert trust["officialApprovalClaimed"] is False
    assert trust["emergencyCommerceClosed"] is True
    assert trust["rooftopCommerceClosed"] is True
    assert trust["professionalMeasurementOnly"] is True
    assert trust["evCableJournalTtlDays"] == 540
    assert trust["pvCleaningJournalTtlDays"] == 730
    assert trust["groundingJournalTtlDays"] == 1095

    injector = read(ROOT / "alo186/deployment/inject_growth_run15.py")
    for marker in [
        'data-alo186-growth-run15-tools="true"',
        'data-alo186-growth-run15-safety="true"',
        'data-alo186-growth-run15-affiliate="true"',
        'data-alo186-growth-run15-service="true"',
        '"directAffiliateLinksAdded": 0', '"rawPersonalDataCollected": False',
        '"unverifiedCommercialFieldsUsed": []', '"noBuyOutcomePreserved": True',
        '"officialApprovalClaimed": False', '"rooftopCommerceClosed": True',
        '"professionalMeasurementOnly": True', '"evCableJournalTtlDays": 540',
        '"pvCleaningJournalTtlDays": 730', '"groundingJournalTtlDays": 1095',
    ]:
        assert marker in injector, marker

    orchestrator = read(ROOT / "alo186/deployment/inject_shortlist_growth.py")
    assert "from inject_growth_run15 import run as run_growth_run15" in orchestrator
    assert "growth_run15 = run_growth_run15(site, base_path)" in orchestrator
    assert '"growthRun15": growth_run15' in orchestrator

    catalog = read(ROOT / "alo186/urun-eslestirme/catalog.js")
    assert "id:'ev_cable'" in catalog
    assert "affiliatePolicy:'after_tool'" in catalog
    assert "/hesaplama/ev-sarj-kablosu-uygunluk/" in catalog


if __name__ == "__main__":
    test_pages(); test_ev_contract(); test_pv_contract(); test_ground_contract(); test_overlay_and_pipeline()
    print("ALO186 growth run15 trust, retention, affiliate and professional measurement contracts: OK")
