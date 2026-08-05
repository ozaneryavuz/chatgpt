#!/usr/bin/env python3
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
ARTICLE=ROOT/'alo186/haberler/elektrik-kesilince-pos-cihazi-yazar-kasa-calisir-mi/index.html'
TOOL=ROOT/'alo186/hesaplama/kucuk-isletme-elektrik-kesintisi-satis-surekliligi-plani/index.html'
GUIDE=ROOT/'alo186/sektor-rehberi/market-kafe-magaza-pos-yazar-kasa-kesinti-surekliligi/index.html'
OVERLAY=ROOT/'alo186/deployment/routing-overlays/growth-v289-small-business-pos-outage.json'
DECISION=ROOT/'alo186/deployment/affiliate-category-decisions/small-business-pos-outage-v289.json'
ROUTES={ARTICLE:'https://alo186.com/haberler/elektrik-kesilince-pos-cihazi-yazar-kasa-calisir-mi/',TOOL:'https://alo186.com/hesaplama/kucuk-isletme-elektrik-kesintisi-satis-surekliligi-plani/',GUIDE:'https://alo186.com/sektor-rehberi/market-kafe-magaza-pos-yazar-kasa-kesinti-surekliligi/'}
def txt(p):
 assert p.is_file(),p
 return p.read_text(encoding='utf-8')
def check_page(p,canonical):
 s=txt(p)
 assert re.findall(r'<link\s+rel="canonical"\s+href="([^"]+)"',s,re.I)==[canonical]
 blocks=re.findall(r'<script\s+type="application/ld\+json">(.*?)</script>',s,re.I|re.S)
 assert blocks
 for b in blocks: json.loads(b)
 for bad in ('https://www.alo186.com','"@type":"Offer"','"@type":"AggregateRating"','"@type":"Review"','"price":','"availability":','"warranty":'):
  assert bad not in s,bad
 return s
def main():
 article=check_page(ARTICLE,ROUTES[ARTICLE]); tool=check_page(TOOL,ROUTES[TOOL]); guide=check_page(GUIDE,ROUTES[GUIDE])
 for x in ('Terminalin açılması, satışın ve mali kaydın tamamlanacağı anlamına gelmez','Yarım kalan işlem için güvenli sıra','Mevcut sistem yeterliyse yeni ürün almayın','Bu sayfada Amazon veya başka mağaza bağlantısı yoktur','ALO186; GİB, banka, ödeme kuruluşu, cihaz üreticisi, yetkili servis, EDAŞ veya kamu kurumu değildir'):
  assert x in article,x
 for x in ('Ücretsiz · kişisel veri yok · mağaza bağlantısı yok','Mevcut sistem yeterli — yeni ürün almayın','30 günlük fiziksel kontrol','90 günlük süreklilik gözden geçirmesi','365 günlük profesyonel kapsam yenilemesi','Bu araçta Amazon veya başka mağaza bağlantısı yoktur'):
  assert x in tool,x
 for bad in ('fetch(','XMLHttpRequest','localStorage.','sessionStorage.','document.cookie','www.amazon.com.tr','type="email"','type="tel"','name="card"','name="amount"'):
  assert bad not in tool,bad
 for x in ('Satış sürekliliğini tek UPS değil, ödeme ve mali kayıt zinciri olarak yönetin','Profesyonel envanter','Tüketici affiliate kapsamı neden sınırlı','Mevcut sistem yeterliyse yeni ürün almayın','Bu sayfada Amazon veya başka mağaza bağlantısı yoktur'):
  assert x in guide,x
 assert 'www.amazon.com.tr' not in article+tool+guide
 overlay=json.loads(txt(OVERLAY)); assert overlay['version']==289 and overlay['name']=='growth-v289-small-business-pos-outage' and len(overlay['routes'])==3
 decision=json.loads(txt(DECISION)); assert decision['decision']=='decision-first-professional-led'; assert decision['consumerAffiliateDecision']['newMerchantLinksAllowed'] is False
 expected={'newMerchantLinks':False,'professionalScopeForFiscalAndPaymentHardware':True,'noBuyOutcomeRequired':True,'activeHazardCommerceClosed':True,'uncertainTransactionCommerceClosed':True,'personalDataCollectionForbidden':True,'noPriceStockRatingWarrantyClaims':True,'affiliateDisclosureRequiredBeforeAnyDownstreamMerchantLink':True,'officialInstitutionImpressionForbidden':True}
 for k,v in expected.items(): assert decision['conversionPolicy'][k] is v,(k,decision['conversionPolicy'][k])
 assert [i['days'] for i in decision['repeatVisitReasons'] if 'days' in i]==[30,90,365]
 assert len(decision['professionalOnlyClasses'])>=8
 assert len(decision['conversionPoints'])>=5
 print(json.dumps({'ok':True,'version':289,'routes':3,'newMerchantLinks':0,'professionalLed':True,'repeatVisitDays':[30,90,365]},ensure_ascii=False))
if __name__=='__main__': main()
