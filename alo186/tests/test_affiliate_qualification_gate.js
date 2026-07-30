'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const matcher=require('../urun-eslestirme/matcher-core.js');
const suitability=require('../hesaplama/akim-korumali-grup-priz-uygunluk/core.js');

const safe=suitability.evaluate({ownership:'candidate',loadType:'office',continuousW:650,peakW:900,hoursDaily:8,requiredOutlets:5,productOutlets:6,ratedCurrentA:16,ratedPowerW:3500,joules:900,usbNeeded:false,usbPorts:0,groundStatus:'verified',recallStatus:'checked_clear',indicatorState:'verified',supervisedTest:'not_done',labelVerified:true,overloadProtection:true,protectionIndicator:true,damageFree:true,dryIndoor:true,directWall:true,uncovered:true});
assert.equal(safe.status,'suitable');
assert.equal(safe.productRouteAllowed,true);
assert.deepEqual(safe.productRequirements,{minOutlets:5,minJoules:900,usb:false});
assert.match(safe.productRoute,/kategori=surge_strip&gate=local/);

const withoutGate=matcher.match('surge_strip',safe.productRequirements,{now:new Date('2026-07-29T12:00:00Z')});
assert.equal(withoutGate.mode,'guide');
assert.equal(withoutGate.matches.length,0);
const withGate=matcher.match('surge_strip',safe.productRequirements,{now:new Date('2026-07-29T12:00:00Z'),qualified:true});
assert.equal(withGate.mode,'direct');
assert.equal(withGate.qualifiedGate,true);
assert.ok(withGate.matches.length>=1);
assert.ok(withGate.matches.every(item=>item.product.category==='surge_strip'));
assert.ok(withGate.matches.every(item=>item.product.attributes.outlets>=5&&item.product.attributes.joules>=900));

const heater=suitability.evaluate({ownership:'candidate',loadType:'heater',continuousW:2000,peakW:2000,hoursDaily:4,requiredOutlets:1,productOutlets:5,ratedCurrentA:10,ratedPowerW:2300,joules:900,usbNeeded:false,usbPorts:0,groundStatus:'unknown',recallStatus:'unknown',indicatorState:'unknown',supervisedTest:'not_done',labelVerified:false,overloadProtection:false,protectionIndicator:false,damageFree:false,dryIndoor:false,directWall:false,uncovered:false});
assert.equal(heater.productRouteAllowed,false);
assert.equal(heater.status,'blocked');

const owned=suitability.evaluate({ownership:'owned',loadType:'router',continuousW:90,peakW:140,hoursDaily:24,requiredOutlets:4,productOutlets:5,ratedCurrentA:10,ratedPowerW:2300,joules:900,usbNeeded:true,usbPorts:2,groundStatus:'verified',recallStatus:'checked_clear',indicatorState:'verified',supervisedTest:'passed',labelVerified:true,overloadProtection:true,protectionIndicator:true,damageFree:true,dryIndoor:true,directWall:true,uncovered:true});
assert.equal(owned.status,'no_purchase');
assert.equal(owned.noPurchase,true);
assert.equal(owned.productRouteAllowed,false);

const recalled=suitability.evaluate({...safe,ownership:'candidate',recallStatus:'recalled'});
assert.equal(recalled.status,'blocked');
assert.equal(recalled.productRouteAllowed,false);

const toolApp=fs.readFileSync(path.join(__dirname,'../hesaplama/akim-korumali-grup-priz-uygunluk/app.js'),'utf8');
const matcherApp=fs.readFileSync(path.join(__dirname,'../urun-eslestirme/app.js'),'utf8');
for(const source of [toolApp,matcherApp]){
  assert.match(source,/alo186_affiliate_qualification_v1/);
  assert.doesNotMatch(source,/email|phone|address|subscription|serialNumber|plate/i);
}
assert.match(toolApp,/30\*60\*1000/);
assert.match(toolApp,/personalData:false/);
assert.match(toolApp,/localStorage\.setItem\(qualificationKey/);
assert.match(toolApp,/data-confirm-need/);
assert.match(toolApp,/data-confirm-technical/);
assert.match(toolApp,/data-confirm-affiliate/);
assert.match(toolApp,/sponsored nofollow noopener/);
assert.match(matcherApp,/gateCompatible/);
assert.match(matcherApp,/catalogFreshness/);
assert.match(matcherApp,/alo186_catalog_recheck_v1/);
assert.match(matcherApp,/qualified_gate/);

console.log(JSON.stringify({ok:true,qualifiedMatches:withGate.matches.length,noBuy:owned.noPurchase,unsafeBlocked:heater.status,recalledBlocked:recalled.status},null,2));
