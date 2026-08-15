from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGES = {
    "/haberler/akilli-priz-elektrik-tasarrufu-saglar-mi/": ROOT / "alo186/haberler/akilli-priz-elektrik-tasarrufu-saglar-mi/index.html",
    "/hesaplama/akilli-priz-net-tasarruf-hesaplama/": ROOT / "alo186/hesaplama/akilli-priz-net-tasarruf-hesaplama/index.html",
    "/enerji-tasarrufu-kontrol-merkezi/": ROOT / "alo186/enerji-tasarrufu-kontrol-merkezi/index.html",
}
GOV = ROOT / "alo186/content/commerce/smart-plug-savings-v370.json"
ROUTING = ROOT / "alo186/deployment/routing-overlays/smart-plug-savings-v370.json"
SELECTOR = "/amazon-elektrik-urunleri/akilli-priz-enerji-olcer-secimi/"


def read(path: Path) -> str:
    assert path.is_file(), path
    return path.read_text(encoding="utf-8")


def main() -> None:
    html_by_route = {route: read(path) for route, path in PAGES.items()}
    for route, html in html_by_route.items():
        low = html.casefold()
        canonical = f"https://alo186.com{route}"
        assert f'<link rel="canonical" href="{canonical}">' in html
        assert "bağımsız bilgi platformudur" in low
        assert "yeni ürün almayın" in low
        for merchant_token in ("amazon.com", "amazon.com.tr", "amzn.to", "tag="):
            assert merchant_token not in low, (route, merchant_token)
        for commercial_schema in ('"@type":"product"', '"@type":"offer"', '"@type":"aggregaterating"', "pricecurrency"):
            assert commercial_schema not in low, (route, commercial_schema)

    article = html_by_route["/haberler/akilli-priz-elektrik-tasarrufu-saglar-mi/"]
    assert '"@type":"Article"' in article
    assert '"@type":"FAQPage"' in article
    assert '"@type":"BreadcrumbList"' in article

    calculator = html_by_route["/hesaplama/akilli-priz-net-tasarruf-hesaplama/"]
    calc_low = calculator.casefold()
    assert '"@type":"WebApplication"' in calculator
    assert "fetch(" not in calc_low
    assert "localstorage" not in calc_low
    assert "sessionstorage" not in calc_low
    assert "geolocation" not in calc_low
    assert "net kwh" in calc_low
    assert "akıllı priz ek tüketimi" in calc_low

    hub = html_by_route["/enerji-tasarrufu-kontrol-merkezi/"]
    assert '"@type":"CollectionPage"' in hub
    assert '"@type":"ItemList"' in hub

    # Disclosure must precede the clickable selector reference. Structured-data URLs do not count as a CTA.
    visible_selector = f'href="{SELECTOR}"'
    for route in (
        "/haberler/akilli-priz-elektrik-tasarrufu-saglar-mi/",
        "/hesaplama/akilli-priz-net-tasarruf-hesaplama/",
        "/enerji-tasarrufu-kontrol-merkezi/",
    ):
        html = html_by_route[route]
        selector_pos = html.find(visible_selector)
        assert selector_pos > 0, route
        disclosure_pos = html.rfind("Satış ortaklığı açıklaması", 0, selector_pos)
        assert disclosure_pos >= 0, route

    gov = json.loads(read(GOV))
    commerce = gov["commerce"]
    assert gov["version"] == 370
    assert commerce["new_affiliate_classes"] == 0
    assert commerce["new_merchant_links"] == 0
    assert commerce["existing_selector"] == SELECTOR
    assert commerce["unverified_price"] is False
    assert commerce["unverified_stock"] is False
    assert commerce["unverified_rating"] is False
    assert commerce["unverified_warranty"] is False
    assert "heaters" in gov["blocked_categories"]
    assert "medical_or_critical_loads" in gov["blocked_categories"]

    routing = json.loads(read(ROUTING))
    assert routing["version"] == 370
    actual = {r["canonicalPath"]: r for r in routing["routes"]}
    assert set(actual) == set(PAGES)
    for route, page in PAGES.items():
        assert actual[route]["source"] == str(page.relative_to(ROOT)).replace("\\", "/")

    print({
        "ok": True,
        "version": 370,
        "routes": list(PAGES),
        "newAffiliateClasses": commerce["new_affiliate_classes"],
        "newMerchantLinks": commerce["new_merchant_links"],
    })


if __name__ == "__main__":
    main()
