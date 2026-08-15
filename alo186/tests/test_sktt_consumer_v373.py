from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGES = {
    "/haberler/2026-elektrik-4000-kwh-siniri-sktt-ne-zaman-baslar/": ROOT / "alo186/haberler/2026-elektrik-4000-kwh-siniri-sktt-ne-zaman-baslar/index.html",
    "/hesaplama/2026-yillik-elektrik-tuketimi-4000-kwh-sktt-kontrolu/": ROOT / "alo186/hesaplama/2026-yillik-elektrik-tuketimi-4000-kwh-sktt-kontrolu/index.html",
    "/elektrik-tedarik-ve-tarife-kontrol-merkezi/": ROOT / "alo186/elektrik-tedarik-ve-tarife-kontrol-merkezi/index.html",
}
REPEAT_HUB = ROOT / "alo186/tekrar-kullanilan-araclar/index.html"
GOV = ROOT / "alo186/content/commerce/sktt-consumer-v373.json"
ROUTING = ROOT / "alo186/deployment/routing-overlays/sktt-consumer-v373.json"


def read(path: Path) -> str:
    assert path.is_file(), path
    return path.read_text(encoding="utf-8")


def main() -> None:
    html_by_route = {route: read(path) for route, path in PAGES.items()}
    for route, html in html_by_route.items():
        low = html.casefold()
        canonical = f"https://alo186.com{route}"
        assert f'<link rel="canonical" href="{canonical}">' in html
        assert "bağımsız" in low
        assert "doğrulanmamış fiyat" in low or "fiyat sonucu üretmez" in low
        for merchant_token in ("amazon.com", "amazon.com.tr", "amzn.to", "tag="):
            assert merchant_token not in low, (route, merchant_token)
        for commercial_schema in ('"@type":"product"', '"@type":"offer"', '"@type":"aggregaterating"', "pricecurrency"):
            assert commercial_schema not in low, (route, commercial_schema)

    article = html_by_route["/haberler/2026-elektrik-4000-kwh-siniri-sktt-ne-zaman-baslar/"]
    article_low = article.casefold()
    assert '"@type":"Article"' in article
    assert '"@type":"FAQPage"' in article
    assert "4.000 kwh" in article_low
    assert "500 kwh" in article_low
    assert "takip eden üçüncü ayın ilk" in article_low
    assert "epdk" in article_low
    assert "EPİAŞ" in article
    assert "merchant bağlantısı yoktur" in article_low

    calculator = html_by_route["/hesaplama/2026-yillik-elektrik-tuketimi-4000-kwh-sktt-kontrolu/"]
    calc_low = calculator.casefold()
    assert '"@type":"WebApplication"' in calculator
    assert "4000-c" in calculator
    assert "p>=500||c>=500" in calculator
    assert "getmonth()+3" in calc_low
    assert "fiyat sonucu üretmez" in calc_low
    assert "merchant/affiliate bağlantısı yoktur" in calc_low
    assert "fetch(" not in calc_low
    assert "localstorage" not in calc_low
    assert "sessionstorage" not in calc_low
    assert "geolocation" not in calc_low
    for sensitive in ("tesisat/abonelik no", "sayaç seri no", "tedarikçi hesabı"):
        assert sensitive in calc_low

    hub = html_by_route["/elektrik-tedarik-ve-tarife-kontrol-merkezi/"]
    hub_low = hub.casefold()
    assert '"@type":"CollectionPage"' in hub
    assert "15.000 kwh" in hub_low
    assert "/fatura-ve-sayac-kontrol-merkezi/" in hub
    assert "doğrudan affiliate/merchant bağlantısı yoktur" in hub_low
    assert "fiyat teklifi sunmaz" in hub_low

    repeat_hub = read(REPEAT_HUB)
    repeat_low = repeat_hub.casefold()
    assert "/elektrik-tedarik-ve-tarife-kontrol-merkezi/" in repeat_hub
    assert "4.000 kwh sktt" in repeat_low
    assert "500 kwh serbest tüketici" in repeat_low
    assert "doğrudan amazon" in repeat_low

    gov = json.loads(read(GOV))
    commerce = gov["commerce"]
    assert gov["version"] == 373
    assert commerce["new_affiliate_classes"] == 0
    assert commerce["new_merchant_links"] == 0
    assert commerce["unverified_price"] is False
    assert commerce["unverified_stock"] is False
    assert commerce["unverified_rating"] is False
    assert commerce["unverified_warranty"] is False
    assert gov["privacy"]["network_submission"] is False
    assert gov["privacy"]["persistent_browser_storage"] is False
    assert "electricity_meters" in gov["blocked_categories"]
    assert "guaranteed_supplier_savings" in gov["prohibited_claims"]

    routing = json.loads(read(ROUTING))
    assert routing["version"] == 373
    actual = {r["canonicalPath"]: r for r in routing["routes"]}
    assert set(actual) == set(PAGES)
    for route, page in PAGES.items():
        assert actual[route]["source"] == str(page.relative_to(ROOT)).replace("\\", "/")

    print({"ok": True, "version": 373, "routes": list(PAGES), "repeatHub": True, "newAffiliateClasses": 0, "newMerchantLinks": 0})


if __name__ == "__main__":
    main()
