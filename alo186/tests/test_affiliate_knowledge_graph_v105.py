from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "affiliate-knowledge-graph"
BASE = json.loads((PAGE / "catalog.json").read_text(encoding="utf-8"))
EXTENSIONS = [
    json.loads((PAGE / name).read_text(encoding="utf-8"))
    for name in [
        "catalog-extension-v103.json",
        "catalog-v104-extension.json",
        "catalog-v104-supplement.json",
        "catalog-v105-extension.json",
    ]
]
APP = (PAGE / "app.js").read_text(encoding="utf-8")
HTML = (PAGE / "index.html").read_text(encoding="utf-8")
V105 = EXTENSIONS[-1]

intents = {}
products = {}
for source in [BASE, *EXTENSIONS]:
    for item in source.get("intents", []):
        intents[item["id"]] = item
    for item in source.get("productClasses", []):
        products[item["id"]] = item

assert V105["version"] == 105
assert V105["generatedAt"] == "2026-07-30"
assert len(V105["intents"]) == 5
assert len(V105["productClasses"]) == 10
assert len(intents) == 33
assert len(products) == 75
assert len({item["id"] for item in V105["productClasses"]}) == 10

v105_intents = {item["id"] for item in V105["intents"]}
for item in V105["productClasses"]:
    assert item["risk"] in {"consumer", "consumer-gated", "professional-gated"}
    assert item["label"] and item["search"] and item["guide"].startswith("/")
    assert len(item["requiredEvidence"]) >= 4
    assert item.get("profiles") and item.get("environments")
    assert item.get("symptoms") and item.get("avoidWhen")
    assert v105_intents.intersection(item["needs"])
    for forbidden in ["price", "stock", "rating", "seller", "delivery", "warranty", "offer", "aggregateRating"]:
        assert forbidden not in item

for intent in V105["intents"]:
    assert len(intent["productClasses"]) == 2
    assert all(item_id in products for item_id in intent["productClasses"])
    assert all(route.startswith("/") for route in intent["routes"])

assert "loadJson('./catalog-v105-extension.json')" in APP
assert "[v103, v104, supplement, v105]" in APP
assert 'id="intentCount">33<' in HTML
assert 'id="productCount">73<' in HTML
assert "73 ürün sınıfı" in HTML
assert 'rel="sponsored nofollow noopener"' in HTML
assert "alo186rehber-21" in APP
assert "localStorage" not in APP and "sessionStorage" not in APP
assert BASE["commercialPolicy"]["pricePublished"] is False
assert BASE["commercialPolicy"]["stockPublished"] is False
assert BASE["commercialPolicy"]["productOfferSchema"] is False

print(json.dumps({
    "ok": True,
    "version": 105,
    "intents": len(intents),
    "productClasses": len(products),
    "newIntents": len(V105["intents"]),
    "newProductClasses": len(V105["productClasses"]),
    "commercialClaims": 0,
}, ensure_ascii=False))
