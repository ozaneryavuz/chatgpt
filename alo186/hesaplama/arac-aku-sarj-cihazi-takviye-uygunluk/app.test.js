'use strict';
const assert=require('node:assert/strict');
const tool=require('./app.js');
const base={
  emergency:false,batteryCondition:'sound',ventilation:'yes',vehicleClass:'passenger',purpose:'recharge',activeBreakdown:'no',manualChecked:'yes',
  voltage:'12',chemistry:'agm',capacityAh:'70',socPercent:'50',manufacturerMaxA:'10',existingType:'none',chargerVoltage:'',chemistryMode:'unknown',chargerCurrentA:'',protections:'unknown',certification:'unknown',temperatureCompensation:'unknown',supervisedTest:'not_tested'
};
const calc=(patch)=>tool.calculate({...base,...patch});
assert.equal(calc({emergency:true}).status,'emergency');
assert.equal(calc({batteryCondition:'frozen'}).status,'stop_use');
assert.equal(calc({batteryCondition:'damaged'}).status,'stop_use');
assert.equal(calc({ventilation:'no'}).status,'stop_use');
assert.equal(calc({vehicleClass:'heavy_24v'}).status,'professional');
assert.equal(calc({vehicleClass:'hybrid_ev'}).status,'professional');
assert.equal(calc({activeBreakdown:'yes'}).status,'active_breakdown');
assert.equal(calc({manualChecked:'no'}).status,'evidence_required');
assert.equal(calc({chemistry:'unknown'}).status,'evidence_required');
assert.equal(calc({chemistry:'lifepo4'}).status,'professional');
assert.equal(calc({purpose:'diagnose'}).status,'evidence_required');
const candidate=calc({existingType:'none'});
assert.equal(candidate.status,'conditional_purchase');
assert.equal(candidate.commercialAllowed,true);
assert.equal(candidate.planningCurrentA,7);
assert.equal(candidate.approxHours,6);
assert.ok(tool.affiliateUrl(candidate).includes('tag=alo186rehber-21'));
assert.equal(calc({purpose:'prepare_jump',existingType:'none'}).productClass,'jump_starter');
assert.equal(calc({existingType:'manual_charger'}).status,'replace_candidate');
assert.equal(calc({existingType:'smart_charger',chargerVoltage:'24',chemistryMode:'yes',chargerCurrentA:'7',protections:'yes',certification:'yes',temperatureCompensation:'yes',supervisedTest:'yes'}).status,'stop_use');
assert.equal(calc({existingType:'smart_charger',chargerVoltage:'12',chemistryMode:'no',chargerCurrentA:'7',protections:'yes',certification:'yes',temperatureCompensation:'yes',supervisedTest:'yes'}).status,'stop_use');
assert.equal(calc({existingType:'smart_charger',chargerVoltage:'12',chemistryMode:'yes',chargerCurrentA:'12',protections:'yes',certification:'yes',temperatureCompensation:'yes',supervisedTest:'yes'}).status,'stop_use');
assert.equal(calc({manufacturerMaxA:'',existingType:'smart_charger',chargerVoltage:'12',chemistryMode:'yes',chargerCurrentA:'12',protections:'yes',certification:'yes',temperatureCompensation:'yes',supervisedTest:'yes'}).status,'evidence_required');
assert.equal(calc({existingType:'smart_charger',chargerVoltage:'12',chemistryMode:'yes',chargerCurrentA:'7',protections:'unknown',certification:'yes',temperatureCompensation:'yes',supervisedTest:'yes'}).status,'evidence_required');
assert.equal(calc({existingType:'smart_charger',chargerVoltage:'12',chemistryMode:'yes',chargerCurrentA:'7',protections:'yes',certification:'yes',temperatureCompensation:'yes',supervisedTest:'not_tested'}).status,'test_existing');
const noBuy=calc({existingType:'smart_charger',chargerVoltage:'12',chemistryMode:'yes',chargerCurrentA:'7',protections:'yes',certification:'yes',temperatureCompensation:'yes',supervisedTest:'yes'});
assert.equal(noBuy.status,'no_buy');
assert.equal(noBuy.commercialAllowed,false);
assert.equal(tool.affiliateUrl(noBuy),null);
console.log(JSON.stringify({ok:true,scenarios:22,noBuy:true,affiliateGate:true,personalData:false}));
