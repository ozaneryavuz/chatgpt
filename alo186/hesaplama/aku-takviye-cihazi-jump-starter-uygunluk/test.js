'use strict';
const assert=require('node:assert/strict');
const app=require('./app.js');
const base={danger:false,batteryDamage:false,frozenBattery:false,activeRoadside:false,vehicleClass:'gasoline',systemVoltage:'12',manualVerified:true,connectionPointsVerified:true,batteryTypeVerified:true,batteryType:'agm',lithiumApproved:false,hasExisting:false,existingTested:false,existingVoltageMatch:false,existingVehicleMatch:false,existingPhysicalSafe:true,existingChargeReady:false,confirmNeed:false,confirmManual:false,confirmAffiliate:false};
assert.equal(app.decide({...base,danger:true}).code,'danger');
assert.equal(app.decide({...base,vehicleClass:'ev'}).commerce,false);
assert.equal(app.decide({...base,hasExisting:true,existingTested:true,existingVoltageMatch:true,existingVehicleMatch:true,existingPhysicalSafe:true,existingChargeReady:true}).code,'no_buy');
assert.equal(app.decide({...base,confirmNeed:true,confirmManual:true,confirmAffiliate:true}).code,'eligible');
console.log(JSON.stringify({ok:true,route:app.ROUTE,noBuy:true,activeRiskCommerce:false}));