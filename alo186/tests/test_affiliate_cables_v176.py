from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "amazon-elektrik-urunleri" / "usb-c-displayport-kablo-secimi" / "index.html"
EXPECTED = {
    "B0C4DB8MLL": "25158",
    "B0B46PHW14": "CAJY000701",
    "B088GQM9CV": "80392",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def main() -> None:
    html = PAGE.read_text(encoding="utf-8")

    canonical = "https://alo186.com/amazon-elektrik-urunleri/usb-c-displayport-kablo-secimi/"
    if html.count(f'<link rel="canonical" href="{canonical}">') != 1:
        fail("Canonical eksik veya yinelenmiş")

    scripts = re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', html, re.S)
    if len(scripts) != 1:
        fail("Tek Knowledge Graph JSON-LD bekleniyor")
    graph = json.loads(scripts[0])["@graph"]
    products = [node for node in graph if node.get("@type") == "Product"]
    lists = [node for node in graph if node.get("@type") == "ItemList"]
    if len(products) != 3 or len(lists) != 1 or lists[0].get("numberOfItems") != 3:
        fail("Product / ItemList sözleşmesi bozuk")

    seen_asins: set[str] = set()
    for product in products:
        if product.get("offers") is not None:
            fail("Offer yayımlanamaz")
        if product.get("brand", {}).get("@type") != "Brand":
            fail("Brand düğümü eksik")
        properties = product.get("additionalProperty", [])
        if len(properties) < 3:
            fail("additionalProperty yetersiz")
        identifiers = {item.get("propertyID"): item.get("value") for item in product.get("identifier", [])}
        asin = identifiers.get("ASIN")
        mpn = identifiers.get("MPN")
        if asin not in EXPECTED or EXPECTED[asin] != mpn:
            fail(f"ASIN/MPN eşleşmesi geçersiz: {asin}/{mpn}")
        if asin in seen_asins:
            fail(f"Duplicate ASIN: {asin}")
        seen_asins.add(asin)

    for forbidden in ("aggregateRating", "priceCurrency", '"price"', '"availability"', '"seller"'):
        if forbidden in scripts[0]:
            fail(f"Yasak ticari alan: {forbidden}")

    if "alo186rehber-21" not in html:
        fail("Affiliate tag eksik")
    if 'rel="sponsored nofollow noopener"' not in html:
        fail("Affiliate rel sözleşmesi eksik")
    if "Mağaza bağlantıları kapalı" not in html or "checks.every" not in html:
        fail("Üçlü güven kapısı eksik")
    if "Satın almama koşulu" not in html or "Reklam / satış ortaklığı açıklaması" not in html:
        fail("Görünür güven metinleri eksik")

    initial_markup = re.sub(r"<script\b[^>]*>.*?</script>", "", html, flags=re.S | re.I)
    static_amazon = re.findall(r'<a\b[^>]*href="https://www\.amazon\.com\.tr/dp/', initial_markup, re.I)
    if static_amazon:
        fail("Amazon bağlantısı ilk HTML DOM içinde kapısız yayımlanamaz")
    if "allowed?`<a class=\"shop\"" not in html:
        fail("Amazon bağlantısı yalnız açık güven kapısında üretilmeli")

    verified = re.search(r"1 Ağustos 2026 tarihinde doğrulandı", html)
    if not verified:
        fail("Tazelik doğrulama tarihi eksik")

    print(json.dumps({"ok": True, "products": len(products), "asins": sorted(seen_asins)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
