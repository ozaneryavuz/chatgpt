from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]
ROUTES = {
    "/haberler/elektrik-guvence-bedeli-iadesi-kac-gunde-nasil-alinir-2026/": ROOT / "alo186/haberler/elektrik-guvence-bedeli-iadesi-kac-gunde-nasil-alinir-2026/index.html",
    "/hesaplama/elektrik-guvence-bedeli-iade-takibi/": ROOT / "alo186/hesaplama/elektrik-guvence-bedeli-iade-takibi/index.html",
    "/abonelik-ve-guvence-bedeli-kontrol-merkezi/": ROOT / "alo186/abonelik-ve-guvence-bedeli-kontrol-merkezi/index.html",
}

for route, path in ROUTES.items():
    assert path.is_file(), path
    html = path.read_text(encoding="utf-8")
    low = html.casefold()
    canonical = f"https://alo186.com{route}"
    assert f'<link rel="canonical" href="{canonical}">' in html, route
    assert '<meta name="robots" content="index,follow,max-image-preview:large">' in html, route
    assert "alo186" in low and "bağımsız" in low, route
    assert "amazon.com.tr" not in low, route
    assert "amzn.to" not in low, route
    assert '"@type":"product"' not in low, route
    assert '"@type":"offer"' not in low, route
    assert "aggregateRating".casefold() not in low, route
    assert "pricecurrency" not in low, route

article = ROUTES["/haberler/elektrik-guvence-bedeli-iadesi-kac-gunde-nasil-alinir-2026/"].read_text(encoding="utf-8")
article_low = article.casefold()
for expected in (
    "epdk.gov.tr",
    "enerji.gov.tr",
    "tuketici.ticaret.gov.tr",
    "5 iş günü",
    "görevli tedarik şirket",
    "alo186; epdk",
    "ürün satın alma problemi değildir",
):
    assert expected.casefold() in article_low, expected
assert "263" not in article, "Do not hard-code 2026 security deposit unit price in evergreen guide"
assert "746" not in article, "Do not hard-code 2026 security deposit unit price in evergreen guide"

calc = ROUTES["/hesaplama/elektrik-guvence-bedeli-iade-takibi/"].read_text(encoding="utf-8")
calc_low = calc.casefold()
for forbidden in ("localstorage", "sessionstorage", "navigator.geolocation", "fetch(", "xmlhttprequest"):
    assert forbidden not in calc_low, forbidden
for pii in ("t.c. kimlik", "abonelik/tesisat no", "banka hesabı"):
    assert pii.casefold() in calc_low, pii
assert "hukuki son gün üretmez" in calc_low
assert "yeni ürün veya hizmet satın almanız gerekmez" in calc_low

hub = ROUTES["/abonelik-ve-guvence-bedeli-kontrol-merkezi/"].read_text(encoding="utf-8")
for target in (
    "/haberler/elektrik-guvence-bedeli-iadesi-kac-gunde-nasil-alinir-2026/",
    "/hesaplama/elektrik-guvence-bedeli-iade-takibi/",
    "/fatura-ve-sayac-kontrol-merkezi/",
    "/tekrar-kullanilan-araclar/",
):
    assert target in hub, target

routing = json.loads((ROOT / "alo186/deployment/routing-overlays/subscription-deposit-refund-v376.json").read_text(encoding="utf-8"))
assert routing["version"] == 376
assert {r["canonicalPath"] for r in routing["routes"]} == set(ROUTES)

commerce = json.loads((ROOT / "alo186/content/commerce/subscription-deposit-refund-v376.json").read_text(encoding="utf-8"))
assert commerce["version"] == 376
assert commerce["commerce"]["new_affiliate_classes"] == 0
assert commerce["commerce"]["new_merchant_links"] == 0
for field in ("unverified_price", "unverified_stock", "unverified_rating", "unverified_warranty"):
    assert commerce["commerce"][field] is False, field
assert commerce["privacy"]["network_submission"] is False
assert commerce["privacy"]["persistent_browser_storage"] is False

for route, path in ROUTES.items():
    html = path.read_text(encoding="utf-8")
    payloads = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S | re.I)
    assert payloads, route
    json.loads(payloads[0])

print({"ok": True, "version": 376, "routes": list(ROUTES), "newMerchantLinks": 0})
