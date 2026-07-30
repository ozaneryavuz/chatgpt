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
V103 = json.loads((PAGE / "catalog-extension-v103.json").read_text(encoding="utf-8"))
V104 = json.loads((PAGE / "catalog-v104-extension.json").read_text(encoding="utf-8"))
SUPPLEMENT = json.loads((PAGE / "catalog-v104-supplement.json").read_text(encoding="utf-8"))
V105 = json.loads((PAGE / "catalog-v105-exact-products.json").read_text(encoding="utf-8"))
OVERLAY = json.loads((ROOT / "deployment/routing-overlays/102-affiliate-knowledge-graph.json").read_text(encoding="utf-8"))
ROUTE = "/affiliate-knowledge-graph/"

assert BASE["version"] == 102
assert V103["version"] == 103
assert V104["version"] == SUPPLEMENT["version"] == 104
assert V105["version"] == 105
assert BASE["generatedAt"] == V103["generatedAt"] == V104["generatedAt"] == SUPPLEMENT["generatedAt"] == V105["generatedAt"] == "2026-07-30"
assert BASE["affiliateTag"] == "alo186rehber-21"

intent_map = {}
product_map = {}
for layer in [BASE, V103, V104, SUPPLEMENT, V105]:
    for item in layer["intents"]:
        intent_map[item["id"]] = item
    for item in layer["productClasses"]:
        product_map[item["id"]] = item
intents = list(intent_map.values())
products = list(product_map.values())
assert len(intents) >= 32
assert len(products) >= 74
assert len({item["id"] for item in intents}) == len(intents)
assert len({item["id"] for item in products}) == len(products)
intent_ids = {item["id"] for item in intents}
risks = {"consumer", "consumer-gated", "professional-gated"}

for item in products:
    assert item["label"] and item["search"] and item["guide"].startswith("/")
    assert item["risk"] in risks
    assert item["requiredEvidence"] and len(item["requiredEvidence"]) >= 3
    assert item["needs"] and set(item["needs"]) <= intent_ids

for item in V103["productClasses"]:
    assert item["symptoms"] and item["avoidWhen"]
for item in V104["productClasses"] + SUPPLEMENT["productClasses"] + V105["productClasses"]:
    assert item["signals"] and len(item["signals"]) >= 1
    assert item["avoidWhen"] and len(item["avoidWhen"]) >= 1
    assert item["profiles"] and item["environments"]

for intent_id in ["telefon-hizli-sarj", "dizustu-yuksek-guc", "harici-ekran", "seyahat-calisma-seti"]:
    assert intent_id in intent_ids
for product_id in [
    "usb-c-sarj-20w", "usb-c-pps-45w", "usb-c-pd31-140w", "usb-c-kablo-100w",
    "usb-c-kablo-240w", "usb-c-hub-4in1", "usb-c-hub-pd", "hdmi-21-kablo",
    "displayport-14-kablo", "usb-c-displayport-kablo", "usb-c-hdmi-kablo",
]:
    assert product_id in product_map

professional = [item for item in products if item["risk"] == "professional-gated"]
assert professional
for product_id in ["poe-ups", "titreşimli-alarm-yardimcisi"]:
    assert any(item["id"] == product_id for item in professional)

assert BASE["commercialPolicy"] == {
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
    "Amazon satış ortaklığı açıklaması", "Daha fazla ürünü", "Mevcut cihaz gerçek görevi",
    "Kullanıcı ve ortam bağlamı", 'rel="sponsored nofollow noopener"', "74", "32",
    "exactProductTemplate", "Doğrulanmış ürün modelleri", "Mevcut güvenli ürünüm bu ihtiyacı karşılamıyor",
]:
    assert token in HTML, token
for script in [
    "/akilli-urun-secimi/catalog.js", "/akilli-urun-secimi/catalog-knowledge-extension.js",
    "/akilli-urun-secimi/catalog-sales-extension.js", "/akilli-urun-secimi/catalog-car-charger-run54.js",
]:
    assert script in HTML

assert "alo186rehber-21" in JS
assert "professional-gated" in JS
assert "aria-disabled" in JS
assert "catalog-extension-v103.json" in JS
assert "catalog-v104-extension.json" in JS
assert "catalog-v104-supplement.json" in JS
assert "catalog-v105-exact-products.json" in JS
assert "mergeCatalog" in JS and "renderExactProducts" in JS
assert "publicAffiliateEligible" in JS and "verificationStatus" in JS
assert "signals" in JS and "avoidWhen" in JS and "profiles" in JS and "environments" in JS
assert all(token not in JS for token in ["localStorage", "sessionStorage", "geolocation"])
for token in [".symptoms", ".avoid", ".context", ".exact-panel", ".exact-metrics", ".properties", ".blocked-note", ".exact-gate"]:
    assert token in CSS
assert "@media(max-width:620px)" in CSS
assert "prefers-reduced-motion" in CSS
assert ":focus-visible" in CSS

assert OVERLAY["version"] == 105
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
    "v105ProductClasses": len(V105["productClasses"]),
    "profileEnvironmentSearch": True,
    "exactProductSection": True,
    "threeStepAffiliateGate": True,
    "professionalCommerceBlocked": True,
    "priceStockRatingPublished": False,
    "productOfferSchema": False,
}, ensure_ascii=False))
