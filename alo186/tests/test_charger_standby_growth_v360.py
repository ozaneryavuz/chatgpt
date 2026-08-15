from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> None:
    article = read("alo186/haberler/sarj-aleti-prizde-kalirsa-elektrik-harcar-mi/index.html")
    hub = read("alo186/sarj-cihazi-ve-kablo-kontrol-merkezi/index.html")
    routing = json.loads(read("alo186/deployment/routing-overlays/360-charger-standby-journey.json"))
    policy = json.loads(read("alo186/deployment/affiliate-category-decisions/charger-standby-v360.json"))

    expected = {
        "/haberler/sarj-aleti-prizde-kalirsa-elektrik-harcar-mi/",
        "/sarj-cihazi-ve-kablo-kontrol-merkezi/",
    }
    assert routing["version"] == 360
    assert {route["canonicalPath"] for route in routing["routes"]} == expected

    assert '<link rel="canonical" href="https://alo186.com/haberler/sarj-aleti-prizde-kalirsa-elektrik-harcar-mi/">' in article
    for schema in ('"@type":"Article"', '"@type":"FAQPage"', '"@type":"BreadcrumbList"'):
        assert schema in article
    for required in (
        "60 saniyelik karar",
        "14 Aralık 2028",
        "evrensel watt",
        "yeni ürün almayın",
        "/hesaplama/bekleme-modu-standby-kwh-hesaplama/",
        "/hesaplama/usb-c-pd-sarj-kablo-uygunluk/",
        "/hesaplama/priz-fis-elektrik-guvenlik-belirti-ayirici/",
        "EDAŞ veya kamu kurumu değildir",
    ):
        assert required in article

    assert '<link rel="canonical" href="https://alo186.com/sarj-cihazi-ve-kablo-kontrol-merkezi/">' in hub
    for schema in ('"@type":"WebPage"', '"@type":"ItemList"', '"@type":"BreadcrumbList"'):
        assert schema in hub
    for required in (
        "No-buy-first ticari kural",
        "mevcut adaptör/kablo güvenli ve yeterliyse yeni ürün almayın",
        "/haberler/usb-c-kablo-kac-watt-60w-240w-pd-farki/",
        "/fatura-ve-sayac-kontrol-merkezi/",
        "EDAŞ veya kamu kurumu değildir",
    ):
        assert required in hub

    for page in (article, hub):
        lowered = page.lower()
        assert "amazon.com.tr" not in lowered
        assert '"@type":"Product"' not in page
        assert '"@type":"Offer"' not in page
        assert "AggregateRating" not in page
        assert "priceCurrency" not in page
        assert "₺" not in page

    commercial = policy["commercialDecision"]
    assert commercial["newAffiliateClass"] is False
    assert commercial["newMerchantLinksOnNewPages"] == 0
    assert commercial["reuseExistingAffiliateClass"] == "usb-c-pd-v355"
    assert set(commercial["claimsForbidden"]) >= {
        "unverified price",
        "unverified stock",
        "unverified rating",
        "unverified warranty",
        "universal no-load watt value",
        "stale electricity unit price presented as current",
    }
    assert policy["trust"]["merchantDisclosureBeforeLinkRequired"] is True
    assert policy["trust"]["officialAffiliationImpressionForbidden"] is True

    print({
        "ok": True,
        "version": 360,
        "routes": sorted(expected),
        "newAffiliateClasses": 0,
        "newMerchantLinks": 0,
        "policy": "measure-first / no-buy-first / disclosure-before-commerce / safety-fail-closed",
    })


if __name__ == "__main__":
    main()
