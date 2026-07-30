'use strict';
const assert=require('node:assert/strict');
const {calculate,START_MULTIPLIERS}=require('./app.js');

const base={
  scenario:'planning',toolType:'drill',supply:'230v',connection:'plug',
  labelMethod:'watts',ratedW:800,voltageV:'',currentA:'',powerFactor:'',manufacturerPeakW:'',
  startClass:'normal',dutyCyclePct:50,otherW:100,targetHours:2,
  environment:'dry',extensionStatus:'verified',groundingVerified:'yes',
  preferredSource:'power_station',sourceStatus:'none',startTest:'untested'
};

assert.equal(START_MULTIPLIERS.normal,3);
assert.equal(START_MULTIPLIERS.heavy,5);

let r=calculate({...base,emergency:true});
assert.equal(r.status,'emergency');assert.equal(r.commercialAllowed,false);

r=calculate({...base,criticalUse:true});
assert.equal(r.status,'professional');assert.equal(r.commercialAllowed,false);

r=calculate({...base,toolType:'unknown'});
assert.equal(r.status,'evidence_required');

r=calculate({...base,supply:'400v'});
assert.equal(r.status,'professional');

r=calculate({...base,connection:'fixed'});
assert.equal(r.status,'professional');

r=calculate({...base,toolType:'welder'});
assert.equal(r.status,'professional');assert.equal(r.commercialAllowed,false);

r=calculate({...base,environment:'wet'});
assert.equal(r.status,'unsafe');

r=calculate({...base,extensionStatus:'unsafe'});
assert.equal(r.status,'unsafe');assert.equal(r.nextTool,'/hesaplama/uzatma-kablosu-uygunluk/');

r=calculate({...base,extensionStatus:'unknown'});
assert.equal(r.status,'evidence_required');

r=calculate({...base,groundingVerified:'no'});
assert.equal(r.status,'unsafe');

r=calculate({...base,startClass:'unknown'});
assert.equal(r.status,'evidence_required');

r=calculate({...base,dutyCyclePct:0});
assert.equal(r.status,'evidence_required');

r=calculate({...base,ratedW:''});
assert.equal(r.status,'evidence_required');

r=calculate({...base,labelMethod:'volts_amps',ratedW:'',voltageV:230,currentA:5,powerFactor:0.8});
assert.equal(r.status,'conditional_purchase');
assert.equal(r.metrics.runningW,920);

r=calculate({...base,manufacturerPeakW:500});
assert.equal(r.status,'evidence_required');

r=calculate({...base,ratedW:3000,startClass:'normal'});
assert.equal(r.status,'professional');

r=calculate({...base,scenario:'active'});
assert.equal(r.status,'active_event');assert.equal(r.commercialAllowed,false);

r=calculate(base);
assert.equal(r.status,'conditional_purchase');
assert.equal(r.metrics.runningW,800);
assert.equal(r.metrics.estimatedStartW,2400);
assert.equal(r.metrics.requiredContinuousW,1150);
assert.equal(r.metrics.requiredSurgeW,2900);
assert.equal(r.metrics.requiredWh,1500);
assert.deepEqual(r.categories,['power_station']);

r=calculate({...base,toolType:'compressor',ratedW:1200,startClass:'heavy',dutyCyclePct:30,targetHours:3,otherW:0,preferredSource:'unsure'});
assert.equal(r.status,'conditional_purchase');
assert.equal(r.metrics.architecture,'generator');
assert.equal(r.metrics.requiredSurgeW,6900);
assert.deepEqual(r.categories,['generator']);
assert.equal(r.nextTool,'/hesaplama/jenerator-guvenli-kullanim-testi/');

r=calculate({...base,sourceStatus:'power_station_existing',existingContinuousW:'',existingSurgeW:'',existingWh:'',existingPureSine:'unknown',existingOutputVerified:'unknown',existingGroundingVerified:'unknown'});
assert.equal(r.status,'evidence_required');

r=calculate({...base,sourceStatus:'power_station_existing',existingContinuousW:1500,existingSurgeW:3200,existingWh:1600,existingPureSine:'yes',existingOutputVerified:'yes',existingGroundingVerified:'yes',startTest:'success'});
assert.equal(r.status,'no_buy');

r=calculate({...base,sourceStatus:'power_station_existing',existingContinuousW:1000,existingSurgeW:3200,existingWh:1600,existingPureSine:'yes',existingOutputVerified:'yes',existingGroundingVerified:'yes',startTest:'success'});
assert.equal(r.status,'conditional_purchase');assert.deepEqual(r.categories,['power_station']);

r=calculate({...base,sourceStatus:'generator_existing',existingContinuousW:2000,existingSurgeW:3500,existingOutputVerified:'yes',existingGroundingVerified:'yes',generatorSafetyVerified:'unknown',startTest:'success'});
assert.equal(r.status,'evidence_required');assert.equal(r.nextTool,'/hesaplama/jenerator-guvenli-kullanim-testi/');

r=calculate({...base,sourceStatus:'power_station_existing',existingContinuousW:1500,existingSurgeW:3200,existingWh:1600,existingPureSine:'yes',existingOutputVerified:'yes',existingGroundingVerified:'yes',startTest:'failed'});
assert.equal(r.status,'professional');

r=calculate({...base,preferredSource:'inverter',sourceStatus:'inverter_existing',existingContinuousW:1500,existingSurgeW:3200,existingWh:1600,existingPureSine:'yes',existingOutputVerified:'yes',existingGroundingVerified:'yes',startTest:'success'});
assert.equal(r.status,'no_buy');assert.equal(r.metrics.architecture,'inverter');

console.log(JSON.stringify({ok:true,scenarios:25},null,2));
