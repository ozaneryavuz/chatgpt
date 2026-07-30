'use strict';
const assert=require('node:assert/strict');
const tool=require('./app.js');

const valid={
  emergency:false,condition:'sound',format:'aa',chemistry:'nimh',rechargeableMark:'yes',
  chargerType:'smart_nimh',supportedChemistry:'nimh',modelCode:'',polarity:'verified',
  capacityMah:'2000',chargeCurrentMa:'500',maxChargeCurrentMa:'1000',cells:'4',
  independentChannels:'yes',protections:'verified',grouping:'matched',
  environment:'safe',unattended:'no',recallChecked:'yes',certification:'yes',
  ownership:'candidate',existingStatus:'none',supervisedTest:'not_done'
};
const run=(patch={})=>tool.calculate({...valid,...patch});

assert.equal(run({emergency:true}).status,'emergency');
for(const condition of ['swollen','leaking','hot','damaged','rusted','wet'])assert.equal(run({condition}).status,'stop_use');
assert.equal(run({condition:'unknown'}).status,'evidence_required');
assert.equal(run({format:'coin'}).status,'stop_use');
assert.equal(run({format:'button'}).status,'stop_use');
assert.equal(run({format:'18650',chemistry:'liion'}).status,'professional');
assert.equal(run({format:'21700',chemistry:'liion'}).status,'professional');
for(const chemistry of ['alkaline','zinc','lithium_primary'])assert.equal(run({chemistry}).status,'stop_use');
assert.equal(run({rechargeableMark:'no'}).status,'stop_use');
assert.equal(run({rechargeableMark:'unknown'}).status,'evidence_required');
assert.equal(run({format:'unknown'}).status,'evidence_required');
assert.equal(run({chemistry:'nicd'}).status,'professional');
assert.equal(run({chemistry:'liion',format:'proprietary'}).status,'professional');
assert.equal(run({chemistry:'lifepo4',format:'proprietary'}).status,'professional');
assert.equal(run({chemistry:'unknown'}).status,'evidence_required');
assert.equal(run({chemistry:'li15',format:'aa'}).status,'evidence_required');
assert.equal(run({chemistry:'li15',format:'proprietary',chargerType:'unknown',supportedChemistry:'li15'}).status,'evidence_required');
assert.equal(run({chemistry:'li15',format:'proprietary',chargerType:'manufacturer_specific',supportedChemistry:'li15',modelCode:''}).status,'evidence_required');
assert.equal(run({chargerType:'universal'}).status,'evidence_required');
assert.equal(run({supportedChemistry:'li15'}).status,'stop_use');
assert.equal(run({polarity:'unknown'}).status,'evidence_required');
assert.equal(run({environment:'wet'}).status,'stop_use');
assert.equal(run({environment:'flammable'}).status,'stop_use');
assert.equal(run({environment:'unknown'}).status,'evidence_required');
assert.equal(run({unattended:'yes'}).status,'stop_use');
assert.equal(run({unattended:'unknown'}).status,'evidence_required');
assert.equal(run({capacityMah:''}).status,'evidence_required');
assert.equal(run({chargeCurrentMa:''}).status,'evidence_required');
assert.equal(run({maxChargeCurrentMa:''}).status,'evidence_required');
assert.equal(run({cells:'0'}).status,'evidence_required');
const over=run({chargeCurrentMa:'1200',maxChargeCurrentMa:'1000'});
assert.equal(over.status,'replace_candidate');
assert.equal(over.commercialAllowed,true);
assert.ok(tool.affiliateUrl(over).includes('tag=alo186rehber-21'));
assert.equal(run({grouping:'mixed',independentChannels:'no'}).status,'stop_use');
assert.equal(run({grouping:'single',independentChannels:'no'}).status,'evidence_required');
assert.equal(run({grouping:'unknown'}).status,'evidence_required');
assert.equal(run({protections:'unknown'}).status,'evidence_required');
assert.equal(run({recallChecked:'recalled'}).status,'stop_use');
assert.equal(run({recallChecked:'unknown'}).status,'evidence_required');
assert.equal(run({certification:'no'}).status,'evidence_required');

const basic=run();
assert.equal(basic.status,'conditional_purchase');
assert.equal(basic.commercialAllowed,true);
assert.equal(basic.productClass,'nimh_charger');
assert.equal(basic.nominalVoltage,1.2);
assert.equal(basic.totalEnergyWh,9.6);
assert.equal(basic.estimatedHours,5.6);
assert.equal(basic.chargeRateC,0.25);

const li15=run({
  format:'proprietary',chemistry:'li15',chargerType:'manufacturer_specific',
  supportedChemistry:'li15',modelCode:'ABC-15',capacityMah:'1800',
  chargeCurrentMa:'600',maxChargeCurrentMa:'700',cells:'4',
  independentChannels:'yes',protections:'verified',grouping:'matched'
});
assert.equal(li15.status,'conditional_purchase');
assert.equal(li15.productClass,'matched_li15_set');
assert.equal(li15.nominalVoltage,1.5);
assert.equal(li15.totalEnergyWh,10.8);
assert.equal(li15.estimatedHours,3.6);
assert.ok(li15.searchTerm.includes('ABC-15'));

const noBuy=run({ownership:'owned',existingStatus:'good',supervisedTest:'pass'});
assert.equal(noBuy.status,'no_buy');
assert.equal(noBuy.commercialAllowed,false);
assert.equal(tool.affiliateUrl(noBuy),null);
assert.equal(run({ownership:'owned',existingStatus:'heats',supervisedTest:'fail'}).status,'stop_use');
assert.equal(run({ownership:'owned',existingStatus:'good',supervisedTest:'not_done'}).status,'test_existing');
assert.equal(run({ownership:'unknown'}).status,'evidence_required');

const metric=tool.metrics(valid);
assert.equal(metric.totalEnergyWh,9.6);
assert.equal(metric.estimatedHours,5.6);
assert.equal(tool.constants.AFFILIATE_TAG,'alo186rehber-21');

console.log(JSON.stringify({
  ok:true,scenarios:52,route:'/hesaplama/sarjli-pil-sarj-cihazi-uygunluk/',
  chemistryGate:true,primaryBatteryBlocked:true,looseLithiumBlocked:true,
  chargeTime:true,noBuy:true,affiliateTripleGate:true,personalData:false,revisitDays:120
},null,2));
