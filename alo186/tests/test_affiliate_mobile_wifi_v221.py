from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
ROUTE = ROOT / "amazon-elektrik-urunleri" / "tasinabilir-4g-mobil-wifi-secimi"
PAGE = ROUTE / "index.html"
CATALOG = ROUTE / "catalog-v221.js"
APP = ROUTE / "app-v221.js"
OVERLAY = ROOT / "deployment" / "routing-overlays" / "221-affiliate-mobile-wifi.json"
EXPECTED = {
    "B079GZNQ2B": "M7200",
    "B01EK8CVHW": "M7350",
    "B08BS3SHZV": "M7000",
}
CANONICAL = "https://alo186.com/amazon-elektrik-urunleri/tasinabilir-4g-mobil-wifi-secimi/"


def fail(message: str) -> None:
    raise AssertionError(message)


def walk_json(value: object):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_json(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_json(child)


def test_page_and_knowledge_graph() -> None:
    html = PAGE.read_text(encoding="utf-8")
    if html.count(f'<link rel="canonical" href="{CANONICAL}">') != 1:
        fail("Apex canonical eksik veya yinelenmiş")
    if "https://www.alo186.com" in html:
        fail("Legacy www canonical/origin yayımlanamaz")

    scripts = re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', html, re.S)
    if len(scripts) != 1:
        fail("Tek Knowledge Graph JSON-LD bekleniyor")
    payload = json.loads(scripts[0])
    graph = payload.get("@graph", [])
    products = [node for node in graph if node.get("@type") == "Product"]
    item_lists = [node for node in graph if node.get("@type") == "ItemList"]
    if len(products) != 3:
        fail("Tam üç Product düğümü bekleniyor")
    if len(item_lists) != 1 or item_lists[0].get("numberOfItems") != 3:
        fail("ItemList sözleşmesi bozuk")
    if len(item_lists[0].get("itemListElement", [])) != 3:
        fail("ItemList üç ürünü bağlamıyor")

    seen: set[str] = set()
    for product in products:
        if product.get("brand", {}).get("@type") != "Brand":
            fail("Brand düğümü eksik")
        identifiers = {
            item.get("propertyID"): item.get("value")
            for item in product.get("identifier", [])
        }
        asin = identifiers.get("ASIN")
        mpn = identifiers.get("MPN")
        if asin not in EXPECTED or EXPECTED[asin] != mpn:
            fail(f"ASIN/MPN eşleşmesi geçersiz: {asin}/{mpn}")
        if asin in seen:
            fail(f"Duplicate ASIN: {asin}")
        seen.add(asin)
        properties = product.get("additionalProperty", [])
        if len(properties) < 4:
            fail(f"additionalProperty yetersiz: {asin}")
        if not all(item.get("@type") == "PropertyValue" for item in properties):
            fail(f"additionalProperty tipi geçersiz: {asin}")

    forbidden_keys = {
        "offers", "price", "priceCurrency", "availability", "seller",
        "aggregateRating", "review", "ratingValue", "warranty",
    }
    for node in walk_json(payload):
        collision = forbidden_keys.intersection(node)
        if collision:
            fail(f"Yasak ticari alan: {sorted(collision)}")
        if node.get("@type") == "Offer":
            fail("Offer şeması yayımlanamaz")

    required_visible = (
        "Reklam / satış ortaklığı açıklaması",
        "Kullanıcı ihtiyacı:",
        "Güçlü yönler",
        "Sınırlamalar",
        "Satın almama koşulu:",
        "Profesyonel ve can güvenliği haberleşmesini bu ürünlerle kurmayın",
    )
    for token in required_visible:
        if token not in html:
            fail(f"Görünür kullanıcı güven alanı eksik: {token}")
    if html.count("Kullanıcı ihtiyacı:") != 3:
        fail("Her ürün kartında kullanıcı ihtiyacı bulunmalı")
    if html.count("Satın almama koşulu:") != 3:
        fail("Her ürün kartında satın almama koşulu bulunmalı")
    if html.count('rel="sponsored nofollow noopener"') != 3:
        fail("Her mağaza hedefinde sponsored/nofollow/noopener zorunlu")
    if re.search(r'href=["\']https://www\.amazon\.com\.tr/', html, re.I):
        fail("Amazon bağlantısı ilk HTML içinde etkin href olarak yayımlanamaz")


def test_after_tool_and_affiliate_contract() -> None:
    html = PAGE.read_text(encoding="utf-8")
    catalog = CATALOG.read_text(encoding="utf-8")
    app = APP.read_text(encoding="utf-8")

    for token in (
        "affiliateTag = 'alo186rehber-21'",
        "verificationMaxAgeDays = 45",
        "affiliatePolicy: 'after_tool'",
        "requiredTool: 'embedded-mobile-wifi-compatibility-v221'",
        "professionalOnly: false",
        "risk: 'consumer-medium'",
    ):
        if token not in catalog:
            fail(f"Katalog güven sözleşmesi eksik: {token}")

    for token in (
        "toolPassed && allChecked(commerceChecks) && freshness.fresh",
        "catalog.category.affiliatePolicy === 'after_tool'",
        "catalog.category.professionalOnly === false",
        "link.removeAttribute('href')",
    ):
        if token not in app:
            fail(f"after_tool fail-closed kapısı eksik: {token}")

    for control in (
        'id="toolCoverage"', 'id="toolSim"', 'id="toolCapacity"',
        'id="toolPower"', 'id="gateNeed"', 'id="gateAffiliate"',
    ):
        if control not in html:
            fail(f"Güven kontrolü eksik: {control}")

    if "amazon.com.tr" in html.casefold():
        fail("Kaynak HTML Amazon alan adı içeremez")
    if "https://www.amazon.com.tr/dp/" not in catalog:
        fail("Kapı sonrası exact ASIN URL üreticisi eksik")


def test_duplicate_asins_repository_wide() -> None:
    allowed_suffixes = {".html", ".js", ".json", ".py", ".md", ".yml", ".yaml"}
    current_test = Path(__file__).resolve()
    duplicates: dict[str, list[str]] = {asin: [] for asin in EXPECTED}
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in allowed_suffixes:
            continue
        resolved = path.resolve()
        if resolved == current_test or ROUTE.resolve() in resolved.parents:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for asin in EXPECTED:
            if asin in text:
                duplicates[asin].append(str(path.relative_to(REPO_ROOT)))
    collisions = {asin: files for asin, files in duplicates.items() if files}
    if collisions:
        fail(f"Repository-geneli duplicate ASIN: {collisions}")


def test_stale_gate_and_javascript() -> None:
    subprocess.run(["node", "--check", str(CATALOG)], check=True)
    subprocess.run(["node", "--check", str(APP)], check=True)
    script = f"""
      const c=require({json.dumps(str(CATALOG))});
      const assert=require('node:assert/strict');
      assert.equal(c.products.length,3);
      assert.deepEqual(c.products.map(x=>x.asin).sort(),{json.dumps(sorted(EXPECTED))});
      assert.equal(c.verificationStatus(new Date('2026-09-16T00:00:00Z')).ageDays,45);
      assert.equal(c.verificationStatus(new Date('2026-09-16T00:00:00Z')).fresh,true);
      assert.equal(c.verificationStatus(new Date('2026-09-17T00:00:00Z')).ageDays,46);
      assert.equal(c.verificationStatus(new Date('2026-09-17T00:00:00Z')).fresh,false);
      for (const asin of Object.keys({json.dumps(EXPECTED)})) {{
        const url=c.amazonProductUrl(asin);
        assert.match(url,new RegExp('/dp/'+asin+'\\?tag=alo186rehber-21$'));
      }}
      assert.throws(()=>c.amazonProductUrl('B000000000'));
    """
    subprocess.run(["node", "-e", script], check=True)


def test_routing_overlay() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    if overlay.get("version") != 221 or len(overlay.get("routes", [])) != 1:
        fail("Routing overlay v221 sözleşmesi bozuk")
    route = overlay["routes"][0]
    if route.get("canonicalPath") != "/amazon-elektrik-urunleri/tasinabilir-4g-mobil-wifi-secimi/":
        fail("Routing canonicalPath yanlış")
    if route.get("source") != "alo186/amazon-elektrik-urunleri/tasinabilir-4g-mobil-wifi-secimi/index.html":
        fail("Routing source yanlış")
    if route.get("type") != "collection":
        fail("Routing type yanlış")


def main() -> None:
    test_page_and_knowledge_graph()
    test_after_tool_and_affiliate_contract()
    test_duplicate_asins_repository_wide()
    test_stale_gate_and_javascript()
    test_routing_overlay()
    print(json.dumps({
        "ok": True,
        "canonical": CANONICAL,
        "products": len(EXPECTED),
        "asins": sorted(EXPECTED),
        "knowledgeGraph": ["Product", "Brand", "ItemList", "identifier", "additionalProperty"],
        "affiliatePolicy": "after_tool",
        "professionalOnlyBypass": False,
        "staticAmazonHref": False,
        "freshDay45": True,
        "staleDay46": True,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
