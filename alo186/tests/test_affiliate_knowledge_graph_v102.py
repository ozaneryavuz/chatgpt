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
EXT103 = json.loads((PAGE / "catalog-extension-v103.json").read_text(encoding="utf-8"))
EXT104 = json.loads((PAGE / "catalog-extension-v104.json").read_text(encoding="utf-8"))
OVERLAY = json.loads((ROOT / "deployment/routing-overlays/102-affiliate-knowledge-graph.json").read_text(encoding="utf-8"))
ROUTE = "/affiliate-knowledge-graph/"

assert BASE["version"] == 102
assert EXT103["version"] == 103
assert EXT104["version"] == 104
assert BASE["generatedAt"] == EXT103["generatedAt"] == EXT104["generatedAt"] == "2026-07-30"
assert BASE["affiliateTag"] == "alo186rehber-21"

intents = BASE["intents"] + EXT103["intents"] + EXT104["intents"]
products = BASE["productClasses"] + EXT103["productClasses"] + EXT104["productClasses"]
journeys = EXT104["journeys"]
assert len(intents) == 26
assert len(products) == 57
assert len(journeys) == 8
assert len({item["id"] for item in intents}) == len(intents)
assert len({item["id"] for item in products}) == len(products)
assert len({item["id"] for item in journeys}) == len(journeys)
intent_ids = {item["id"] for item in intents}
product_ids = {item["id"] for item in products}
risks = {"consumer", "consumer-gated", "professional-gated"}

for item in products:
    assert item["label"] and item["search"] and item["guide"].startswith("/")
    assert item["risk"] in risks
    assert item["requiredEvidence"] and len(item["requiredEvidence"]) >= 3
    assert item["needs"] and set(item["needs"]) <= intent_ids

for item in EXT103["productClasses"]:
    assert item["symptoms"] and item["avoidWhen"]

for item in EXT104["productClasses"]:
    assert item["symptoms"] and len(item["symptoms"]) >= 1
    assert item["avoidWhen"] and len(item["avoidWhen"]) >= 1
    assert item["noBuyWhen"] and len(item["noBuyWhen"]) >= 1
    assert set(item["companions"]) <= product_ids

for journey in journeys:
    assert journey["label"] and journey["problem"]
    assert len(journey["steps"]) >= 4
    assert journey["route"].startswith("/")
    assert journey["productClasses"] and set(journey["productClasses"]) <= product_ids

required_new_products = {
    "priz-test-cihazi-type-ef",
    "rcd-testli-priz-test-cihazi",
    "true-rms-multimetre-cat",
    "true-rms-pens-ampermetre",
    "arac-aku-akilli-sarj-cihazi",
    "arac-takviye-cihazi",
    "akulu-alet-yedek-batarya",
    "akulu-alet-sarj-cihazi",
    "buzdolabi-dondurucu-termometresi",
    "bilgisayar-nas-saf-sinus-ups",
    "kombi-saf-sinus-ups",
    "e-bisiklet-scooter-onayli-sarj-cihazi",
    "tasinabilir-evse",
    "evse-kablo-askisi",
    "led-serit-sabit-gerilim-guc-kaynagi",
    "led-dimmer-kontrolcu",
    "led-kablo-konnektor-seti",
}
assert required_new_products <= product_ids
assert len(EXT104["productClasses"]) == 18
assert any(item["id"] == "temassiz-gerilim-dedektoru" for item in EXT104["productClasses"])

professional_ids = {item["id"] for item in products if item["risk"] == "professional-gated"}
for item_id in {
    "true-rms-multimetre-cat",
    "true-rms-pens-ampermetre",
    "kombi-saf-sinus-ups",
    "e-bisiklet-scooter-onayli-sarj-cihazi",
    "tasinabilir-evse",
}:
    assert item_id in professional_ids

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
    "Amazon satış ortaklığı açıklaması",
    "Daha fazla ürünü",
    "57 ürün sınıfı",
    "26 kullanıcı ihtiyacı",
    "8 karar paketi",
    "Karar paketi nedir?",
    "Birlikte değerlendirin; ayrı ayrı doğrulayın",
    "Yeni ürün gerekmeyebilir",
    'rel="sponsored nofollow noopener"',
]:
    assert token in HTML

for token in [
    "alo186rehber-21",
    "professional-gated",
    "return null",
    "aria-disabled",
    "catalog-extension-v103.json",
    "catalog-extension-v104.json",
    "mergeCatalog",
    "renderJourneys",
    "journeyTemplate",
    "noBuyWhen",
    "companions",
]:
    assert token in JS or token in HTML
assert all(token not in JS for token in ["localStorage", "sessionStorage", "geolocation"])
for token in [
    "@media(max-width:620px)",
    "prefers-reduced-motion",
    ":focus-visible",
    ".journey-grid",
    ".no-buy-when",
    ".companions",
]:
    assert token in CSS

assert OVERLAY["version"] == 104
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
    "newProductClasses": len(EXT104["productClasses"]),
    "journeys": len(journeys),
    "symptomSearch": True,
    "noBuyPerProduct": True,
    "companionRelations": True,
    "professionalCommerceBlocked": True,
    "conditionalAffiliateGate": True,
    "priceStockRatingPublished": False,
    "productOfferSchema": False,
}, ensure_ascii=False))
