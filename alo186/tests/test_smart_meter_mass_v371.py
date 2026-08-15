from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NEW_PAGES = {
    "/haberler/milli-akilli-sayac-sistemi-mass-nedir-2026/": ROOT / "alo186/haberler/milli-akilli-sayac-sistemi-mass-nedir-2026/index.html",
    "/hesaplama/akilli-sayac-mass-gecis-kontrolu/": ROOT / "alo186/hesaplama/akilli-sayac-mass-gecis-kontrolu/index.html",
}
HUB = ROOT / "alo186/fatura-ve-sayac-kontrol-merkezi/index.html"
GOV = ROOT / "alo186/content/commerce/smart-meter-mass-v371.json"
ROUTING = ROOT / "alo186/deployment/routing-overlays/smart-meter-mass-v371.json"


def read(path: Path) -> str:
    assert path.is_file(), path
    return path.read_text(encoding="utf-8")


def main() -> None:
    html_by_route = {route: read(path) for route, path in NEW_PAGES.items()}
    for route, html in html_by_route.items():
        low = html.casefold()
        canonical = f"https://alo186.com{route}"
        assert f'<link rel="canonical" href="{canonical}">' in html
        assert "bağımsız" in low
        assert any(token in low for token in (
            "yeni ürün almayın",
            "yeni bir ürün satın alma gerekçesi değildir",
            "satın almanız gerektiğini varsaymayın",
        )), route
        for merchant_token in ("amazon.com", "amazon.com.tr", "amzn.to", "tag="):
            assert merchant_token not in low, (route, merchant_token)
        for commercial_schema in ('"@type":"product"', '"@type":"offer"', '"@type":"aggregaterating"', "pricecurrency"):
            assert commercial_schema not in low, (route, commercial_schema)

    article = html_by_route["/haberler/milli-akilli-sayac-sistemi-mass-nedir-2026/"]
    article_low = article.casefold()
    assert '"@type":"Article"' in article
    assert '"@type":"FAQPage"' in article
    assert "2,8 milyon" in article_low
    assert "12 milyon" in article_low
    assert "ücret alınmayacağı" in article_low
    assert "kullanıcıya özel" in article_low
    assert "epdk" in article_low

    calculator = html_by_route["/hesaplama/akilli-sayac-mass-gecis-kontrolu/"]
    calc_low = calculator.casefold()
    assert '"@type":"WebApplication"' in calculator
    assert "fetch(" not in calc_low
    assert "localstorage" not in calc_low
    assert "sessionstorage" not in calc_low
    assert "geolocation" not in calc_low
    for sensitive in ("tesisat/abonelik no", "sayaç seri no", "hesap parolası"):
        assert sensitive in calc_low
    assert "merchant/affiliate bağlantısı yoktur" in calc_low
    assert "/hesaplama/elektrik-sayaci-endeks-kwh-gun-takibi/" in calculator

    hub = read(HUB)
    hub_low = hub.casefold()
    assert "/haberler/milli-akilli-sayac-sistemi-mass-nedir-2026/" in hub
    assert "/hesaplama/akilli-sayac-mass-gecis-kontrolu/" in hub
    assert "sayaç değişim başvurusu" in hub_low
    assert "amazon türkiye satış ortaklığı" in hub_low

    gov = json.loads(read(GOV))
    commerce = gov["commerce"]
    assert gov["version"] == 371
    assert commerce["new_affiliate_classes"] == 0
    assert commerce["new_merchant_links"] == 0
    assert commerce["unverified_price"] is False
    assert commerce["unverified_stock"] is False
    assert commerce["unverified_rating"] is False
    assert commerce["unverified_warranty"] is False
    assert gov["privacy"]["network_submission"] is False
    assert gov["privacy"]["persistent_browser_storage"] is False
    assert "electricity_meters" in gov["blocked_categories"]
    assert "meter_communications_modems" in gov["blocked_categories"]

    routing = json.loads(read(ROUTING))
    assert routing["version"] == 371
    actual = {r["canonicalPath"]: r for r in routing["routes"]}
    assert set(actual) == set(NEW_PAGES)
    for route, page in NEW_PAGES.items():
        assert actual[route]["source"] == str(page.relative_to(ROOT)).replace("\\", "/")

    print({"ok": True, "version": 371, "routes": list(NEW_PAGES), "newAffiliateClasses": 0, "newMerchantLinks": 0})


if __name__ == "__main__":
    main()
