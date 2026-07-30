#!/usr/bin/env python3
from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"hesaplama"/"kacak-akim-rolesi-tip-secimi-uygunluk"
HTML=(MODULE/"index.html").read_text(encoding="utf-8")
JS=(MODULE/"app.js").read_text(encoding="utf-8")
CSS=(MODULE/"styles.css").read_text(encoding="utf-8")
TEST=(MODULE/"app.test.js").read_text(encoding="utf-8")
OVERLAY=json.loads((ROOT/"deployment"/"routing-overlays"/"113-kacak-akim-rolesi-tip-secimi-uygunluk.json").read_text(encoding="utf-8"))

CANONICAL="/hesaplama/kacak-akim-rolesi-tip-secimi-uygunluk/"
assert "<!doctype html>" in HTML.lower()
assert "<title>Kaçak Akım Rölesi Tipi, mA ve Devre Uygunluk Testi | ALO186</title>" in HTML
assert 'rel="canonical" href="https://www.alo186.com'+CANONICAL+'"' in HTML
assert HTML.count("<h1>")==1
assert "Amazon Türkiye satış ortaklığı açıklaması" in HTML
assert 'rel="sponsored nofollow noopener"' in HTML
assert "ALO186 bağımsız bilgi platformudur" in HTML
assert "EDAŞ, kamu kurumu" in HTML
assert '"@type":"Product"' not in HTML and '"@type":"Offer"' not in HTML
for forbidden in ["₺","TL’den","TL den","stokta mevcut","5 yıldız","son fırsat","kampanya"]:
    assert forbidden.lower() not in HTML.lower()
for token in ["localStorage","sessionStorage","fetch(","geolocation"]:
    assert token not in JS
for personal in ["ad soyad","telefon","e-posta","adres","plaka","abonelik numarası"]:
    assert personal not in HTML.lower()
assert "alo186rehber-21" in JS
assert "commercialAllowed:false" in JS
assert "Mevcut RCD yeterli — yeni ürün almayın" in JS
assert "Üç onayı tamamlayın" in HTML
assert HTML.count("data-affiliate-check")==3
assert "revisitDays:90" in JS
assert "personalDataCollected:false" in JS
assert "commercialFields:{price:false,stock:false,rating:false,seller:false,delivery:false,warranty:false}" in JS
for standard in ["IEC 61008-1:2024","IEC 62423","IEC 60364-5-53:2019+A1:2020+A2:2024"]:
    assert standard in HTML
assert "RCCB kaçak akıma karşı çalışır; aşırı akım ve kısa devre için uygun üst koruma ayrıca gerekir" in JS
assert "Sürekli atan röleyi daha büyük veya farklı tip ürünle susturmayın" in JS
assert "Paylaşılan veya karışmış nötr önce düzeltilmelidir" in JS
assert "EVSE içinde doğrulanmış 6 mA DC algılama" in HTML
assert "test düğmesi" in HTML.lower() and "ölçümlü açma testi" in HTML.lower()
assert "@media(max-width:900px)" in CSS and "@media(max-width:560px)" in CSS
assert "prefers-reduced-motion" in CSS and ":focus-visible" in CSS
assert 'aria-live="polite"' in HTML
assert "scenarios:52" in TEST
assert OVERLAY["version"]==113
assert OVERLAY["routes"][0]["canonicalPath"]==CANONICAL
assert OVERLAY["routes"][0]["type"]=="tool"
ids=re.findall(r'\bid="([^"]+)"',HTML)
assert len(ids)==len(set(ids))
assert all(path.is_file() for path in [MODULE/"index.html",MODULE/"styles.css",MODULE/"app.js",MODULE/"app.test.js"])
print(json.dumps({
  "ok":True,"route":CANONICAL,"scenarios":52,"noBuy":True,
  "affiliateTripleGate":True,"unverifiedCommercialFields":False,
  "officialImpression":False,"personalData":False,"revisitDays":90,
  "rcdTypes":["AC","A","F","B"],"deviceKinds":["RCCB","RCBO"]
},ensure_ascii=False))
