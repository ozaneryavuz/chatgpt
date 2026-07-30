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
RUN7_MODELS = {
    "apc-bx1600mi-gr",
    "cyberpower-cp1500epfclcd",
    "fluke-117",
    "fluke-325",
    "flir-c5",
    "bosch-universaltemp-06036831z0",
    "ctek-mxs-5-0-eu",
    "noco-genius5",
    "bosch-procore18v-5-5ah-1600a02149",
    "milwaukee-m18-hb5-5-4932464712",
}
RUN7_CATEGORIES = {"computer_ups", "multimeter", "thermal_imager", "battery_charger", "tool_battery"}
RUN7_NEEDS = {
    "computer-network-continuity",
    "safe-electrical-measurement",
    "thermal-inspection",
    "vehicle-battery-maintenance",
    "cordless-tool-continuity",
}
EXPECTED_TOOLS = {
    "computer_ups": "/hesaplama/bilgisayar-gaming-pc-nas-ups-uygunluk/",
    "multimeter": "/hesaplama/multimetre-pensampermetre-cat-uygunluk/",
    "thermal_imager": "/hesaplama/termal-kamera-kizilotesi-termometre-uygunluk/",
    "battery_charger": "/hesaplama/arac-aku-sarj-cihazi-takviye-uygunluk/",
    "tool_battery": "/hesaplama/akulu-el-aleti-batarya-sarj-uygunluk/",
}


def node_snapshot() -> dict:
    script = r"""
const c=require('./alo186/urun-eslestirme/catalog-growth-run7.js');
const now=new Date('2026-07-30T12:00:00Z');
process.stdout.write(JSON.stringify({
  tag:c.affiliateTag,
  summary:c.knowledgeGraphSummary({now}),
  needs:c.needs,
  categories:c.categories,
  relations:c.categoryRelations,
  products:c.products.map(x=>({
    id:x.id,category:x.category,asin:x.asin,status:x.status,linkMode:x.linkMode,
    url:x.url,source:x.technicalSource||null,needIds:x.needIds||[],
    relatedTools:x.relatedTools||[],requiredEvidence:x.requiredEvidence||[]
  })),
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
    routes = [item for item in manifest["routes"] if item["canonicalPath"] == ROUTE]
    assert len(routes) == 1
    assert routes[0]["source"] == "alo186/urun-bilgi-grafigi/index.html"
    assert routes[0]["type"] == "commerce-guide"

    page = (REPO_ROOT / "alo186/urun-bilgi-grafigi/index.html").read_text(encoding="utf-8")
    app = (REPO_ROOT / "alo186/urun-bilgi-grafigi/app.js").read_text(encoding="utf-8")
    run7 = (REPO_ROOT / "alo186/urun-eslestirme/catalog-growth-run7.js").read_text(encoding="utf-8")
    injector = (REPO_ROOT / "alo186/deployment/inject_affiliate_product_graph.py").read_text(encoding="utf-8")
    placeholder = json.loads((REPO_ROOT / "alo186/urun-bilgi-grafigi/product-graph.json").read_text(encoding="utf-8"))
    snapshot = node_snapshot()

    assert snapshot["tag"] == "alo186rehber-21"
    assert snapshot["summary"] == {
        "version": "2026-07-30-run7-user-growth",
        "generatedAt": "2026-07-30",
        "needCount": 23,
        "categoryCount": 23,
        "productCount": 55,
        "exactListingCount": 20,
        "manufacturerSearchCount": 35,
        "publicProductCount": 13,
        "gatedCandidateCount": 42,
        "affiliatePolicies": ["verified_direct", "after_tool", "professional_only"],
    }
    assert len(snapshot["products"]) == 55
    assert len(snapshot["publicProductIds"]) == 13
    assert RUN7_NEEDS.issubset({item["id"] for item in snapshot["needs"]})

    categories = {item["id"]: item for item in snapshot["categories"]}
    products = {item["id"]: item for item in snapshot["products"]}
    assert RUN7_CATEGORIES.issubset(categories)
    for category_id in RUN7_CATEGORIES:
        assert categories[category_id]["affiliatePolicy"] == "after_tool"
        assert EXPECTED_TOOLS[category_id] in snapshot["relations"][category_id]["tools"]
        category_products = [item for item in products.values() if item["category"] == category_id]
        assert len(category_products) == 2

    for product_id in RUN7_MODELS:
        product = products[product_id]
        assert product["asin"] is None
        assert product["status"] == "manufacturer_verified_search"
        assert product["linkMode"] == "exact_model_search"
        assert product["source"].startswith("https://")
        assert product["url"].startswith("https://www.amazon.com.tr/s?k=")
        assert "tag=alo186rehber-21" in product["url"]
        assert product["needIds"]
        assert product["relatedTools"]
        assert len(product["requiredEvidence"]) >= 4
        assert product_id not in snapshot["publicProductIds"]

    graph_nodes = snapshot["schema"]["@graph"]
    product_nodes = [node for node in graph_nodes if node.get("@type") == "Product"]
    term_nodes = [node for node in graph_nodes if node.get("@type") == "DefinedTerm"]
    candidate_nodes = [
        node for node in term_nodes
        if (node.get("inDefinedTermSet") or {}).get("@id", "").endswith("/gated-product-candidates#termset")
    ]
    assert len(product_nodes) == 13
    assert len(term_nodes) == 88
    assert len(candidate_nodes) == 42
    assert not any(node.get("@type") == "Offer" for node in graph_nodes)
    assert not any("offers" in node or "aggregateRating" in node for node in product_nodes)
    assert RUN7_MODELS.issubset({node.get("termCode") for node in candidate_nodes})
    assert not RUN7_MODELS.intersection({node.get("sku") for node in product_nodes})

    assert 'rel="canonical" href="https://www.alo186.com/urun-bilgi-grafigi/"' in page
    assert "55 ürün/model düğümü" in page
    assert "35 üretici kaynaklı" in page
    assert "Beş yeni kullanıcı yolculuğu" in page
    assert "catalog-growth-run7.js" in page
    for route in EXPECTED_TOOLS.values():
        assert route in page
    assert "amazon.com.tr" not in page.casefold()
    assert "sponsored nofollow noopener" in app
    assert "localStorage" not in app and "sessionStorage" not in app

    for token in RUN7_MODELS | RUN7_NEEDS | RUN7_CATEGORIES | {"2026-07-30-run7-user-growth"}:
        assert token in run7
    for token in [
        "GROWTH_RUN6_EXTENSION",
        "GROWTH_RUN7_EXTENSION",
        "catalog-growth-run7.js",
        "manufacturerVerifiedSearchRequiresExactModelRecheck",
        "noBuyOutcomePreserved",
    ]:
        assert token in injector

    assert placeholder["needs"] == []
    assert placeholder["categories"] == []
    assert placeholder["products"] == []
    assert placeholder["commercialPolicy"]["noBuyOutcomePreserved"] is True

    keys: set[str] = set()
    collect_keys(snapshot["products"], keys)
    assert not FORBIDDEN.intersection(keys)

    print(json.dumps({
        "ok": True,
        "routingVersion": manifest["version"],
        "needNodes": 23,
        "categoryNodes": 23,
        "sourceProductRecords": 55,
        "exactAsins": 20,
        "manufacturerModels": 35,
        "publicProductNodes": 13,
        "gatedCandidateNodes": 42,
        "newUserJourneys": 5,
        "newManufacturerModels": 10,
        "commercialRankingFieldsUsed": [],
        "noBuyOutcomePreserved": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
