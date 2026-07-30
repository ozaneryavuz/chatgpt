from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = REPO_ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))
from build_static_site import load_effective_manifest

ROUTE = "/urun-bilgi-grafigi/"
FORBIDDEN = {"price", "stock", "rating", "seller", "delivery", "warranty", "affiliateCommission"}
NEW_EXACT = {"anker-737-a1289", "anker-a1383-20k-87w"}
RUN50_MODELS = {
    "ugreen-nexode-100w-4port", "tp-link-tapo-p115", "tp-link-tapo-p115m",
    "ecoflow-river-2-max", "ecoflow-delta-2-max", "x-sense-xc01-r",
}
RUN51_MODELS = {
    "samsung-eb-p4520-20k-45w", "ugreen-nexode-x-65w-3port",
    "ugreen-90440-240w-usb-c", "ecoflow-river-3", "ecoflow-river-3-plus",
    "ecoflow-delta-3-plus", "bluetti-ac70p", "honda-eu22i",
    "victron-phoenix-vedirect-12-1200", "x-sense-sc07-mr",
}
BASE_MODELS = {"tp-link-tapo-p110", "tp-link-tapo-p110m", "ecoflow-river-2", "x-sense-xs01"}
ALL_MODELS = BASE_MODELS | RUN50_MODELS | RUN51_MODELS


def node_snapshot() -> dict:
    script = r"""
const c=require('./alo186/urun-eslestirme/catalog-sales-extension.js');
const now=new Date('2026-07-30T12:00:00Z');
process.stdout.write(JSON.stringify({
 tag:c.affiliateTag, summary:c.knowledgeGraphSummary({now}),
 products:c.products.map(x=>({id:x.id,category:x.category,asin:x.asin,status:x.status,linkMode:x.linkMode,url:x.url,source:x.technicalSource||null,needIds:x.needIds||[]})),
 publicProductIds:c.products.filter(x=>c.publicAffiliateEligible(x,{now})).map(x=>x.id),
 schema:c.knowledgeGraph({now})
}));
"""
    result = subprocess.run(["node", "-e", script], cwd=REPO_ROOT, check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


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
    assert manifest["version"] >= 71
    routes = [item for item in manifest["routes"] if item["canonicalPath"] == ROUTE]
    assert len(routes) == 1
    assert routes[0]["source"] == "alo186/urun-bilgi-grafigi/index.html"
    assert routes[0]["type"] == "commerce-guide"

    page = (REPO_ROOT / "alo186/urun-bilgi-grafigi/index.html").read_text(encoding="utf-8")
    app = (REPO_ROOT / "alo186/urun-bilgi-grafigi/app.js").read_text(encoding="utf-8")
    extension = (REPO_ROOT / "alo186/urun-eslestirme/catalog-knowledge-extension.js").read_text(encoding="utf-8")
    sales = (REPO_ROOT / "alo186/urun-eslestirme/catalog-sales-extension.js").read_text(encoding="utf-8")
    bridge = (REPO_ROOT / "alo186/akilli-urun-secimi/catalog-knowledge-extension.js").read_text(encoding="utf-8")
    injector = (REPO_ROOT / "alo186/deployment/inject_affiliate_product_graph.py").read_text(encoding="utf-8")
    pipeline = (REPO_ROOT / "alo186/deployment/inject_growth_run15.py").read_text(encoding="utf-8")
    placeholder = json.loads((REPO_ROOT / "alo186/urun-bilgi-grafigi/product-graph.json").read_text(encoding="utf-8"))
    snapshot = node_snapshot()

    expected_summary = {
        "version": "2026-07-30-run51", "generatedAt": "2026-07-30",
        "needCount": 18, "categoryCount": 18, "productCount": 40,
        "exactListingCount": 20, "manufacturerSearchCount": 20,
        "publicProductCount": 13, "gatedCandidateCount": 27,
        "affiliatePolicies": ["verified_direct", "after_tool", "professional_only"],
    }
    assert snapshot["tag"] == "alo186rehber-21"
    assert snapshot["summary"] == expected_summary
    assert len(snapshot["products"]) == 40
    assert len(snapshot["publicProductIds"]) == 13
    assert NEW_EXACT.issubset(set(snapshot["publicProductIds"]))

    public_categories = {
        item["category"] for item in snapshot["products"]
        if item["id"] in snapshot["publicProductIds"]
    }
    assert public_categories == {"powerbank", "usb_c_charger", "usb_c_cable", "usb_c_hub", "display_cable"}
    assert ALL_MODELS == {
        item["id"] for item in snapshot["products"]
        if item["status"] == "manufacturer_verified_search"
    }
    assert all(item["needIds"] for item in snapshot["products"])
    assert all("tag=alo186rehber-21" in item["url"] for item in snapshot["products"])

    for item in snapshot["products"]:
        if item["id"] in RUN51_MODELS:
            assert item["asin"] is None
            assert item["linkMode"] == "exact_model_search"
            assert item["source"].startswith("https://")

    graph_nodes = snapshot["schema"]["@graph"]
    product_nodes = [node for node in graph_nodes if node.get("@type") == "Product"]
    term_nodes = [node for node in graph_nodes if node.get("@type") == "DefinedTerm"]
    candidate_nodes = [
        node for node in term_nodes
        if (node.get("inDefinedTermSet") or {}).get("@id", "").endswith("/gated-product-candidates#termset")
    ]
    assert len(product_nodes) == 13
    assert len(term_nodes) == 63
    assert len(candidate_nodes) == 27
    assert not any(node.get("@type") == "Offer" for node in graph_nodes)
    assert not any("offers" in node or "aggregateRating" in node for node in product_nodes)
    assert {node.get("sku") for node in product_nodes} == set(snapshot["publicProductIds"])
    assert not ALL_MODELS.intersection({node.get("sku") for node in product_nodes})
    assert ALL_MODELS.issubset({node.get("termCode") for node in candidate_nodes})

    assert 'rel="canonical" href="https://www.alo186.com/urun-bilgi-grafigi/"' in page
    assert "CollectionPage" in page and "FAQPage" in page and "BreadcrumbList" in page
    assert "affiliateProductGraphJsonLd" in page and "catalog-sales-extension.js" in page
    assert "40 ürün/model düğümü" in page
    assert "amazon.com.tr" not in page.casefold()
    assert "sponsored nofollow noopener" in app
    assert "localStorage" not in app and "sessionStorage" not in app
    for token in ["manufacturer_verified_search", "gated-product-candidates", "knowledgeGraphSummary"]:
        assert token in extension
    for token in [
        "anker-737-a1289", "samsung-eb-p4520-20k-45w", "ugreen-90440-240w-usb-c",
        "ecoflow-delta-3-plus", "bluetti-ac70p", "honda-eu22i",
        "victron-phoenix-vedirect-12-1200", "x-sense-sc07-mr", "2026-07-30-run51",
    ]:
        assert token in sales
    for token in [
        "usb-c-hub-connectivity", "usb-c-display-output", "usb_c_hub",
        "display_cable", "usb-c-urun-kabul-testi",
    ]:
        assert token in bridge or token in sales

    assert placeholder["needs"] == [] and placeholder["categories"] == [] and placeholder["products"] == []
    assert placeholder["commercialPolicy"]["noBuyOutcomePreserved"] is True
    for token in [
        "node_payload", "affiliateProductKnowledgeGraph", "commercialRankingFieldsUsed",
        "graph_metadata", "SALES_EXTENSION",
    ]:
        assert token in injector
    assert "run_affiliate_product_graph" in pipeline

    keys: set[str] = set()
    collect_keys(snapshot["products"], keys)
    assert not FORBIDDEN.intersection(keys)

    print(json.dumps({
        "ok": True,
        "routingVersion": manifest["version"],
        "needNodes": 18,
        "categoryNodes": 18,
        "sourceProductRecords": 40,
        "publicProductNodes": 13,
        "gatedCandidateNodes": 27,
        "exactAsins": 20,
        "manufacturerModels": 20,
        "newProducts": 10,
        "commercialRankingFieldsUsed": [],
        "noBuyOutcomePreserved": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
