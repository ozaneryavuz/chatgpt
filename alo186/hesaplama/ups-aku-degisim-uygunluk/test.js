'use strict';
const assert=require('assert');
const fs=require('fs');
const path=require('path');
const core=require('./core.js');

const base={upsClass:'desktop',upsAgeYears:3,chemistry:'vrla',batteryAgeYears:2,physicalState:'normal',fullyCharged:true,selfTest:'pass',measuredRuntimeMin:25,requiredRuntimeMin:15,runtimeTrend:'stable',repeatBatteryAlarm:false,outageDrop:false,exactModelVerified:true,userReplaceable:true,exactCartridgeVerified:false,candidateType:'not-selected',preassembledCartridge:false,fullSetReplacement:false,supportActive:true,externalBatteryPacks:false,recyclingPlan:false,lifeSupport:false};
const run=overrides=>core.analyze({...base,...overrides});

const healthy=run({});
assert.equal(healthy.status,'no-purchase');
assert.equal(healthy.noPurchaseNeeded,true);
assert.equal(healthy.commercialAllowed,false);
assert.equal(healthy.runtimeCoveragePct,166.7);

const replace=run({batteryAgeYears:4,selfTest:'replace',measuredRuntimeMin:6,requiredRuntimeMin:20,runtimeTrend:'declined',repeatBatteryAlarm:true,outageDrop:true,candidateType:'manufacturer-exact',exactCartridgeVerified:true,preassembledCartridge:true,fullSetReplacement:true,recyclingPlan:true});
assert.equal(replace.status,'replace-cartridge');
assert.equal(replace.commercialAllowed,true);
assert(replace.replacementReasons.length>=3);

const notCharged=run({fullyCharged:false,selfTest:'replace',measuredRuntimeMin:null,runtimeTrend:'unknown'});
assert.equal(notCharged.status,'test-first');
assert.equal(notCharged.commercialAllowed,false);

const hazard=run({physicalState:'hazard',candidateType:'manufacturer-exact',exactCartridgeVerified:true,preassembledCartridge:true,fullSetReplacement:true,selfTest:'replace'});
assert.equal(hazard.status,'stop-use');
assert.equal(hazard.commercialAllowed,false);
assert(hazard.blockerCodes.includes('physical_hazard'));

const medical=run({lifeSupport:true,selfTest:'replace',candidateType:'manufacturer-exact',exactCartridgeVerified:true,preassembledCartridge:true,fullSetReplacement:true});
assert.equal(medical.status,'service');
assert.equal(medical.commercialAllowed,false);

const oldUps=run({upsAgeYears:8,selfTest:'replace',runtimeTrend:'declined',measuredRuntimeMin:5,requiredRuntimeMin:20,candidateType:'manufacturer-exact',exactCartridgeVerified:true,preassembledCartridge:true,fullSetReplacement:true});
assert.equal(oldUps.status,'compare-unit');
assert.equal(oldUps.commercialAllowed,false);
assert.equal(oldUps.alternativeRoute,'/hesaplama/yedek-guc-maliyet-karsilastirma/');

const capacity=run({selfTest:'pass',measuredRuntimeMin:5,requiredRuntimeMin:20,runtimeTrend:'always-short'});
assert.equal(capacity.status,'capacity-review');
assert.equal(capacity.commercialAllowed,false);
assert.equal(capacity.alternativeRoute,'/hesaplama/ups-suresi/');

const preventive=run({batteryAgeYears:5,selfTest:'pass',measuredRuntimeMin:20,requiredRuntimeMin:15,runtimeTrend:'stable'});
assert.equal(preventive.status,'plan-replacement');
assert.equal(preventive.commercialAllowed,false);

for(const overrides of [
  {upsClass:'large'},
  {externalBatteryPacks:true},
  {candidateType:'generic-loose'},
  {userReplaceable:false,selfTest:'replace',candidateType:'manufacturer-exact',exactCartridgeVerified:true,preassembledCartridge:true,fullSetReplacement:true},
  {exactModelVerified:false,selfTest:'replace',candidateType:'manufacturer-exact',exactCartridgeVerified:true,preassembledCartridge:true,fullSetReplacement:true},
  {candidateType:'manufacturer-exact',exactCartridgeVerified:false,preassembledCartridge:true,fullSetReplacement:true,selfTest:'replace'}
]){
  const result=run(overrides);
  assert.equal(result.commercialAllowed,false);
}

assert.equal(core.ageSignals('vrla',3).planning,true);
assert.equal(core.ageSignals('vrla',5).due,true);
assert.equal(core.ageSignals('liion',8).planning,true);
assert.equal(core.ageSignals('liion',10).due,true);

const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
assert(html.includes('https://www.alo186.com/hesaplama/ups-aku-degisim-uygunluk/'));
assert(html.includes('Şeffaf satış ortaklığı'));
assert(html.includes('Satın almama sonucu'));
assert(html.includes('Schneider Electric'));
assert(html.includes('Eaton'));
assert(html.includes('28 Temmuz 2026'));
assert(!/amazon\.(com|com\.tr)/i.test(html));
const fields=[...html.matchAll(/<(?:input|select|textarea)\b[^>]*(?:id|name)="([^"]+)"/gi)].map(match=>match[1]);
assert(!fields.some(field=>/(^|[-_])(name|email|phone|telefon|address|adres|abonelik|tc|identity|plaka|serial|seri)([-_]|$)/i.test(field)));
assert(html.includes('aria-live="polite"'));
assert(html.includes('type="application/ld+json"'));
assert(html.includes('Tıbbi veya yaşam destek yükü bağlı'));
console.log('UPS aküsü değişim ve kartuş uygunluk testleri başarılı.');
