from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGES = {
    "solar": ROOT / "alo186/hesaplama/power-station-gunes-paneli-uygunluk/index.html",
    "alarm": ROOT / "alo186/hesaplama/duman-co-alarmi-bakim-gunlugu/index.html",
    "ats": ROOT / "alo186/hesaplama/jenerator-ats-test-gunlugu/index.html",
}
ROUTES = {
    "solar": "/hesaplama/power-station-gunes-paneli-uygunluk/",
    "alarm": "/hesaplama/duman-co-alarmi-bakim-gunlugu/",
    "ats": "/hesaplama/jenerator-ats-test-gunlugu/",
}


def read(path: Path) -> str:
    assert path.is_file(), path
    return path.read_text(encoding="utf-8")


def jsonld(html: str) -> list[dict]:
    blocks = re.findall(r'<script\s+type="application/ld\+json">(.*?)</script>', html, re.S | re.I)
    assert blocks
    return [json.loads(block) for block in blocks]


def schema_types(graphs: list[dict]) -> set[str]:
    result: set[str] = set()
    for graph in graphs:
        for node in graph.get("@graph", [graph]):
            value = node.get("@type") if isinstance(node, dict) else None
            if isinstance(value, str): result.add(value)
            elif isinstance(value, list): result.update(map(str, value))
    return result


def test_pages() -> None:
    for key, path in PAGES.items():
        html = read(path); lower = html.lower(); app = read(path.with_name("app.js")); combined_lower = (html + app).lower()
        assert html.count("<h1") == 1, key
        assert f'https://www.alo186.com{ROUTES[key]}' in html, key
        assert {"WebApplication", "FAQPage", "BreadcrumbList"} <= schema_types(jsonld(html)), key
        assert '<script src="./app.js"></script>' in html, key
        assert "amazon.com" not in lower and "amzn." not in lower, key
        assert '"@type":"product"' not in lower and '"@type":"offer"' not in lower, key
        if key in {"solar", "alarm"}:
            for field in ("fiyat", "stok", "puan", "garanti"):
                assert field in combined_lower, (key, field)
        assert "resmî" in lower or "resmi" in lower or "üretici onayı" in lower, key
        assert "satın almayın" in combined_lower or "satın alma" in combined_lower, key


def test_solar_gate() -> None:
    html = read(PAGES["solar"]); app = read(PAGES["solar"].with_name("app.js")); combined = html + app
    for token in [
        "arrayVoc=v.voc*v.series", "arrayIsc=v.isc*v.parallel", "arrayW=v.pmax*v.series*v.parallel",
        "!v.manual", "!v.connector", "!v.cold", "arrayVoc>=v.maxV*.9", "v.purpose==='buy'",
        "commercialRouteOpened:commercial", "officialApproval:false", "priceStockRatingWarrantyUsed:false",
        "Reklam / satış ortaklığı açıklaması", "Mevcut panel/dizi ihtiyacınızı karşılıyorsa yeni ürün satın almayın",
        "faq.jackery.com",
    ]:
        assert token in combined, token
    assert "/amazon-elektrik-urunleri/ges-malzemeleri-secimi" in html


def test_alarm_journal() -> None:
    html = read(PAGES["alarm"]); app = read(PAGES["alarm"].with_name("app.js")); combined = html + app
    for token in [
        "alo186.alarmMaintenanceJournal.v1", "TTL=400*86400000", "MAX=24",
        "expiresAt:new Date(now+TTL).toISOString()", "entry.emergency", "112",
        "entry.testResult==='fail'&&!entry.retested", "entry.testResult==='fail'&&entry.retested",
        "commercial=false", "commercial=true", "smoke_alarm", "co_alarm",
        "retentionDays:400", "30 günlük test hatırlatması", "usfa.fema.gov", "cpsc.gov",
    ]:
        assert token in combined, token
    assert "sayfayı ziyaret etmek eski kayıtların süresini uzatmaz" in html.lower()


def test_generator_journal() -> None:
    html = read(PAGES["ats"]); app = read(PAGES["ats"].with_name("app.js")); combined = html + app
    for token in [
        "alo186.generatorAtsJournal.v1", "TTL=540*86400000", "MAX=18",
        "e.mode==='exercise'", "Jeneratörün başlaması yük transferini kanıtlamaz",
        "e.hazard", "112", "service=true", "service=false", "retentionDays:540",
        "/hizmetler/elektrik-surekliligi-izleme/", "se.com", "support.generac.com",
    ]:
        assert token in combined, token
    assert "amazon" not in combined.lower()
    assert "yeni ats, jeneratör veya kontrolör satın almayın" in combined.lower()


def test_overlay_and_pipeline() -> None:
    overlay = json.loads(read(ROOT / "alo186/deployment/routing-overlays/growth-trust-retention-run11.json"))
    assert overlay["version"] == 54
    assert {item["canonicalPath"] for item in overlay["routes"]} == set(ROUTES.values())
    assert overlay["trust"]["directAffiliateLinksAdded"] == 0
    assert overlay["trust"]["unverifiedCommercialFieldsUsed"] == []
    assert overlay["trust"]["noBuyOutcomePreserved"] is True
    assert overlay["trust"]["emergencyCommerceClosed"] is True
    injector = read(ROOT / "alo186/deployment/inject_growth_run11.py")
    for token in [
        'data-alo186-growth-run11-tools="true"',
        'data-alo186-growth-run11-journey="true"',
        'data-alo186-growth-run11-product-gates="true"',
        'data-alo186-growth-run11-service="true"',
        '"rawPersonalDataCollected": False',
        '"directAffiliateLinksAdded": 0',
        '"unverifiedCommercialFieldsUsed": []',
        '"noBuyOutcomePreserved": True',
        '"officialApprovalClaimed": False',
        '"emergencyCommerceClosed": True',
        '"alarmJournalTtlDays": 400',
        '"generatorAtsJournalTtlDays": 540',
    ]:
        assert token in injector, token
    orchestrator = read(ROOT / "alo186/deployment/inject_shortlist_growth.py")
    assert "from inject_growth_run11 import run as run_growth_run11" in orchestrator
    assert "growth_run11 = run_growth_run11(site, base_path)" in orchestrator
    assert '"growthRun11": growth_run11' in orchestrator


if __name__ == "__main__":
    test_pages(); test_solar_gate(); test_alarm_journal(); test_generator_journal(); test_overlay_and_pipeline()
    print("ALO186 growth run11 trust, retention and conversion contracts: OK")
