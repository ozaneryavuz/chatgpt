'use strict';
const assert=require('node:assert/strict');
const {calculate}=require('./app.js');

const base={
  scenario:'planning',computerType:'usb_c_laptop',transferTolerance:'seconds_ok',
  laptopW:65,laptopInternalHours:1,laptopPdVerified:'yes',chargerAdequate:'yes',cableAdequate:'yes',
  modemW:12,ontW:8,routerW:0,monitorW:0,dockW:0,otherW:0,targetHours:4,
  networkVoltageVerified:'yes',networkPolarityVerified:'yes',networkJackVerified:'yes',
  sourceStatus:'none',blackoutTest:'untested'
};

let r=calculate({...base,emergency:true});
assert.equal(r.status,'emergency');assert.equal(r.commercialAllowed,false);

r=calculate({...base,criticalUse:true});
assert.equal(r.status,'professional');assert.equal(r.commercialAllowed,false);

r=calculate({...base,targetHours:0});
assert.equal(r.status,'evidence_required');

r=calculate({...base,computerType:'unknown'});
assert.equal(r.status,'evidence_required');

r=calculate({...base,laptopInternalHours:4,modemW:0,ontW:0,routerW:0});
assert.equal(r.status,'no_buy');assert.equal(r.metrics.architecture,'no_external');

r=calculate({...base,laptopPdVerified:'unknown'});
assert.equal(r.status,'evidence_required');

r=calculate({...base,chargerAdequate:'unknown'});
assert.equal(r.status,'evidence_required');

r=calculate({...base,networkVoltageVerified:'unknown'});
assert.equal(r.status,'evidence_required');

r=calculate(base);
assert.equal(r.status,'conditional_purchase');
assert.equal(r.metrics.architecture,'split_dc');
assert.equal(r.metrics.requiredPdW,75);
assert.equal(r.metrics.requiredPowerbankWh,280);
assert.equal(r.metrics.requiredMiniUpsW,25);
assert.equal(r.metrics.requiredMiniUpsWh,115);
assert.equal(r.metrics.requiredPowerStationW,110);
assert.equal(r.metrics.requiredPowerStationWh,410);
assert.deepEqual(r.categories,['powerbank','mini_ups']);

r=calculate({...base,modemW:0,ontW:0,routerW:0,chargerAdequate:'no',cableAdequate:'no'});
assert.equal(r.metrics.architecture,'powerbank_only');
assert.deepEqual(r.categories,['powerbank','usb_c_charger','usb_c_cable']);

r=calculate({...base,computerType:'none',laptopW:'',laptopInternalHours:0,laptopPdVerified:'unknown',chargerAdequate:'unknown',cableAdequate:'unknown'});
assert.equal(r.metrics.architecture,'network_only');
assert.equal(r.metrics.requiredMiniUpsWh,115);
assert.deepEqual(r.categories,['mini_ups']);

r=calculate({...base,scenario:'active'});
assert.equal(r.status,'active_event');assert.equal(r.commercialAllowed,false);

r=calculate({...base,sourceStatus:'split_existing',existingPowerbankPDW:100,existingPowerbankWh:300,existingMiniUpsW:30,existingMiniUpsWh:150,networkOutputVerified:'yes',blackoutTest:'success'});
assert.equal(r.status,'no_buy');

r=calculate({...base,sourceStatus:'split_existing',existingPowerbankPDW:100,existingPowerbankWh:200,existingMiniUpsW:30,existingMiniUpsWh:150,networkOutputVerified:'yes',blackoutTest:'success'});
assert.equal(r.status,'conditional_purchase');assert.deepEqual(r.categories,['powerbank']);

r=calculate({...base,monitorW:40,sourceStatus:'split_existing'});
assert.equal(r.status,'conditional_purchase');assert.deepEqual(r.categories,['power_station']);

const barrel={...base,computerType:'barrel_laptop',laptopW:90,laptopInternalHours:0,laptopPdVerified:'unknown',chargerAdequate:'unknown',cableAdequate:'unknown',monitorW:50};
r=calculate(barrel);
assert.equal(r.metrics.architecture,'power_station');
assert.equal(r.metrics.requiredPowerStationW,200);
assert.equal(r.metrics.requiredPowerStationWh,950);
assert.deepEqual(r.categories,['power_station']);

r=calculate({...barrel,sourceStatus:'power_station_existing',existingPowerStationW:300,existingPowerStationWh:1000,existingPureSine:'yes',existingOutputVerified:'yes',blackoutTest:'success'});
assert.equal(r.status,'no_buy');

r=calculate({...barrel,sourceStatus:'power_station_existing',existingPowerStationW:300,existingPowerStationWh:900,existingPureSine:'yes',existingOutputVerified:'yes',blackoutTest:'success'});
assert.equal(r.status,'conditional_purchase');assert.deepEqual(r.categories,['power_station']);

r=calculate({...base,computerType:'desktop',laptopW:250,laptopInternalHours:0});
assert.equal(r.status,'ups_path');assert.equal(r.nextTool,'/hesaplama/ups-va-topoloji-uygunluk/');

r=calculate({...base,transferTolerance:'zero'});
assert.equal(r.status,'ups_path');

r=calculate({...barrel,laptopW:1300,monitorW:300});
assert.equal(r.status,'professional');

// Post-merge CI tetikleyicisi: hesap ve karar sözleşmesi değişmeden korunur.
console.log(JSON.stringify({ok:true,scenarios:21},null,2));
