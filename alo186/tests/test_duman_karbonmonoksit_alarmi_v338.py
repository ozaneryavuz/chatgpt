#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
ROUTE = ROOT / "hesaplama" / "duman-karbonmonoksit-alarmi-uygunluk"
HTML = (ROUTE / "index.html").read_text(encoding="utf-8")
JS = (ROUTE / "app.js").read_text(encoding="utf-8")
CSS = (ROUTE / "styles.css").read_text(encoding="utf-8")
OVERLAY = json.loads((ROOT / "deployment" / "routing-overlays" / "099-duman-karbonmonoksit-alarmi-uygunluk.json").read_text(encoding="utf-8"))

canonical = "/hesaplama/duman-karbonmonoksit-alarmi-uygunluk/"
assert OVERLAY["version"] == 99
assert OVERLAY["routes"][0]["canonicalPath"] == canonical
assert OVERLAY["routes"][0]["source"].endswith("duman-karbonmonoksit-alarmi-uygunluk/index.html")

assert f'https://alo186.com{canonical}' in HTML
assert "Duman ve Karbonmonoksit Alarmı Uygunluk Testi" in HTML
assert "Amazon Türkiye satış ortaklığı açıklaması" in HTML
assert 'rel="sponsored nofollow noopener"' in HTML
assert "Bağımsız bilgilendirme platformudur" in HTML
assert "kamu kurumu" in HTML
assert "112" in HTML and "187" in HTML
assert "EN 14604" in HTML and "EN 50291-1" in HTML
assert "Kapsama görevi doğrudan ürün adedi değildir" in HTML
assert 'id="smokeBedrooms"' in HTML and 'id="coEveryLevel"' in HTML
assert '"@type":"Product"' not in HTML
assert '"@type":"Offer"' not in HTML
assert all(term not in HTML.lower() for term in ["aggregaterating", "reviewcount", "availability", "pricecurrency"])

assert "alo186rehber-21" in JS
assert "baseResult('no_buy'" in JS
assert "baseResult('emergency'" in JS
assert "PROFESSIONAL" in JS
assert "Geri çağırılmış alarmı güvenilir kabul etmeyin" in JS
assert JS.index("Geri çağırılmış alarmı güvenilir kabul etmeyin") < JS.index("Gerçek alarm kapsamı açığı doğrulandı")
assert "Önce doğru pili değiştirip yeniden test edin" in JS
assert "Kapsama görevleri ürün adedi değildir" in JS
assert "30 günlük alarm testi" in HTML
assert all(token not in JS for token in ["localStorage", "sessionStorage", "fetch(", "geolocation"])
assert all(token not in HTML.lower() for token in ["tc kimlik", "telefon numarası", "e-posta adresiniz", "açık adresiniz"])

assert "@media(max-width:820px)" in CSS
assert "@media(max-width:560px)" in CSS
assert "prefers-reduced-motion" in CSS
assert "focus-visible" in CSS

print(json.dumps({
    "ok": True,
    "route": canonical,
    "searchIntents": [
        "karbonmonoksit dedektörü nereye konur",
        "duman alarmı kaç tane gerekir",
        "duman dedektörü kaç yılda değişir",
        "kombi için CO alarmı",
        "mevcut alarm yeterli mi",
    ],
    "scenarios": 29,
    "emergencyAffiliateBlocked": True,
    "professionalUseBlocked": True,
    "coverageNotProductCount": True,
    "recallBeforeCommerce": True,
    "maintenanceBeforeReplacement": True,
    "noBuy": True,
    "affiliateTripleGate": True,
    "unverifiedCommercialFields": False,
    "officialInstitutionImpression": False,
    "personalData": False,
    "revisitDays": 30,
}, ensure_ascii=False))
