from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGES = {
    "damage": ROOT / "alo186/hesaplama/cihaz-hasari-basvuru-takibi/index.html",
    "home": ROOT / "alo186/hesaplama/ev-elektrik-guvenligi-kontrolu/index.html",
    "co": ROOT / "alo186/hesaplama/karbonmonoksit-alarmi-jenerator-guvenligi/index.html",
}
ROUTES = {
    "damage": "/hesaplama/cihaz-hasari-basvuru-takibi/",
    "home": "/hesaplama/ev-elektrik-guvenligi-kontrolu/",
    "co": "/hesaplama/karbonmonoksit-alarmi-jenerator-guvenligi/",
}


def read(path: Path) -> str:
    assert path.is_file(), path
    return path.read_text(encoding="utf-8")


def jsonld_types(html: str) -> set[str]:
    found: set[str] = set()
    blocks = re.findall(r'<script\s+type="application/ld\+json">(.*?)</script>', html, re.S | re.I)
    assert blocks
    for block in blocks:
        data = json.loads(block)
        nodes = data.get("@graph", [data])
        for node in nodes:
            value = node.get("@type") if isinstance(node, dict) else None
            if isinstance(value, str):
                found.add(value)
            elif isinstance(value, list):
                found.update(map(str, value))
    return found


def test_pages() -> None:
    for key, path in PAGES.items():
        html = read(path)
        lower = html.lower()
        assert html.count("<h1") == 1, key
        assert f"https://www.alo186.com{ROUTES[key]}" in html, key
        assert {"WebApplication", "FAQPage", "BreadcrumbList"} <= jsonld_types(html), key
        assert 'src="./app.js"' in html and path.with_name("app.js").is_file(), key
        assert "amazon.com" not in lower and "amzn." not in lower, key
        assert '"@type":"product"' not in lower and '"@type":"offer"' not in lower, key
        assert "adres" in lower and ("kişisel veri" in lower or "kişisel verisiz" in lower), key
        assert "alo186" in lower and ("edaş veya kamu kurumu değildir" in lower or "resmî" in lower or "resmi" in lower), key


def test_damage_contract() -> None:
    html = read(PAGES["damage"])
    app = read(PAGES["damage"].with_name("app.js"))
    lower = html.lower()
    assert "10 iş günü" in lower
    assert not re.search(r"\b30\s*gün\b", lower)
    for token in ["resmî tatilleri otomatik hesaplamaz", "hukuki danışmanlık vermez", "/edas-bul", "/hesaplama/kesinti-gunlugu/", "başvuru değildir"]:
        assert token in lower, token
    for token in ["addBusinessDays(event,10)", "officialHolidaysExcluded:false", "businessDayWindow:10", "officialApplication:false", "legalAdvice:false"]:
        assert token in app, token
    assert "localStorage" in app and "365*86400000" in app


def test_home_contract() -> None:
    html = read(PAGES["home"])
    app = read(PAGES["home"].with_name("app.js"))
    lower = html.lower()
    for token in ["sıcak", "cızırtı", "sigorta", "uzatma", "kaçak akım", "duman alarmı", "satın almama"]:
        assert token in lower, token
    assert "/hesaplama/elektrikci-is-emri-ozeti/" in html
    assert "/hesaplama/duman-alarmi-yerlesim-bakim-uygunluk/" in app
    assert "/hesaplama/acil-aydinlatma-sure-uygunluk/" in app
    assert "critical.length>0||technical.length>0||consumer.length===0" in app
    assert "ticari ve ürün yolları kapatıldı" in app.lower()
    assert "noBuyOutcome" in app and "reviewDays:180" in app


def test_co_contract() -> None:
    html = read(PAGES["co"])
    app = read(PAGES["co"].with_name("app.js"))
    lower = html.lower()
    for token in ["20 feet", "yaklaşık 6 metre", "co alarmı", "temiz havaya", "112", "kapalı alanda güvenli yapar mı"]:
        assert token in lower, token
    assert "/akilli-urun-secimi?kategori=co_alarm" in html
    assert "emergency||unsafeGenerator||!alarmGap" in app
    assert "affiliateAllowed:!emergency&&!unsafeGenerator&&alarmGap" in app
    assert "bütün affiliate ve ürün yönlendirmeleri bu sonuçta kapalıdır" in app.lower()
    assert "noBuyOutcome:!emergency&&!unsafeGenerator&&!alarmGap" in app


def test_catalog_gate() -> None:
    catalog = read(ROOT / "alo186/urun-eslestirme/catalog.js")
    app = read(ROOT / "alo186/urun-eslestirme/app.js")
    assert "id:'co_alarm'" in catalog
    assert "affiliatePolicy:'after_tool'" in catalog[catalog.index("id:'co_alarm'"):catalog.index("id:'co_alarm'") + 800]
    assert "karbonmonoksit-alarmi-jenerator-guvenligi" in catalog
    assert "EN 50291" in catalog and "co_alarm:[" in app
    assert "category:'co_alarm'" not in catalog, "Doğrulanmış ürün eklenmeden doğrudan ürün kartı açılmamalı"


def test_routing_and_injector() -> None:
    overlay = json.loads(read(ROOT / "alo186/deployment/routing-overlays/growth-damage-home-co-run9.json"))
    assert overlay["version"] == 52
    assert {item["canonicalPath"] for item in overlay["routes"]} == set(ROUTES.values())
    injector = read(ROOT / "alo186/deployment/inject_growth_run9.py")
    for token in [
        'data-alo186-growth-run9-tools="true"',
        'data-alo186-growth-run9-journey="true"',
        'data-alo186-growth-run9-affiliate="true"',
        'data-alo186-growth-run9-business="true"',
        '"rawPersonalDataCollected": False',
        '"directAffiliateLinksAdded": 0',
        '"unverifiedCommercialFieldsUsed": []',
        '"noBuyOutcomePreserved": True',
        '"deviceDamageWindowBusinessDays": 10',
        '"homeSafetyReviewDays": 180',
        '"coAlarmAffiliateGate": True',
        '"indoorGeneratorAffiliateBlocked": True',
    ]:
        assert token in injector, token
    orchestrator = read(ROOT / "alo186/deployment/inject_shortlist_growth.py")
    assert "from inject_growth_run9 import run as run_growth_run9" in orchestrator
    assert "growth_run9 = run_growth_run9(site, base_path)" in orchestrator
    assert '"growthRun9": growth_run9' in orchestrator


if __name__ == "__main__":
    test_pages()
    test_damage_contract()
    test_home_contract()
    test_co_contract()
    test_catalog_gate()
    test_routing_and_injector()
    print("ALO186 growth run9 contracts: OK")
