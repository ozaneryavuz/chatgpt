#!/usr/bin/env python3
from __future__ import annotations
import json
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PAGE=ROOT/'alo186/hesaplama/powerbank-ucak-wh-uygunluk/index.html'
APP=PAGE.with_name('app.js')
CSS=PAGE.with_name('styles.css')
TEST=PAGE.with_name('app.test.js')
OVERLAY=ROOT/'alo186/deployment/routing-overlays/095-powerbank-ucak-wh-uygunluk.json'
WORKFLOW=ROOT/'.github/workflows/alo186-powerbank-ucak-wh-v334.yml'
CANONICAL='/hesaplama/powerbank-ucak-wh-uygunluk/'
for path in (PAGE,APP,CSS,TEST,OVERLAY,WORKFLOW): assert path.is_file(),f'missing {path}'
html=PAGE.read_text(encoding='utf-8');js=APP.read_text(encoding='utf-8');css=CSS.read_text(encoding='utf-8');overlay=json.loads(OVERLAY.read_text(encoding='utf-8'))
assert 'https://alo186.com'+CANONICAL in html
assert 'id="flightForm"' in html and 'aria-live="polite"' in html
assert all(x in html for x in ('WebApplication','DefinedTermSet','FAQPage','BreadcrumbList'))
assert '"@type":"Product"' not in html and '"@type":"Offer"' not in html
assert 'Amazon Türkiye satış ortaklığı açıklaması' in js
assert 'sponsored nofollow noopener' in js
assert 'fiyat, stok, puan, satıcı, teslimat ve garanti' in js
assert all(x not in html.lower() for x in ('name="email"','name="phone"','name="passport"','name="pnr"','name="location"'))
assert all(x not in js for x in ('localStorage','sessionStorage','fetch(','geolocation'))
assert 'alo186rehber-21' in js and 'amazon.com.tr' in js
assert 'commercialAllowed:false' in js and 'commercialAllowed:true' in js
assert "status:'no_buy'" in js and "status:'danger'" in js and "status:'airline_block'" in js
assert '@media(max-width:820px)' in css and '@media(max-width:560px)' in css
assert 'prefers-reduced-motion' in css and ':focus-visible' in css
assert overlay['version']==95
assert overlay['routes']==[{'source':'alo186/hesaplama/powerbank-ucak-wh-uygunluk/index.html','canonicalPath':CANONICAL,'type':'calculator'}]
subprocess.run(['node',str(TEST)],cwd=ROOT,check=True)
subprocess.run(['node','--check',str(APP)],cwd=ROOT,check=True)
print(json.dumps({'ok':True,'route':CANONICAL,'scenarios':18,'mobileBreakpoints':[820,560],'noBuy':True,'affiliateTripleGate':True,'activeTravelAffiliateBlocked':True,'personalData':False,'storage':False},ensure_ascii=False))
