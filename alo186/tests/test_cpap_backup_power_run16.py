from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "hesaplama/cpap-apap-bipap-yedek-guc-uygunluk"
HTML = (TOOL / "index.html").read_text(encoding="utf-8")
JS = (TOOL / "app.js").read_text(encoding="utf-8")
CSS = (TOOL / "styles.css").read_text(encoding="utf-8")
HUB = (ROOT / "hesaplama/index.html").read_text(encoding="utf-8")
OVERLAY = json.loads((ROOT / "deployment/routing-overlays/115-cpap-apap-bipap-yedek-guc-uygunluk.json").read_text(encoding="utf-8"))
ROUTE = "/hesaplama/cpap-apap-bipap-yedek-guc-uygunluk/"

for path in [TOOL / "index.html", TOOL / "app.js", TOOL / "styles.css", TOOL / "app.test.js"]:
    assert path.is_file(), path

assert HTML.count("<h1") == 1
assert 'https://www.alo186.com/hesaplama/cpap-apap-bipap-yedek-guc-uygunluk/' in HTML
for schema_type in ["WebApplication", "DefinedTermSet", "FAQPage", "BreadcrumbList"]:
    assert f'"@type":"{schema_type}"' in HTML
for forbidden in [
    '"@type":"Product"', '"@type":"Offer"', "priceCurrency", "aggregateRating", "availability",
    "amazon.com.tr", "amzn.to",
]:
    assert forbidden not in HTML, forbidden

for token in [
    "CPAP, APAP ve BiPAP Yedek Güç Uygunluğu",
    "Amazon satış ortaklığı bağlantısıdır",
    "Mevcut üretici uyumlu çözümün hedef süreyi karşılamadığını doğruladım",
    "Kişisel sağlık verisi yok",
    "Aktif kesintide satış yok",
    "90 günlük yeniden test",
    "Tüketici ürün bağlantısı kapalıdır",
    "ResMed batarya ve dönüştürücüler",
    "Philips DreamStation Go güç yolu",
]:
    assert token in HTML, token

for field in [
    "emergency", "physicalCondition", "scenario", "deviceType", "dependence", "supplementalOxygen",
    "exactModelVerified", "manufacturerPowerGuide", "humidifier", "heatedTube", "accessoriesIncluded",
    "maxW", "targetHours", "energyMode", "averageW", "referenceWh", "referenceHours", "powerPath",
    "sourceStatus", "sourceContinuousW", "sourceWh", "sourceOutputVerified", "daytimeTest",
]:
    assert f'name="{field}"' in HTML, field

assert 'type="text"' not in HTML
assert 'type="email"' not in HTML
assert 'type="tel"' not in HTML
assert "<textarea" not in HTML
assert "localStorage" not in JS
assert "sessionStorage" not in JS
assert "geolocation" not in JS
assert "amazon.com.tr" not in JS
assert "alo186rehber-21" not in JS
assert "/amazon-elektrik-urunleri/tasinabilir-guc-istasyonu-secimi?from=cpap" in JS
assert "manufacturerPowerGuide" in JS
assert "usedUpperBound" in JS
assert "Mevcut üretici uyumlu kaynak" in JS
assert "Aktif kesinti sırasında ürün teslimatı" in JS
assert "daytimeTest" in JS

for forbidden in ["priceCurrency", "aggregateRating", "availability", '"@type":"Offer"', '"@type":"Product"']:
    assert forbidden not in JS

for token in [":focus-visible", "@media(max-width:620px)", "prefers-reduced-motion", "@media print", ".commerce", ".professional"]:
    assert token in CSS, token

assert 'href="./cpap-apap-bipap-yedek-guc-uygunluk/"' in HUB
assert "CPAP/APAP Yedek Güç Uygunluğu" in HUB
assert "45 çekirdek araç" in HUB
assert "44 çekirdek araç" not in HUB

assert OVERLAY == {
    "version": 115,
    "generatedAt": "2026-07-30",
    "routes": [{
        "source": "alo186/hesaplama/cpap-apap-bipap-yedek-guc-uygunluk/index.html",
        "canonicalPath": ROUTE,
        "type": "tool",
    }],
}

# Form fields remain structured; no free-form medical note capture is introduced.
assert not re.search(r'<input[^>]+name="(?:name|email|phone|address|diagnosis|pressure|location)"', HTML, re.I)

subprocess.run(["node", "--check", str(TOOL / "app.js")], check=True)
subprocess.run(["node", str(TOOL / "app.test.js")], check=True)

print(json.dumps({
    "ok": True,
    "route": ROUTE,
    "coreTools": 45,
    "directAmazonLinks": 0,
    "medicalFreeTextFields": 0,
    "activeOutageCommerceClosed": True,
    "noBuyOutcome": True,
    "reminderDays": 90,
}, ensure_ascii=False))
