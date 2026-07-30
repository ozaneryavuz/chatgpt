#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALO = ROOT / "alo186"
ROUTE = ALO / "hesaplama" / "seyahat-priz-adaptoru-voltaj-uygunluk"
HTML = (ROUTE / "index.html").read_text(encoding="utf-8")
APP = (ROUTE / "app.js").read_text(encoding="utf-8")
CORE = (ROUTE / "core.js").read_text(encoding="utf-8")
CSS = (ROUTE / "styles.css").read_text(encoding="utf-8")
HUB = (ALO / "hesaplama" / "index.html").read_text(encoding="utf-8")
OVERLAY = json.loads((ALO / "deployment" / "routing-overlays" / "087-travel-adapter-suitability.json").read_text(encoding="utf-8"))

CANONICAL = "https://alo186.com/hesaplama/seyahat-priz-adaptoru-voltaj-uygunluk/"
PATH = "/hesaplama/seyahat-priz-adaptoru-voltaj-uygunluk/"

assert '<link rel="canonical" href="%s">' % CANONICAL in HTML
assert HTML.count("<h1") == 1
assert "Seyahat Priz Adaptörü ve Voltaj Uygunluk Testi" in HTML
assert "Priz adaptörü voltaj veya frekans dönüştürmez" in HTML
assert "Mevcut adaptör yeterliyse yeni ürün almayın" in HTML
assert "Amazon satış ortaklığı bağlantısı" in HTML
assert 'rel="sponsored nofollow noopener"' in HTML
assert "Fiyat, stok, satıcı, puan, teslimat ve garanti" in HTML
assert "EDAŞ, seyahat acentesi, üretici, satıcı veya yetkili servis değildir" in HTML
assert "IEC 60884-2-5:2017" in HTML
assert "25 Haziran 2026" in HTML

scripts = re.findall(r'<script type="application/ld\+json">(.*?)</script>', HTML, flags=re.S)
assert scripts, "JSON-LD bulunamadı"
types: set[str] = set()
for raw in scripts:
    payload = json.loads(raw)
    nodes = payload.get("@graph", [payload]) if isinstance(payload, dict) else []
    for node in nodes:
        if isinstance(node, dict) and isinstance(node.get("@type"), str):
            types.add(node["@type"])
assert {"WebApplication", "DefinedTermSet", "FAQPage", "BreadcrumbList"} <= types

for forbidden in ("localStorage", "sessionStorage", "navigator.geolocation", "fetch(", "XMLHttpRequest"):
    assert forbidden not in APP
for personal in ('type="email"', 'type="tel"', 'name="address"', "T.C. kimlik", "abonelik numarası"):
    assert personal not in HTML
for schema_forbidden in ('"Offer"', '"AggregateOffer"', '"offers"', '"aggregateRating"', '"review"'):
    assert schema_forbidden not in HTML

assert "alo186rehber-21" in APP
assert "aria-disabled" in APP
assert "affiliateGate" in HTML and "affiliateGate" in APP
assert "JSON sonuç fişi" in HTML and ".ics" not in HTML.lower()
assert "BEGIN:VCALENDAR" in APP and "7 gün önce" in HTML
assert "adaptörleri art arda" in CORE.lower()
assert "recallChecked==='no'" in CORE
assert "50/60 Hz (bölgeye göre)" in CORE
assert "@media(max-width:580px)" in CSS
assert "prefers-reduced-motion" in CSS
assert "@media print" in CSS

assert OVERLAY["version"] == 87
route = next(item for item in OVERLAY["routes"] if item["canonicalPath"] == PATH)
assert route["source"] == "alo186/hesaplama/seyahat-priz-adaptoru-voltaj-uygunluk/index.html"
assert route["type"] == "tool"
assert "./seyahat-priz-adaptoru-voltaj-uygunluk/" in HUB
assert "41 çekirdek araç" in HUB
assert "Seyahat Priz Adaptörü ve Voltaj Uygunluğu" in HUB

subprocess.run(["node", str(ROUTE / "core.test.js")], cwd=ROOT, check=True)
subprocess.run(["node", "--check", str(ROUTE / "core.js")], cwd=ROOT, check=True)
subprocess.run(["node", "--check", str(ROUTE / "app.js")], cwd=ROOT, check=True)

print(json.dumps({
    "ok": True,
    "canonical": CANONICAL,
    "routingVersion": OVERLAY["version"],
    "jsonLdTypes": sorted(types),
    "commerce": "conditional and disclosed",
    "unverifiedCommercialFields": 0,
    "personalDataFields": 0,
}, ensure_ascii=False, indent=2))
