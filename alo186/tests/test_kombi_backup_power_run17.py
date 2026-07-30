from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTE = ROOT / "hesaplama/kombi-ups-yedek-guc-uygunluk"
HTML = (ROUTE / "index.html").read_text(encoding="utf-8")
JS = (ROUTE / "app.js").read_text(encoding="utf-8")
CSS = (ROUTE / "styles.css").read_text(encoding="utf-8")
HUB = (ROOT / "hesaplama/index.html").read_text(encoding="utf-8")
OVERLAY = json.loads((ROOT / "deployment/routing-overlays/116-kombi-ups-yedek-guc-uygunluk.json").read_text(encoding="utf-8"))
CANONICAL = "https://www.alo186.com/hesaplama/kombi-ups-yedek-guc-uygunluk/"

for name in ["index.html", "app.js", "app.test.js", "styles.css"]:
    assert (ROUTE / name).is_file(), name

assert HTML.count("<h1>") == 1
assert CANONICAL in HTML
assert "Kombi İçin UPS Kaç VA?" in HTML
assert "ısıl kW" in HTML
assert "187" in HTML and "112" in HTML
assert "Bağımsız bilgilendirme platformudur" in HTML
assert "doğal gaz dağıtım şirketi" in HTML
assert "Amazon satış ortaklığı bağlantısı" in HTML
assert 'rel="sponsored nofollow noopener"' in HTML
assert "Mevcut güvenli kaynağımın hedef süreyi karşılamadığı doğrulandı" in HTML
assert HTML.count('type="checkbox"') >= 4
assert "90 günlük" in HTML
assert "yeni ürün almayın" in HTML.lower()
assert "fiyat, stok, puan, satıcı, teslimat veya garanti" in HTML

for schema in ["WebApplication", "DefinedTermSet", "FAQPage", "BreadcrumbList"]:
    assert f'"@type":"{schema}"' in HTML
for forbidden in [
    '"@type":"Product"', '"@type":"Offer"', "priceCurrency", "availability",
    "aggregateRating", "reviewCount", "offers",
]:
    assert forbidden not in HTML, forbidden

assert "gas_combi" in JS
assert "electric_boiler" in JS and "central_boiler" in JS and "heat_pump" in JS
assert "pure_sine_ups" in JS and "portable_power" in JS
assert "kesintisiz-guc-kaynagi-secimi?from=kombi" in JS
assert "tasinabilir-guc-istasyonu-secimi?from=kombi" in JS
assert "Yeni ürün almayın" in JS
assert "187" in JS and "112" in JS
assert "active_outage" in JS
assert "no_buy" in JS
assert "sourceSurgeW" in JS and "sourceWh" in JS and "sourcePureSine" in JS
assert "commercial.allowed=true" in JS
assert "amazon.com.tr" not in JS.lower()
for forbidden in ["localStorage", "sessionStorage", "geolocation", "fetch(", "XMLHttpRequest"]:
    assert forbidden not in JS, forbidden

for token in [
    "@media(max-width:620px)", "@media(max-width:900px)", "prefers-reduced-motion",
    ":focus-visible", "@media print", ".result.no_buy", ".result.emergency",
]:
    assert token in CSS, token

assert OVERLAY == {
    "version": 116,
    "generatedAt": "2026-07-30",
    "routes": [{
        "source": "alo186/hesaplama/kombi-ups-yedek-guc-uygunluk/index.html",
        "canonicalPath": "/hesaplama/kombi-ups-yedek-guc-uygunluk/",
        "type": "tool",
    }],
}

assert "Kombi UPS ve Yedek Güç Uygunluğu" in HUB
assert "./kombi-ups-yedek-guc-uygunluk/" in HUB
assert "46 çekirdek araç" in HUB
assert "Gaz/CO ve can güvenliğinde 187/112" in HUB
assert HUB.count("<h1>") == 1

json_ld_blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', HTML, re.S)
assert json_ld_blocks
for block in json_ld_blocks:
    json.loads(block)

subprocess.run(["node", "--check", str(ROUTE / "app.js")], check=True)
subprocess.run(["node", str(ROUTE / "app.test.js")], check=True)

print(json.dumps({
    "ok": True,
    "route": "/hesaplama/kombi-ups-yedek-guc-uygunluk/",
    "canonical": CANONICAL,
    "hubTools": 46,
    "decisionScenarios": 27,
    "gasEmergencyCommerceClosed": True,
    "professionalSystemsCommerceClosed": True,
    "noBuyProtected": True,
    "threeStepAffiliateGate": True,
    "directAmazonLinks": 0,
    "productOfferSchema": False,
}, ensure_ascii=False))
