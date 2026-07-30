from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "affiliate-knowledge-graph"
HTML = (PAGE / "index.html").read_text(encoding="utf-8")
JS = (PAGE / "app.js").read_text(encoding="utf-8")
CSS = (PAGE / "styles.css").read_text(encoding="utf-8")
CATALOG = json.loads((PAGE / "catalog.json").read_text(encoding="utf-8"))
OVERLAY = json.loads((ROOT / "deployment/routing-overlays/102-affiliate-knowledge-graph.json").read_text(encoding="utf-8"))
ROUTE = "/affiliate-knowledge-graph/"

assert CATALOG["version"] == 102
assert CATALOG["generatedAt"] == "2026-07-30"
assert CATALOG["affiliateTag"] == "alo186rehber-21"
assert len(CATALOG["intents"]) >= 12
assert len(CATALOG["productClasses"]) >= 23
assert len({item["id"] for item in CATALOG["intents"]}) == len(CATALOG["intents"])
assert len({item["id"] for item in CATALOG["productClasses"]}) == len(CATALOG["productClasses"])
intent_ids = {item["id"] for item in CATALOG["intents"]}
risks = {"consumer", "consumer-gated", "professional-gated"}
for item in CATALOG["productClasses"]:
    assert item["label"] and item["search"] and item["guide"].startswith("/")
    assert item["risk"] in risks
    assert item["requiredEvidence"] and len(item["requiredEvidence"]) >= 3
    assert item["needs"] and set(item["needs"]) <= intent_ids

policy = CATALOG["commercialPolicy"]
assert policy == {
    "pricePublished": False,
    "stockPublished": False,
    "ratingPublished": False,
    "productOfferSchema": False,
    "directLinkRequiresVerifiedModel": True,
    "fixedInstallationCommerceBlocked": True,
}

assert f'https://alo186.com{ROUTE}' in HTML
assert HTML.count("<h1>") == 1
for schema in ["CollectionPage", "DefinedTerm", "FAQPage", "BreadcrumbList"]:
    assert f'"@type":"{schema}"' in HTML
for forbidden in ['"@type":"Product"', '"@type":"Offer"', "aggregateRating", "priceCurrency", "availability"]:
    assert forbidden not in HTML
for token in [
    "Amazon satış ortaklığı açıklaması", "Daha fazla ürün değil",
    "Mevcut ürün yeterliyse", 'rel="sponsored nofollow noopener"'
]:
    assert token in HTML

assert "alo186rehber-21" in JS
assert "professional-gated" in JS
assert "return null" in JS
assert "aria-disabled" in JS
assert "fetch('./catalog.json'" in JS
assert all(token not in JS for token in ["localStorage", "sessionStorage", "geolocation"])
assert "@media(max-width:620px)" in CSS
assert "prefers-reduced-motion" in CSS
assert ":focus-visible" in CSS

assert OVERLAY["version"] == 102
assert OVERLAY["routes"] == [{
    "source": "alo186/affiliate-knowledge-graph/index.html",
    "canonicalPath": ROUTE,
    "type": "collection",
}]

subprocess.run(["node", "--check", str(PAGE / "app.js")], check=True)
print(json.dumps({
    "ok": True,
    "route": ROUTE,
    "intents": len(CATALOG["intents"]),
    "productClasses": len(CATALOG["productClasses"]),
    "professionalCommerceBlocked": True,
    "conditionalAffiliateGate": True,
    "priceStockRatingPublished": False,
    "productOfferSchema": False,
}, ensure_ascii=False))
