from __future__ import annotations
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TOOL=ROOT/"hesaplama/elektrik-faturasi-kwh-anomali-sayac-kontrolu"
HTML=(TOOL/"index.html").read_text(encoding="utf-8")
JS=(TOOL/"app.js").read_text(encoding="utf-8")
CSS=(TOOL/"styles.css").read_text(encoding="utf-8")
OVERLAY=json.loads((ROOT/"deployment/routing-overlays/114-elektrik-faturasi-kwh-anomali-sayac-kontrolu.json").read_text(encoding="utf-8"))
ROUTE="/hesaplama/elektrik-faturasi-kwh-anomali-sayac-kontrolu/"

assert HTML.count("<h1>")==1
assert f'https://www.alo186.com{ROUTE}' in HTML
for token in ['name="description"','id="kwhForm"','id="result"','id="affiliatePanel"','id="downloadJson"','id="downloadIcs"','id="printResult"','rel="sponsored nofollow noopener"','Amazon satış ortaklığı açıklaması','25–35 günlük','kWh/gün','yeni ürün alınmaz','EPDK, EDAŞ, görevli tedarik şirketi','ALO186 başvuru almaz','fiyat, stok, puan, satıcı, teslimat ve garanti','abone numarası']:
    assert token.lower() in HTML.lower(), token
for schema in ["WebApplication","DefinedTermSet","DefinedTerm","FAQPage","BreadcrumbList"]:
    assert f'"@type":"{schema}"' in HTML
for forbidden in ['"@type":"Product"','"@type":"Offer"','aggregateRating','priceCurrency','availability']:
    assert forbidden not in HTML
for token in ["percentChange","indexMismatchPct","periodFlag","official_check","monitoring_gap","no_buy","professional","needs_evidence","alo186rehber-21","amazon.com.tr","pricePublished:false","stockPublished:false","ratingPublished:false","sellerPublished:false","warrantyPublished:false","BEGIN:VCALENDAR"]:
    assert token in JS,token
for forbidden in ["localStorage","sessionStorage","geolocation","fetch(","XMLHttpRequest"]:
    assert forbidden not in JS
for token in ["@media(max-width:920px)","@media(max-width:620px)","prefers-reduced-motion",":focus-visible","@media print",".affiliate .button[aria-disabled=true]"]:
    assert token in CSS
assert OVERLAY=={"version":114,"generatedAt":"2026-07-30","routes":[{"source":"alo186/hesaplama/elektrik-faturasi-kwh-anomali-sayac-kontrolu/index.html","canonicalPath":ROUTE,"type":"tool"}]}
subprocess.run(["node","--check",str(TOOL/"app.js")],check=True)
subprocess.run(["node",str(TOOL/"app.test.js")],check=True)
print(json.dumps({"ok":True,"route":ROUTE,"officialFirst":True,"dailyNormalization":True,"indexEvidence":True,"noBuyOutcome":True,"affiliateTripleGate":True,"repeatVisitIcs":True,"personalDataCollected":False,"priceStockRatingWarrantyPublished":False},ensure_ascii=False))
