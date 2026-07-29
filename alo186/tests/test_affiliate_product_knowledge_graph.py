from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = REPO_ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

from build_static_site import load_effective_manifest  # noqa: E402

ROUTE = "/urun-bilgi-grafigi/"
FORBIDDEN = {"price", "stock", "rating", "seller", "delivery", "warranty", "affiliateCommission"}
NEW_PRODUCTS = {"tp-link-tapo-p110", "tp-link-tapo-p110m", "ecoflow-river-2", "x-sense-xs01"}


def node_snapshot() -> dict:
    script = r"""
const c=require('./alo186/akilli-urun-secimi/catalog-knowledge-extension.js');
process.stdout.write(JSON.stringify({
 tag:c.affiliateTag, summary:c.knowledgeGraphSummary(),
 categories:c.categories.map(x=>x.id).sort(), needs:c.needs.map(x=>x.id).sort(),
 products:c.products.map(x=>({id:x.id,category:x.category,asin:x.asin,status:x.status,linkMode:x.linkMode,url:x.url,source:x.technicalSource||null})).sort((a,b)=>a.id.localeCompare(b.id)),
 schema:c.knowledgeGraph({now:new Date('2026-07-29T12:00:00Z')})
}));
"""
    result = subprocess.run(["node", "-e", script], cwd=REPO_ROOT, check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def collect_keys(value, result: set[str]) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            result.add(str(key)); collect_keys(nested, result)
    elif isinstance(value, list):
        for nested in value: collect_keys(nested, result)


def main() -> None:
    manifest = load_effective_manifest(REPO_ROOT)
    assert manifest["version"] >= 64
    routes = [item for item in manifest["routes"] if item["canonicalPath"] == ROUTE]
    assert len(routes) == 1
    assert routes[0]["source"] == "alo186/urun-bilgi-grafigi/index.html"
    assert routes[0]["type"] == "commerce-guide"

    page = (REPO_ROOT / "alo186/urun-bilgi-grafigi/index.html").read_text(encoding="utf-8")
    app = (REPO_ROOT / "alo186/urun-bilgi-grafigi/app.js").read_text(encoding="utf-8")
    extension = (REPO_ROOT / "alo186/akilli-urun-secimi/catalog-knowledge-extension.js").read_text(encoding="utf-8")
    injector = (REPO_ROOT / "alo186/deployment/inject_affiliate_product_graph.py").read_text(encoding="utf-8")
    pipeline = (REPO_ROOT / "alo186/deployment/inject_growth_run15.py").read_text(encoding="utf-8")
    placeholder = json.loads((REPO_ROOT / "alo186/urun-bilgi-grafigi/product-graph.json").read_text(encoding="utf-8"))
    snapshot = node_snapshot()

    assert snapshot["tag"] == "alo186rehber-21"
    assert snapshot["summary"] == {"version":"2026-07-29-run34b","generatedAt":"2026-07-29","needCount":14,"categoryCount":14,"productCount":14,"exactListingCount":10,"manufacturerSearchCount":4,"affiliatePolicies":["verified_direct","after_tool","professional_only"]}
    assert len(snapshot["products"]) == 14
    assert NEW_PRODUCTS == {item["id"] for item in snapshot["products"] if item["status"] == "manufacturer_verified_search"}
    assert all(item["asin"] is None and item["linkMode"] == "exact_model_search" and item["source"] for item in snapshot["products"] if item["id"] in NEW_PRODUCTS)
    assert all("tag=alo186rehber-21" in item["url"] for item in snapshot["products"])

    graph_nodes = snapshot["schema"]["@graph"]
    product_nodes = [node for node in graph_nodes if node.get("@type") == "Product"]
    assert len(product_nodes) == 14
    assert len([node for node in graph_nodes if node.get("@type") == "DefinedTerm"]) == 28
    assert not any(node.get("@type") == "Offer" for node in graph_nodes)
    assert not any("offers" in node or "aggregateRating" in node for node in product_nodes)

    assert 'rel="canonical" href="https://www.alo186.com/urun-bilgi-grafigi/"' in page
    assert "CollectionPage" in page and "FAQPage" in page and "BreadcrumbList" in page
    assert "affiliateProductGraphJsonLd" in page
    assert "catalog-knowledge-extension.js" in page
    assert "Tapo P110" in page and "EcoFlow RIVER 2" in page and "X-Sense XS01" in page
    assert "amazon.com.tr" not in page.casefold()
    assert "<form" not in page.casefold() and 'type="email"' not in page.casefold() and 'type="tel"' not in page.casefold()

    assert "sponsored nofollow noopener" in app
    assert "Mevcut ürünüm güvenli biçimde ihtiyacı karşılamıyor" in app
    assert "localStorage" not in app and "sessionStorage" not in app
    assert "allChecked" in app and "exact_model_search" in app

    assert "alo186rehber-21" in extension
    assert "manufacturer_verified_search" in extension
    assert "productsFor('smart_plug')" not in extension
    assert "technicalSource" in extension and "knowledgeGraphSummary" in extension

    assert placeholder["needs"] == [] and placeholder["categories"] == [] and placeholder["products"] == []
    assert placeholder["commercialPolicy"]["noBuyOutcomePreserved"] is True
    assert placeholder["commercialPolicy"]["professionalOnlyCategoriesNeverExposeAffiliateLinks"] is True

    for token in ["node_payload", "data-alo186-product-graph-entry", "affiliateProductKnowledgeGraph", "commercialRankingFieldsUsed", "directStoreLinksOnGraphJson"]:
        assert token in injector
    assert "run_affiliate_product_graph" in pipeline
    assert pipeline.index("run_affiliate_product_graph(site, base_path)") > pipeline.index("recompute(site)")

    keys: set[str] = set(); collect_keys(snapshot["products"], keys)
    assert not FORBIDDEN.intersection(keys)

    print(json.dumps({"ok":True,"routingVersion":manifest["version"],"needNodes":14,"categoryNodes":14,"productNodes":14,"exactAsins":10,"newManufacturerModels":4,"affiliateTag":"alo186rehber-21","commercialRankingFieldsUsed":[],"noBuyOutcomePreserved":True}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
