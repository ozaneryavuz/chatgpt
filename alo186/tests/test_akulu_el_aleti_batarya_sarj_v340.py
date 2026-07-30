from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "hesaplama" / "akulu-el-aleti-batarya-sarj-uygunluk"
HTML = (PAGE / "index.html").read_text(encoding="utf-8")
JS = (PAGE / "app.js").read_text(encoding="utf-8")
CSS = (PAGE / "styles.css").read_text(encoding="utf-8")
OVERLAY = ROOT / "deployment" / "routing-overlays" / "099-akulu-el-aleti-batarya-sarj-uygunluk.json"

assert '<link rel="canonical" href="https://alo186.com/hesaplama/akulu-el-aleti-batarya-sarj-uygunluk/">' in HTML
assert '<meta name="viewport"' in HTML
assert '<h1>' in HTML and HTML.count("<h1>") == 1
assert 'aria-live="polite"' in HTML
assert 'class="skip-link"' in HTML
assert "@media(max-width:820px)" in CSS
assert "@media(max-width:560px)" in CSS
assert "@media(prefers-reduced-motion:reduce)" in CSS

schema_match = re.search(r'<script type="application/ld\+json">(.*?)</script>', HTML, re.S)
assert schema_match
schema = json.loads(schema_match.group(1))
types = {item["@type"] for item in schema["@graph"]}
assert {"WebApplication", "DefinedTermSet", "FAQPage", "BreadcrumbList"} <= types
assert "Product" not in types and "Offer" not in types

for token in [
    "Amazon Türkiye satış ortaklığı açıklamasını anladım",
    'rel="sponsored nofollow noopener"',
    "ALO186 fiyat, stok, puan, satıcı, teslimat veya garanti bilgisi yayımlamaz",
    "Kişisel veri yok",
    "Mevcut batarya çalışıyorsa yenisini almayın",
    "Üçüncü taraf batarya adaptörüyle şarj etmeyin",
    "Geri çağrılmış ürünü kullanmayın",
]:
    assert token in HTML or token in JS, token

for forbidden in [
    "localStorage", "sessionStorage", "fetch(", "geolocation",
    'type="email"', 'type="tel"', 'name="email"', 'name="phone"',
]:
    assert forbidden not in HTML + JS

assert "alo186rehber-21" in JS
assert "baseResult('emergency'" in JS
assert "baseResult('no_buy'" in JS
assert "baseResult('conditional_purchase'" in JS
assert "batteryWh" in JS and "chargeHours" in JS
assert "CHARGE_LOSS=1.20" in JS

overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
assert overlay["version"] == 99
assert overlay["routes"] == [{
    "source": "alo186/hesaplama/akulu-el-aleti-batarya-sarj-uygunluk/index.html",
    "canonicalPath": "/hesaplama/akulu-el-aleti-batarya-sarj-uygunluk/",
    "type": "calculator",
}]

print(json.dumps({
    "ok": True,
    "route": "/hesaplama/akulu-el-aleti-batarya-sarj-uygunluk/",
    "mobileBreakpoints": [820, 560],
    "personalData": False,
    "storage": False,
    "affiliateTripleGate": True,
    "structuredData": sorted(types),
}, ensure_ascii=False))
