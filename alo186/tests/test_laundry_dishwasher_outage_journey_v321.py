from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "alo186"
OVERLAY = SITE / "deployment/routing-overlays/laundry-dishwasher-outage-journey-v321.json"
DECISION = SITE / "deployment/affiliate-category-decisions/laundry-dishwasher-outage-v321.json"

ROUTES = {
    "/haberler/elektrik-kesilince-camasir-bulasik-makinesi-programi-yarida-kalir-mi/": SITE / "haberler/elektrik-kesilince-camasir-bulasik-makinesi-programi-yarida-kalir-mi/index.html",
    "/hesaplama/camasir-bulasik-makinesi-elektrik-kesintisi-guvenli-devam-plani/": SITE / "hesaplama/camasir-bulasik-makinesi-elektrik-kesintisi-guvenli-devam-plani/index.html",
    "/sektor-rehberi/otel-camasirhane-mutfak-bulasik-makinesi-kesinti-surekliligi/": SITE / "sektor-rehberi/otel-camasirhane-mutfak-bulasik-makinesi-kesinti-surekliligi/index.html",
}
MERCHANT_MARKERS = ("amazon.com.tr", "amzn.to", "alo186rehber-21")
COMMERCIAL_SCHEMA = {"Product", "Offer", "AggregateRating", "Review"}


def visible_text(html: str) -> str:
    value = re.sub(r"<script\b.*?</script>", " ", html, flags=re.I | re.S)
    value = re.sub(r"<style\b.*?</style>", " ", value, flags=re.I | re.S)
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", unescape(value)).strip()


def schema_types(value: object) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        kind = value.get("@type")
        if isinstance(kind, str):
            found.add(kind)
        elif isinstance(kind, list):
            found.update(str(item) for item in kind)
        for child in value.values():
            found.update(schema_types(child))
    elif isinstance(value, list):
        for child in value:
            found.update(schema_types(child))
    return found


def load_schema(html: str) -> object:
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    assert len(blocks) == 1
    return json.loads(blocks[0])


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 321
    assert overlay["generatedAt"] == "2026-08-06"
    assert {item["canonicalPath"] for item in overlay["routes"]} == set(ROUTES)

    decision = json.loads(DECISION.read_text(encoding="utf-8"))
    assert decision["version"] == 321
    assert decision["newMerchantLinks"] == 0
    assert decision["affiliatePolicy"]["consumerAffiliateClasses"] == 0
    assert decision["affiliatePolicy"]["activeHazardCommerceClosed"] is True
    assert decision["affiliatePolicy"]["activeOutageCommerceClosed"] is True
    assert decision["affiliatePolicy"]["highLoadWetApplianceCommerceClosed"] is True
    assert decision["affiliatePolicy"]["unverifiedCommercialClaims"] == 0
    assert decision["privacyPolicy"]["personalDataFields"] == 0
    assert decision["privacyPolicy"]["serverSubmission"] is False
    assert decision["privacyPolicy"]["persistentBrowserStorage"] is False
    assert decision["privacyPolicy"]["localIcsGeneration"] is True
    assert [item["days"] for item in decision["repeatVisitReasons"]] == [30, 90, 365]

    pages = {route: path.read_text(encoding="utf-8") for route, path in ROUTES.items()}
    for route, html in pages.items():
        folded = html.casefold()
        text_folded = visible_text(html).casefold()
        assert '<meta name="viewport"' in html and "width=device-width" in html
        assert f'<link rel="canonical" href="https://alo186.com{route}">' in html
        assert len(re.findall(r"<h1\b", html, re.I)) == 1
        assert all(marker not in folded for marker in MERCHANT_MARKERS)
        assert not COMMERCIAL_SCHEMA.intersection(schema_types(load_schema(html)))
        assert "resmî kurum" in text_folded or "kamu kurumu" in text_folded
        assert "yeni ürün almayın" in text_folded
        assert "professional-only" in text_folded

    guide = pages["/haberler/elektrik-kesilince-camasir-bulasik-makinesi-programi-yarida-kalir-mi/"]
    guide_text = visible_text(guide)
    assert {"Article", "FAQPage", "BreadcrumbList", "Question", "Answer"}.issubset(schema_types(load_schema(guide)))
    for required in (
        "Programın devam edeceğini varsaymayın",
        "Kapıyı, kilidi veya mandalı zorlamayın",
        "Kararsız besleme",
        "Aktif tehlikede form ve ticaret kapalıdır",
        "Samsung Türkiye · UC besleme gerilimi hatası",
        "6 Ağustos 2026",
        "/hesaplama/camasir-bulasik-makinesi-elektrik-kesintisi-guvenli-devam-plani/",
        "/sektor-rehberi/otel-camasirhane-mutfak-bulasik-makinesi-kesinti-surekliligi/",
    ):
        assert required in guide or required in guide_text, required

    planner = pages["/hesaplama/camasir-bulasik-makinesi-elektrik-kesintisi-guvenli-devam-plani/"]
    planner_text = visible_text(planner)
    assert {"WebApplication", "FAQPage", "BreadcrumbList"}.issubset(schema_types(load_schema(planner)))
    assert not re.search(r'<input[^>]+type=["\'](?:text|email|tel|file|hidden)["\']', planner, re.I)
    lowered = planner.casefold()
    for forbidden in ("fetch(", "xmlhttprequest", "localstorage", "sessionstorage", "sendbeacon", "document.cookie", "navigator.geolocation"):
        assert forbidden not in lowered
    for required in (
        "new Blob",
        "URL.createObjectURL",
        "BEGIN:VCALENDAR",
        "30/90/365",
        "Form ve ticaret kapalıdır",
        "Professional-only kabul gerekir",
        "Mevcut güvenli devam planı yeterli — yeni ürün almayın",
        "Bu sayfada Amazon veya başka mağaza bağlantısı yoktur",
    ):
        assert required in planner, required
    assert "ad, telefon, e-posta, adres" in planner_text
    assert "Seçimler sunucuya gönderilmez" in planner_text
    assert "kalıcı tarayıcı depolaması kullanılmaz" in planner_text

    sector = pages["/sektor-rehberi/otel-camasirhane-mutfak-bulasik-makinesi-kesinti-surekliligi/"]
    sector_text = visible_text(sector)
    assert {"Article", "FAQPage", "BreadcrumbList"}.issubset(schema_types(load_schema(sector)))
    for required in (
        "Professional-only kabul matrisi",
        "Jeneratör–ATS görev kabulü",
        "Kimyasal dozaj",
        "Hijyen ve yeniden işleme",
        "Yeni merchant bağlantısı ve tüketici affiliate sınıfı yoktur",
        "30 gün",
        "90 gün",
        "365 gün",
    ):
        assert required in sector or required in sector_text, required

    print(json.dumps({
        "ok": True,
        "routingVersion": 321,
        "newRoutes": list(ROUTES),
        "merchantLinksAdded": 0,
        "consumerAffiliateClasses": 0,
        "professionalOnlyClasses": len(decision["professionalOnlyClasses"]),
        "personalDataFields": 0,
        "networkSubmission": False,
        "browserStorage": False,
        "noBuyOutcome": True,
        "revisitCycle": [30, 90, 365],
        "activeHazardCommerceClosed": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
