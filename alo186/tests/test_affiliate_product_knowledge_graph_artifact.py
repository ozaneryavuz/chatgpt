from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

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
TOOL_ROUTES = {
    "/hesaplama/bilgisayar-gaming-pc-nas-ups-uygunluk/",
    "/hesaplama/multimetre-pensampermetre-cat-uygunluk/",
    "/hesaplama/termal-kamera-kizilotesi-termometre-uygunluk/",
    "/hesaplama/arac-aku-sarj-cihazi-takviye-uygunluk/",
    "/hesaplama/akulu-el-aleti-batarya-sarj-uygunluk/",
}
FORBIDDEN = {"price", "stock", "rating", "seller", "delivery", "warranty", "affiliateCommission"}


def normalize_base_path(value: str) -> str:
    cleaned = str(value or "").strip()
    return "" if not cleaned or cleaned == "/" else "/" + cleaned.strip("/")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    root = args.site.resolve()
    prefix = normalize_base_path(args.base_path)
    graph_dir = root / "urun-bilgi-grafigi"
    matcher_dir = root / "akilli-urun-secimi"

    for path in [
        graph_dir / "index.html",
        graph_dir / "product-graph.json",
        graph_dir / "catalog-growth-run7.js",
        matcher_dir / "catalog-growth-run6.js",
        matcher_dir / "catalog-growth-run7.js",
    ]:
        assert path.is_file(), path

    graph = json.loads((graph_dir / "product-graph.json").read_text(encoding="utf-8"))
    assert graph["version"] == "2026-07-30-run7-user-growth"
    assert len(graph["needs"]) == 23
    assert len(graph["categories"]) == 23
    assert len(graph["products"]) == 55
    categories = {item["id"]: item for item in graph["categories"]}
    products = {item["id"]: item for item in graph["products"]}
    assert RUN7_CATEGORIES.issubset(categories)
    assert RUN7_MODELS.issubset(products)
    assert sum(item["verificationStatus"] == "verified_listing" for item in products.values()) == 20
    assert sum(item["verificationStatus"] == "manufacturer_verified_search" for item in products.values()) == 35
    assert graph["commercialPolicy"]["noBuyOutcomePreserved"] is True
    assert graph["commercialPolicy"]["manufacturerVerifiedSearchRequiresExactModelRecheck"] is True

    for item_id in RUN7_MODELS:
        item = products[item_id]
        assert item["identifier"]["type"] == "Model"
        assert item["linkMode"] == "exact_model_search"
        assert item["officialSource"].startswith("https://")
        assert item["relatedTools"]
        assert len(item["requiredEvidence"]) >= 4
        assert not FORBIDDEN.intersection(item)

    expected_tools = {f"{prefix}{route}" if prefix else route for route in TOOL_ROUTES}
    actual_tools = {url for item in products.values() for url in item.get("relatedTools", [])}
    assert expected_tools.issubset(actual_tools), sorted(expected_tools - actual_tools)

    html = (graph_dir / "index.html").read_text(encoding="utf-8")
    assert "55 ürün/model düğümü" in html
    assert "Beş yeni kullanıcı yolculuğu" in html
    assert "catalog-growth-run7.js" in html
    payloads = [
        json.loads(block)
        for block in re.findall(r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S | re.I)
    ]
    nodes = [node for payload in payloads for node in payload.get("@graph", [])]
    product_nodes = [node for node in nodes if isinstance(node, dict) and node.get("@type") == "Product"]
    term_nodes = [node for node in nodes if isinstance(node, dict) and node.get("@type") == "DefinedTerm"]
    candidates = [
        node
        for node in term_nodes
        if (node.get("inDefinedTermSet") or {}).get("@id", "").endswith("/gated-product-candidates#termset")
    ]
    assert len(product_nodes) == 13
    assert len(term_nodes) == 88
    assert len(candidates) == 42
    assert RUN7_MODELS.issubset({node.get("termCode") for node in candidates})
    assert not RUN7_MODELS.intersection({node.get("sku") for node in product_nodes})
    assert not any("offers" in node or "aggregateRating" in node for node in product_nodes)

    release = json.loads((root / "alo186-release.json").read_text(encoding="utf-8"))
    pages = json.loads((root / "pages-release.json").read_text(encoding="utf-8"))
    metadata = release["affiliateProductKnowledgeGraph"]
    assert metadata["needCount"] == 23
    assert metadata["categoryCount"] == 23
    assert metadata["productCount"] == 55
    assert metadata["exactAsinCount"] == 20
    assert metadata["manufacturerVerifiedSearchCount"] == 35
    assert metadata["publicProductCount"] == 13
    assert metadata["gatedCandidateCount"] == 42
    assert metadata["commercialRankingFieldsUsed"] == []
    assert metadata["noBuyOutcomePreserved"] is True
    assert pages["affiliateProductKnowledgeGraph"]["productCount"] == 55

    matcher = (matcher_dir / "index.html").read_text(encoding="utf-8")
    assert "catalog-growth-run6.js" in matcher
    assert "catalog-growth-run7.js" in matcher
    expected_route = f"{prefix}/urun-bilgi-grafigi/" if prefix else "/urun-bilgi-grafigi/"
    assert metadata["route"] == expected_route

    print(json.dumps({
        "ok": True,
        "basePath": prefix,
        "needs": 23,
        "categories": 23,
        "products": 55,
        "exactAsins": 20,
        "manufacturerModels": 35,
        "publicProducts": 13,
        "gatedCandidates": 42,
        "run7Models": 10,
        "userJourneys": 5,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
