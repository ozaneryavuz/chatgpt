#!/usr/bin/env python3
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
ARTICLE=ROOT/'alo186/haberler/elektrik-kesilince-diafon-calisir-mi/index.html'
TOOL=ROOT/'alo186/hesaplama/diafon-elektrik-kesintisi-haberlesme-plani/index.html'
GUIDE=ROOT/'alo186/sektor-rehberi/apartman-site-diafon-interkom-kesinti-surekliligi/index.html'
OVERLAY=ROOT/'alo186/deployment/routing-overlays/growth-v287-intercom-outage.json'
DECISION=ROOT/'alo186/deployment/affiliate-category-decisions/intercom-outage-v287.json'
POLICY=ROOT/'alo186/deployment/affiliate_route_risk_policy_v265.json'
ROUTES={ARTICLE:'https://alo186.com/haberler/elektrik-kesilince-diafon-calisir-mi/',TOOL:'https://alo186.com/hesaplama/diafon-elektrik-kesintisi-haberlesme-plani/',GUIDE:'https://alo186.com/sektor-rehberi/apartman-site-diafon-interkom-kesinti-surekliligi/'}
def txt(p):
 assert p.is_file(),p
 return p.read_text(encoding='utf-8')
def check_page(p,canonical):
 s=txt(p); assert re.findall(r'<link\s+rel="canonical"\s+href="([^"]+)"',s,re.I)==[canonical]
 blocks=re.findall(r'<script\s+type="application/ld\+json">(.*?)</script>',s,re.I|re.S); assert blocks
 for b in blocks: json.loads(b)
 for bad in ('https://www.alo186.com','"@type":"Offer"','"@type":"AggregateRating"','"@type":"Review"','"price":','"availability":','"warranty":'): assert bad not in s,bad
 return s
def main():
 article=check_page(ARTICLE,ROUTES[ARTICLE]); tool=check_page(TOOL,ROUTES[TOOL]); guide=check_page(GUIDE,ROUTES[GUIDE])
 for x in ('Tek cihazı yedeklemek bütün işlevleri garanti etmez','PoE anahtarı','kapı açma','yeni ürün almayın','Röle, kilit ve güç kaynağını köprülemeyin','ALO186 EDAŞ, kamu kurumu, üretici, servis veya satıcı değildir'): assert x in article,x
 for x in ('Ücretsiz · kişisel veri yok · mağaza bağlantısı yok','Mevcut sistem yeterli — yeni ürün almayın','Çıkış güvenliği önceliklidir','Yaşam güvenliği ve profesyonel kapsam','30 günlük gösterge kontrolü','90 günlük kesinti testi','365 günlük bakım kapsamı'): assert x in tool,x
 for bad in ('fetch(','XMLHttpRequest','localStorage.','sessionStorage.','document.cookie','www.amazon.com.tr','type="email"','type="tel"'): assert bad not in tool,bad
 for x in ('Diafonu tek cihaz değil, iletişim ve kapı erişim zinciri olarak test edin','Profesyonel envanter','Tüketici affiliate kapsamı neden kapalı','Mevcut sistem; çağrı, ses, video, kapı açma','Bu sayfada Amazon veya başka mağaza bağlantısı yoktur'): assert x in guide,x
 assert 'www.amazon.com.tr' not in article+guide
 overlay=json.loads(txt(OVERLAY)); assert overlay['version']==287 and overlay['name']=='growth-v287-intercom-outage' and len(overlay['routes'])==3
 decision=json.loads(txt(DECISION)); assert decision['decision']=='professional-lead-only'; assert decision['consumerAffiliateDecision']['allowed'] is False
 for k in ('merchantLinks','professionalScopeOnly','noBuyOutcomeRequired','activeHazardCommerceClosed','blockedEgressCommerceClosed','personalDataCollectionForbidden','noPriceStockRatingWarrantyClaims'):
  expected=False if k=='merchantLinks' else True; assert decision['conversionPolicy'][k] is expected,(k,decision['conversionPolicy'][k])
 assert [i['days'] for i in decision['repeatVisitReasons']]==[30,90,365]
 policy=json.loads(txt(POLICY)); pro=policy['professionalLeadOnlyRoutePatterns']
 for x in ('diafon','interkom','goruntulu-kapi-telefonu','sip-interkom'): assert x in pro,x
 print(json.dumps({'ok':True,'version':287,'routes':3,'merchantLinks':0,'professionalOnly':True,'repeatVisitDays':[30,90,365]},ensure_ascii=False))
if __name__=='__main__': main()
