#!/usr/bin/env python3
from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"hesaplama"/"serit-led-guc-kaynagi-uygunluk"
HTML=(MODULE/"index.html").read_text(encoding="utf-8")
JS=(MODULE/"app.js").read_text(encoding="utf-8")
CSS=(MODULE/"styles.css").read_text(encoding="utf-8")
TEST=(MODULE/"app.test.js").read_text(encoding="utf-8")
OVERLAY=json.loads((ROOT/"deployment"/"routing-overlays"/"102-serit-led-guc-kaynagi-uygunluk.json").read_text(encoding="utf-8"))

CANONICAL="/hesaplama/serit-led-guc-kaynagi-uygunluk/"
assert "<!doctype html>" in HTML.lower()
assert "<title>Şerit LED Güç Kaynağı ve Kablo Uygunluk Testi | ALO186</title>" in HTML
assert 'rel="canonical" href="https://alo186.com'+CANONICAL+'"' in HTML
assert HTML.count("<h1>")==1
assert "Amazon Türkiye satış ortaklığı açıklaması" in HTML
assert 'rel="sponsored nofollow noopener"' in HTML
assert "ALO186 bağımsız bilgi platformudur" in HTML
assert "EDAŞ veya kamu kurumu değildir" in HTML
assert '"@type":"Product"' not in HTML and '"@type":"Offer"' not in HTML
for forbidden in ["₺","TL’den","TL den","stokta mevcut","5 yıldız"]:
    assert forbidden.lower() not in HTML.lower()
for token in ["localStorage","sessionStorage","fetch(","geolocation"]:
    assert token not in JS
assert "alo186rehber-21" in JS
assert "commercialAllowed:false" in JS
assert "Mevcut sistem yeterli — yeni ürün almayın" in JS
assert "Üç onayı tamamlayın" in HTML
assert HTML.count("data-affiliate-check")==3
assert "revisitDays:180" in JS
assert "commercialFields:{price:false,stock:false,rating:false,seller:false,warranty:false}" in JS
assert "IEC 61347-2-13:2024" in HTML and "IEC 62031:2026" in HTML
assert "@media(max-width:820px)" in CSS and "@media(max-width:560px)" in CSS
assert "prefers-reduced-motion" in CSS and ":focus-visible" in CSS
assert "aria-live=\"polite\"" in HTML
assert "scenarios:43" in TEST
assert OVERLAY["version"]==102
assert OVERLAY["routes"][0]["canonicalPath"]==CANONICAL
assert OVERLAY["routes"][0]["type"]=="calculator"
ids=re.findall(r'\bid="([^"]+)"',HTML)
assert len(ids)==len(set(ids))
assert all(path.is_file() for path in [MODULE/"index.html",MODULE/"styles.css",MODULE/"app.js",MODULE/"app.test.js"])
print(json.dumps({
  "ok":True,
  "route":CANONICAL,
  "scenarios":43,
  "noBuy":True,
  "affiliateTripleGate":True,
  "unverifiedCommercialFields":False,
  "officialImpression":False,
  "personalData":False,
  "revisitDays":180
},ensure_ascii=False))
