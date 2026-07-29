from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = REPO_ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

from build_static_site import load_effective_manifest  # noqa: E402
from inject_affiliate_product_graph import load_graph, schema_graph  # noqa: E402

ROUTE = "/urun-bilgi-grafigi/"
SOURCE = "alo186/urun-bilgi-grafigi/index.html"
NEW_PRODUCTS = {"tp-link-tapo-p110", "tp-link-tapo-p110m", "ecoflow-river-2", "x-sense-xs01"}
FORBIDDEN_COMMERCIAL = {"price", "stock", "rating", "seller", "delivery", "warranty", "affiliateCommission"}


def node_catalog_summary() -> dict:
    script = r"""
const c=require('./alo186/urun-eslestirme/catalog.js');
process.stdout.write(JSON.stringify({
  categories:c.categories.map(x=>x.id).sort(),
  needs:c.needs.map(x=>x.id).sort(),
  products:c.products.map(x=>x.id).sort(),
  newProducts:c.products.filter(x=>x.status==='manufacturer_verified_search').map(x=>({id:x.id,category:x.category,source:x.technicalSource,linkMode:x.linkMode,asin:x.asin,url:x.url})).sort((a,b)=>a.id.localeCompare(b.id)),
  summary:c.knowledgeGraphSummary()
}));
"""
    completed = subprocess.run(["node", "-e", script], cwd=REPO_ROOT, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def collect_keys(value, result: set[str]) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            result.add(str(key))
            collect_keys(nested, result)
    elif isinstance(value, list):
        for nested in value:
            collect_keys(nested, result)


def main() -> None:
    manifest = load_effective_manifest(REPO_ROOT)
    assert manifest["version"] >= 64
    routes = [route for route in manifest["routes"] if route["canonicalPath"] == ROUTE]
    assert len(routes) == 1
    assert routes[0]["source"] == SOURCE
    assert routes[0]["type"] == "commerce-guide"

    graph_path = REPO_ROOT / "alo186/urun-bilgi-grafigi/product-graph.json"
    graph = load_graph(REPO_ROOT / "alo186")
    page = (REPO_ROOT / SOURCE).read_text(encoding="utf-8")
    app = (REPO_ROOT / "alo186/urun-bilgi-grafigi/app.js").read_text(encoding="utf-8")
    styles = REPO_ROOT / "alo186/urun-bilgi-grafigi/styles.css"
    injector = (REPO_ROOT / "alo186/deployment/inject_affiliate_product_graph.py").read_text(encoding="utf-8")
    pipeline = (REPO_ROOT / "alo186/deployment/inject_growth_run15.py").read_text(encoding="utf-8")
    catalog_summary = node_catalog_summary()

    assert graph_path.is_file()
    assert styles.is_file() and styles.stat().st_size > 6000
    assert len(graph["needs"]) == 14
    assert len(graph["categories"]) == 14
    assert len(graph["products"]) == 11
    graph_product_ids = {product["id"] for product in graph["products"]}
    assert graph_product_ids == set(catalog_summary["products"])
    assert {category["id"] for category in graph["categories"]} == set(catalog_summary["categories"])
    assert {need["id"] for need in graph["needs"]} == set(catalog_summary["needs"])
    assert NEW_PRODUCTS.issubset(graph_product_ids)
    assert {item["id"] for item in catalog_summary["newProducts"]} == NEW_PRODUCTS

    for item in catalog_summary["newProducts"]:
        assert item["asin"] is None
        assert item["linkMode"] == "exact_model_search"
        assert item["source"].startswith("https://")
        assert item["url"].startswith("https://www.amazon.com.tr/s?k=")
        assert "tag=alo186hazirlik-21" in item["url"]

    assert 'rel="canonical" href="https://www.alo186.com/urun-bilgi-grafigi/"' in page
    assert "CollectionPage" in page and "FAQPage" in page and "BreadcrumbList" in page
    assert 'id="affiliateProductGraphJsonLd"' in page
    assert 'href="./product-graph.json"' in page
    assert "/akilli-urun-secimi/catalog.js" in page
    assert "Tapo P110" in page and "EcoFlow RIVER 2" in page and "X-Sense XS01" in page
    assert "amazon.com.tr" not in page.casefold(), "Kaynak HTML doğrudan mağaza linki taşımamalı; bağlantılar katalog ve güven kapısından gelmeli"
    assert "<form" not in page.casefold() and "type=\"email\"" not in page.casefold() and "type=\"tel\"" not in page.casefold()

    assert "sponsored nofollow noopener" in app
    assert "gateReady" in app
    assert "İlgili ücretsiz uygunluk aracını tamamladım" in app
    assert "Mevcut ürünüm güvenli biçimde ihtiyacı karşılamıyor" in app
    assert "affiliate_knowledge_graph_link_opened" in app
    assert "localStorage" not in app and "sessionStorage" not in app
    assert "innerHTML" not in app, "Grafik ürün düğümleri ham HTML ile üretilmemeli"

    keys: set[str] = set()
    collect_keys(graph["products"], keys)
    assert not FORBIDDEN_COMMERCIAL.intersection(keys)
    assert graph["commercialPolicy"]["noBuyOutcomePreserved"] is True
    assert graph["commercialPolicy"]["professionalOnlyCategoriesNeverExposeAffiliateLinks"] is True
    assert graph["commercialPolicy"]["manufacturerVerifiedSearchRequiresExactModelRecheck"] is True

    schema = schema_graph(graph)
    product_nodes = [node for node in schema["@graph"] if node.get("@type") == "Product"]
    assert len(product_nodes) == 11
    assert not any("offers" in node for node in product_nodes)
    assert not any("aggregateRating" in node for node in product_nodes)
    assert {node["@id"].split("#product-", 1)[1] for node in product_nodes} == graph_product_ids
    for product in graph["products"]:
        node = next(item for item in product_nodes if item["@id"].endswith(f"#product-{product['id']}"))
        if product.get("officialSource"):
            assert node.get("sameAs") == product["officialSource"]

    for token in ["data-alo186-product-graph-entry", "affiliateProductKnowledgeGraph", "commercialRankingFieldsUsed", "directStoreLinksOnGraphData"]:
        assert token in injector
    assert "run_affiliate_product_graph" in pipeline
    assert pipeline.index("run_affiliate_product_graph(site, base_path)") > pipeline.index("recompute(site)")

    print(json.dumps({
        "ok": True,
        "routingVersion": manifest["version"],
        "needNodes": len(graph["needs"]),
        "categoryNodes": len(graph["categories"]),
        "productNodes": len(graph["products"]),
        "newManufacturerVerifiedSearchNodes": len(NEW_PRODUCTS),
        "directStoreLinksInGraphJson": 0,
        "commercialRankingFieldsUsed": [],
        "noBuyOutcomePreserved": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
