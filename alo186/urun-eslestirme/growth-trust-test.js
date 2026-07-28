'use strict';

const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const catalog=require('./catalog.js');
const matcher=require('./matcher-core.js');

const freshNow=new Date('2026-07-28T12:00:00Z');
const staleNow=new Date('2026-10-01T12:00:00Z');

assert.equal(catalog.verificationMaxAgeDays,45,'Doğrulama süresi 45 gün olmalı.');
assert.equal(catalog.verificationStatus(catalog.products[0],freshNow).fresh,true,'Yeni doğrulama güncel sayılmalı.');
assert.equal(catalog.verificationStatus(catalog.products[0],staleNow).fresh,false,'Süresi geçen doğrulama güncel sayılmamalı.');

const freshPowerbank=matcher.match('powerbank',{minCapacityMah:20000,minOutputW:25,wireless:false},{now:freshNow});
assert.ok(freshPowerbank.matches.length>0,'Güncel doğrulanmış tüketici ürünü eşleşmeli.');
assert.equal(freshPowerbank.staleProductCount,0,'Yeni katalog stale ürün göstermemeli.');
assert.equal(freshPowerbank.affiliatePolicy,'verified_direct');

const stalePowerbank=matcher.match('powerbank',{minCapacityMah:10000,minOutputW:10,wireless:false},{now:staleNow});
assert.equal(stalePowerbank.matches.length,0,'Süresi geçmiş kart doğrudan ürün eşleşmesine girmemeli.');
assert.ok(stalePowerbank.staleProductCount>0,'Süresi geçmiş kart sayısı raporlanmalı.');
assert.equal(stalePowerbank.catalogFresh,false);

const miniUps=matcher.match('mini_ups',{}, {now:freshNow});
assert.equal(miniUps.mode,'guide');
assert.equal(miniUps.affiliatePolicy,'after_tool');
assert.equal(miniUps.professionalSelectionRequired,true);
assert.match(miniUps.nextStep.url,/modem-internet-yedekleme/);

const powerStation=matcher.match('power_station',{}, {now:freshNow});
assert.equal(powerStation.affiliatePolicy,'after_tool');
assert.match(powerStation.nextStep.url,/ups-suresi/);

const outletTester=matcher.match('outlet_tester',{}, {now:freshNow});
assert.equal(outletTester.affiliatePolicy,'professional_only');
assert.equal(outletTester.professionalSelectionRequired,true);
assert.match(outletTester.nextStep.url,/karar-motoru/);

const emergencyLight=matcher.match('emergency_light',{}, {now:freshNow});
assert.equal(emergencyLight.affiliatePolicy,'after_checklist');
assert.equal(emergencyLight.professionalSelectionRequired,false);

const smokeAlarm=matcher.match('smoke_alarm',{}, {now:freshNow});
assert.equal(smokeAlarm.affiliatePolicy,'after_checklist');
assert.equal(smokeAlarm.professionalSelectionRequired,true);

const app=fs.readFileSync(path.join(__dirname,'app.js'),'utf8');
const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
const styles=fs.readFileSync(path.join(__dirname,'styles.css'),'utf8');

assert.match(app,/affiliatePolicy==='after_tool'\|\|result\.affiliatePolicy==='professional_only'/,'Profesyonel ve araç gerektiren kategoriler ayrı kapıdan geçmeli.');
assert.match(app,/affiliate_exposure_blocked/,'Engellenen ticari gösterimler ölçülmeli.');
assert.match(app,/stale_catalog/,'Eski katalog nedeniyle affiliate bloklama bulunmalı.');
assert.match(app,/alo186_product_decision_v1/,'Son karar yalnız tarayıcıda saklanmalı.');
assert.match(app,/reviewDays=30/,'Tekrar kontrol döngüsü 30 gün olmalı.');
assert.match(html,/id="savedDecision"/,'Geri dönüş paneli görünür arayüzde bulunmalı.');
assert.match(html,/Kişisel veri|ad, adres, abonelik/,'Veri minimizasyonu açıkça belirtilmeli.');
assert.match(html,/satış ortaklığı/,'Affiliate açıklaması görünür olmalı.');
assert.match(html,/EDAŞ veya kamu kurumu değildir/,'Resmî kurum izlenimi reddedilmeli.');
assert.match(styles,/\.disabled-link\{pointer-events:none/,'Onay verilmeden affiliate bağlantısı etkinleşmemeli.');

console.log('ALO186 affiliate trust ve repeat-visit testleri başarılı.');
