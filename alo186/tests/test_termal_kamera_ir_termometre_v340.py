from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTE = ROOT / "hesaplama" / "termal-kamera-kizilotesi-termometre-uygunluk"
HTML = (ROUTE / "index.html").read_text(encoding="utf-8")
JS = (ROUTE / "app.js").read_text(encoding="utf-8")
CSS = (ROUTE / "styles.css").read_text(encoding="utf-8")
TEST = (ROUTE / "app.test.js").read_text(encoding="utf-8")
OVERLAY_PATH = ROOT / "deployment" / "routing-overlays" / "100-termal-kamera-kizilotesi-termometre-uygunluk.json"
OVERLAY = json.loads(OVERLAY_PATH.read_text(encoding="utf-8"))

CANONICAL = "/hesaplama/termal-kamera-kizilotesi-termometre-uygunluk/"

assert '<html lang="tr">' in HTML
assert f'https://alo186.com{CANONICAL}' in HTML
assert 'Termal Kamera mı Kızılötesi Termometre mi?' in HTML
assert 'ALO186 bağımsız bilgi platformudur' in HTML
assert 'EDAŞ, kamu kurumu' in HTML
assert 'Amazon Türkiye satış ortaklığı açıklaması' in HTML
assert 'rel="sponsored nofollow noopener"' in HTML
assert 'Fiyat ve stok yok' in HTML
assert 'Satın almama sonucu' in HTML
assert 'Termal görüntü, enerjili panoda çalışma izni değildir' in HTML
assert 'Normal cam' in HTML
assert 'Emissivite' in HTML or 'emissivite' in HTML
assert 'ISO 18434-1:2008' in HTML
assert 'OSHA 29 CFR 1910.333' in HTML
assert '30 Temmuz 2026' in HTML

for forbidden in [
    '"@type":"Product"', '"@type": "Product"',
    '"@type":"Offer"', '"@type": "Offer"',
    '"offers"', '"aggregateRating"', '"review"',
]:
    assert forbidden not in HTML

for token in ["localStorage", "sessionStorage", "fetch(", "geolocation"]:
    assert token not in JS

assert "alo186rehber-21" in JS
assert "commercialAllowed:false" in JS
assert "baseResult('emergency'" in JS
assert "baseResult('professional'" in JS
assert "baseResult('no_buy'" in JS
assert "Mevcut cihaz yeterli — yeni ürün almayın" in JS
assert "Açık enerjili ekipmanda tüketici ürünü akışı kapalı" in JS
assert "Geri çağırılmış cihazı güvenilir kabul etmeyin" in JS
assert "Fiyat veya kampanya takibi değildir" in JS
assert "price:false" in JS and "stock:false" in JS and "warranty:false" in JS

for field in ["confirmNeed", "confirmTech", "confirmAffiliate"]:
    assert f'id="{field}"' in HTML
    assert field in JS

assert "@media(max-width:820px)" in CSS
assert "@media(max-width:560px)" in CSS
assert "prefers-reduced-motion" in CSS
assert "aria-live" in HTML
assert "skip-link" in HTML

assert "scenarios:24" in TEST
assert "no_buy" in TEST
assert "professional" in TEST
assert "conditional_purchase" in TEST

assert OVERLAY["version"] == 100
assert OVERLAY["generatedAt"] == "2026-07-30"
assert OVERLAY["routes"] == [{
    "source": "alo186/hesaplama/termal-kamera-kizilotesi-termometre-uygunluk/index.html",
    "canonicalPath": CANONICAL,
    "type": "calculator",
}]

links = re.findall(r'href="([^"]+)"', HTML)
assert all(not link.startswith("http://") for link in links)
assert "Product" not in json.dumps(json.loads(re.search(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', HTML, re.S).group(1)))

print(json.dumps({
    "ok": True,
    "canonical": CANONICAL,
    "scenarios": 24,
    "affiliateTripleGate": True,
    "noBuy": True,
    "energizedProfessionalBoundary": True,
    "commercialFields": False,
    "personalData": False,
    "storage": False,
    "revisitDays": 90,
}, ensure_ascii=False))
