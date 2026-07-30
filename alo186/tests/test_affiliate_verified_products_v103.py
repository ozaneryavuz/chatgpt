from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "affiliate-knowledge-graph"
APP = (PAGE / "app.js").read_text(encoding="utf-8")
BASE = json.loads((PAGE / "catalog.json").read_text(encoding="utf-8"))
EXTENSION = json.loads((PAGE / "catalog-extension-v103.json").read_text(encoding="utf-8"))
VERIFIED = json.loads((PAGE / "verified-products.json").read_text(encoding="utf-8"))

class_ids = {item["id"] for item in BASE["productClasses"]} | {item["id"] for item in EXTENSION["productClasses"]}
assert "usb-c-hub" in class_ids
assert VERIFIED["version"] == 103
assert VERIFIED["verifiedAt"] == "2026-07-30"
assert VERIFIED["maxAgeDays"] == 45
assert len(VERIFIED["products"]) == 3

ids: set[str] = set()
asins: set[str] = set()
for product in VERIFIED["products"]:
    assert product["id"] not in ids
    assert product["asin"] not in asins
    ids.add(product["id"])
    asins.add(product["asin"])
    assert product["classId"] in class_ids
    assert product["brand"] and product["mpn"] and product["userNeed"]
    assert len(product["strengths"]) >= 3
    assert len(product["limits"]) >= 2
    assert any(word in product["doNotBuyWhen"].lower() for word in ["almayın", "değiştirmeyin"])
    assert re.fullmatch(r"B[A-Z0-9]{9}", product["asin"])
    assert product["url"] == f'https://www.amazon.com.tr/dp/{product["asin"]}?tag=alo186rehber-21'
    for forbidden in ["price", "stock", "rating", "seller", "warranty", "offer", "review"]:
        assert forbidden not in product

assert asins == {"B0B46PHW14", "B0144AE0V6", "B093FKT9BF"}
for token in [
    "loadJson('./verified-products.json')",
    "injectVerifiedProductGraph",
    "'@type': 'Product'",
    "'@type': 'Brand'",
    "propertyID: 'ASIN'",
    "propertyID: 'MPN'",
    "additionalProperty",
    "sponsored nofollow noopener",
    "aria-disabled"
]:
    assert token in APP
for forbidden in ["localStorage", "sessionStorage", "geolocation"]:
    assert forbidden not in APP

subprocess.run(["node", "--check", str(PAGE / "app.js")], check=True)
print(json.dumps({"ok": True, "verifiedProducts": 3, "uniqueAsins": 3, "usbCHubClass": True}, ensure_ascii=False))
