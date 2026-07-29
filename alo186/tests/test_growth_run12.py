from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGES = {
    "outage": ROOT / "alo186/hesaplama/elektrik-kesintisi-dayaniklilik-plani/index.html",
    "rcd": ROOT / "alo186/hesaplama/kacak-akim-rolesi-olay-gunlugu/index.html",
    "pv": ROOT / "alo186/hesaplama/ges-aylik-uretim-saglik-gunlugu/index.html",
}
ROUTES = {
    "outage": "/hesaplama/elektrik-kesintisi-dayaniklilik-plani/",
    "rcd": "/hesaplama/kacak-akim-rolesi-olay-gunlugu/",
    "pv": "/hesaplama/ges-aylik-uretim-saglik-gunlugu/",
}


def read(path: Path) -> str:
    assert path.is_file(), path
    return path.read_text(encoding="utf-8")


def jsonld(html: str) -> set[str]:
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
        assert {"WebApplication", "FAQPage", "BreadcrumbList"} <= jsonld(html), key
        assert '<script src="./app.js"></script>' in html, key
        assert "amazon.com" not in lower and "amzn." not in lower, key
        assert '"@type":"product"' not in lower and '"@type":"offer"' not in lower, key
        assert "fiyat" in lower and ("stok" in lower or key in {"rcd", "pv"}), key
        assert "kişisel veri" in lower or "kişisel verisiz" in lower, key
        assert "resmî" in lower or "resmi" in lower, key
        assert "satın al" in lower or "ürün yönlendirmesi yok" in lower, key
        assert "URL.createObjectURL" in app, key


def test_outage_contract() -> None:
    html = read(PAGES["outage"])
    app = read(PAGES["outage"].with_name("app.js"))
    combined = html + app
    for token in [
        "medicalCritical",
        "affiliateShown",
        "priceStockRatingWarrantyUsed:false",
        "/amazon-elektrik-urunleri/modem-mini-ups-secimi",
        "/amazon-elektrik-urunleri/tasinabilir-guc-istasyonu-secimi",
        "Reklam / satış ortaklığı açıklaması",
        "112",
        "Mevcut yedeklerim yeterli mi?",
    ]:
        assert token in combined, token
    assert "Tıbbi veya yaşam destek cihazı için tüketici ürünü önerilmez" in app
    assert "showCommercial=false" in app


def test_rcd_contract() -> None:
    html = read(PAGES["rcd"])
    app = read(PAGES["rcd"].with_name("app.js"))
    combined = html + app
    for token in [
        "alo186.rcdEventJournal.v1",
        "TTL=365*86400000",
        "MAX=20",
        "retentionMode:'per-record'",
        "Elektrik çarpması",
        "Devreyi zorlamayın",
        "/hesaplama/elektrikci-is-emri-ozeti/",
        "Ticari yönlendirme",
    ]:
        assert token in combined, token
    assert "Amazon" not in html and "affiliate" not in html.lower()
    assert "localStorage" in app


def test_pv_contract() -> None:
    html = read(PAGES["pv"])
    app = read(PAGES["pv"].with_name("app.js"))
    combined = html + app
    for token in [
        "alo186.pvMonthlyHealth.v1",
        "TTL=730*86400000",
        "MAX=24",
        "retentionMode:'per-record'",
        "incomeEstimate:false",
        "kWh/kWp",
        "Tekrarlayan doğrulanmış düşüş",
        "/haberler/ges-string-akimi-dusuk-mppt-uretim-farki",
        "/hizmetler/ges-batarya-ev-sarj-fizibilitesi/",
        "nrel.gov",
    ]:
        assert token in combined, token
    assert "Amazon" not in html and "affiliate" not in html.lower()


def test_pipeline() -> None:
    overlay = json.loads(read(ROOT / "alo186/deployment/routing-overlays/growth-resilience-diagnostics-run12.json"))
    assert overlay["version"] == 55
    assert {item["canonicalPath"] for item in overlay["routes"]} == set(ROUTES.values())
    assert overlay["trust"]["directAffiliateLinksAdded"] == 0
    assert overlay["trust"]["unverifiedCommercialFieldsUsed"] == []
    injector = read(ROOT / "alo186/deployment/inject_growth_run12.py")
    for marker in [
        'data-alo186-growth-run12-tools="true"',
        'data-alo186-growth-run12-journey="true"',
        'data-alo186-growth-run12-affiliate="true"',
        'data-alo186-growth-run12-service="true"',
        '"rawPersonalDataCollected": False',
        '"directAffiliateLinksAdded": 0',
        '"noBuyOutcomePreserved": True',
        '"emergencyCommerceClosed": True',
        '"rcdJournalTtlDays": 365',
        '"pvJournalTtlDays": 730',
    ]:
        assert marker in injector, marker
    orchestrator = read(ROOT / "alo186/deployment/inject_shortlist_growth.py")
    assert "from inject_growth_run12 import run as run_growth_run12" in orchestrator
    assert "growth_run12 = run_growth_run12(site, base_path)" in orchestrator
    assert '"growthRun12": growth_run12' in orchestrator


if __name__ == "__main__":
    test_pages()
    test_outage_contract()
    test_rcd_contract()
    test_pv_contract()
    test_pipeline()
    print("ALO186 growth run12 contracts: OK")
