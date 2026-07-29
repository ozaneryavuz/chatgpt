from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGES = {
    "extension": ROOT / "alo186/hesaplama/uzatma-kablosu-kablo-makarasi-uygunluk/index.html",
    "emergency": ROOT / "alo186/hesaplama/acil-aydinlatma-test-bakim-gunlugu/index.html",
    "voltage": ROOT / "alo186/hesaplama/gerilim-olayi-edas-olcum-talebi/index.html",
}
APPS = {key: path.with_name("app.js") for key, path in PAGES.items()}
ROUTES = {
    "extension": "/hesaplama/uzatma-kablosu-kablo-makarasi-uygunluk/",
    "emergency": "/hesaplama/acil-aydinlatma-test-bakim-gunlugu/",
    "voltage": "/hesaplama/gerilim-olayi-edas-olcum-talebi/",
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
        html = read(path)
        lower = html.lower()
        assert html.count("<h1") == 1, key
        assert f'https://www.alo186.com{ROUTES[key]}' in html, key
        assert {"WebApplication", "FAQPage", "BreadcrumbList"} <= schema_types(html), key
        assert "amazon.com" not in lower and "amzn." not in lower, key
        assert '"@type":"product"' not in lower and '"@type":"offer"' not in lower, key
        assert APPS[key].is_file(), key
    for key in ("extension", "emergency"):
        lower = read(PAGES[key]).lower()
        assert "fiyat, stok, puan" in lower or "fiyat, stok" in lower, key
    assert "adres, tesis adı" in read(PAGES["emergency"]).lower()
    assert "adres, abone/sayaç numarası" in read(PAGES["voltage"]).lower()


def test_extension_contract() -> None:
    html = read(PAGES["extension"])
    app = read(APPS["extension"])
    combined = html + app
    for token in [
        "IEC 60884-2-7:2025",
        "IEC 61242",
        "Reklam / satış ortaklığı açıklaması",
        "Mevcut ürün güvenli, hasarsız ve etiket sınırları içindeyse yeni ürün satın almayın",
        "type==='reel'&&!unwound",
        "purpose==='shopping'",
        "!hazard&&earth&&!motor",
        "dropPct>3",
        "ratio>.8",
        "kategori=extension_cord",
    ]:
        assert token in combined, token
    assert "Akım taşıma kapasitesi veya mevzuat uygunluğu yerine geçmez" in html


def test_emergency_lighting_contract() -> None:
    html = read(PAGES["emergency"])
    app = read(APPS["emergency"])
    combined = html + app
    for token in [
        "BS EN 50172:2024",
        "IEC 62034:2012",
        "IEC 60598-2-22:2021",
        "TTL=540*86400000",
        "MAX=18",
        "retentionMode:'per-record'",
        "İlk başarısızlık doğrudan ürün değişimi değildir",
        "Bakım sonrası yeniden test de başarısız",
        "x.system==='portable'&&x.purpose==='replacement'",
        "Sabit kaçış sistemi için bu yol açılmaz",
        "kategori=emergency_light",
    ]:
        assert token in combined, token
    assert "Mevcut süre yeterliyse yeni armatür gerekir mi?" in html


def test_voltage_contract() -> None:
    html = read(PAGES["voltage"])
    app = read(APPS["voltage"])
    combined = html + app
    for token in [
        "EDAŞ veya kamu kurumu değildir",
        "tuketici.epdk.gov.tr",
        "epdk.gov.tr",
        "TTL=365*86400000",
        "MAX=30",
        "retentionMode:'per-record'",
        "officialApplication:false",
        "Tekrarlayan ve geniş kapsamlı olay için resmî ölçüm talebi hazırlayın",
        "Olay yerel jeneratör/UPS kaynağında görünüyor",
        "Bir haftalık ölçüm sürecinde",
    ]:
        assert token in combined, token
    assert "Reklam / satış ortaklığı" not in html
    assert "amazon" not in html.lower()


def test_overlay_and_pipeline() -> None:
    overlay = json.loads(read(ROOT / "alo186/deployment/routing-overlays/growth-trust-revenue-run14.json"))
    assert overlay["version"] == 59
    actual = {item["canonicalPath"]: item["type"] for item in overlay["routes"]}
    assert actual == {
        ROUTES["extension"]: "calculator",
        ROUTES["emergency"]: "calculator",
        ROUTES["voltage"]: "business-tool",
    }
    trust = overlay["trust"]
    assert trust["rawPersonalDataCollected"] is False
    assert trust["directAffiliateLinksAdded"] == 0
    assert trust["unverifiedCommercialFieldsUsed"] == []
    assert trust["noBuyOutcomePreserved"] is True
    assert trust["affiliateDisclosureRequired"] is True
    assert trust["officialApprovalClaimed"] is False
    assert trust["emergencyCommerceClosed"] is True
    assert trust["emergencyLightingJournalTtlDays"] == 540
    assert trust["voltageEventJournalTtlDays"] == 365

    injector = read(ROOT / "alo186/deployment/inject_growth_run14.py")
    for marker in [
        'data-alo186-growth-run14-tools="true"',
        'data-alo186-growth-run14-official="true"',
        'data-alo186-growth-run14-affiliate="true"',
        'data-alo186-growth-run14-service="true"',
        '"directAffiliateLinksAdded": 0',
        '"rawPersonalDataCollected": False',
        '"unverifiedCommercialFieldsUsed": []',
        '"noBuyOutcomePreserved": True',
        '"officialApprovalClaimed": False',
        '"emergencyCommerceClosed": True',
        '"emergencyLightingJournalTtlDays": 540',
        '"voltageEventJournalTtlDays": 365',
    ]:
        assert marker in injector, marker

    orchestrator = read(ROOT / "alo186/deployment/inject_shortlist_growth.py")
    assert "from inject_growth_run14 import run as run_growth_run14" in orchestrator
    assert "growth_run14 = run_growth_run14(site, base_path)" in orchestrator
    assert '"growthRun14": growth_run14' in orchestrator

    catalog = read(ROOT / "alo186/urun-eslestirme/catalog.js")
    assert "id:'extension_cord'" in catalog
    assert "affiliatePolicy:'after_tool'" in catalog
    assert ROUTES["extension"] in catalog


if __name__ == "__main__":
    test_pages()
    test_extension_contract()
    test_emergency_lighting_contract()
    test_voltage_contract()
    test_overlay_and_pipeline()
    print("ALO186 growth run14 trust, retention, affiliate and official handoff contracts: OK")
