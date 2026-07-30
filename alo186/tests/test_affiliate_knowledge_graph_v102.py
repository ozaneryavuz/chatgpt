from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "affiliate-knowledge-graph"
HTML = (PAGE / "index.html").read_text(encoding="utf-8")
JS = (PAGE / "app.js").read_text(encoding="utf-8")
CSS = (PAGE / "styles.css").read_text(encoding="utf-8")
BASE = json.loads((PAGE / "catalog.json").read_text(encoding="utf-8"))
EXT = json.loads((PAGE / "catalog-extension-v103.json").read_text(encoding="utf-8"))
OVERLAY = json.loads((ROOT / "deployment/routing-overlays/102-affiliate-knowledge-graph.json").read_text(encoding="utf-8"))
ROUTE = "/affiliate-knowledge-graph/"

assert BASE["version"] == 102
assert EXT["version"] == 103
assert BASE["generatedAt"] == EXT["generatedAt"] == "2026-07-30"
assert BASE["affiliateTag"] == "alo186rehber-21"

intents = BASE["intents"] + EXT["intents"]
products = BASE["productClasses"] + EXT["productClasses"]
assert len(intents) >= 18
assert len(products) >= 39
assert len({item["id"] for item in intents}) == len(intents)
assert len({item["id"] for item in products}) == len(products)
intent_ids = {item["id"] for item in intents}
risks = {"consumer", "consumer-gated", "professional-gated"}

for item in products:
    assert item["label"] and item["search"] and item["guide"].startswith("/")
    assert item["risk"] in risks
    assert item["requiredEvidence"] and len(item["requiredEvidence"]) >= 3
    assert item["needs"] and set(item["needs"]) <= intent_ids

for item in EXT["productClasses"]:
    assert item["symptoms"] and len(item["symptoms"]) >= 1
    assert item["avoidWhen"] and len(item["avoidWhen"]) >= 1

professional = [item for item in products if item["risk"] == "professional-gated"]
assert professional
assert any(item["id"] == "aku-sarj-bakim-cihazi" for item in professional)
assert any(item["id"] == "yakıt-su-ayirma-huni" for item in professional)

policy = BASE["commercialPolicy"]
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
    "Amazon satış ortaklığı açıklaması", "Daha fazla ürünü",
    "Mevcut ürün yeterliyse", "Bu durumda alışveriş yapmayın",
    'rel="sponsored nofollow noopener"', "39 ürün sınıfı", "18"
]:
    assert token in HTML

assert "alo186rehber-21" in JS
assert "professional-gated" in JS
assert "return null" in JS
assert "aria-disabled" in JS
assert "catalog-extension-v103.json" in JS
assert "mergeCatalog" in JS
assert "symptoms" in JS and "avoidWhen" in JS
assert all(token not in JS for token in ["localStorage", "sessionStorage", "geolocation"])
assert "@media(max-width:620px)" in CSS
assert "prefers-reduced-motion" in CSS
assert ":focus-visible" in CSS
assert ".symptoms" in CSS and ".avoid" in CSS

assert OVERLAY["version"] == 103
assert OVERLAY["routes"] == [{
    "source": "alo186/affiliate-knowledge-graph/index.html",
    "canonicalPath": ROUTE,
    "type": "collection",
}]

subprocess.run(["node", "--check", str(PAGE / "app.js")], check=True)
print(json.dumps({
    "ok": True,
    "route": ROUTE,
    "intents": len(intents),
    "productClasses": len(products),
    "newProductClasses": len(EXT["productClasses"]),
    "symptomSearch": True,
    "avoidWhenCommerceGate": True,
    "professionalCommerceBlocked": True,
    "conditionalAffiliateGate": True,
    "priceStockRatingPublished": False,
    "productOfferSchema": False,
}, ensure_ascii=False))
