from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROUTE = "/urun-bilgi-grafigi/"
PAGE = Path("urun-bilgi-grafigi/index.html")
GRAPH = Path("urun-bilgi-grafigi/product-graph.json")
CATALOG = Path("akilli-urun-secimi/catalog.js")
EXTENSION = Path("akilli-urun-secimi/catalog-knowledge-extension.js")
MARKER = 'data-alo186-product-graph-entry="true"'
EXTENSION_MARKER = 'data-alo186-product-graph-extension="true"'
SCHEMA_ID = "affiliateProductGraphJsonLd"
TARGETS = [
    Path("amazon-elektrik-urunleri/index.html"),
    Path("akilli-urun-secimi/index.html"),
    Path("katalog-guven-durumu/index.html"),
    Path("elektrik-portali/index.html"),
    Path("index.html"),
]
FORBIDDEN = {"price", "stock", "rating", "seller", "delivery", "warranty", "affiliateCommission"}


def normalize_base_path(value: str) -> str:
    cleaned = str(value or "").strip()
    return "" if not cleaned or cleaned == "/" else "/" + cleaned.strip("/")


def public_url(base_path: str, route: str) -> str:
    route = "/" + route.lstrip("/")
    return f"{base_path}{route}" if base_path else route


def collect_keys(value, result: set[str]) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            result.add(str(key))
            collect_keys(nested, result)
    elif isinstance(value, list):
        for nested in value:
            collect_keys(nested, result)


def node_payload(site: Path) -> dict:
    extension = (site / EXTENSION).resolve()
    if not extension.is_file() or not (site / CATALOG).is_file():
        raise FileNotFoundError("Affiliate katalog veya Knowledge Graph uzantısı artifactta eksik")
    script = f"""
const catalog=require({json.dumps(str(extension))});
const categories=catalog.categories.map(category=>{{
 const relation=catalog.categoryRelations[category.id]||{{}};
 return {{id:category.id,name:category.name,needIds:catalog.categoryNeeds[category.id]||[],affiliatePolicy:category.affiliatePolicy,risk:category.risk,toolUrls:relation.tools||[],guideUrls:relation.guides||[],requiredEvidence:relation.evidence||[]}};
}});
const products=catalog.products.filter(catalog.isCatalogProduct).map(product=>({{
 id:product.id,categoryId:product.category,name:product.name,brand:product.brand,model:product.model||product.mpn||product.id,
 identifier:{{type:product.asin?'ASIN':'Model',value:product.asin||product.model}},verificationStatus:product.status,verifiedAt:product.verifiedAt,
 linkMode:product.linkMode||'asin_detail',officialSource:product.technicalSource||undefined,needIds:product.needIds||catalog.categoryNeeds[product.category]||[],
 technicalProperties:product.attributes||{{}},relatedTools:product.relatedTools||[],relatedGuides:product.relatedGuides||[],requiredEvidence:product.requiredEvidence||[]
}}));
process.stdout.write(JSON.stringify({{graph:{{version:'2026-07-29-run34b',generatedAt:'2026-07-29',canonicalUrl:'https://www.alo186.com/urun-bilgi-grafigi/',commercialPolicy:{{affiliateDisclosureRequired:true,commercialRankingFieldsExcluded:['price','stock','rating','seller','delivery','warranty','affiliateCommission'],verificationMaxAgeDays:45,noBuyOutcomePreserved:true,professionalOnlyCategoriesNeverExposeAffiliateLinks:true,manufacturerVerifiedSearchRequiresExactModelRecheck:true}},needs:catalog.needs,categories,products}},schema:catalog.knowledgeGraph({{now:new Date('2026-07-29T12:00:00Z')}}),summary:catalog.knowledgeGraphSummary()}}));
"""
    completed = subprocess.run(["node", "-e", script], check=True, capture_output=True, text=True)
    payload = json.loads(completed.stdout)
    graph = payload["graph"]
    summary = payload["summary"]
    if (len(graph["needs"]), len(graph["categories"]), len(graph["products"])) != (14, 14, 14):
        raise ValueError("Affiliate Product Knowledge Graph düğüm sayıları 14/14/14 değil")
    if summary.get("exactListingCount") != 10 or summary.get("manufacturerSearchCount") != 4:
        raise ValueError("ASIN/model doğrulama dağılımı 10/4 değil")
    keys: set[str] = set()
    collect_keys(graph["products"], keys)
    forbidden = FORBIDDEN.intersection(keys)
    if forbidden:
        raise ValueError(f"Graph ürün düğümlerinde yasak ticari alanlar bulundu: {sorted(forbidden)}")
    return payload


def write_graph_and_schema(site: Path, payload: dict) -> None:
    graph_path = site / GRAPH
    graph_path.write_text(json.dumps(payload["graph"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    page_path = site / PAGE
    text = page_path.read_text(encoding="utf-8")
    pattern = re.compile(rf'(<script\s+id=["\']{SCHEMA_ID}["\']\s+type=["\']application/ld\+json["\']>)(.*?)(</script>)', re.I | re.S)
    updated, count = pattern.subn(r"\1" + json.dumps(payload["schema"], ensure_ascii=False, separators=(",", ":")) + r"\3", text, count=1)
    if count != 1:
        raise RuntimeError("Affiliate Product Knowledge Graph JSON-LD hedefi bulunamadı")
    page_path.write_text(updated, encoding="utf-8")


def inject_extension_scripts(site: Path, base_path: str) -> int:
    src = public_url(base_path, "/akilli-urun-secimi/catalog-knowledge-extension.js")
    tag = f'<script {EXTENSION_MARKER} src="{src}"></script>'
    injected = 0
    for path in site.rglob("*.html"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "akilli-urun-secimi/catalog.js" not in text or EXTENSION_MARKER in text:
            continue
        match = re.search(r'<script[^>]+src=["\'][^"\']*akilli-urun-secimi/catalog\.js["\'][^>]*></script>', text, re.I)
        if not match:
            continue
        path.write_text(text[: match.end()] + tag + text[match.end() :], encoding="utf-8")
        injected += 1
    return injected


def entry_block(href: str, title: str, body: str) -> str:
    return f'<section {MARKER} style="max-width:1160px;margin:28px auto;padding:24px;border:1px solid #d9e3ef;border-radius:22px;background:#f4f8fd"><span style="font-size:.76rem;font-weight:900;color:#174bb9;text-transform:uppercase;letter-spacing:.07em">Affiliate Product Knowledge Graph</span><h2 style="color:#071631">{title}</h2><p>{body}</p><a href="{href}" style="display:inline-flex;min-height:44px;align-items:center;font-weight:900;color:#174bb9">Ürün bilgi grafiğini aç →</a><small style="display:block;margin-top:10px">Fiyat, stok, puan, satıcı, garanti ve komisyon sıralama alanı değildir.</small></section>'


def inject_entries(site: Path, base_path: str) -> int:
    href = public_url(base_path, ROUTE)
    copy = {
        "amazon-elektrik-urunleri/index.html": ("Ürünleri yalnız kategori olarak değil, ihtiyaç ve kanıt ilişkileriyle görün.", "ASIN, üretici modeli, ücretsiz araç, risk sınırı ve affiliate politikasını tek grafikte inceleyin."),
        "akilli-urun-secimi/index.html": ("Teknik eşleştirmenin arkasındaki ürün ilişkilerini inceleyin.", "Mevcut on ASIN korunurken dört üretici kaynaklı model düğümü tam model aramasıyla eklendi."),
        "katalog-guven-durumu/index.html": ("Doğrulanmış ASIN ile üretici model doğrulamasını ayırın.", "Katalog tazeliği, kaynak türü ve mağaza bağlantısı biçimi ayrı düğümler olarak yayımlanır."),
        "elektrik-portali/index.html": ("Affiliate ürün Knowledge Graph", "İhtiyaçtan kategoriye, ücretsiz araca ve kaynak doğrulamalı ürün düğümüne ilerleyin."),
        "index.html": ("Affiliate ürün ilişkilerini görün.", "Ürün, ihtiyaç, teknik kanıt ve kaynak düğümlerini tek görünümde inceleyin."),
    }
    count = 0
    for relative in TARGETS:
        path = site / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if MARKER in text:
            continue
        if "</main>" not in text:
            continue
        title, body = copy[relative.as_posix()]
        path.write_text(text.replace("</main>", entry_block(href, title, body) + "</main>", 1), encoding="utf-8")
        count += 1
    return count


def add_offline(site: Path, base_path: str) -> list[str]:
    path = site / "sw.js"
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    match = re.search(r"const CRITICAL=(\[.*?\]);", text, re.S)
    if not match:
        return []
    routes = json.loads(match.group(1))
    candidates = [public_url(base_path, ROUTE), public_url(base_path, "/urun-bilgi-grafigi/product-graph.json")]
    added = []
    for route in candidates:
        if route not in routes:
            routes.append(route)
            added.append(route)
    if added:
        path.write_text(text[: match.start(1)] + json.dumps(routes, ensure_ascii=False) + text[match.end(1) :], encoding="utf-8")
    return added


def update_manifest(site: Path, base_path: str) -> None:
    path = site / "manifest.webmanifest"
    if not path.is_file():
        return
    manifest = json.loads(path.read_text(encoding="utf-8"))
    shortcuts = manifest.setdefault("shortcuts", [])
    url = public_url(base_path, ROUTE)
    if not any(isinstance(item, dict) and item.get("url") == url for item in shortcuts):
        shortcuts.append({"name": "Affiliate Ürün Bilgi Grafiği", "short_name": "Ürün Grafiği", "url": url})
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_release(site: Path, base_path: str, payload: dict, cards: int, scripts: int, offline: list[str]) -> None:
    summary = payload["summary"]
    metadata = {"version": summary["version"], "route": public_url(base_path, ROUTE), "graph": public_url(base_path, "/urun-bilgi-grafigi/product-graph.json"), "needCount": 14, "categoryCount": 14, "productCount": 14, "exactAsinCount": 10, "manufacturerVerifiedSearchCount": 4, "entryCardsInjected": cards, "extensionScriptsInjected": scripts, "offlineAssetsAdded": offline, "commercialRankingFieldsUsed": [], "noBuyOutcomePreserved": True, "directStoreLinksOnGraphJson": 0}
    core_path = site / "alo186-release.json"
    core = json.loads(core_path.read_text(encoding="utf-8"))
    core["affiliateProductKnowledgeGraph"] = metadata
    core_path.write_text(json.dumps(core, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pages_path = site / "pages-release.json"
    if pages_path.is_file():
        pages = json.loads(pages_path.read_text(encoding="utf-8"))
        pages["affiliateProductKnowledgeGraph"] = metadata
        pages["offlineCriticalRouteCount"] = int(pages.get("offlineCriticalRouteCount") or 0) + len(offline)
        pages_path.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def recompute(site: Path) -> None:
    path = site / "checksums.sha256"
    if path.exists():
        path.unlink()
    files = sorted(item for item in site.rglob("*") if item.is_file())
    path.write_text("\n".join(f"{hashlib.sha256(item.read_bytes()).hexdigest()}  {item.relative_to(site).as_posix()}" for item in files) + "\n", encoding="utf-8")


def run(site: Path, base_path: str = "") -> dict:
    site = site.resolve()
    base_path = normalize_base_path(base_path)
    payload = node_payload(site)
    write_graph_and_schema(site, payload)
    scripts = inject_extension_scripts(site, base_path)
    cards = inject_entries(site, base_path)
    offline = add_offline(site, base_path)
    update_manifest(site, base_path)
    update_release(site, base_path, payload, cards, scripts, offline)
    recompute(site)
    return {"ok": True, "basePath": base_path, "route": public_url(base_path, ROUTE), "needCount": 14, "categoryCount": 14, "productCount": 14, "exactAsinCount": 10, "manufacturerVerifiedSearchCount": 4, "entryCardsInjected": cards, "extensionScriptsInjected": scripts, "offlineAssetsAdded": offline}


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 affiliate ürünlerini kaynaklı Product Knowledge Graph olarak yayımlar.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
