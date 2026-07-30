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
NEW_PRODUCTS = {"tp-link-tapo-p110", "tp-link-tapo-p110m", "ecoflow-river-2", "x-sense-xs01"}
USB_DISPLAY_PRODUCTS = {"ugreen-usbc-dp14-2m", "ugreen-usbc-dp14-3m", "daytona-hc01-usbc-hdmi-18m"}
NATIVE_DISPLAY_PRODUCTS = {"ugreen-dp14-2m", "ugreen-hdmi21-3m"}


def node_snapshot() -> dict:
    script = r"""
const c=require('./alo186/akilli-urun-secimi/catalog-knowledge-extension.js');
const now=new Date('2026-07-29T12:00:00Z');
process.stdout.write(JSON.stringify({
 tag:c.affiliateTag, summary:c.knowledgeGraphSummary(),
 products:c.products.map(x=>({id:x.id,category:x.category,asin:x.asin,status:x.status,linkMode:x.linkMode,url:x.url,source:x.technicalSource||null,needIds:x.needIds||[],relatedTools:x.relatedTools||[],requiredEvidence:x.requiredEvidence||[]})),
 publicProductIds:c.products.filter(x=>c.publicAffiliateEligible(x,{now})).map(x=>x.id),
 schema:c.knowledgeGraph({now})
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
    assert manifest["version"] >= 71
    routes = [item for item in manifest["routes"] if item["canonicalPath"] == ROUTE]
    assert len(routes) == 1
    assert routes[0]["source"] == "alo186/urun-bilgi-grafigi/index.html"
    assert routes[0]["type"] == "commerce-guide"

    page = (REPO_ROOT / "alo186/urun-bilgi-grafigi/index.html").read_text(encoding="utf-8")
    app = (REPO_ROOT / "alo186/urun-bilgi-grafigi/app.js").read_text(encoding="utf-8")
    extension = (REPO_ROOT / "alo186/urun-eslestirme/catalog-knowledge-extension.js").read_text(encoding="utf-8")
    bridge = (REPO_ROOT / "alo186/akilli-urun-secimi/catalog-knowledge-extension.js").read_text(encoding="utf-8")
    injector = (REPO_ROOT / "alo186/deployment/inject_affiliate_product_graph.py").read_text(encoding="utf-8")
    pipeline = (REPO_ROOT / "alo186/deployment/inject_growth_run15.py").read_text(encoding="utf-8")
    placeholder = json.loads((REPO_ROOT / "alo186/urun-bilgi-grafigi/product-graph.json").read_text(encoding="utf-8"))
    snapshot = node_snapshot()

    expected_summary = {
        "version": "2026-07-29-run39", "generatedAt": "2026-07-29",
        "needCount": 19, "categoryCount": 18, "productCount": 28,
        "exactListingCount": 24, "manufacturerSearchCount": 4,
        "publicProductCount": 17, "gatedCandidateCount": 11,
        "affiliatePolicies": ["verified_direct", "after_tool", "professional_only"],
    }
    assert snapshot["tag"] == "alo186rehber-21"
    assert snapshot["summary"] == expected_summary
    assert len(snapshot["products"]) == 28
    assert len(snapshot["publicProductIds"]) == 17
    public_categories = {item["category"] for item in snapshot["products"] if item["id"] in snapshot["publicProductIds"]}
    assert public_categories == {"powerbank", "usb_c_charger", "usb_c_cable", "usb_c_hub", "display_cable"}
    assert NEW_PRODUCTS == {item["id"] for item in snapshot["products"] if item["status"] == "manufacturer_verified_search"}
    assert all(item["needIds"] for item in snapshot["products"])
    assert all("tag=alo186rehber-21" in item["url"] for item in snapshot["products"])

    products_by_id = {item["id"]: item for item in snapshot["products"]}
    for item_id in USB_DISPLAY_PRODUCTS:
        item = products_by_id[item_id]
        assert item["needIds"] == ["usb-c-display-output"]
        assert "/hesaplama/usb-c-urun-kabul-testi/" in item["relatedTools"]
        assert any("Alt Mode" in evidence for evidence in item["requiredEvidence"])
    for item_id in NATIVE_DISPLAY_PRODUCTS:
        item = products_by_id[item_id]
        assert item["needIds"] == ["display-link-compatibility"]
        assert "/hesaplama/usb-c-urun-kabul-testi/" not in item["relatedTools"]
        assert not any("Alt Mode" in evidence for evidence in item["requiredEvidence"])
        assert any("konektör" in evidence for evidence in item["requiredEvidence"])

    graph_nodes = snapshot["schema"]["@graph"]
    product_nodes = [node for node in graph_nodes if node.get("@type") == "Product"]
    term_nodes = [node for node in graph_nodes if node.get("@type") == "DefinedTerm"]
    candidate_nodes = [node for node in term_nodes if (node.get("inDefinedTermSet") or {}).get("@id", "").endswith("/gated-product-candidates#termset")]
    assert len(product_nodes) == 17
    assert len(term_nodes) == 48
    assert len(candidate_nodes) == 11
    assert not any(node.get("@type") == "Offer" for node in graph_nodes)
    assert not any("offers" in node or "aggregateRating" in node for node in product_nodes)
    assert {node.get("sku") for node in product_nodes} == set(snapshot["publicProductIds"])
    assert not NEW_PRODUCTS.intersection({node.get("sku") for node in product_nodes})
    assert NEW_PRODUCTS.issubset({node.get("termCode") for node in candidate_nodes})

    assert 'rel="canonical" href="https://www.alo186.com/urun-bilgi-grafigi/"' in page
    assert "CollectionPage" in page and "FAQPage" in page and "BreadcrumbList" in page
    assert "affiliateProductGraphJsonLd" in page and "catalog-knowledge-extension.js" in page
    assert "amazon.com.tr" not in page.casefold()
    assert "sponsored nofollow noopener" in app
    assert "localStorage" not in app and "sessionStorage" not in app
    for token in ["manufacturer_verified_search", "gated-product-candidates", "knowledgeGraphSummary"]: assert token in extension
    for token in ["usb-c-hub-connectivity", "usb-c-display-output", "display-link-compatibility", "usb_c_hub", "display_cable", "usb-c-urun-kabul-testi"]: assert token in bridge

    assert placeholder["needs"] == [] and placeholder["categories"] == [] and placeholder["products"] == []
    assert placeholder["commercialPolicy"]["noBuyOutcomePreserved"] is True
    for token in ["node_payload", "affiliateProductKnowledgeGraph", "commercialRankingFieldsUsed", "graph_metadata"]: assert token in injector
    assert "run_affiliate_product_graph" in pipeline

    keys: set[str] = set(); collect_keys(snapshot["products"], keys)
    assert not FORBIDDEN.intersection(keys)
    print(json.dumps({"ok": True, "routingVersion": manifest["version"], "needNodes": 19, "categoryNodes": 18, "sourceProductRecords": 28, "publicProductNodes": 17, "gatedCandidateNodes": 11, "exactAsins": 24, "newManufacturerModels": 4, "connectorSpecificDisplayRelations": True, "commercialRankingFieldsUsed": [], "noBuyOutcomePreserved": True}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
