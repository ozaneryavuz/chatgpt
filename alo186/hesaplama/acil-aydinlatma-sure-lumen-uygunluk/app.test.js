'use strict';
const assert=require('node:assert/strict');
const app=require('./app.js');

const base={
  emergency:false,medical:false,regulated:'no',use:'orientation',areaM2:20,targetLux:'',
  lightCount:1,lumensEach:500,wattsEach:5,sourceType:'wh',batteryWh:74,
  targetHours:6,environment:'dry',ipStatus:'rated',currentEquipment:'working'
};

assert.equal(app.batteryWh({sourceType:'mah',batteryMah:20000,batteryVoltage:3.7}),74);
assert.equal(app.evaluate({...base,emergency:true}).status,'emergency');
assert.equal(app.evaluate({...base,medical:true}).status,'professional');
assert.equal(app.evaluate({...base,regulated:'yes'}).status,'professional');
assert.equal(app.evaluate({...base,environment:'wet',ipStatus:'not_rated'}).status,'stop');
assert.equal(app.evaluate({...base,batteryWh:''}).status,'evidence_required');
assert.equal(app.evaluate({...base,regulated:'unknown'}).status,'prerequisite');

const noBuy=app.evaluate(base);
assert.equal(noBuy.status,'no_buy');
assert.equal(noBuy.commerceClosed,true);
assert(noBuy.metrics.providedLumens>=noBuy.metrics.requiredLumens);
assert(noBuy.metrics.estimatedRuntime>=noBuy.metrics.targetHours);

const lightingGap=app.evaluate({...base,use:'reading',targetLux:100,targetHours:2});
assert.equal(lightingGap.status,'conditional_purchase');
assert.deepEqual(lightingGap.commerceCategories,['emergency_light']);

const runtimeGap=app.evaluate({...base,batteryWh:10,targetHours:6});
assert.equal(runtimeGap.status,'conditional_purchase');
assert.deepEqual(runtimeGap.commerceCategories,['powerbank']);

const bothGap=app.evaluate({...base,use:'reading',targetLux:100,lumensEach:300,wattsEach:30,batteryWh:20,targetHours:8});
assert.equal(bothGap.status,'conditional_purchase');
assert.deepEqual(bothGap.commerceCategories,['emergency_light','power_station']);

const professional=app.evaluate({...base,areaM2:120,lightCount:20,lumensEach:1200,wattsEach:15,batteryWh:2000});
assert.equal(professional.status,'professional');
assert.equal(professional.commerceClosed,true);

assert.equal(app.constants.EFFICIENCY,0.85);
assert.equal(app.constants.USABLE_FRACTION,0.80);
assert.equal(app.constants.LIGHT_RESERVE,1.30);
assert(!Object.values(app.constants.CATEGORY_LINKS).some(item=>item.href.includes('amazon.')));

console.log(JSON.stringify({ok:true,scenarios:11,route:'/hesaplama/acil-aydinlatma-sure-lumen-uygunluk/'},null,2));
