from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "alo186"
OVERLAY = SITE / "deployment/routing-overlays/mobile-communication-outage-v338.json"
DECISION = SITE / "deployment/affiliate-category-decisions/mobile-communication-outage-v338.json"
GUIDE = SITE / "haberler/elektrik-kesilince-telefon-neden-cekmiyor-baz-istasyonu-calisir-mi/index.html"
PLANNER = SITE / "hesaplama/elektrik-kesintisi-mobil-iletisim-hazirlik-plani/index.html"
PRO = SITE / "sektor-rehberi/otel-site-isletme-mobil-iletisim-elektrik-kesintisi-surekliligi/index.html"
PHONE_SELECTOR = SITE / "amazon-elektrik-urunleri/telefon-powerbank-kablo-secimi/index.html"
ROUTES = {
    "/haberler/elektrik-kesilince-telefon-neden-cekmiyor-baz-istasyonu-calisir-mi/": GUIDE,
    "/hesaplama/elektrik-kesintisi-mobil-iletisim-hazirlik-plani/": PLANNER,
    "/sektor-rehberi/otel-site-isletme-mobil-iletisim-elektrik-kesintisi-surekliligi/": PRO,
}
COMMERCIAL_SCHEMA = {"Product", "Offer", "AggregateRating", "Review"}


def visible_text(html: str) -> str:
    html = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", html, flags=re.I | re.S)
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", html))).strip()


def schema_types(value: object) -> set[str]:
    result: set[str] = set()
    if isinstance(value, dict):
        kind = value.get("@type")
        if isinstance(kind, str):
            result.add(kind)
        for item in value.values():
            result.update(schema_types(item))
    elif isinstance(value, list):
        for item in value:
            result.update(schema_types(item))
    return result


def schema(html: str) -> object:
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    assert len(blocks) == 1
    return json.loads(blocks[0])


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 338
    assert {item["canonicalPath"] for item in overlay["routes"]} == set(ROUTES)

    decision = json.loads(DECISION.read_text(encoding="utf-8"))
    assert decision["version"] == 338
    assert decision["newAffiliateClasses"] == 0
    assert decision["newMerchantLinks"] == 0
    assert "/amazon-elektrik-urunleri/telefon-powerbank-kablo-secimi/" in decision["reusedInternalRoutes"]
    assert "powerbank-restores-mobile-coverage" in decision["mustNotClaim"]
    assert PHONE_SELECTOR.is_file()

    pages = {route: path.read_text(encoding="utf-8") for route, path in ROUTES.items()}
    for route, html in pages.items():
        visible = visible_text(html).casefold()
        assert f"https://alo186.com{route}" in html
        assert '<meta name="viewport"' in html
        assert len(re.findall(r"<h1\b", html, re.I)) == 1
        assert "edaş" in visible
        assert "kamu kurumu" in visible
        assert "satış ortaklığı" in visible
        assert "amazon.com.tr" not in html.casefold()
        assert not COMMERCIAL_SCHEMA.intersection(schema_types(schema(html)))
        for word in ("fiyat", "stok", "puan", "garanti"):
            assert word in visible

    guide = GUIDE.read_text(encoding="utf-8")
    guide_visible = visible_text(guide).casefold()
    for required in (
        "powerbank mobil kapsama sağlamaz",
        "baz istasyonları güç üniteleri",
        "şebeke kapasitesi",
        "ev interneti / wi‑fi",
        "btks",
    ):
        if required == "btks":
            assert "tuketici.btk.gov.tr" in guide
        else:
            assert required.casefold() in guide_visible
    assert "afad.gov.tr" in guide
    assert "112" in guide_visible and "186" in guide_visible

    planner = PLANNER.read_text(encoding="utf-8")
    planner_visible = visible_text(planner).casefold()
    assert not re.search(r'<input[^>]+type=["\'](?:text|email|tel|file|hidden)["\']', planner, re.I)
    for forbidden in (
        "fetch(",
        "xmlhttprequest",
        "sendbeacon",
        "localstorage.setitem",
        "sessionstorage.setitem",
    ):
        assert forbidden not in planner.casefold()
    for required in (
        "new Blob",
        "URL.createObjectURL",
        "BEGIN:VCALENDAR",
        "30/90/365",
        "Form ve ticaret kapalı",
        "Mevcut hazırlık yeterli — yeni ürün almayın",
        "/hesaplama/telefon-elektrik-kesintisi-sarj-plani/",
        "Powerbank mobil kapsama sağlamaz",
    ):
        assert required in planner or required.casefold() in planner_visible

    pro = PRO.read_text(encoding="utf-8")
    pro_visible = visible_text(pro).casefold()
    for required in (
        "professional-only",
        "kritik iletişim görevi",
        "mobil hizmet",
        "sabit internet",
        "yerel ağ ve enerji",
        "ups / batarya",
        "jeneratör / ats",
        "personel prosedürü",
        "30 / 90 / 365",
        "/kurumsal-elektrik-surekliligi-on-degerlendirme",
    ):
        assert required.casefold() in pro_visible or required in pro

    print(json.dumps({
        "ok": True,
        "routingVersion": 338,
        "newRoutes": list(ROUTES),
        "newAffiliateClasses": 0,
        "newMerchantLinks": 0,
        "reusedLowRiskAffiliatePath": "/amazon-elektrik-urunleri/telefon-powerbank-kablo-secimi/",
        "personalDataFields": 0,
        "networkSubmission": False,
        "browserStorageWrites": False,
        "activeIncidentCommerceClosed": True,
        "noBuyOutcome": True,
        "powerbankCoverageClaimBlocked": True,
        "professionalOnlyBusinessContinuity": True,
        "revisitCycle": [30, 90, 365],
        "unverifiedPriceStockRatingWarranty": 0,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
