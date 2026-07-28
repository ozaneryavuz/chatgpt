'use strict';

const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const repoRoot=path.resolve(__dirname,'../..');
const read=relative=>fs.readFileSync(path.join(repoRoot,relative),'utf8');
const wallet=require('../hesaplama/evidence-wallet.js');
const router=require('../hesaplama/intent-action-router.js');

wallet.clear();
const now=new Date('2026-07-28T19:00:00.000Z');
assert.equal(wallet.safePath('https://www.alo186.com/hesaplama/powerbank-usb-c-uygunluk/?mah=20000'),'/hesaplama/powerbank-usb-c-uygunluk/');
assert.equal(wallet.safePath('https://www.amazon.com.tr/dp/B0SECRET?tag=affiliate'),'');
assert.equal(wallet.categoryFromPath('/hesaplama/powerbank-usb-c-uygunluk/'),'powerbank');
assert.equal(wallet.categoryFromPath('/hesaplama/duman-alarmi-yerlesim-bakim-uygunluk/'),'smoke_alarm');
const evidence=wallet.record('powerbank','/hesaplama/powerbank-usb-c-uygunluk/',now);
assert.equal(evidence.category,'powerbank');
assert.equal(evidence.expiresAt,'2026-09-11T19:00:00.000Z');
assert.equal(wallet.status('powerbank',new Date('2026-08-10T00:00:00.000Z')).state,'current');
assert.equal(wallet.status('powerbank',new Date('2026-09-08T00:00:00.000Z')).state,'expiring');
assert.equal(wallet.status('powerbank',new Date('2026-09-20T00:00:00.000Z')).state,'expired');
assert.equal(wallet.status('ev_cable',now).state,'missing');
assert.doesNotMatch(JSON.stringify(evidence),/email|phone|address|asin|price|stock|seller|warranty|mah|watt/i);
wallet.clear();

assert.equal(router.resolve('/haberler/ups-surekli-otuyor-bip-sesi-ne-anlama-gelir').id,'backup');
assert.equal(router.resolve('/haberler/kacak-akim-rolesi-tip-s-selektivite-nedir').id,'protection');
assert.equal(router.resolve('/haberler/ges-inverter-afci-dc-ark-hatasi').id,'solar');
assert.equal(router.resolve('/haberler/ev-sarj-gucu-neden-dusuk-yavas-sarj').id,'ev');
assert.equal(router.resolve('/haberler/vpp-sanal-guc-santrali-nedir').id,'business');
assert.equal(router.resolve('/karar-motoru'),null);
for(const group of router.GROUPS){
  assert.ok(group.primary[0].startsWith('/'),'Birincil CTA ALO186 iç rotası olmalı.');
  assert.ok(group.secondary[0].startsWith('/'),'İkincil CTA ALO186 iç rotası olmalı.');
  assert.doesNotMatch(JSON.stringify(group),/amazon\.|fiyat|stok|puan|garanti/i);
}

const common=read('alo186/hesaplama/common.js');
const conversion=read('alo186/urun-eslestirme/conversion-growth.js');
const planHtml=read('alo186/hesaplama/elektrik-planim/index.html');
const planGrowth=read('alo186/hesaplama/elektrik-planim/growth.js');
const evidenceSource=read('alo186/hesaplama/evidence-wallet.js');
const intentSource=read('alo186/hesaplama/intent-action-router.js');

assert.match(common,/evidence-wallet\.js/);
assert.match(common,/intent-action-router\.js/);
assert.match(conversion,/qualifiedEvidenceStatus/);
assert.match(conversion,/evidence\.state==='current'/);
assert.match(conversion,/box\.disabled=true/);
assert.match(conversion,/45|gün geçerli/);
assert.match(planHtml,/Teknik Doğrulama Cüzdanı/);
assert.match(planHtml,/45 gün/);
assert.match(planGrowth,/technicalEvidenceLifecycle/);
assert.match(planGrowth,/technical_evidence_lifecycle_opened/);
assert.match(planGrowth,/Ham hesap/);
assert.match(intentSource,/Arama niyetinden güvenli sonraki adıma/);
assert.match(intentSource,/Bu kartta ürün veya satış ortaklığı bağlantısı yoktur/);
assert.match(evidenceSource,/MAX_RECORDS=12/);
assert.match(evidenceSource,/TTL_DAYS=45/);
assert.doesNotMatch(evidenceSource,/amazon\.com\.tr\/dp|ASIN|price|stock|seller|warranty/i);
assert.doesNotMatch(planHtml,/type="(?:email|tel|text)"|<textarea/i);

console.log('ALO186 intent/evidence growth: arama niyeti CTA, teknik kanıt cüzdanı, affiliate otomatik kapı ve tekrar ziyaret testleri başarılı.');
