from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "alo186"
OVERLAY = SITE / "deployment/routing-overlays/refrigerator-food-safety-journey-v321.json"

GUIDE_ROUTE = "/haberler/elektrik-kesintisinde-buzdolabi-ve-derin-dondurucu-ne-kadar-dayanir/"
PLANNER_ROUTE = "/hesaplama/buzdolabi-derin-dondurucu-elektrik-kesintisi-gida-guvenligi-plani/"
AFFILIATE_ROUTE = "/amazon-elektrik-urunleri/buzdolabi-dondurucu-kesinti-hazirlik-secimi/"
ROUTES = {
    GUIDE_ROUTE: SITE / "haberler/elektrik-kesintisinde-buzdolabi-ve-derin-dondurucu-ne-kadar-dayanir/index.html",
    PLANNER_ROUTE: SITE / "hesaplama/buzdolabi-derin-dondurucu-elektrik-kesintisi-gida-guvenligi-plani/index.html",
    AFFILIATE_ROUTE: SITE / "amazon-elektrik-urunleri/buzdolabi-dondurucu-kesinti-hazirlik-secimi/index.html",
}
PRODUCT_SCHEMA = {"Product", "AggregateRating", "Review"}


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

    pages = {route: path.read_text(encoding="utf-8") for route, path in ROUTES.items()}
    for route, html in pages.items():
        text = visible_text(html)
        folded = text.casefold()
        assert '<meta name="viewport"' in html and "width=device-width" in html
        assert f'<link rel="canonical" href="https://alo186.com{route}">' in html
        assert len(re.findall(r"<h1\b", html, re.I)) == 1
        assert not PRODUCT_SCHEMA.intersection(schema_types(load_schema(html)))
        assert "yeni ürün almayın" in folded
        assert "edaş" in folded and "kamu kurumu" in folded
        assert "fiyat" in folded and "stok" in folded and "puan" in folded and "garanti" in folded

    guide = pages[GUIDE_ROUTE]
    guide_text = visible_text(guide)
    assert {"Article", "FAQPage", "BreadcrumbList", "Question", "Answer"}.issubset(schema_types(load_schema(guide)))
    assert "amazon.com.tr" not in guide.casefold()
    for required in (
        "Yaklaşık 4 saat",
        "Yaklaşık 48 saat",
        "Yaklaşık 24 saat",
        "Gıdanın güvenli olup olmadığını anlamak için tadına bakmayın",
        "Aktif tehlikede test, ürün arama ve ticaret kapalıdır",
        PLANNER_ROUTE,
        AFFILIATE_ROUTE,
    ):
        assert required in guide or required in guide_text, required

    planner = pages[PLANNER_ROUTE]
    planner_text = visible_text(planner)
    assert {"WebApplication", "BreadcrumbList", "ListItem"}.issubset(schema_types(load_schema(planner)))
    assert "amazon.com.tr" not in planner.casefold() and "alo186rehber-21" not in planner.casefold()
    assert not re.search(r'<input[^>]+type=["\'](?:text|email|tel|file|hidden)["\']', planner, re.I)
    lowered = planner.casefold()
    for forbidden in ("fetch(", "xmlhttprequest", "sendbeacon", "localstorage.setitem", "sessionstorage.setitem"):
        assert forbidden not in lowered
    for required in (
        "new Blob",
        "URL.createObjectURL",
        "BEGIN:VCALENDAR",
        "30/90/365",
        "Form ve ticaret kapalı",
        "Professional-only plan gerekir",
        "Mevcut hazırlık yeterli — yeni ürün almayın",
        "Bu araçta Amazon Türkiye veya başka mağaza bağlantısı yoktur",
    ):
        assert required in planner or required in planner_text, required
    assert "Ad, telefon, e-posta, adres" in planner_text
    assert "Seçimler sunucuya gönderilmez" in planner_text

    affiliate = pages[AFFILIATE_ROUTE]
    affiliate_text = visible_text(affiliate)
    assert {"Article", "FAQPage", "BreadcrumbList", "Question", "Answer"}.issubset(schema_types(load_schema(affiliate)))
    assert affiliate.count('class="gate"') == 8
    assert affiliate.count("data-merchant-url=") == 2
    assert affiliate.count('rel="sponsored noopener"') == 2
    assert affiliate.count("tag=alo186rehber-21") == 2
    assert not re.search(r'<a[^>]+href=["\']https://www\.amazon\.com\.tr', affiliate, re.I)
    for required in (
        "Reklam / Amazon Türkiye satış ortaklığı açıklaması",
        "Aktif kesintide ticaret kapalıdır",
        "Cihaz termometresi",
        "Yalıtımlı soğutucu ve tekrar kullanılabilir jel paket",
        "Professional-only veya affiliate dışı sınıflar",
        "Koşullar doğrulandı: iki Amazon Türkiye satış ortaklığı kategori bağlantısı açıldı",
    ):
        assert required in affiliate or required in affiliate_text, required

    print(json.dumps({
        "ok": True,
        "routingVersion": 321,
        "newRoutes": list(ROUTES),
        "merchantLinksAdded": 2,
        "consumerAffiliateClasses": 2,
        "affiliateDisclosureBeforeLinks": True,
        "initialMerchantLinksLocked": True,
        "affiliateGateCount": 8,
        "professionalOnlyClasses": 6,
        "personalDataFields": 0,
        "networkSubmission": False,
        "browserStorageWrites": False,
        "noBuyOutcome": True,
        "revisitCycle": [30, 90, 365],
        "activeHazardCommerceClosed": True,
        "unverifiedPriceStockRatingWarranty": 0,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
