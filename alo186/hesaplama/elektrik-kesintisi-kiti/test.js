'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const core=require('./core.js');
const now=new Date('2026-07-28T12:00:00.000Z');

const base={profile:'home',outageHours:6,needs:['mobile','internet','lighting'],inventory:{powerbank:'tested',mini_ups:'missing',emergency_light:'unknown',smoke_alarm:'tested',surge_strip:'unknown',power_station:'missing'}};
const result=core.evaluate(base);
assert.equal(result.status,'gaps');
assert.equal(result.metrics.required,4);
assert.equal(result.metrics.covered,2);
assert.equal(result.metrics.verify,1);
assert.equal(result.metrics.missing,1);
assert.equal(result.metrics.noBuy,2);
assert.equal(result.items.find(item=>item.id==='mini_ups').affiliateAllowed,true);
assert.equal(result.items.find(item=>item.id==='emergency_light').affiliateAllowed,false);
assert.equal(result.items.find(item=>item.id==='powerbank').status,'covered');
assert.ok(!result.items.some(item=>item.id==='power_station'));

const long=core.evaluate({...base,outageHours:12,needs:['mobile','internet','lighting','cold_chain']});
assert.ok(long.items.some(item=>item.id==='power_station'));
assert.equal(long.items.find(item=>item.id==='power_station').status,'missing');

const medical=core.evaluate({...base,needs:['mobile','medical']});
assert.equal(medical.status,'professional');
assert.equal(medical.professionalRequired,true);
assert.ok(medical.items.every(item=>item.status==='professional'));
assert.equal(medical.affiliateAllowed,false);

const hotel=core.evaluate({...base,profile:'hotel_site'});
assert.equal(hotel.status,'professional');
assert.ok(hotel.items.every(item=>item.status==='professional'));

const business=core.evaluate({...base,profile:'small_business',outageHours:12,needs:['cold_chain'],inventory:{power_station:'missing',emergency_light:'tested',smoke_alarm:'tested'}});
assert.equal(business.items.find(item=>item.id==='power_station').status,'professional');

const ready=core.evaluate({...base,inventory:{powerbank:'tested',mini_ups:'tested',emergency_light:'tested',smoke_alarm:'tested'}});
assert.equal(ready.status,'ready');
assert.equal(ready.metrics.missing,0);
assert.equal(ready.metrics.noBuy,4);
assert.equal(ready.affiliateAllowed,false);

const record=core.record(base,now);
assert.equal(record.reviewAt,'2026-10-26T12:00:00.000Z');
assert.ok(core.isValidRecord(record));
assert.deepEqual(Object.keys(record).sort(),['createdAt','inventory','metrics','missingCategories','needs','outageHours','professionalCategories','profile','reviewAt','score','status','verifyCategories','version'].sort());

const brief=core.brief(result);
assert.match(brief,/Marka Bağımsız Elektrik Kesintisi Kiti/);
assert.match(brief,/MEVCUT — yeni ürün önerilmez/);
assert.match(brief,/satış ortaklığı/);
assert.doesNotMatch(brief,/\b(?:TL|₺|fiyat:\s*\d|stok:\s*\d|puan:\s*\d|garanti:\s*\d)/i);
assert.doesNotMatch(brief,/amazon\.(?:com|com\.tr)/i);

const share=core.sharePayload(result);
assert.equal(share.url,'https://www.alo186.com/hesaplama/elektrik-kesintisi-kiti/');
assert.doesNotMatch(JSON.stringify(share),/email|phone|address|subscription|serial|seller|price|asin/i);

const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
assert.match(html,/https:\/\/www\.alo186\.com\/hesaplama\/elektrik-kesintisi-kiti\//);
assert.match(html,/WebApplication/);
assert.match(html,/FAQPage/);
assert.match(html,/Reklam \/ satış ortaklığı açıklaması/);
assert.match(html,/Mevcut ürün önce/);
assert.match(html,/id="installBtn"/);
assert.doesNotMatch(html,/type="(?:email|tel|text)"|<textarea/i);
assert.doesNotMatch(html,/amazon\.(?:com|com\.tr)\//i);

console.log('Elektrik kesintisi kiti: envanter, satın almama, teknik kapı, profesyonel sınır, PWA ve gizlilik testleri başarılı.');
