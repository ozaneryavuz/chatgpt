from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

CANONICAL_PATH = "/urun-bilgi-grafigi/"
GRAPH_RELATIVE = Path("urun-bilgi-grafigi/product-graph.json")
PAGE_RELATIVE = Path("urun-bilgi-grafigi/index.html")
CATALOG_RELATIVE = Path("akilli-urun-secimi/catalog.js")
PRODUCT_HUB = Path("amazon-elektrik-urunleri/index.html")
PRODUCT_CENTER = Path("akilli-urun-secimi/index.html")
TRUST_CENTER = Path("katalog-guven-durumu/index.html")
PORTAL = Path("elektrik-portali/index.html")
GATEWAY = Path("index.html")
CARD_MARKER = 'data-alo186-product-graph-entry="true"'
SCHEMA_ID = "affiliateProductGraphJsonLd"
FORBIDDEN_FIELDS = {"price", "stock", "rating", "seller", "delivery", "warranty", "affiliateCommission"}


def normalize_base_path(value: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned or cleaned == "/":
        return ""
    return "/" + cleaned.strip("/")


def public_url(base_path: str, route: str) -> str:
    route = "/" + route.lstrip("/")
    return f"{base_path}{route}" if base_path else route


def walk_keys(value, found: set[str]) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            found.add(str(key))
            walk_keys(nested, found)
    elif isinstance(value, list):
        for nested in value:
            walk_keys(nested, found)


def load_graph(site: Path) -> dict:
    path = site / GRAPH_RELATIVE
    if not path.is_file():
        raise FileNotFoundError(f"Affiliate ürün bilgi grafiği verisi eksik: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    needs = payload.get("needs")
    categories = payload.get("categories")
    products = payload.get("products")
    if not isinstance(needs, list) or len(needs) < 10:
        raise ValueError("Affiliate ürün bilgi grafiği ihtiyaç düğümleri eksik")
    if not isinstance(categories, list) or len(categories) < 10:
        raise ValueError("Affiliate ürün bilgi grafiği kategori düğümleri eksik")
    if not isinstance(products, list) or len(products) < 10:
        raise ValueError("Affiliate ürün bilgi grafiği ürün düğümleri eksik")
    category_ids = {item.get("id") for item in categories}
    need_ids = {item.get("id") for item in needs}
    product_ids: set[str] = set()
    for product in products:
        product_id = str(product.get("id") or "")
        if not product_id or product_id in product_ids:
            raise ValueError(f"Affiliate ürün bilgi grafiğinde geçersiz/yinelenen ürün: {product_id!r}")
        product_ids.add(product_id)
        if product.get("categoryId") not in category_ids:
            raise ValueError(f"Ürün kategori ilişkisi bozuk: {product_id}")
        if not set(product.get("needIds") or []).issubset(need_ids):
            raise ValueError(f"Ürün ihtiyaç ilişkisi bozuk: {product_id}")
        if product.get("verificationStatus") not in {"verified_listing", "manufacturer_verified_search"}:
            raise ValueError(f"Ürün doğrulama durumu desteklenmiyor: {product_id}")
        if product.get("linkMode") not in {"asin_detail", "exact_model_search"}:
            raise ValueError(f"Ürün link biçimi desteklenmiyor: {product_id}")
        if product.get("verificationStatus") == "verified_listing" and product.get("identifier", {}).get("type") != "ASIN":
            raise ValueError(f"Doğrulanmış listing ASIN taşımıyor: {product_id}")
        if product.get("verificationStatus") == "manufacturer_verified_search" and not product.get("officialSource"):
            raise ValueError(f"Üretici doğrulamalı model resmî kaynak taşımıyor: {product_id}")
    keys: set[str] = set()
    walk_keys(payload.get("products"), keys)
    forbidden = FORBIDDEN_FIELDS.intersection(keys)
    if forbidden:
        raise ValueError(f"Ürün bilgi grafiğinde yasak ticari alanlar bulundu: {sorted(forbidden)}")
    return payload


def schema_graph(payload: dict) -> dict:
    base = "https://www.alo186.com/urun-bilgi-grafigi/"
    nodes: list[dict] = [
        {"@type": "DefinedTermSet", "@id": f"{base}#need-set", "name": "ALO186 elektrik kullanıcı ihtiyaçları"},
        {"@type": "DefinedTermSet", "@id": f"{base}#category-set", "name": "ALO186 affiliate ürün kategorileri"},
    ]
    for need in payload["needs"]:
        nodes.append({
            "@type": "DefinedTerm",
            "@id": f"{base}#need-{need['id']}",
            "name": need["name"],
            "inDefinedTermSet": {"@id": f"{base}#need-set"},
        })
    for category in payload["categories"]:
        nodes.append({
            "@type": "DefinedTerm",
            "@id": f"{base}#category-{category['id']}",
            "name": category["name"],
            "inDefinedTermSet": {"@id": f"{base}#category-set"},
            "isRelatedTo": [{"@id": f"{base}#need-{need_id}"} for need_id in category.get("needIds", [])],
            "additionalProperty": [
                {"@type": "PropertyValue", "name": "Affiliate policy", "value": category.get("affiliatePolicy")},
                {"@type": "PropertyValue", "name": "Risk class", "value": category.get("risk")},
            ],
        })
    for product in payload["products"]:
        properties = [
            {"@type": "PropertyValue", "name": str(key), "value": str(value)}
            for key, value in (product.get("technicalProperties") or {}).items()
        ]
        properties.extend([
            {"@type": "PropertyValue", "name": "Verification status", "value": product["verificationStatus"]},
            {"@type": "PropertyValue", "name": "Verified at", "value": product["verifiedAt"]},
            {"@type": "PropertyValue", "name": "Affiliate link mode", "value": product["linkMode"]},
        ])
        node = {
            "@type": "Product",
            "@id": f"{base}#product-{product['id']}",
            "name": product["name"],
            "brand": {"@type": "Brand", "name": product["brand"]},
            "model": product["model"],
            "identifier": {
                "@type": "PropertyValue",
                "propertyID": product["identifier"]["type"],
                "value": product["identifier"]["value"],
            },
            "category": {"@id": f"{base}#category-{product['categoryId']}"},
            "url": f"{base}#product-{product['id']}",
            "additionalProperty": properties,
            "isRelatedTo": [
                *({"@id": f"{base}#need-{need_id}"} for need_id in product.get("needIds", [])),
                *({"@type": "WebApplication", "url": f"https://www.alo186.com{url}"} for url in product.get("relatedTools", [])),
                *({"@type": "Article", "url": f"https://www.alo186.com{url}"} for url in product.get("relatedGuides", [])),
            ],
        }
        if product.get("officialSource"):
            node["sameAs"] = product["officialSource"]
        nodes.append(node)
    nodes.insert(0, {
        "@type": "ItemList",
        "@id": f"{base}#product-list",
        "name": "ALO186 kaynak doğrulamalı affiliate ürün düğümleri",
        "numberOfItems": len(payload["products"]),
        "itemListElement": [
            {"@type": "ListItem", "position": index + 1, "item": {"@id": f"{base}#product-{product['id']}"}}
            for index, product in enumerate(payload["products"])
        ],
    })
    return {"@context": "https://schema.org", "@graph": nodes}


def inject_schema(site: Path, payload: dict) -> None:
    path = site / PAGE_RELATIVE
    if not path.is_file():
        raise FileNotFoundError(f"Affiliate ürün bilgi grafiği sayfası eksik: {path}")
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(
        rf'(<script\s+id=["\']{re.escape(SCHEMA_ID)}["\']\s+type=["\']application/ld\+json["\']>)(.*?)(</script>)',
        re.I | re.S,
    )
    replacement = r"\1" + json.dumps(schema_graph(payload), ensure_ascii=False, separators=(",", ":")) + r"\3"
    updated, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise RuntimeError("Affiliate ürün bilgi grafiği JSON-LD hedefi bulunamadı")
    path.write_text(updated, encoding="utf-8")


def insert_before(text: str, marker: str, block: str) -> tuple[str, bool]:
    if CARD_MARKER in text:
        return text, False
    if marker not in text:
        return text, False
    return text.replace(marker, block + marker, 1), True


def inject_entry_cards(site: Path, base_path: str) -> int:
    href = public_url(base_path, CANONICAL_PATH)
    cards = 0
    targets = [
        (
            PRODUCT_HUB,
            '<section class="section"',
            f'<section class="section" {CARD_MARKER}><div class="section-head"><div><span class="eyebrow">Knowledge Graph</span><h2>Ürünleri ihtiyaç, kanıt ve kaynak ilişkileriyle inceleyin.</h2><p class="lead">Kategori listesinden daha fazlasını görün: ücretsiz araç, üretici kaynağı, model/ASIN ayrımı, risk kapısı ve satın almama sonucu tek grafikte bağlıdır.</p></div><a class="button primary" href="{href}">Ürün bilgi grafiğini aç</a></div></section>',
        ),
        (
            PRODUCT_CENTER,
            '<section id="matcher"',
            f'<section class="content-section" {CARD_MARKER}><div class="panel"><span class="eyebrow">Affiliate Product Knowledge Graph</span><h2>Bu kategori ve ürün düğümleri hangi kanıtlara bağlı?</h2><p>Üretici kaynağı, ücretsiz araç, risk sınırı, model/ASIN ve affiliate politikası ilişkilerini görün. Yeni Tapo P110/P110M, EcoFlow RIVER 2 ve X-Sense XS01 düğümleri kaynaklarıyla eklendi.</p><div class="actions"><a class="btn btn-secondary" href="{href}">Ürün bilgi grafiğini aç</a></div><small>Fiyat, stok, puan, satıcı, garanti veya komisyon sıralama alanı değildir.</small></div></section>',
        ),
        (
            TRUST_CENTER,
            '<section class="catalog-section"',
            f'<section class="partner-cta" {CARD_MARKER}><div><span class="eyebrow">Makine okunabilir ürün ilişkileri</span><h2>Katalog güvenini Knowledge Graph üzerinde izleyin.</h2><p>Doğrulanmış ASIN ile üretici teknik verisi doğrulanmış tam model aramasını ayrı düğümler olarak görün.</p></div><a class="button primary" href="{href}">Bilgi grafiğini aç</a></section>',
        ),
    ]
    for relative, marker, block in targets:
        path = site / relative
        if not path.is_file():
            continue
        text, added = insert_before(path.read_text(encoding="utf-8"), marker, block)
        if added:
            path.write_text(text, encoding="utf-8")
            cards += 1

    for relative, gateway in [(PORTAL, False), (GATEWAY, True)]:
        path = site / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if CARD_MARKER in text:
            continue
        if gateway:
            card = f'<a class="card" {CARD_MARKER} href="{href}"><strong>Affiliate ürün ilişkilerini görün</strong><p>İhtiyaç, kategori, teknik kanıt ve kaynak düğümlerini tek grafikte inceleyin.</p><span>Ürün bilgi grafiğini aç →</span></a>'
        else:
            card = f'<a class="card" {CARD_MARKER} href="{href}"><span class="tag">Knowledge Graph · affiliate şeffaflığı</span><h2>Ürün Bilgi Grafiği</h2><p>ASIN, tam model, üretici kaynağı, ücretsiz araç ve risk sınırını tek ilişkisel görünümde inceleyin.</p><b>Bilgi grafiğini aç →</b></a>'
        for match in re.finditer(r'<section\b[^>]*>', text, re.I):
            classes = re.search(r'class=["\']([^"\']*)["\']', match.group(0), re.I)
            if classes and "grid" in classes.group(1).split():
                text = text[: match.end()] + card + text[match.end() :]
                path.write_text(text, encoding="utf-8")
                cards += 1
                break
    return cards


def update_manifest(site: Path, base_path: str) -> None:
    path = site / "manifest.webmanifest"
    if not path.is_file():
        return
    manifest = json.loads(path.read_text(encoding="utf-8"))
    shortcuts = manifest.setdefault("shortcuts", [])
    url = public_url(base_path, CANONICAL_PATH)
    if not any(isinstance(item, dict) and item.get("url") == url for item in shortcuts):
        shortcuts.append({"name": "Affiliate Ürün Bilgi Grafiği", "short_name": "Ürün Grafiği", "url": url})
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def add_offline(site: Path, base_path: str) -> list[str]:
    path = site / "sw.js"
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    match = re.search(r"const CRITICAL=(\[.*?\]);", text, re.S)
    if not match:
        raise RuntimeError("Service worker CRITICAL rota dizisi bulunamadı")
    routes = json.loads(match.group(1))
    candidates = [public_url(base_path, CANONICAL_PATH), public_url(base_path, "/urun-bilgi-grafigi/product-graph.json")]
    added: list[str] = []
    for route in candidates:
        if route not in routes:
            routes.append(route)
            added.append(route)
    if added:
        path.write_text(text[: match.start(1)] + json.dumps(routes, ensure_ascii=False) + text[match.end(1) :], encoding="utf-8")
    return added


def update_release(site: Path, base_path: str, payload: dict, cards: int, offline_added: list[str]) -> None:
    exact = sum(1 for product in payload["products"] if product["verificationStatus"] == "verified_listing")
    manufacturer = sum(1 for product in payload["products"] if product["verificationStatus"] == "manufacturer_verified_search")
    metadata = {
        "version": payload["version"],
        "route": public_url(base_path, CANONICAL_PATH),
        "graph": public_url(base_path, "/urun-bilgi-grafigi/product-graph.json"),
        "needCount": len(payload["needs"]),
        "categoryCount": len(payload["categories"]),
        "productCount": len(payload["products"]),
        "exactAsinCount": exact,
        "manufacturerVerifiedSearchCount": manufacturer,
        "entryCardsInjected": cards,
        "offlineAssetsAdded": offline_added,
        "commercialRankingFieldsUsed": [],
        "noBuyOutcomePreserved": True,
        "directStoreLinksOnGraphData": 0,
    }
    core_path = site / "alo186-release.json"
    core = json.loads(core_path.read_text(encoding="utf-8"))
    core["affiliateProductKnowledgeGraph"] = metadata
    core_path.write_text(json.dumps(core, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pages_path = site / "pages-release.json"
    if pages_path.is_file():
        pages = json.loads(pages_path.read_text(encoding="utf-8"))
        pages["affiliateProductKnowledgeGraph"] = metadata
        pages["offlineCriticalRouteCount"] = int(pages.get("offlineCriticalRouteCount") or 0) + len(offline_added)
        pages_path.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def recompute(site: Path) -> None:
    checksum = site / "checksums.sha256"
    if checksum.exists():
        checksum.unlink()
    lines = [
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(site).as_posix()}"
        for path in sorted(item for item in site.rglob("*") if item.is_file())
    ]
    checksum.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(site: Path, base_path: str = "") -> dict:
    site = site.resolve()
    base_path = normalize_base_path(base_path)
    if not (site / CATALOG_RELATIVE).is_file():
        raise FileNotFoundError("Affiliate ürün kataloğu artifactta eksik")
    payload = load_graph(site)
    inject_schema(site, payload)
    cards = inject_entry_cards(site, base_path)
    update_manifest(site, base_path)
    offline_added = add_offline(site, base_path)
    update_release(site, base_path, payload, cards, offline_added)
    recompute(site)
    return {
        "ok": True,
        "basePath": base_path,
        "route": public_url(base_path, CANONICAL_PATH),
        "needCount": len(payload["needs"]),
        "categoryCount": len(payload["categories"]),
        "productCount": len(payload["products"]),
        "manufacturerVerifiedSearchCount": sum(1 for product in payload["products"] if product["verificationStatus"] == "manufacturer_verified_search"),
        "entryCardsInjected": cards,
        "offlineAssetsAdded": offline_added,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 affiliate ürünlerini Knowledge Graph, schema ve güvenli giriş noktalarıyla yayınlar.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
