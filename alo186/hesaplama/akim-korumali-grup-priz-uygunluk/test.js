'use strict';

const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const core=require('./core.js');

const safeInput={
  ownership:'candidate',loadType:'office',continuousW:650,peakW:900,hoursDaily:8,requiredOutlets:5,productOutlets:6,
  ratedCurrentA:16,ratedPowerW:3500,joules:900,usbNeeded:false,usbPorts:0,groundStatus:'verified',labelVerified:true,
  overloadProtection:true,protectionIndicator:true,damageFree:true,dryIndoor:true,directWall:true,uncovered:true
};

const safe=core.evaluate(safeInput);
assert.equal(safe.status,'suitable');
assert.equal(safe.productRouteAllowed,true);
assert.equal(safe.currentA,2.83);
assert.equal(safe.screeningLimitW,2800);
assert.equal(safe.recommendedCurrentA,6);

const owned=core.evaluate({...safeInput,ownership:'owned'});
assert.equal(owned.status,'no_purchase');
assert.equal(owned.noPurchase,true);
assert.equal(owned.productRouteAllowed,false);

const heater=core.evaluate({...safeInput,loadType:'heater',continuousW:2000,peakW:2000,hoursDaily:4,ratedCurrentA:16,ratedPowerW:3500});
assert.equal(heater.status,'blocked');
assert.equal(heater.productRouteAllowed,false);
assert.ok(heater.blocks.some(item=>item.includes('Isıtıcı')));

const daisy=core.evaluate({...safeInput,directWall:false});
assert.equal(daisy.status,'blocked');
assert.ok(daisy.blocks.some(item=>item.includes('başka bir grup prize')));

const overloaded=core.evaluate({...safeInput,continuousW:2000,peakW:2200,ratedCurrentA:10,ratedPowerW:2300,hoursDaily:8});
assert.equal(overloaded.status,'insufficient');
assert.equal(overloaded.screeningLimitW,1840);
assert.ok(overloaded.failures.some(item=>item.includes('ön kontrol sınırı')));

const unknownGround=core.evaluate({...safeInput,groundStatus:'unknown'});
assert.equal(unknownGround.status,'conditional');
assert.equal(unknownGround.productRouteAllowed,false);
assert.ok(unknownGround.unknowns.some(item=>item.includes('koruma iletkeni')));

const fewOutlets=core.evaluate({...safeInput,requiredOutlets:6,productOutlets:5});
assert.equal(fewOutlets.status,'insufficient');
assert.ok(fewOutlets.failures.some(item=>item.includes('en az 6 priz')));

const unverified=core.evaluate({...safeInput,labelVerified:false});
assert.equal(unverified.status,'conditional');
assert.equal(unverified.productRouteAllowed,false);

const medical=core.evaluate({...safeInput,loadType:'medical'});
assert.equal(medical.status,'blocked');
assert.equal(medical.productRouteAllowed,false);

const usbMismatch=core.evaluate({...safeInput,usbNeeded:true,usbPorts:0});
assert.equal(usbMismatch.status,'insufficient');
assert.ok(usbMismatch.failures.some(item=>item.includes('USB')));

assert.throws(()=>core.evaluate({...safeInput,peakW:300,continuousW:600}),/Tepe yük/);

const repoRoot=path.resolve(__dirname,'../../..');
const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
const hub=fs.readFileSync(path.join(__dirname,'..','index.html'),'utf8');
const manifest=fs.readFileSync(path.join(repoRoot,'alo186','deployment','routing-manifest.json'),'utf8');
const sitemap=fs.readFileSync(path.join(repoRoot,'alo186','sitemap.xml'),'utf8');

assert.match(html,/https:\/\/www\.alo186\.com\/hesaplama\/akim-korumali-grup-priz-uygunluk\//);
assert.match(html,/Satış ortaklığı açıklaması/);
assert.match(html,/Kişisel veri yok/);
assert.match(html,/Joule değeri.*tek başına koruma garantisi değildir/s);
assert.doesNotMatch(html,/amazon\.(com|com\.tr)\//i);
assert.doesNotMatch(html,/type="(?:email|tel|text)"/i);
assert.doesNotMatch(html,/name="(?:address|phone|email|subscription|tc|identity|note)"/i);
assert.match(hub,/29 çekirdek araç/);
assert.match(hub,/\.\/akim-korumali-grup-priz-uygunluk\//);
assert.match(manifest,/alo186\/hesaplama\/akim-korumali-grup-priz-uygunluk\/index\.html/);
assert.match(sitemap,/https:\/\/www\.alo186\.com\/hesaplama\/akim-korumali-grup-priz-uygunluk\//);

console.log('Akım korumalı grup priz: yük, güvenlik, satın almama, affiliate, gizlilik ve yayın entegrasyon testleri başarılı.');
