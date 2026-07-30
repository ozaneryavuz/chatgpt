'use strict';
const assert=require('assert');
const {calculate,metrics,affiliateUrl,constants}=require('./app.js');

const valid={
  emergency:false,
  batteryCondition:'sound',
  terminals:'clean',
  chargeArea:'safe',
  goal:'battery',
  brand:'Bosch Professional',
  platform:'18V Professional',
  chemistry:'liion',
  adapterUse:'none',
  oemAdapterEvidence:'no',
  platformEvidence:'exact',
  toolVoltage:'18',
  candidateVoltage:'18',
  candidateAh:'5',
  toolDuty:'normal',
  highOutputEvidence:'yes',
  existingStatus:'none',
  workGap:'yes',
  crossTest:'yes',
  chargerMatch:'exact',
  chargerCurrent:'4',
  fastChargeAllowed:'yes',
  manualVerified:'yes',
  traceability:'yes',
  certification:'yes',
  recallChecked:'yes',
  supervisedTest:'yes'
};
const run=(patch)=>calculate({...valid,...patch});

assert.equal(run({emergency:true}).status,'emergency');
for(const condition of ['swollen','cracked','leaking','burned','wet']){
  assert.equal(run({batteryCondition:condition}).status,'stop_use');
}
for(const terminals of ['damaged','corroded','bridged']){
  assert.equal(run({terminals}).status,'stop_use');
}
for(const chargeArea of ['flammable','unattended','hotcold','wet']){
  assert.equal(run({chargeArea}).status,'stop_use');
}
assert.equal(run({goal:'diagnose'}).status,'professional');
assert.equal(run({brand:''}).status,'evidence_required');
assert.equal(run({platform:''}).status,'evidence_required');
assert.equal(run({chemistry:'unknown'}).status,'evidence_required');
assert.equal(run({adapterUse:'third_party'}).status,'stop_use');
assert.equal(run({adapterUse:'oem',oemAdapterEvidence:'no'}).status,'evidence_required');
assert.equal(run({platformEvidence:'physical'}).status,'stop_use');
assert.equal(run({platformEvidence:'unknown'}).status,'evidence_required');
assert.equal(run({candidateVoltage:'12'}).status,'stop_use');
assert.equal(run({candidateAh:''}).status,'evidence_required');
assert.equal(run({toolDuty:'high',highOutputEvidence:'no'}).status,'evidence_required');
assert.equal(run({recallChecked:'recalled'}).status,'stop_use');
assert.equal(run({recallChecked:'unknown'}).status,'evidence_required');
assert.equal(run({manualVerified:'no'}).status,'evidence_required');
assert.equal(run({traceability:'no'}).status,'evidence_required');
assert.equal(run({certification:'no'}).status,'evidence_required');
assert.equal(run({goal:'charger',chargerMatch:'no'}).status,'stop_use');
assert.equal(run({goal:'charger',chargerMatch:'unknown'}).status,'evidence_required');
assert.equal(run({goal:'charger',chargerCurrent:''}).status,'evidence_required');
assert.equal(run({goal:'charger',fastChargeAllowed:'no'}).status,'stop_use');
assert.equal(run({goal:'battery',existingStatus:'good'}).status,'no_buy');
assert.equal(run({goal:'charger',existingStatus:'good'}).status,'no_buy');
assert.equal(run({goal:'second_battery',workGap:'no'}).status,'no_buy');
assert.equal(run({existingStatus:'weak',crossTest:'no'}).status,'test_existing');
assert.equal(run({supervisedTest:'no'}).status,'test_existing');

const result=run({});
assert.equal(result.status,'conditional_purchase');
assert.equal(result.commercialAllowed,true);
assert.equal(result.productClass,'tool_battery');
assert.equal(Math.round(result.batteryWh),90);
assert.equal(Number(result.chargeHours.toFixed(1)),1.5);
assert.ok(result.searchTerm.includes('Bosch Professional'));
assert.ok(result.searchTerm.includes('18V'));
assert.ok(result.searchTerm.includes('5Ah'));
const url=affiliateUrl(result);
assert.ok(url.includes('amazon.com.tr'));
assert.ok(url.includes(`tag=${constants.AFFILIATE_TAG}`));

const charger=run({goal:'charger'});
assert.equal(charger.status,'conditional_purchase');
assert.equal(charger.productClass,'battery_charger');
assert.equal(Number(charger.chargeHours.toFixed(1)),1.5);
assert.ok(charger.searchTerm.includes('şarj cihazı'));

const kit=run({goal:'kit'});
assert.equal(kit.productClass,'battery_charger_kit');
assert.ok(kit.searchTerm.includes('akü şarj seti'));

const marketingPair=run({toolVoltage:'18',candidateVoltage:'20'});
assert.equal(marketingPair.status,'conditional_purchase');

assert.equal(affiliateUrl(run({emergency:true})),null);
assert.deepEqual(metrics({toolVoltage:'18',candidateVoltage:'18',candidateAh:'5',chargerCurrent:'4'}),{
  toolVoltage:18,candidateVoltage:18,candidateAh:5,chargerCurrent:4,batteryWh:90,chargeHours:1.5
});

console.log(JSON.stringify({ok:true,scenarios:38,affiliateTripleGate:true,noBuy:true,emergencyBlocked:true,adapterBlocked:true,whCalculation:true,chargeTime:true}));
