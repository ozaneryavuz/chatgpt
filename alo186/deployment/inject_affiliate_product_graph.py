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
SALES_EXTENSION = Path("akilli-urun-secimi/catalog-sales-extension.js")
GROWTH_EXTENSION = Path("akilli-urun-secimi/catalog-growth-run6.js")
MISSING_COMPONENT = Path("akilli-urun-secimi/run6-missing-component-set.js")
MARKER = 'data-alo186-product-graph-entry="true"'
EXTENSION_MARKER = 'data-alo186-product-graph-extension="true"'
SALES_EXTENSION_MARKER = 'data-alo186-product-sales-extension="true"'
GROWTH_EXTENSION_MARKER = 'data-alo186-product-growth-run6="true"'
MISSING_COMPONENT_MARKER = 'data-alo186-missing-component-run6="true"'
SCHEMA_ID = "affiliateProductGraphJsonLd"
TARGETS = [Path("amazon-elektrik-urunleri/index.html"), Path("akilli-urun-secimi/index.html"), Path("katalog-guven-durumu/index.html"), Path("elektrik-portali/index.html"), Path("index.html")]
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
            result.add(str(key)); collect_keys(nested, result)
    elif isinstance(value, list):
        for nested in value: collect_keys(nested, result)


def node_payload(site: Path) -> dict:
    growth_extension = (site / GROWTH_EXTENSION).resolve()
    required = [site / CATALOG, site / EXTENSION, site / SALES_EXTENSION, growth_extension, site / MISSING_COMPONENT]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Affiliate katalog/Knowledge Graph katmanı artifactta eksik: {missing}")
    script = f"""
const catalog=require({json.dumps(str(growth_extension))});
const categories=catalog.categories.map(category=>{{const relation=catalog.categoryRelations[category.id]||{{}};return {{id:category.id,name:category.name,needIds:catalog.categoryNeeds[category.id]||[],affiliatePolicy:category.affiliatePolicy,risk:category.risk,toolUrls:relation.tools||[],guideUrls:relation.guides||[],requiredEvidence:relation.evidence||[]}};}});
const products=catalog.products.filter(catalog.isCatalogProduct).map(product=>({{id:product.id,categoryId:product.category,name:product.name,brand:product.brand,model:product.model||product.mpn||product.id,identifier:{{type:product.asin?'ASIN':'Model',value:product.asin||product.model}},verificationStatus:product.status,verifiedAt:product.verifiedAt,linkMode:product.linkMode||'asin_detail',officialSource:product.technicalSource||undefined,needIds:product.needIds||catalog.categoryNeeds[product.category]||[],technicalProperties:product.attributes||{{}},relatedTools:product.relatedTools||[],relatedGuides:product.relatedGuides||[],requiredEvidence:product.requiredEvidence||[]}}));
const summary=catalog.knowledgeGraphSummary({{now:new Date('2026-07-30T12:00:00Z')}});
process.stdout.write(JSON.stringify({{graph:{{version:summary.version,generatedAt:summary.generatedAt,canonicalUrl:'https://www.alo186.com/urun-bilgi-grafigi/',commercialPolicy:{{affiliateDisclosureRequired:true,commercialRankingFieldsExcluded:['price','stock','rating','seller','delivery','warranty','affiliateCommission'],verificationMaxAgeDays:45,noBuyOutcomePreserved:true,professionalOnlyCategoriesNeverExposeAffiliateLinks:true,manufacturerVerifiedSearchRequiresExactModelRecheck:true}},needs:catalog.needs,categories,products}},schema:catalog.knowledgeGraph({{now:new Date('2026-07-30T12:00:00Z')}}),summary}}));
"""
    completed = subprocess.run(["node", "-e", script], check=True, capture_output=True, text=True)
    payload = json.loads(completed.stdout); graph = payload["graph"]; summary = payload["summary"]
    for key in ("needs", "categories", "products"):
        if not isinstance(graph.get(key), list) or not graph[key]: raise ValueError(f"Affiliate Product Knowledge Graph {key} düğümleri boş")
        ids = [item.get("id") for item in graph[key] if isinstance(item, dict)]
        if len(ids) != len(set(ids)) or any(not item for item in ids): raise ValueError(f"Affiliate Product Knowledge Graph {key} kimlikleri tekil değil")
    category_ids = {item["id"] for item in graph["categories"]}; need_ids = {item["id"] for item in graph["needs"]}
    if any(product.get("categoryId") not in category_ids for product in graph["products"]): raise ValueError("Ürün düğümünde katalogda bulunmayan kategori var")
    if any(not set(product.get("needIds") or []).issubset(need_ids) for product in graph["products"]): raise ValueError("Ürün düğümünde katalogda bulunmayan ihtiyaç ilişkisi var")
    exact_count = sum(product.get("identifier", {}).get("type") == "ASIN" for product in graph["products"])
    manufacturer_count = sum(product.get("identifier", {}).get("type") == "Model" for product in graph["products"])
    expected = {"needCount": len(graph["needs"]), "categoryCount": len(graph["categories"]), "productCount": len(graph["products"]), "exactListingCount": exact_count, "manufacturerSearchCount": manufacturer_count}
    for key, value in expected.items():
        if summary.get(key) != value: raise ValueError(f"Affiliate Product Knowledge Graph özeti uyuşmuyor: {key}={summary.get(key)} beklenen={value}")
    keys: set[str] = set(); collect_keys(graph["products"], keys); forbidden = FORBIDDEN.intersection(keys)
    if forbidden: raise ValueError(f"Graph ürün düğümlerinde yasak ticari alanlar bulundu: {sorted(forbidden)}")
    return payload


def write_graph_and_schema(site: Path, payload: dict) -> None:
    (site / GRAPH).write_text(json.dumps(payload["graph"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    page_path = site / PAGE; text = page_path.read_text(encoding="utf-8")
    pattern = re.compile(rf'(<script\s+id=["\']{SCHEMA_ID}["\']\s+type=["\']application/ld\+json["\']>)(.*?)(</script>)', re.I | re.S)
    updated, count = pattern.subn(r"\1" + json.dumps(payload["schema"], ensure_ascii=False, separators=(",", ":")) + r"\3", text, count=1)
    if count != 1: raise RuntimeError("Affiliate Product Knowledge Graph JSON-LD hedefi bulunamadı")
    page_path.write_text(updated, encoding="utf-8")


def inject_extension_scripts(site: Path, base_path: str) -> int:
    sources = [
        ("catalog-knowledge-extension.js", EXTENSION_MARKER, public_url(base_path, "/akilli-urun-secimi/catalog-knowledge-extension.js")),
        ("catalog-sales-extension.js", SALES_EXTENSION_MARKER, public_url(base_path, "/akilli-urun-secimi/catalog-sales-extension.js")),
        ("catalog-growth-run6.js", GROWTH_EXTENSION_MARKER, public_url(base_path, "/akilli-urun-secimi/catalog-growth-run6.js")),
    ]
    injected = 0
    for path in site.rglob("*.html"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "akilli-urun-secimi/catalog.js" not in text: continue
        catalog_match = re.search(r'<script[^>]+src=["\'][^"\']*akilli-urun-secimi/catalog\.js["\'][^>]*></script>', text, re.I)
        if not catalog_match: continue
        anchor = catalog_match.end()
        for filename, marker, src in sources:
            current = re.search(rf'<script[^>]+src=["\'][^"\']*{re.escape(filename)}["\'][^>]*></script>', text, re.I)
            if current:
                anchor = current.end(); continue
            tag = f'<script {marker} src="{src}"></script>'
            text = text[:anchor] + tag + text[anchor:]; anchor += len(tag); injected += 1
        if path.relative_to(site).as_posix() == "akilli-urun-secimi/index.html" and "run6-missing-component-set.js" not in text:
            tag = f'<script {MISSING_COMPONENT_MARKER} src="{public_url(base_path, "/akilli-urun-secimi/run6-missing-component-set.js")}"></script>'
            text = text.replace("</body>", tag + "</body>", 1); injected += 1
        path.write_text(text, encoding="utf-8")
    return injected


def entry_block(href: str, title: str, body: str) -> str:
    return f'<section {MARKER} style="max-width:1160px;margin:28px auto;padding:24px;border:1px solid #d9e3ef;border-radius:22px;background:#f4f8fd"><span style="font-size:.76rem;font-weight:900;color:#174bb9;text-transform:uppercase;letter-spacing:.07em">Affiliate Product Knowledge Graph</span><h2 style="color:#071631">{title}</h2><p>{body}</p><a href="{href}" style="display:inline-flex;min-height:44px;align-items:center;font-weight:900;color:#174bb9">Ürün bilgi grafiğini aç →</a><small style="display:block;margin-top:10px">Fiyat, stok, puan, satıcı, garanti ve komisyon sıralama alanı değildir.</small></section>'


def inject_entries(site: Path, base_path: str) -> int:
    href = public_url(base_path, ROUTE)
    copy = {"amazon-elektrik-urunleri/index.html": ("Ürünleri yalnız kategori olarak değil, ihtiyaç ve kanıt ilişkileriyle görün.", "Doğrulanmış ASIN, üretici modeli, ücretsiz araç, risk sınırı ve affiliate politikasını tek grafikte inceleyin."), "akilli-urun-secimi/index.html": ("Teknik eşleştirmenin arkasındaki ürün ilişkilerini inceleyin.", "Güncel katalogdaki doğrulanmış ürün ve üretici model düğümleri kaynak türüyle ayrı gösterilir."), "katalog-guven-durumu/index.html": ("Doğrulanmış ASIN ile üretici model doğrulamasını ayırın.", "Katalog tazeliği, kaynak türü ve mağaza bağlantısı biçimi ayrı düğümler olarak yayımlanır."), "elektrik-portali/index.html": ("Affiliate ürün Knowledge Graph", "İhtiyaçtan kategoriye, ücretsiz araca ve kaynak doğrulamalı ürün düğümüne ilerleyin."), "index.html": ("Affiliate ürün ilişkilerini görün.", "Ürün, ihtiyaç, teknik kanıt ve kaynak düğümlerini tek görünümde inceleyin.")}
    count = 0
    for relative in TARGETS:
        path = site / relative
        if not path.is_file(): continue
        text = path.read_text(encoding="utf-8")
        if MARKER in text or "</main>" not in text: continue
        title, body = copy[relative.as_posix()]
        path.write_text(text.replace("</main>", entry_block(href, title, body) + "</main>", 1), encoding="utf-8"); count += 1
    return count


def add_offline(site: Path, base_path: str) -> list[str]:
    path = site / "sw.js"
    if not path.is_file(): return []
    text = path.read_text(encoding="utf-8"); match = re.search(r"const CRITICAL=(\[.*?\]);", text, re.S)
    if not match: return []
    routes = json.loads(match.group(1)); candidates = [public_url(base_path, ROUTE), public_url(base_path, "/urun-bilgi-grafigi/product-graph.json")]
    added = [route for route in candidates if route not in routes]
    if added: routes.extend(added); path.write_text(text[:match.start(1)] + json.dumps(routes, ensure_ascii=False) + text[match.end(1):], encoding="utf-8")
    return added


def update_manifest(site: Path, base_path: str) -> None:
    path = site / "manifest.webmanifest"
    if not path.is_file(): return
    manifest = json.loads(path.read_text(encoding="utf-8")); shortcuts = manifest.setdefault("shortcuts", []); url = public_url(base_path, ROUTE)
    if not any(isinstance(item, dict) and item.get("url") == url for item in shortcuts): shortcuts.append({"name": "Affiliate Ürün Bilgi Grafiği", "short_name": "Ürün Grafiği", "url": url})
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def graph_metadata(base_path: str, payload: dict, cards: int, scripts: int, offline: list[str]) -> dict:
    graph = payload["graph"]; summary = payload["summary"]
    return {"version": summary["version"], "route": public_url(base_path, ROUTE), "graph": public_url(base_path, "/urun-bilgi-grafigi/product-graph.json"), "needCount": len(graph["needs"]), "categoryCount": len(graph["categories"]), "productCount": len(graph["products"]), "exactAsinCount": summary["exactListingCount"], "manufacturerVerifiedSearchCount": summary["manufacturerSearchCount"], "publicProductCount": summary.get("publicProductCount"), "gatedCandidateCount": summary.get("gatedCandidateCount"), "entryCardsInjected": cards, "extensionScriptsInjected": scripts, "offlineAssetsAdded": offline, "commercialRankingFieldsUsed": [], "noBuyOutcomePreserved": True, "directStoreLinksOnGraphJson": 0}


def update_release(site: Path, base_path: str, payload: dict, cards: int, scripts: int, offline: list[str]) -> None:
    metadata = graph_metadata(base_path, payload, cards, scripts, offline)
    core_path = site / "alo186-release.json"; core = json.loads(core_path.read_text(encoding="utf-8")); core["affiliateProductKnowledgeGraph"] = metadata; core_path.write_text(json.dumps(core, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pages_path = site / "pages-release.json"
    if pages_path.is_file():
        pages = json.loads(pages_path.read_text(encoding="utf-8")); pages["affiliateProductKnowledgeGraph"] = metadata; pages["offlineCriticalRouteCount"] = int(pages.get("offlineCriticalRouteCount") or 0) + len(offline); pages_path.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def recompute(site: Path) -> None:
    path = site / "checksums.sha256"
    if path.exists(): path.unlink()
    files = sorted(item for item in site.rglob("*") if item.is_file())
    path.write_text("\n".join(f"{hashlib.sha256(item.read_bytes()).hexdigest()}  {item.relative_to(site).as_posix()}" for item in files) + "\n", encoding="utf-8")


def run(site: Path, base_path: str = "") -> dict:
    site = site.resolve(); base_path = normalize_base_path(base_path); payload = node_payload(site); write_graph_and_schema(site, payload); scripts = inject_extension_scripts(site, base_path); cards = inject_entries(site, base_path); offline = add_offline(site, base_path); update_manifest(site, base_path); update_release(site, base_path, payload, cards, scripts, offline); recompute(site)
    return {"ok": True, "basePath": base_path, **graph_metadata(base_path, payload, cards, scripts, offline)}


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 affiliate ürünlerini kaynaklı Product Knowledge Graph olarak yayımlar."); parser.add_argument("--site", type=Path, required=True); parser.add_argument("--base-path", default=""); args = parser.parse_args(); print(json.dumps(run(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__": main()
