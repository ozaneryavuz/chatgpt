'use strict';

const assert=require('node:assert/strict');
const core=require('./documentation-growth-core.js');

const now=new Date('2026-07-28T12:00:00.000Z');

const completePowerbank=core.assessProduct({
  category:'powerbank',verifiedAt:'2026-07-27',
  attributes:{capacityMah:20000,energyWh:72,maxOutputW:200,wireless:false,usbCPorts:2,display:true}
},{now,maxAgeDays:45});
assert.equal(completePowerbank.status,'complete');
assert.equal(completePowerbank.score,100);
assert.equal(completePowerbank.affiliateAllowed,true);
assert.deepEqual(completePowerbank.criticalMissing,[]);

const blockedPowerbank=core.assessProduct({
  category:'powerbank',verifiedAt:'2026-07-27',
  attributes:{capacityMah:10000,energyWh:null,maxOutputW:null,wireless:true,usbCPorts:null,display:false}
},{now,maxAgeDays:45});
assert.equal(blockedPowerbank.status,'blocked');
assert.equal(blockedPowerbank.affiliateAllowed,false);
assert.ok(blockedPowerbank.criticalMissing.includes('max_output_w'));
assert.ok(blockedPowerbank.questions.some(q=>q.includes('USB-C PD')));

const conditionalStrip=core.assessProduct({
  category:'surge_strip',verifiedAt:'2026-07-27',
  attributes:{outlets:6,joules:1000,maxCurrentA:16,maxPowerW:3500,usbPorts:null,cableM:null}
},{now,maxAgeDays:45});
assert.equal(conditionalStrip.status,'conditional');
assert.equal(conditionalStrip.affiliateAllowed,true);
assert.equal(conditionalStrip.criticalMissing.length,0);

const stale=core.assessProduct({
  category:'surge_strip',verifiedAt:'2026-01-01',
  attributes:{outlets:6,joules:1000,maxCurrentA:16,maxPowerW:3500}
},{now,maxAgeDays:45});
assert.equal(stale.status,'stale');
assert.equal(stale.affiliateAllowed,false);

const generic=core.assessProduct({category:'power_station',verifiedAt:'2026-07-27',attributes:{}},{now});
assert.equal(generic.status,'blocked');
assert.equal(generic.professionalOnly,false);
assert.ok(generic.criticalMissing.includes('usable_wh'));

const professional=core.assessProduct({category:'generator',verifiedAt:'2026-07-27',attributes:{}},{now});
assert.equal(professional.professionalOnly,true);
assert.equal(professional.affiliateAllowed,false);

const questions=core.questionPack('ev_cable',['phase_current','ip_temperature']);
assert.equal(questions.length,2);
assert.ok(questions.every(item=>item.critical));
const text=core.buildQuestionText('ev_cable','Type 2 ürün kartı',['phase_current','ip_temperature']);
assert.match(text,/Marka Bağımsız Teknik Veri Soru Paketi/);
assert.match(text,/Kablo monofaze\/trifaze hangi akım ve güç sınıflarını destekler/);
assert.match(text,/IP sınıfı ile çalışma\/saklama sıcaklıkları/);
assert.match(text,/fiyat, stok, puan, garanti veya ürün uygunluk onayı değildir/i);
assert.doesNotMatch(text,/amazon|asin|satıcı puanı|kampanya/i);

const route=core.supplierRoute('surge_strip',['joules','max_current_a','invalid','asin']);
assert.match(route,/^\/tedarikci-ve-uretici-isbirligi\?/);
assert.match(route,/source=documentation_gap/);
assert.match(route,/category=safety/);
assert.match(route,/fields=joules%2Cmax_current_a/);
assert.doesNotMatch(route,/invalid|asin/);

const review=core.sanitizeReview({category:'powerbank',productId:'anker-a1336',missing:['energy_wh','invalid']},now);
assert.equal(review.category,'powerbank');
assert.deepEqual(review.missing,['energy_wh']);
assert.equal(review.reviewAt,'2026-08-11T12:00:00.000Z');
assert.equal(review.expiresAt,'2026-09-11T12:00:00.000Z');
assert.equal(core.hasForbiddenData(review),false);

const bad={...review,email:'user@example.com'};
assert.equal(core.normalizeReviews([bad],now).length,0);
const clean=core.normalizeReviews([review],now);
assert.equal(clean.length,1);

const ics=core.buildReviewIcs(review,'https://www.alo186.com');
assert.match(ics,/BEGIN:VCALENDAR/);
assert.match(ics,/DTSTART;VALUE=DATE:20260811/);
assert.match(ics,/akilli-urun-secimi\?kategori=powerbank/);
assert.doesNotMatch(ics,/ATTENDEE|ORGANIZER|LOCATION|EMAIL|PHONE/i);

const exported=core.exportPayload([review],now);
assert.equal(exported.schema,'alo186-documentation-reviews-v1');
assert.equal(exported.records.length,1);
assert.equal(core.hasForbiddenData(exported.records[0]),false);
assert.doesNotMatch(JSON.stringify(exported.records),/asin|price|stock|seller|warranty|email|phone|address/i);
assert.match(exported.privacy,/ASIN/);

console.log('ALO186 belge öncelikli ürün güveni: kapsam skoru, kritik alan, soru paketi, tedarikçi rotası ve 14 günlük tekrar kontrol testleri başarılı.');
