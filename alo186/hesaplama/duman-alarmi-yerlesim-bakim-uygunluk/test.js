'use strict';

const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const core=require('./core.js');

const base={
  useCase:'home',ownership:'candidate',floors:1,basement:false,bedrooms:2,sleepingAreas:1,sleepingLevels:1,
  existingWorking:1,plannedNew:2,cookingDistanceM:4,alarmAgeYears:0,interconnect:'yes',
  certificationVerified:true,exactModelVerified:true,testButton:true,lowBatteryWarning:true,manufactureDateKnown:true,
  monthlyTestPassed:false,placementVerified:true,notDisabled:true,damageFree:true,accessibilityRequired:false,
  accessibilitySupported:false,activeEmergency:false
};

let result=core.evaluate(base);
assert.equal(result.minimumAlarms,3);
assert.equal(result.totalAfterPlan,3);
assert.equal(result.shortage,0);
assert.equal(result.purchaseNeed,2);
assert.equal(result.status,'suitable');
assert.equal(result.productRouteAllowed,true);
assert.equal(result.productRoute,'/akilli-urun-secimi?kategori=smoke_alarm');

const duplex=core.minimumAlarmCount({floors:2,basement:false,bedrooms:3,sleepingAreas:1,sleepingLevels:1});
assert.deepEqual(duplex,{totalLevels:2,extraLevelCoverage:1,count:5});
const basement=core.minimumAlarmCount({floors:2,basement:true,bedrooms:3,sleepingAreas:2,sleepingLevels:2});
assert.deepEqual(basement,{totalLevels:3,extraLevelCoverage:1,count:6});

result=core.evaluate({...base,ownership:'owned',existingWorking:3,plannedNew:0,monthlyTestPassed:true,alarmAgeYears:4});
assert.equal(result.status,'no_purchase');
assert.equal(result.noPurchase,true);
assert.equal(result.productRouteAllowed,false);

result=core.evaluate({...base,existingWorking:0,plannedNew:1});
assert.equal(result.status,'insufficient');
assert.equal(result.shortage,2);
assert(result.failures.some(item=>/2 adet eksik/i.test(item)));

result=core.evaluate({...base,cookingDistanceM:1.5});
assert.equal(result.status,'insufficient');
assert(result.failures.some(item=>/3 m/i.test(item)));

result=core.evaluate({...base,alarmAgeYears:10,ownership:'owned',existingWorking:3,plannedNew:0,monthlyTestPassed:true});
assert.equal(result.status,'insufficient');
assert(result.failures.some(item=>/10 yaş/i.test(item)));

result=core.evaluate({...base,certificationVerified:false});
assert.equal(result.status,'conditional');
assert.equal(result.productRouteAllowed,false);

result=core.evaluate({...base,interconnect:'unknown'});
assert.equal(result.status,'conditional');
assert(result.unknowns.some(item=>/bağlı çalışma/i.test(item)));

result=core.evaluate({...base,accessibilityRequired:true,accessibilitySupported:false});
assert.equal(result.status,'insufficient');
assert(result.failures.some(item=>/İşitme güçlüğü/i.test(item)));

result=core.evaluate({...base,useCase:'hotel'});
assert.equal(result.status,'professional');
assert.equal(result.productRouteAllowed,false);

result=core.evaluate({...base,activeEmergency:true});
assert.equal(result.status,'emergency');
assert.equal(result.productRouteAllowed,false);
assert(result.blocks.some(item=>/112/i.test(item)));

result=core.evaluate({...base,notDisabled:false});
assert.equal(result.status,'professional');
assert(result.blocks.some(item=>/devre dışı/i.test(item)));

assert.throws(()=>core.evaluate({...base,sleepingLevels:3}),/Uyuma alanı bulunan kat sayısı/);
assert.throws(()=>core.evaluate({...base,bedrooms:1.5}),/tam sayı/);

const repoRoot=path.resolve(__dirname,'../../..');
const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
const app=fs.readFileSync(path.join(__dirname,'app.js'),'utf8');
const hub=fs.readFileSync(path.join(__dirname,'..','index.html'),'utf8');
const manifest=fs.readFileSync(path.join(repoRoot,'alo186','deployment','routing-manifest.json'),'utf8');
const sitemap=fs.readFileSync(path.join(repoRoot,'alo186','sitemap.xml'),'utf8');
const catalog=require(path.join(repoRoot,'alo186','urun-eslestirme','catalog.js'));
const journeys=require(path.join(repoRoot,'alo186','urun-eslestirme','journey-retention-core.js'));

assert.match(html,/rel="canonical" href="https:\/\/www\.alo186\.com\/hesaplama\/duman-alarmi-yerlesim-bakim-uygunluk\//);
assert.match(html,/"@type":"WebApplication"/);
assert.match(html,/"@type":"FAQPage"/);
assert.match(html,/Satış ortaklığı açıklaması/);
assert.match(html,/U\.S\. Fire Administration/);
assert.match(html,/EN 14604/);
assert.match(html,/Kişisel veri yok/);
assert.doesNotMatch(html,/amazon\.(com|com\.tr)\//i);
assert.doesNotMatch(html,/type="(?:email|tel|text|file)"/i);
assert.doesNotMatch(html,/name="(?:address|phone|email|subscription|identity|serial|freeText)"/i);
assert.match(app,/smoke_alarm_suitability_completed/);
assert.match(app,/smoke_alarm_product_route_opened/);
assert.match(app,/Şimdilik satın alma/);
assert.match(hub,/href="\.\/duman-alarmi-yerlesim-bakim-uygunluk\//);
assert.match(hub,/\d+ çekirdek araç/);
assert.match(manifest,/alo186\/hesaplama\/duman-alarmi-yerlesim-bakim-uygunluk\/index\.html/);
assert.match(sitemap,/https:\/\/alo186\.com\/hesaplama\/duman-alarmi-yerlesim-bakim-uygunluk\//);

const category=catalog.getCategory('smoke_alarm');
assert(category);
assert.equal(category.mode,'guide');
assert.equal(category.affiliatePolicy,'after_tool');
assert.equal(category.nextStepUrl,'https://www.alo186.com/hesaplama/duman-alarmi-yerlesim-bakim-uygunluk/');
assert.equal(catalog.productsFor('smoke_alarm').length,0);
const journey=journeys.getJourney('smoke_alarm');
assert.equal(journey.calculate.url,'/hesaplama/duman-alarmi-yerlesim-bakim-uygunluk/');
assert(journey.maintenance.length>=3);

console.log('Duman alarmı yerleşim ve bakım uygunluğu: adet, 3 m mutfak uzaklığı, 10 yıl, aylık test, erişilebilirlik, affiliate ve yayın testleri başarılı.');
