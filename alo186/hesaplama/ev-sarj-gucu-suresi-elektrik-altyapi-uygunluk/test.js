'use strict';
const assert=require('assert');
const {analyze,commonPowerClass}=require('./core.js');

const base={
  usage:'private',ownership:'candidate',phase:'single',batteryKwh:60,currentSoc:20,targetSoc:80,
  planningEfficiencyPct:90,targetHours:8,vehicleAcMaxKw:7.4,evseMaxKw:7.4,installationMaxKw:7.4,
  connectorVerified:true,vehicleDocsVerified:true,evseDocsVerified:true,installationPowerVerified:true,
  dedicatedCircuit:true,protectionCoordinationVerified:true,residualProtectionVerified:true,earthVerified:true,
  commissioningPassed:true,damageFree:true,noRecurringTrips:true,directEvseConnection:true,
  loadManagementRequired:false,loadManagementVerified:false,advancedEnergySystem:false,existingSafeSolutionAdequate:false
};
const run=patch=>analyze({...base,...patch});

let r=run({});
assert.strictEqual(r.batteryEnergyKwh,36);
assert.strictEqual(r.gridEnergyKwh,40);
assert.strictEqual(r.effectivePowerKw,7.4);
assert.ok(r.chargeTimeHours>5.3&&r.chargeTimeHours<5.5);
assert.strictEqual(r.targetFeasibleByVehicleAndSite,true);
assert.strictEqual(r.candidateMeetsTime,true);
assert.strictEqual(r.candidateWithinUsefulCeiling,true);
assert.strictEqual(r.commercialAllowed,true);
assert.strictEqual(r.blockers.length,0);

r=run({phase:'three',batteryKwh:75,vehicleAcMaxKw:11,evseMaxKw:11,installationMaxKw:11});
assert.ok(r.approximateCurrentA>15&&r.approximateCurrentA<17);
assert.strictEqual(r.effectivePowerKw,11);

r=run({vehicleAcMaxKw:11,evseMaxKw:22,installationMaxKw:22});
assert.strictEqual(r.effectivePowerKw,11);
assert.ok(r.warnings.some(x=>x.includes('daha büyük wallbox')));
assert.strictEqual(r.candidateWithinUsefulCeiling,false);
assert.strictEqual(r.commercialAllowed,false);

r=run({vehicleAcMaxKw:7.4,evseMaxKw:11,installationMaxKw:7.4});
assert.strictEqual(r.effectivePowerKw,7.4);
assert.ok(r.warnings.some(x=>x.includes('tesisat sınırından yüksek')));
assert.strictEqual(r.commercialAllowed,false);

r=run({targetHours:2});
assert.strictEqual(r.targetFeasibleByVehicleAndSite,false);
assert.ok(r.warnings.some(x=>x.includes('yalnız daha güçlü wallbox')));
assert.strictEqual(r.commercialAllowed,false);

r=run({evseMaxKw:3.7,targetHours:8});
assert.strictEqual(r.candidateMeetsTime,false);
assert.strictEqual(r.commercialAllowed,false);

r=run({noRecurringTrips:false});
assert.ok(r.blockerCodes.includes('trips'));
assert.strictEqual(r.commercialAllowed,false);

r=run({directEvseConnection:false});
assert.ok(r.blockerCodes.includes('extension'));
assert.strictEqual(r.commercialAllowed,false);

r=run({residualProtectionVerified:false});
assert.ok(r.blockerCodes.includes('residual'));
assert.strictEqual(r.commercialAllowed,false);

r=run({earthVerified:false});
assert.ok(r.blockerCodes.includes('earth'));
assert.strictEqual(r.commercialAllowed,false);

r=run({usage:'shared'});
assert.ok(r.blockerCodes.includes('shared'));
assert.strictEqual(r.professionalRequired,true);

r=run({usage:'commercial'});
assert.ok(r.blockerCodes.includes('commercial'));
assert.strictEqual(r.commercialAllowed,false);

r=run({advancedEnergySystem:true});
assert.ok(r.blockerCodes.includes('advanced'));
assert.strictEqual(r.commercialAllowed,false);

r=run({loadManagementRequired:true,loadManagementVerified:false});
assert.ok(r.blockerCodes.includes('load_management'));

r=run({ownership:'owned',existingSafeSolutionAdequate:true});
assert.strictEqual(r.noPurchaseNeeded,true);
assert.strictEqual(r.commercialAllowed,false);

r=run({ownership:'owned'});
assert.strictEqual(r.noPurchaseNeeded,true);
assert.strictEqual(r.commercialAllowed,false);

r=run({vehicleDocsVerified:false});
assert.ok(r.warnings.some(x=>x.includes('Araç üreticisinin')));
assert.strictEqual(r.commercialAllowed,false);

assert.strictEqual(commonPowerClass(6.5),7.4);
assert.strictEqual(commonPowerClass(10.2),11);
assert.strictEqual(commonPowerClass(23),null);
assert.throws(()=>run({targetSoc:10}),/Hedef SOC/);
console.log('ALO186 EV ev şarj gücü ve süre v352: PASS');
