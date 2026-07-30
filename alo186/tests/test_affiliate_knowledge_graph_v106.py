from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "affiliate-knowledge-graph"
FILES = [
    "catalog.json", "catalog-extension-v103.json", "catalog-v104-extension.json",
    "catalog-v104-supplement.json", "catalog-v105-extension.json", "catalog-v106-extension.json",
]
LAYERS = [json.loads((PAGE / name).read_text(encoding="utf-8")) for name in FILES]
BASE, V103, V104, SUPPLEMENT, V105, V106 = LAYERS
APP = (PAGE / "app.js").read_text(encoding="utf-8")
HTML = (PAGE / "index.html").read_text(encoding="utf-8")
CSS = (PAGE / "styles.css").read_text(encoding="utf-8")

intents: dict[str, dict] = {}
products: dict[str, dict] = {}
journeys: dict[str, dict] = {}
for layer in LAYERS:
    for item in layer.get("intents", []): intents[item["id"]] = item
    for item in layer.get("productClasses", []): products[item["id"]] = item
    for item in layer.get("journeys", []): journeys[item["id"]] = item

assert V106["version"] == 106
assert V106["generatedAt"] == "2026-07-30"
assert len(V106["intents"]) == 8
assert len(V106["productClasses"]) == 16
assert len(V106["journeys"]) == 8
assert len(intents) == 41
assert len(products) == 91
assert len(journeys) == 8
assert len({item["id"] for item in V106["productClasses"]}) == 16

intent_ids = set(intents)
product_ids = set(products)
existing_before_v106 = {
    item["id"] for layer in LAYERS[:-1] for item in layer.get("productClasses", [])
}
assert not existing_before_v106.intersection({item["id"] for item in V106["productClasses"]})
assert "buzdolabi-dondurucu-termometresi" in existing_before_v106
assert "ev-kablo-duvar-askisi" in existing_before_v106

for item in V106["productClasses"]:
    assert item["risk"] in {"consumer", "consumer-gated", "professional-gated"}
    assert item["label"] and item["search"] and item["guide"].startswith("/")
    assert len(item["requiredEvidence"]) >= 4
    assert item["signals"] and item["avoidWhen"] and item["noBuyWhen"]
    assert item["profiles"] and item["environments"]
    assert set(item["needs"]) <= intent_ids
    assert set(item["companions"]) <= product_ids
    for forbidden in ["price", "stock", "rating", "seller", "delivery", "warranty", "offer", "aggregateRating"]:
        assert forbidden not in item

for journey in V106["journeys"]:
    assert journey["label"] and journey["problem"]
    assert len(journey["steps"]) >= 4
    assert journey["route"].startswith("/")
    assert set(journey["productClasses"]) <= product_ids

professional = {item["id"] for item in products.values() if item["risk"] == "professional-gated"}
for item_id in [
    "temassiz-gerilim-dedektoru", "true-rms-multimetre-cat", "true-rms-pens-ampermetre",
    "kombi-saf-sinus-ups", "e-bisiklet-scooter-onayli-sarj-cihazi", "tasinabilir-evse",
]:
    assert item_id in professional

assert BASE["commercialPolicy"]["pricePublished"] is False
assert BASE["commercialPolicy"]["stockPublished"] is False
assert BASE["commercialPolicy"]["ratingPublished"] is False
assert BASE["commercialPolicy"]["productOfferSchema"] is False

assert 'id="intentCount">41<' in HTML
assert 'id="productCount">91<' in HTML
assert 'id="journeyCount">8<' in HTML
for token in [
    "91 ürün sınıfı", "41 kullanıcı ihtiyacını", "8 karar paketi",
    "Amazon satış ortaklığı açıklaması", "Karar paketi nedir?",
    "Yeni ürün gerekmeyebilir", "Birlikte değerlendirin; ayrı ayrı doğrulayın",
    'rel="sponsored nofollow noopener"',
]:
    assert token in HTML, token
for forbidden in ['"@type":"Product"', '"@type":"Offer"', "aggregateRating", "priceCurrency", "availability"]:
    assert forbidden not in HTML

assert "loadJson('./catalog-v106-extension.json')" in APP
assert "[v103, v104, supplement, v105, v106]" in APP
for token in ["renderJourneys", "noBuyWhen", "companions", "profiles", "environments", "professional-gated", "alo186rehber-21"]:
    assert token in APP
assert "localStorage" not in APP and "sessionStorage" not in APP and "geolocation" not in APP
for token in [".journey-grid", ".no-buy-when", ".companions", ".context", ":focus-visible", "prefers-reduced-motion"]:
    assert token in CSS

subprocess.run(["node", "--check", str(PAGE / "app.js")], check=True)
print(json.dumps({
    "ok": True, "version": 106, "intents": len(intents), "productClasses": len(products),
    "newIntents": len(V106["intents"]), "newProductClasses": len(V106["productClasses"]),
    "journeys": len(journeys), "noBuyPerProduct": True, "companionRelations": True,
    "professionalCommerceBlocked": True, "commercialClaims": 0,
}, ensure_ascii=False))
