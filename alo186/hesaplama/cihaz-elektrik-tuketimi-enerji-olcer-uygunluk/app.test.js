'use strict';
const assert=require('node:assert/strict');
const tool=require('./app.js');
const base={
  emergency:false,condition:'sound',environment:'dry',connection:'plug',useCase:'electronics',
  goal:'measure_device',measurementBasis:'measured_w',activePowerW:'120',hoursPerDay:'8',
  daysPerMonth:'30',dutyCyclePct:'100',standbyW:'10',standbyHoursPerDay:'16',
  measuredKWh:'',measuredDays:'',tariff:'3',deviceCurrentA:'1',
  existingType:'none',existingMaxA:'',existingEnergyKwh:'unknown',existingCertificate:'unknown',
  existingAccuracyClass:'unknown',existingCondition:'unknown',temperatureTest:'not_tested'
};
const calc=(patch)=>tool.calculate({...base,...patch});
assert.equal(calc({emergency:true}).status,'emergency');
assert.equal(calc({condition:'hot'}).status,'stop_use');
assert.equal(calc({condition:'loose'}).status,'stop_use');
assert.equal(calc({environment:'wet'}).status,'professional');
assert.equal(calc({environment:'outdoor'}).status,'professional');
assert.equal(calc({connection:'hardwired'}).status,'professional');
assert.equal(calc({connection:'three_phase'}).status,'professional');
assert.equal(calc({useCase:'ev'}).status,'professional');
assert.equal(calc({useCase:'medical'}).status,'professional');
assert.equal(calc({daysPerMonth:'0'}).status,'evidence_required');
assert.equal(calc({tariff:''}).status,'evidence_required');
assert.equal(calc({measurementBasis:'unknown'}).status,'evidence_required');
assert.equal(calc({activePowerW:'0'}).status,'evidence_required');
assert.equal(calc({hoursPerDay:'12',standbyHoursPerDay:'13'}).status,'evidence_required');
assert.equal(calc({deviceCurrentA:''}).status,'evidence_required');
assert.equal(calc({deviceCurrentA:'17'}).status,'professional');
assert.equal(calc({deviceCurrentA:'12'}).status,'professional');
const candidate=calc({});
assert.equal(candidate.status,'conditional_purchase');
assert.equal(candidate.commercialAllowed,true);
assert.equal(candidate.monthlyKWh,33.6);
assert.equal(candidate.activeKWh,28.8);
assert.equal(candidate.standbyKWh,4.8);
assert.equal(candidate.monthlyCost,100.8);
assert.equal(candidate.annualCost,1209.6);
assert.ok(tool.affiliateUrl(candidate).includes('tag=alo186rehber-21'));
assert.equal(calc({measurementBasis:'nameplate_w'}).status,'estimate_only');
assert.equal(calc({goal:'estimate_bill'}).status,'no_buy');
const measured=calc({measurementBasis:'measured_kwh',measuredKWh:'12',measuredDays:'10',goal:'estimate_bill'});
assert.equal(measured.monthlyKWh,36);
assert.equal(measured.monthlyCost,108);
assert.equal(calc({useCase:'heater',goal:'remote_control'}).status,'measurement_only');
assert.equal(calc({existingType:'plug_meter',existingMaxA:'0'}).status,'evidence_required');
assert.equal(calc({existingType:'plug_meter',existingMaxA:'1',existingCondition:'sound'}).status,'replace_candidate');
assert.equal(calc({existingType:'plug_meter',existingMaxA:'16',existingCondition:'sound',existingEnergyKwh:'no'}).status,'evidence_required');
assert.equal(calc({existingType:'plug_meter',existingMaxA:'16',existingCondition:'sound',existingEnergyKwh:'yes',existingCertificate:'no'}).status,'evidence_required');
assert.equal(calc({existingType:'plug_meter',existingMaxA:'16',existingCondition:'sound',existingEnergyKwh:'yes',existingCertificate:'yes',existingAccuracyClass:'yes',temperatureTest:'no'}).status,'stop_use');
assert.equal(calc({existingType:'plug_meter',existingMaxA:'16',existingCondition:'sound',existingEnergyKwh:'yes',existingCertificate:'yes',existingAccuracyClass:'yes',temperatureTest:'not_tested'}).status,'test_existing');
const noBuy=calc({existingType:'plug_meter',existingMaxA:'16',existingCondition:'sound',existingEnergyKwh:'yes',existingCertificate:'yes',existingAccuracyClass:'yes',temperatureTest:'yes'});
assert.equal(noBuy.status,'no_buy');
assert.equal(noBuy.commercialAllowed,false);
assert.equal(tool.affiliateUrl(noBuy),null);
assert.equal(calc({useCase:'refrigerator',existingType:'smart_plug',existingMaxA:'16',existingCondition:'sound',existingEnergyKwh:'yes',existingCertificate:'yes',existingAccuracyClass:'yes',temperatureTest:'yes'}).status,'measurement_only');
console.log(JSON.stringify({ok:true,scenarios:31,monthlyKWh:candidate.monthlyKWh,monthlyCost:candidate.monthlyCost,noBuy:true,affiliateGate:true,personalData:false}));
