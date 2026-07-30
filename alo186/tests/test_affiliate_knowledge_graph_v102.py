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
assert len(intents) == 22
assert len(products) == 50
assert len({item["id"] for item in intents}) == len(intents)
assert len({item["id"] for item in products}) == len(products)
intent_ids = {item["id"] for item in intents}
risks = {"consumer", "consumer-gated", "professional-gated"}

for item in products:
    assert item["label"] and item["search"] and item["guide"].startswith("/")
    assert item["risk"] in risks
    assert item["requiredEvidence"] and len(item["requiredEvidence"]) >= 3
    assert item["needs"] and set(item["needs"]) <= intent_ids

for extension in [EXT103, EXT104]:
    for item in extension["productClasses"]:
        assert item["symptoms"] and len(item["symptoms"]) >= 1
        assert item["avoidWhen"] and len(item["avoidWhen"]) >= 1

assert {item["id"] for item in EXT104["intents"]} == {
    "telefon-hizli-sarj", "dizustu-yuksek-guc", "harici-ekran", "seyahat-calisma-seti"
}
for product_id in [
    "usb-c-sarj-20w", "usb-c-pps-45w", "usb-c-pd31-140w", "usb-c-kablo-100w",
    "usb-c-kablo-240w", "usb-c-hub-4in1", "usb-c-hub-pd", "hdmi-21-kablo",
    "displayport-14-kablo", "usb-c-displayport-kablo", "usb-c-hdmi-kablo"
]:
    assert any(item["id"] == product_id for item in EXT104["productClasses"])

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
    "Amazon satış ortaklığı açıklaması", "Daha fazla ürünü", "Mevcut ürün yeterliyse",
    "50 ürün sınıfı", "22", "exactProductTemplate", "Doğrulanmış ürün modelleri",
    'rel="sponsored nofollow noopener"', "Mevcut güvenli ürünüm bu ihtiyacı karşılamıyor"
]:
    assert token in HTML
for script in [
    "/akilli-urun-secimi/catalog.js", "/akilli-urun-secimi/catalog-knowledge-extension.js",
    "/akilli-urun-secimi/catalog-sales-extension.js", "/akilli-urun-secimi/catalog-car-charger-run54.js"
]:
    assert script in HTML

assert "alo186rehber-21" in JS
assert "professional-gated" in JS
assert "catalog-extension-v104.json" in JS
assert "mergeCatalog" in JS
assert "renderExactProducts" in JS
assert "publicAffiliateEligible" in JS
assert "verificationStatus" in JS
assert "exact-gate" in HTML
assert "symptoms" in JS and "avoidWhen" in JS
assert all(token not in JS for token in ["localStorage", "sessionStorage", "geolocation"])
for token in [".exact-panel", ".exact-metrics", ".properties", ".blocked-note", ".exact-gate"]:
    assert token in CSS
assert "@media(max-width:620px)" in CSS
assert "prefers-reduced-motion" in CSS
assert ":focus-visible" in CSS

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
    "newV104ProductClasses": len(EXT104["productClasses"]),
    "exactProductSection": True,
    "professionalCommerceBlocked": True,
    "threeStepAffiliateGate": True,
    "priceStockRatingPublished": False,
    "productOfferSchema": False,
}, ensure_ascii=False))
