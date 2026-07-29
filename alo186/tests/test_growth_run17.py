from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

from build_static_site import load_effective_manifest  # noqa: E402

ROUTES = {
    "mode2": "/hesaplama/tasinabilir-ev-sarj-cihazi-priz-uygunluk/",
    "mini": "/hesaplama/modem-ont-mini-ups-sure-saglik-gunlugu/",
    "voltage": "/hesaplama/priz-tipi-gerilim-monitoru-uygunluk/",
}
PAGES = {key: ROOT / "alo186" / route.strip("/") / "index.html" for key, route in ROUTES.items()}
APPS = {key: path.with_name("app.js") for key, path in PAGES.items()}


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
            if not isinstance(item, dict):
                continue
            value = item.get("@type")
            if isinstance(value, str):
                found.add(value)
            elif isinstance(value, list):
                found.update(str(entry) for entry in value)
    return found


def test_pages() -> None:
    for key, page in PAGES.items():
        html = read(page)
        lower = html.casefold()
        assert html.count("<h1") == 1, key
        assert f'https://www.alo186.com{ROUTES[key]}' in html, key
        assert {"WebApplication", "FAQPage", "BreadcrumbList"} <= schema_types(html), key
        assert "amazon.com.tr" not in lower and "amzn." not in lower, key
        assert '"@type":"product"' not in lower and '"@type":"offer"' not in lower, key
        assert not any(token in lower for token in ["güncel fiyat", "stokta", "kullanıcı puanı", "garanti süresi"]), key
        assert APPS[key].is_file(), key
    assert "Affiliate sınırı" in read(PAGES["mode2"])
    assert "mağaza veya satış ortaklığı bağlantısı bulunmaz" in read(PAGES["mode2"])
    assert "Affiliate sınırı" in read(PAGES["voltage"])
    assert "mağaza veya satış ortaklığı bağlantısı göstermez" in read(PAGES["voltage"])
    assert "Reklam / satış ortaklığı açıklaması" in read(PAGES["mini"])


def test_mode2_contract() -> None:
    combined = read(PAGES["mode2"]) + read(APPS["mode2"])
    for token in [
        "IEC 62752:2024",
        "TTL=540*86400000",
        "MAX=18",
        "retentionMode:'per-record'",
        "directAffiliateLinks:false",
        "Tehlike sürerken ticari veya ücretli yönlendirme gösterilmez",
        "service=false",
        "$('service').classList.toggle('hidden',!out.service)",
        "useCase==='daily'",
        "currentClass==='high'",
        "Seyrek kullanım senaryosu için kurulum kanıtları büyük ölçüde tamam",
        "Bu araçta affiliate veya mağaza yönlendirmesi açılmaz",
    ]:
        assert token in combined, token
    assert "kategori=ev_mobile_charger" not in combined
    assert "commercial=true" not in combined


def test_mini_ups_contract() -> None:
    combined = read(PAGES["mini"]) + read(APPS["mini"])
    for token in [
        "TTL=730*86400000",
        "MAX=24",
        "retentionMode:'per-record'",
        "function comparablePrior",
        "testTime(r)<currentTime",
        "Number(r.target)===Number(current.target)",
        "priorFailed",
        "Karşılaştırılabilir ilk kayıt eksik",
        "Tek yeni düşüş affiliate veya değişim kararı açmaz",
        "İki karşılaştırılabilir testte hedef süre sağlanamadı",
        "r.stage==='retest'&&failed(r)&&priorFailed",
        "if(r.purpose==='replacement'){commercial=true",
        "if(r.hazard)",
        "Tehlike sürerken affiliate yolu kapalıdır",
    ]:
        assert token in combined, token
    assert combined.index("if(r.hazard)") < combined.index("commercial=true")
    assert "officialRecord:false" in combined


def test_voltage_contract() -> None:
    combined = read(PAGES["voltage"]) + read(APPS["voltage"])
    for token in [
        "IEC 61000‑4‑30:2025",
        "EPDK elektrik piyasası yönetmelikleri",
        "TTL=365*86400000",
        "MAX=30",
        "retentionMode:'per-record'",
        "directAffiliateLinks:false",
        "officialGoal",
        "sharedGrid",
        "pqGoal",
        "buildingScope",
        "Görevli dağıtım şirketi süreci",
        "ALO186 veya bağımsız hizmet sağlayıcı resmî dağıtım şirketi kararının yerine geçmez",
        "Bina içi kaynak ayrımı",
        "service=false",
        "$('service').classList.toggle('hidden',!out.service)",
        "Mevcut cihazınız işlevleri karşılıyorsa yenisini almayın",
    ]:
        assert token in combined, token
    assert "kategori=voltage_monitor" not in combined
    assert "commercial=true" not in combined
    assert "resmî ölçüm mercii değildir" in combined


def test_overlay_and_pipeline() -> None:
    overlay = json.loads(read(ROOT / "alo186/deployment/routing-overlays/growth-trust-revenue-run17.json"))
    assert overlay["version"] == 65
    assert {item["canonicalPath"] for item in overlay["routes"]} == set(ROUTES.values())
    assert all(item["type"] == "calculator" for item in overlay["routes"])

    manifest = load_effective_manifest(ROOT)
    assert manifest["version"] >= 65
    effective = {item["canonicalPath"]: item for item in manifest["routes"]}
    for route in ROUTES.values():
        assert route in effective

    injector = read(ROOT / "alo186/deployment/inject_growth_run17.py")
    for token in [
        'data-alo186-growth-run17-tools="true"',
        'data-alo186-growth-run17-evidence="true"',
        'data-alo186-growth-run17-trust="true"',
        'data-alo186-growth-run17-service="true"',
        '"directAffiliateLinksAdded": 0',
        '"unverifiedCommercialFieldsUsed": []',
        '"noBuyOutcomePreserved": True',
        '"officialApprovalClaimed": False',
        '"officialInstitutionImpressionPrevented": True',
        '"mode2CommerceClosed": True',
        '"voltageMonitorCommerceClosed": True',
        '"miniUpsRepeatedComparableFailureRequired": True',
        '"mode2JournalTtlDays": 540',
        '"miniUpsJournalTtlDays": 730',
        '"voltageMonitorJournalTtlDays": 365',
    ]:
        assert token in injector, token
    assert "patch_catalog" not in injector
    assert "ev_mobile_charger" not in injector
    assert "voltage_monitor" not in injector

    run15 = read(ROOT / "alo186/deployment/inject_growth_run15.py")
    assert "from inject_growth_run17 import run as run_growth_run17" in run15
    assert "growth_run17 = run_growth_run17(site, base_path)" in run15
    assert run15.index("growth_run17 = run_growth_run17") < run15.index("product_graph = run_affiliate_product_graph")
    assert '"growthRun17": growth_run17' in run15


if __name__ == "__main__":
    test_pages()
    test_mode2_contract()
    test_mini_ups_contract()
    test_voltage_contract()
    test_overlay_and_pipeline()
    print(json.dumps({
        "ok": True,
        "routingVersion": 65,
        "actions": 3,
        "directAffiliateLinksAdded": 0,
        "mode2CommerceClosed": True,
        "voltageMonitorCommerceClosed": True,
        "miniUpsRepeatedComparableFailureRequired": True,
        "noBuyOutcomePreserved": True,
    }, ensure_ascii=False, indent=2))
