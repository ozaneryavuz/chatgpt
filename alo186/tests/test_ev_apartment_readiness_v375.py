from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGES = {
    "/haberler/apartmanda-elektrikli-arac-sarj-istasyonu-kurulur-mu-2026/": ROOT / "alo186/haberler/apartmanda-elektrikli-arac-sarj-istasyonu-kurulur-mu-2026/index.html",
    "/hesaplama/apartman-elektrikli-arac-sarj-kurulum-on-kontrolu/": ROOT / "alo186/hesaplama/apartman-elektrikli-arac-sarj-kurulum-on-kontrolu/index.html",
    "/sektor-rehberi/site-apartman-elektrikli-arac-sarj-altyapisi-kabul/": ROOT / "alo186/sektor-rehberi/site-apartman-elektrikli-arac-sarj-altyapisi-kabul/index.html",
}
GOV = ROOT / "alo186/content/commerce/ev-apartment-readiness-v375.json"
ROUTING = ROOT / "alo186/deployment/routing-overlays/ev-apartment-readiness-v375.json"


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
        assert "fiyat" in low and "stok" in low and "puan" in low and "garanti" in low
        for merchant_token in ("amazon.com", "amazon.com.tr", "amzn.to", "tag="):
            assert merchant_token not in low, (route, merchant_token)
        for commercial_schema in ('"@type":"product"', '"@type":"offer"', '"@type":"aggregaterating"', "pricecurrency"):
            assert commercial_schema not in low, (route, commercial_schema)

    article = html_by_route["/haberler/apartmanda-elektrikli-arac-sarj-istasyonu-kurulur-mu-2026/"]
    article_low = article.casefold()
    assert '"@type":"Article"' in article
    assert '"@type":"FAQPage"' in article
    assert "sayı ve arsa payı çoğunluğu" in article_low
    assert "bağımsız bölüm eklentisi" in article_low
    assert "güç artışı" in article_low
    assert "epdk" in article_low
    assert "wallbox" in article_low
    assert "affiliate/merchant bağlantısı yoktur" in article_low

    calc = html_by_route["/hesaplama/apartman-elektrikli-arac-sarj-kurulum-on-kontrolu/"]
    calc_low = calc.casefold()
    assert '"@type":"WebApplication"' in calc
    assert "ortak kullanım alanı" in calc_low
    assert "güç artışı" in calc_low
    assert "ticari şarj" in calc_low
    assert "fetch(" not in calc_low
    assert "localstorage" not in calc_low
    assert "sessionstorage" not in calc_low
    assert "geolocation" not in calc_low
    for sensitive in ("adres", "plaka", "tesisat/abonelik no", "sayaç seri no"):
        assert sensitive in calc_low

    guide = html_by_route["/sektor-rehberi/site-apartman-elektrikli-arac-sarj-altyapisi-kabul/"]
    guide_low = guide.casefold()
    for token in ("yük yönetimi", "kapasite", "devreye alma", "professional-only", "yeni ürün almayın"):
        assert token in guide_low
    assert "/hesaplama/apartman-elektrikli-arac-sarj-kurulum-on-kontrolu/" in guide

    gov = json.loads(read(GOV))
    assert gov["version"] == 375
    commerce = gov["commerce"]
    assert commerce["new_affiliate_classes"] == 0
    assert commerce["new_merchant_links"] == 0
    assert commerce["unverified_price"] is False
    assert commerce["unverified_stock"] is False
    assert commerce["unverified_rating"] is False
    assert commerce["unverified_warranty"] is False
    assert gov["privacy"]["network_submission"] is False
    assert gov["privacy"]["persistent_browser_storage"] is False
    assert "wallbox" in gov["blocked_categories"]

    routing = json.loads(read(ROUTING))
    assert routing["version"] == 375
    actual = {r["canonicalPath"]: r for r in routing["routes"]}
    assert set(actual) == set(PAGES)
    for route, page in PAGES.items():
        assert actual[route]["source"] == str(page.relative_to(ROOT)).replace("\\", "/")

    print({"ok": True, "version": 375, "routes": list(PAGES), "newAffiliateClasses": 0, "newMerchantLinks": 0})


if __name__ == "__main__":
    main()
