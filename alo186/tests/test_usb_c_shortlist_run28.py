from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROUTE = "/hesaplama/usb-c-set-kisa-listesi/"
PAGE = ROOT / "alo186/hesaplama/usb-c-set-kisa-listesi/index.html"
APP = ROOT / "alo186/hesaplama/usb-c-set-kisa-listesi/app.js"
LOADER = ROOT / "alo186/hesaplama/usb-c-set-kisa-listesi/catalog-loader.js"
EXTENSION = ROOT / "alo186/urun-eslestirme/catalog-qualified-commerce-run53.js"
STYLES = ROOT / "alo186/hesaplama/usb-c-set-kisa-listesi/styles.css"
HUB = ROOT / "alo186/hesaplama/index.html"
COMMON = ROOT / "alo186/hesaplama/common.js"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/usb-c-shortlist-run28.json"

html = PAGE.read_text(encoding="utf-8")
app = APP.read_text(encoding="utf-8")
loader = LOADER.read_text(encoding="utf-8")
extension = EXTENSION.read_text(encoding="utf-8")
styles = STYLES.read_text(encoding="utf-8")
hub = HUB.read_text(encoding="utf-8")
common = COMMON.read_text(encoding="utf-8")
overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))

assert overlay["version"] == 80
assert overlay["generatedAt"] == "2026-07-30"
assert overlay["routes"] == [{
    "source": "alo186/hesaplama/usb-c-set-kisa-listesi/index.html",
    "canonicalPath": ROUTE,
    "type": "calculator",
}]

assert html.count("<h1") == 1
assert "USB-C Şarj Seti ve Teknik Kısa Liste" in html
assert '<link rel="canonical" href="https://alo186.com/hesaplama/usb-c-set-kisa-listesi/">' in html
for schema_type in ["WebApplication", "DefinedTermSet", "FAQPage", "BreadcrumbList"]:
    assert schema_type in html
assert "Amazon satış ortaklığı bağlantılarıdır" in html
assert "ALO186 EDAŞ, kamu kurumu, üretici veya ürün satıcısı değildir" in html
assert "Mevcut zincir yeterliyse sonuç satın almamadır" in html
assert "240 W şarj kablosu 10 Gbps veri taşır mı?" in html
assert 'rel="sponsored nofollow noopener"' not in html, "Ürün linkleri uygulama tarafından güvenli şekilde üretilir."
assert not re.search(r"priceCurrency|aggregateRating|availability|offers|seller|warranty", html, re.I)
assert not re.search(r'type=["\'](?:email|tel|text|file|password)["\']', html, re.I)
for token in [
    "actualMissing", "compatibilityChecked", "affiliateAccepted", "devicePowerKnown",
    "hostVideoKnown", "hostDataKnown", "needMultiPortCharging", "cableRole",
    "needHubEthernet", "needHubCardReader", "needHub4k60", "needHub10Gbps",
]:
    assert token in html

for token in [
    "verified_listing",
    "publicAffiliateEligible",
    "rel=\"sponsored nofollow noopener\"",
    "STORAGE_KEY",
    "TTL_MS=30*86400000",
    "LIMIT=6",
    "text/calendar",
    "status:'no_buy'",
    "status:'hazard'",
    "status:'evidence_required'",
    "maxSingleDeviceW",
    "needMultiPortCharging",
    "needHub10Gbps",
    "cableRole==='high_speed'",
]:
    assert token in app
assert "fetch(" not in app and "XMLHttpRequest" not in app
assert "localStorage" in app
assert "catalog-qualified-commerce-run53.js" in loader
assert "B0B127GW4D" in extension and "ugreen-nexode-140w-90322" in extension
for forbidden in ["price:", "stock:", "rating:", "seller:", "warranty:", "availability:", "offers:"]:
    assert forbidden not in extension
assert "@media(max-width:640px)" in styles
assert "prefers-reduced-motion" in styles

tool_match = re.search(r"(\d+) çekirdek araç", hub)
assert tool_match, "Hesaplama Merkezi çekirdek araç sayısı bulunamadı."
tool_count = int(tool_match.group(1))
assert re.search(rf"{tool_count} çekirdek araç", common), "Hub ve runtime araç sayıları ayrıştı."
assert './usb-c-set-kisa-listesi/' in hub
assert "USB-C Şarj Seti ve Teknik Kısa Liste" in hub

print(json.dumps({
    "ok": True,
    "route": ROUTE,
    "actions": [
        "verified_140w_pd31_charger",
        "feature_qualified_hub_shortlist",
        "charging_vs_high_speed_cable_gate",
    ],
    "toolCount": tool_count,
    "commercialFieldsPublished": 0,
    "officialAffiliationClaimed": False,
}, ensure_ascii=False))
