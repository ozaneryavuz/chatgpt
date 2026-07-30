'use strict';
const assert=require('node:assert/strict');
const {calculate,OUTLETS,CHARGING_EFFICIENCY}=require('./app.js');

const base={
  emergency:false,scenario:'planning',outletType:'schuko',socketCondition:'normal',extensionUse:'none',
  outdoorUse:'no',ipVerified:'unknown',dedicatedCircuit:'yes',protectiveEarth:'yes',
  protection:'type_a_6ma',socketInspection:'yes',documentedCurrentA:10,
  dailyKm:40,consumptionKwh100:18,availableHours:8,vehicleAcMaxKw:11,
  evseMaxA:10,evseAdjustable:'yes',connectorVerified:'yes',sourceStatus:'none',
  thermalTest:'untested',chargeTest:'untested'
};

assert.equal(CHARGING_EFFICIENCY,0.90);
assert.equal(OUTLETS.schuko.maxA,10);
assert.equal(OUTLETS.cee_blue_32.maxA,32);

let r=calculate({...base,emergency:true});
assert.equal(r.status,'emergency');assert.equal(r.commercialAllowed,false);

r=calculate({...base,socketCondition:'hot'});
assert.equal(r.status,'stop_use');

r=calculate({...base,extensionUse:'reel'});
assert.equal(r.status,'stop_use');

r=calculate({...base,outletType:'unknown'});
assert.equal(r.status,'evidence_required');

r=calculate({...base,outletType:'wallbox'});
assert.equal(r.status,'wallbox_path');assert.equal(r.nextTool,'/hesaplama/ev-sarj-uygunluk/');

r=calculate({...base,dedicatedCircuit:'no'});
assert.equal(r.status,'professional');

r=calculate({...base,protectiveEarth:'no'});
assert.equal(r.status,'stop_use');

r=calculate({...base,protection:'none'});
assert.equal(r.status,'stop_use');

r=calculate({...base,socketInspection:'unknown'});
assert.equal(r.status,'evidence_required');

r=calculate({...base,outdoorUse:'yes',ipVerified:'no'});
assert.equal(r.status,'stop_use');

r=calculate({...base,connectorVerified:'no'});
assert.equal(r.status,'evidence_required');

r=calculate({...base,dailyKm:0});
assert.equal(r.status,'evidence_required');

r=calculate({...base,documentedCurrentA:16});
assert.equal(r.status,'evidence_required');

r=calculate({...base,evseMaxA:16,evseAdjustable:'no'});
assert.equal(r.status,'stop_use');

r=calculate(base);
assert.equal(r.status,'conditional_purchase');
assert.equal(r.metrics.usableCurrentA,10);
assert.equal(r.metrics.availablePowerKw,2.3);
assert.equal(r.metrics.mainsEnergyKwh,8);
assert.equal(r.metrics.requiredHours,3.48);
assert.equal(r.metrics.deliverableKm,92);
assert.deepEqual(r.categories,['portable_evse']);

r=calculate({...base,sourceStatus:'existing',thermalTest:'success',chargeTest:'success'});
assert.equal(r.status,'no_buy');assert.equal(r.commercialAllowed,false);

r=calculate({...base,sourceStatus:'existing',thermalTest:'failed',chargeTest:'success'});
assert.equal(r.status,'stop_use');

r=calculate({...base,sourceStatus:'existing',thermalTest:'success',chargeTest:'untested'});
assert.equal(r.status,'evidence_required');

r=calculate({...base,dailyKm:150});
assert.equal(r.status,'wallbox_path');assert.equal(r.metrics.deliverableKm,92);

r=calculate({...base,outletType:'cee_blue_32',documentedCurrentA:32,evseMaxA:32,dailyKm:250});
assert.equal(r.status,'conditional_purchase');
assert.equal(r.metrics.availablePowerKw,7.36);
assert.equal(r.metrics.deliverableKm,294);

r=calculate({...base,outletType:'cee_red_16',documentedCurrentA:16,evseMaxA:16,dailyKm:300,vehicleAcMaxKw:11});
assert.equal(r.status,'conditional_purchase');
assert.equal(r.metrics.phase,'three');
assert.equal(r.metrics.availablePowerKw,11);
assert.equal(r.metrics.deliverableKm,440);

r=calculate({...base,outletType:'cee_blue_16',documentedCurrentA:16,evseMaxA:6,dailyKm:80,sourceStatus:'existing',thermalTest:'success',chargeTest:'success'});
assert.equal(r.status,'conditional_purchase');
assert.equal(r.metrics.limitingFactor,'evse');
assert.deepEqual(r.categories,['portable_evse']);

r=calculate({...base,scenario:'active'});
assert.equal(r.status,'active_event');assert.equal(r.commercialAllowed,false);

console.log(JSON.stringify({ok:true,scenarios:22},null,2));
