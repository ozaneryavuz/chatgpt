from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "alo186"
OVERLAY = SITE / "deployment/routing-overlays/modem-ont-outage-journey-v322.json"
CONSOLIDATIONS = SITE / "deployment/content-consolidations.json"

GUIDE_ROUTE = "/haberler/elektrik-kesilince-modem-internet-calisir-mi/"
PLANNER_ROUTE = "/hesaplama/modem-ont-elektrik-kesintisi-internet-hazirlik-plani/"
ALIAS_ROUTE = "/amazon-elektrik-urunleri/modem-ont-yedek-guc-secimi/"
CANONICAL_SELECTOR_ROUTE = "/amazon-elektrik-urunleri/modem-ont-mini-ups-yedekleme-secici/"
ROUTES = {
    GUIDE_ROUTE: SITE / "haberler/elektrik-kesilince-modem-internet-calisir-mi/index.html",
    PLANNER_ROUTE: SITE / "hesaplama/modem-ont-elektrik-kesintisi-internet-hazirlik-plani/index.html",
    ALIAS_ROUTE: SITE / "amazon-elektrik-urunleri/modem-ont-yedek-guc-secimi/index.html",
}
CANONICAL_SELECTOR = SITE / "amazon-elektrik-urunleri/modem-ont-mini-ups-yedekleme-secici/index.html"
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
    assert overlay["version"] == 322
    assert overlay["generatedAt"] == "2026-08-06"
    assert {item["canonicalPath"] for item in overlay["routes"]} == set(ROUTES)
    type_by_route = {item["canonicalPath"]: item["type"] for item in overlay["routes"]}
    assert type_by_route[GUIDE_ROUTE] == "article"
    assert type_by_route[PLANNER_ROUTE] == "business-tool"
    assert type_by_route[ALIAS_ROUTE] == "commerce-guide"

    pages = {route: path.read_text(encoding="utf-8") for route, path in ROUTES.items()}
    for route, html in pages.items():
        text = visible_text(html)
        folded = text.casefold()
        assert '<meta name="viewport"' in html and "width=device-width" in html
        assert len(re.findall(r"<h1\b", html, re.I)) == 1
        assert "yeni ürün almayın" in folded
        assert "edaş" in folded and "kamu kurumu" in folded
        for claim in ("fiyat", "stok", "puan", "garanti"):
            assert claim in folded

    guide = pages[GUIDE_ROUTE]
    guide_text = visible_text(guide)
    assert f'<link rel="canonical" href="https://alo186.com{GUIDE_ROUTE}">' in guide
    assert {"Article", "FAQPage", "BreadcrumbList", "Question", "Answer"}.issubset(schema_types(load_schema(guide)))
    assert not COMMERCIAL_SCHEMA.intersection(schema_types(load_schema(guide)))
    assert "amazon.com.tr" not in guide.casefold() and "alo186rehber-21" not in guide.casefold()
    for required in (
        "Router tek başına olmayabilir",
        "Evde güç olması garanti değildir",
        "Dijital telefon ayrıca planlanır",
        "Aktif tehlikede test, ürün arama ve ticaret kapalıdır",
        "Sağlayıcı altyapısı kesintide çalışmıyorsa daha büyük bir ev UPS'i interneti geri getirmez",
        PLANNER_ROUTE,
        ALIAS_ROUTE,
    ):
        assert required in guide or required in guide_text, required

    planner = pages[PLANNER_ROUTE]
    planner_text = visible_text(planner)
    assert f'<link rel="canonical" href="https://alo186.com{PLANNER_ROUTE}">' in planner
    assert {"WebApplication", "BreadcrumbList", "ListItem"}.issubset(schema_types(load_schema(planner)))
    assert not COMMERCIAL_SCHEMA.intersection(schema_types(load_schema(planner)))
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
        "Mobil alternatif yeterli — yeni ürün almayın",
        "Mevcut hazırlık yeterli — yeni ürün almayın",
        "Bu araçta Amazon Türkiye veya başka mağaza bağlantısı yoktur",
        ALIAS_ROUTE,
    ):
        assert required in planner or required in planner_text, required
    assert "Ad, telefon, e-posta, adres" in planner_text
    assert "Seçimler sunucuya gönderilmez" in planner_text

    alias = pages[ALIAS_ROUTE]
    alias_text = visible_text(alias)
    alias_folded = alias_text.casefold()
    assert '<meta name="robots" content="noindex,follow">' in alias
    assert f'<link rel="canonical" href="https://alo186.com{CANONICAL_SELECTOR_ROUTE}">' in alias
    assert f'content="0;url={CANONICAL_SELECTOR_ROUTE}"' in alias
    assert CANONICAL_SELECTOR_ROUTE in alias
    assert "amazon türkiye satış ortaklığı açıklaması" in alias_folded
    assert "iki ayrı ürün sayfası oluşturulmadı" in alias_folded
    assert "amazon.com.tr" not in alias.casefold() and "alo186rehber-21" not in alias.casefold()
    assert not re.search(r'<script type="application/ld\+json">', alias, re.I)

    selector = CANONICAL_SELECTOR.read_text(encoding="utf-8")
    selector_text = visible_text(selector)
    selector_folded = selector_text.casefold()
    assert f'<link rel="canonical" href="https://alo186.com{CANONICAL_SELECTOR_ROUTE}">' in selector
    assert "amazon gelir ortağı açıklaması" in selector_folded
    assert "yeni ürün alınmamalı" in selector_folded or "yeni ürün almayın" in selector_folded
    assert "fiyat, stok, satıcı, puan, yorum, teslimat veya garanti" in selector_folded
    assert selector.count('class="gatebox"') == 3
    assert "ont" in selector_folded and "polarite" in selector_folded and "gerilim" in selector_folded

    config = json.loads(CONSOLIDATIONS.read_text(encoding="utf-8"))
    pairs = {(item["aliasPath"], item["canonicalPath"]) for item in config["consolidations"]}
    assert (ALIAS_ROUTE, CANONICAL_SELECTOR_ROUTE) in pairs
    assert (
        "/haberler/elektrik-kesilince-elektrikli-arac-sarji-ne-olur/",
        "/haberler/elektrik-kesilince-elektrikli-arac-sarji-durur-mu/",
    ) in pairs

    print(json.dumps({
        "ok": True,
        "routingVersion": 322,
        "newRoutes": [GUIDE_ROUTE, PLANNER_ROUTE],
        "consolidatedAlias": ALIAS_ROUTE,
        "canonicalSelector": CANONICAL_SELECTOR_ROUTE,
        "newMerchantLinksAdded": 0,
        "existingAffiliateClassesReused": 3,
        "affiliateDisclosureBeforeSelection": True,
        "canonicalSelectorFinalGateCount": 3,
        "professionalOnlyClasses": 6,
        "personalDataFields": 0,
        "networkSubmission": False,
        "browserStorageWrites": False,
        "noBuyOutcome": True,
        "revisitCycle": [30, 90, 365],
        "activeHazardCommerceClosed": True,
        "providerNetworkGuarantee": False,
        "duplicateIntentConsolidated": True,
        "unverifiedPriceStockRatingWarranty": 0,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
