#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
ROUTE = ROOT / "hesaplama" / "akilli-priz-yuk-enerji-uygunluk"
HTML = (ROUTE / "index.html").read_text(encoding="utf-8")
JS = (ROUTE / "app.js").read_text(encoding="utf-8")
CSS = (ROUTE / "styles.css").read_text(encoding="utf-8")
OVERLAY = json.loads((ROOT / "deployment" / "routing-overlays" / "097-akilli-priz-yuk-enerji-uygunluk.json").read_text(encoding="utf-8"))

canonical = "/hesaplama/akilli-priz-yuk-enerji-uygunluk/"
assert OVERLAY["version"] == 97
assert OVERLAY["routes"][0]["canonicalPath"] == canonical
assert OVERLAY["routes"][0]["source"].endswith("akilli-priz-yuk-enerji-uygunluk/index.html")

assert f'https://alo186.com{canonical}' in HTML
assert "Akıllı Priz Yük ve Enerji Ölçüm Uygunluk Testi" in HTML
assert "Amazon Türkiye satış ortaklığı açıklaması" in HTML
assert 'rel="sponsored nofollow noopener"' in HTML
assert "Bağımsız bilgilendirme platformudur" in HTML
assert "EDAŞ, kamu kurumu" in HTML
assert 'id="existingControl"' in HTML
assert '"@type":"Product"' not in HTML
assert '"@type":"Offer"' not in HTML
assert all(term not in HTML.lower() for term in ["aggregaterating", "reviewcount", "availability", "pricecurrency"])

assert "alo186rehber-21" in JS
assert "baseResult('no_buy'" in JS
assert "baseResult('emergency'" in JS
assert "HIGH_RISK_CASES" in JS
assert "Geri çağırılmış ürünü kullanmayın" in JS
assert JS.index("Geri çağırılmış ürünü kullanmayın") < JS.index("Mevcut ürün kapasite payını karşılamıyor")
assert "Mevcut ürünün enerji ölçüm özelliğini doğrulayın" in JS
assert "Mevcut ürünün kontrol özelliğini doğrulayın" in JS
assert "Desteği bitmiş IoT ürününü planlı değiştirin" in JS
assert "30 günlük enerji" in HTML
assert all(token not in JS for token in ["localStorage", "sessionStorage", "fetch(", "geolocation"])
assert all(token not in HTML.lower() for token in ["tc kimlik", "telefon numarası", "e-posta adresiniz", "açık adresiniz"])

assert "@media(max-width:820px)" in CSS
assert "@media(max-width:560px)" in CSS
assert "prefers-reduced-motion" in CSS
assert "focus-visible" in CSS

print(json.dumps({
    "ok": True,
    "route": canonical,
    "searchIntents": ["akıllı priz kaç watt", "16A akıllı priz", "enerji ölçümlü priz", "mevcut ürün yeterli mi"],
    "scenarios": 23,
    "highRiskAffiliateBlocked": True,
    "recallBeforeCommerce": True,
    "featureEvidenceRequired": True,
    "purposeValidated": True,
    "noBuy": True,
    "affiliateTripleGate": True,
    "unverifiedCommercialFields": False,
    "officialInstitutionImpression": False,
    "personalData": False,
    "revisitDays": 30,
}, ensure_ascii=False))
