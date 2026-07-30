from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROUTE = "/hesaplama/usb-c-set-kisa-listesi/"
PAGE = ROOT / "alo186/hesaplama/usb-c-set-kisa-listesi/index.html"
APP = ROOT / "alo186/hesaplama/usb-c-set-kisa-listesi/app.js"
STYLES = ROOT / "alo186/hesaplama/usb-c-set-kisa-listesi/styles.css"
HUB = ROOT / "alo186/hesaplama/index.html"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/usb-c-shortlist-run28.json"

html = PAGE.read_text(encoding="utf-8")
app = APP.read_text(encoding="utf-8")
styles = STYLES.read_text(encoding="utf-8")
hub = HUB.read_text(encoding="utf-8")
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
assert 'rel="sponsored nofollow noopener"' not in html, "Ürün linkleri uygulama tarafından güvenli şekilde üretilir."
assert not re.search(r"priceCurrency|aggregateRating|availability|offers|seller|warranty", html, re.I)
assert not re.search(r'type=["\'](?:email|tel|text|file|password)["\']', html, re.I)
for token in ["actualMissing", "compatibilityChecked", "affiliateAccepted", "devicePowerKnown", "hostVideoKnown", "hostDataKnown"]:
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
]:
    assert token in app
assert "fetch(" not in app and "XMLHttpRequest" not in app
assert "localStorage" in app
assert "@media(max-width:640px)" in styles
assert "prefers-reduced-motion" in styles

assert "35 çekirdek araç" in hub
assert './usb-c-set-kisa-listesi/' in hub
assert "USB-C Şarj Seti ve Teknik Kısa Liste" in hub

print(json.dumps({
    "ok": True,
    "route": ROUTE,
    "actions": [
        "no_buy_usb_c_chain",
        "missing_component_affiliate_shortlist",
        "local_shortlist_and_30_day_recheck",
    ],
    "commercialFieldsPublished": 0,
    "officialAffiliationClaimed": False,
}, ensure_ascii=False))
