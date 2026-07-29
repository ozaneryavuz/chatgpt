from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PAGES = {
    "vpp": ROOT / "alo186/hesaplama/vpp-esnek-yuk-hazirlik/index.html",
    "ev": ROOT / "alo186/hesaplama/apartman-site-ev-sarj-karar-paketi/index.html",
    "runtime": ROOT / "alo186/hesaplama/yedek-guc-runtime-saglik-gunlugu/index.html",
}
CORES = {
    key: path.with_name("core.js") for key, path in PAGES.items()
}
APPS = {
    key: path.with_name("app.js") for key, path in PAGES.items()
}
ROUTES = {
    "vpp": "/hesaplama/vpp-esnek-yuk-hazirlik/",
    "ev": "/hesaplama/apartman-site-ev-sarj-karar-paketi/",
    "runtime": "/hesaplama/yedek-guc-runtime-saglik-gunlugu/",
}
PRIVACY_TOKENS = {
    "vpp": ("tesis adı", "adres", "sayaç numarası"),
    "ev": ("adres", "malik/kullanıcı adı", "sayaç/abone numarası"),
    "runtime": ("adres", "iletişim", "seri numarası"),
}
CANONICAL_FEASIBILITY = "/hizmetler/ges-batarya-ev-sarj-fizibilitesi/"
LEGACY_FEASIBILITY = "/hizmetler/ges-batarya-ev-fizibilitesi/"


def read(path: Path) -> str:
    assert path.is_file(), path
    return path.read_text(encoding="utf-8")


def jsonld(html: str) -> list[dict]:
    blocks = re.findall(r'<script\s+type="application/ld\+json">(.*?)</script>', html, re.S | re.I)
    assert blocks
    return [json.loads(block) for block in blocks]


def types(graphs: list[dict]) -> set[str]:
    found: set[str] = set()
    for item in graphs:
        nodes = item.get("@graph", [item])
        for node in nodes:
            value = node.get("@type") if isinstance(node, dict) else None
            if isinstance(value, str):
                found.add(value)
            elif isinstance(value, list):
                found.update(str(v) for v in value)
    return found


def test_pages() -> None:
    for key, path in PAGES.items():
        html = read(path)
        lower = html.lower()
        assert html.count("<h1") == 1, key
        assert f'https://www.alo186.com{ROUTES[key]}' in html, key
        assert {"WebApplication", "FAQPage", "BreadcrumbList"} <= types(jsonld(html)), key
        assert "amazon.com" not in lower and "amzn." not in lower, key
        assert '"@type":"product"' not in lower and '"@type":"offer"' not in lower, key
        for token in PRIVACY_TOKENS[key]:
            assert token in lower, (key, token)
        assert "kişisel veri" in lower or "kişisel verisiz" in lower, key
        assert '<script src="./core.js"></script>' in html, key
        assert '<script src="./app.js"></script>' in html, key
        assert CORES[key].is_file() and APPS[key].is_file(), key
    for key in ("vpp", "ev"):
        lower = read(PAGES[key]).lower()
        assert "resmî" in lower or "resmi" in lower, key


def test_vpp_contract() -> None:
    html = read(PAGES["vpp"])
    core = read(CORES["vpp"])
    combined = html + core + read(APPS["vpp"])
    for token in [
        "incomeEstimate:false",
        "aggregatorRanking:false",
        "officialApproval:false",
        "kişisel veri",
        "gelir garantisi",
        "teias.gov.tr",
        "30 günlük",
        "assetRequired",
        "Math.min(rawScore,8)",
    ]:
        assert token in combined, token
    assert "toplayıcı sıralamaz" in html.lower()
    assert CANONICAL_FEASIBILITY in html
    assert LEGACY_FEASIBILITY not in html


def test_ev_contract() -> None:
    html = read(PAGES["ev"])
    core = read(CORES["ev"])
    app = read(APPS["ev"])
    combined = html + core + app
    for token in [
        "officialApproval:false",
        "managementDecision:false",
        "directAffiliateLinks:false",
        "epdk.gov.tr",
        "ayrı abonelik",
        "dinamik yük yönetimi",
        "45 günlük",
        "MAX_SCORE=11",
        "maxScore:MAX_SCORE",
    ]:
        assert token in combined, token
    assert "doğrudan affiliate/mağaza yönlendirmesi yapılmaz" in html.lower()
    assert "/hesaplama/teknik-sartname-talep-paketi/" in html
    assert CANONICAL_FEASIBILITY in html
    assert LEGACY_FEASIBILITY not in html


def test_runtime_contract() -> None:
    html = read(PAGES["runtime"])
    core = read(CORES["runtime"])
    app = read(APPS["runtime"])
    combined = html + core + app
    for token in [
        "alo186.backupRuntimeJournal.v1",
        "TTL_MS=540*86400000",
        "MAX_RECORDS=12",
        "localStorage",
        "Mevcut ürünle devam",
        "satın almayın",
        "Affiliate ve yeni ürün yönlendirmesi bu sonuçta kapalıdır",
        "/amazon-elektrik-urunleri/modem-mini-ups-secimi",
        "/amazon-elektrik-urunleri/tasinabilir-guc-istasyonu-secimi",
        "retentionMode:'per-record'",
        "compareOrder(item,focus)<0",
        "repeatedSignificantDrop",
        "state:'confirmation_needed'",
        "state:'repeated_drop'",
    ]:
        assert token in combined, token
    assert "Reklam / satış ortaklığı açıklaması" in html
    assert "fiyat, stok, puan, satıcı" in html.lower()
    assert "function render" in app and "persist();render(entry)" in app
    assert "expiresAt:new Date(now+TTL_MS).toISOString()" in core


def test_overlay_and_pipeline() -> None:
    overlay = json.loads(read(ROOT / "alo186/deployment/routing-overlays/growth-vpp-ev-runtime-run8.json"))
    assert overlay["version"] == 50
    actual = {item["canonicalPath"]: item["type"] for item in overlay["routes"]}
    assert actual == {
        ROUTES["vpp"]: "business-tool",
        ROUTES["ev"]: "business-tool",
        ROUTES["runtime"]: "calculator",
    }
    injector = read(ROOT / "alo186/deployment/inject_growth_run8.py")
    for marker in [
        'data-alo186-growth-run8-tools="true"',
        'data-alo186-growth-run8-journey="true"',
        'data-alo186-growth-run8-affiliate="true"',
        'data-alo186-growth-run8-business="true"',
        '"rawPersonalDataCollected": False',
        '"directAffiliateLinksAdded": 0',
        '"unverifiedCommercialFieldsUsed": []',
        '"noBuyOutcomePreserved": True',
        '"aggregatorRanking": False',
        '"incomeEstimatePublished": False',
        '"officialApprovalClaimed": False',
        '"runtimeJournalTtlDays": 540',
        '"fixedInstallationDirectAffiliate": False',
    ]:
        assert marker in injector, marker
    orchestrator = read(ROOT / "alo186/deployment/inject_shortlist_growth.py")
    assert "from inject_growth_run8 import run as run_growth_run8" in orchestrator
    assert "growth_run8 = run_growth_run8(site, base_path)" in orchestrator
    assert '"growthRun8": growth_run8' in orchestrator


if __name__ == "__main__":
    test_pages()
    test_vpp_contract()
    test_ev_contract()
    test_runtime_contract()
    test_overlay_and_pipeline()
    print("ALO186 growth run8 contracts: OK")
