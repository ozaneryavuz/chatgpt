from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGES = {
    "damage": ROOT / "alo186/hesaplama/elektrik-cihaz-hasari-edas-basvuru-paketi/index.html",
    "energy": ROOT / "alo186/hesaplama/akilli-priz-enerji-anomali-gunlugu/index.html",
    "surge": ROOT / "alo186/hesaplama/akim-korumali-grup-priz-saglik-gunlugu/index.html",
}
ROUTES = {
    "damage": "/hesaplama/elektrik-cihaz-hasari-edas-basvuru-paketi/",
    "energy": "/hesaplama/akilli-priz-enerji-anomali-gunlugu/",
    "surge": "/hesaplama/akim-korumali-grup-priz-saglik-gunlugu/",
}


def read(path: Path) -> str:
    assert path.is_file(), path
    return path.read_text(encoding="utf-8")


def schema_types(html: str) -> set[str]:
    found: set[str] = set()
    for raw in re.findall(r'<script\s+type="application/ld\+json">(.*?)</script>', html, re.S | re.I):
        data = json.loads(raw)
        for node in data.get("@graph", [data]):
            value = node.get("@type") if isinstance(node, dict) else None
            if isinstance(value, str):
                found.add(value)
            elif isinstance(value, list):
                found.update(str(item) for item in value)
    return found


def test_pages() -> None:
    for key, page in PAGES.items():
        html = read(page)
        lower = html.lower()
        app = read(page.with_name("app.js"))
        assert html.count("<h1") == 1, key
        assert f"https://www.alo186.com{ROUTES[key]}" in html, key
        assert {"WebApplication", "FAQPage", "BreadcrumbList"} <= schema_types(html), key
        assert '<script src="./app.js"></script>' in html, key
        assert "amazon.com" not in lower and "amzn." not in lower, key
        assert '"@type":"product"' not in lower and '"@type":"offer"' not in lower, key
        assert "kişisel veri" in lower or "kişisel verisiz" in lower, key
        assert "bağımsız" in lower, key
        assert "url.createobjecturl" in app.lower(), key
    assert "Affiliate veya ürün satış bağlantısı içermez" in read(PAGES["damage"])
    assert "Reklam / satış ortaklığı açıklaması" in read(PAGES["energy"])
    assert "Reklam / satış ortaklığı açıklaması" in read(PAGES["surge"])


def test_damage_contract() -> None:
    html = read(PAGES["damage"])
    app = read(PAGES["damage"].with_name("app.js"))
    combined = html + app
    for token in [
        "10 iş günü",
        "deviceDamageApplicationPack.v1",
        "deadlineEstimateExcludesPublicHolidays:true",
        "officialDecision:false",
        "compensationEstimate:false",
        "affiliateLinks:false",
        "/elektrik-kesintisi/",
        "tuketici.epdk.gov.tr",
    ]:
        assert token in combined, token
    assert "30 gün" not in combined
    assert "Fiyat" not in html and "stok" not in html.lower()


def test_energy_contract() -> None:
    html = read(PAGES["energy"])
    app = read(PAGES["energy"].with_name("app.js"))
    combined = html + app
    for token in [
        "alo186.smartPlugEnergyJournal.v1",
        "TTL=730*86400000",
        "MAX=24",
        "retentionMode:'per-record'",
        "latest.avgW<=500",
        "['motor','heater'].includes",
        "Mevcut ölçüm aracınız güvenli ve ihtiyacı karşılıyorsa yeni ürün satın almayın",
        "/amazon-elektrik-urunleri/akilli-priz-enerji-olcer-secimi",
        "IEC 60884-3-2:2026",
    ]:
        assert token in combined, token
    assert "showCommercial=!danger&&!restricted" in app
    assert "fiyat, stok, puan, satıcı" in html.lower()


def test_surge_contract() -> None:
    html = read(PAGES["surge"])
    app = read(PAGES["surge"].with_name("app.js"))
    combined = html + app
    for token in [
        "alo186.surgeStripHealth.v1",
        "TTL=540*86400000",
        "MAX=12",
        "retentionMode:'per-record'",
        "!groundFault&&!breakerFault&&!highLoad",
        "Affiliate ve yeni ürün yönlendirmesi bu sonuçta kapalıdır",
        "Mevcut ürünle devam",
        "/amazon-elektrik-urunleri/akim-korumali-grup-priz-secimi",
        "ul.com/insights/guide-power-strips-and-surge-protectors",
    ]:
        assert token in combined, token
    assert "Üç yılda bir bütün grup prizler değiştirilmeli mi?" in html
    assert "Evrensel bir süre kullanılmaz" in html


def test_pipeline() -> None:
    overlay = json.loads(read(ROOT / "alo186/deployment/routing-overlays/growth-trust-revenue-run13.json"))
    assert overlay["version"] == 57
    assert {item["canonicalPath"] for item in overlay["routes"]} == set(ROUTES.values())
    assert overlay["trust"]["directAffiliateLinksAdded"] == 0
    assert overlay["trust"]["unverifiedCommercialFieldsUsed"] == []
    assert overlay["trust"]["deviceDamageDeadlineBusinessDays"] == 10
    injector = read(ROOT / "alo186/deployment/inject_growth_run13.py")
    for marker in [
        'data-alo186-growth-run13-tools="true"',
        'data-alo186-growth-run13-official="true"',
        'data-alo186-growth-run13-affiliate="true"',
        'data-alo186-growth-run13-service="true"',
        '"rawPersonalDataCollected": False',
        '"directAffiliateLinksAdded": 0',
        '"noBuyOutcomePreserved": True',
        '"emergencyCommerceClosed": True',
        '"deviceDamageDeadlineBusinessDays": 10',
        '"smartPlugJournalTtlDays": 730',
        '"surgeStripJournalTtlDays": 540',
    ]:
        assert marker in injector, marker
    orchestrator = read(ROOT / "alo186/deployment/inject_shortlist_growth.py")
    assert "from inject_growth_run13 import run as run_growth_run13" in orchestrator
    assert "growth_run13 = run_growth_run13(site, base_path)" in orchestrator
    assert '"growthRun13": growth_run13' in orchestrator


if __name__ == "__main__":
    test_pages()
    test_damage_contract()
    test_energy_contract()
    test_surge_contract()
    test_pipeline()
    print("ALO186 growth run13 contracts: OK")
