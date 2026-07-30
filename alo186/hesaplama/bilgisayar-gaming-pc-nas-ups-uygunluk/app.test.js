'use strict';
const assert=require('node:assert/strict');
const tool=require('./app.js');
const base={
  emergency:false,upsCondition:'sound',installation:'dry',useCase:'gaming_pc',hardwired:'no',
  loadEvidence:'measured',computerW:'450',monitorW:'40',networkW:'20',nasW:'40',otherW:'0',
  peakW:'',targetMinutes:'30',activePfc:'yes',activeOutage:'no',existingType:'none',
  existingVA:'',existingW:'',pureSine:'unknown',certification:'unknown',upsModeCertified:'unknown',
  transferTest:'not_tested',batterySelfTest:'not_tested',batteryAgeYears:'',
  manufacturerRuntimeMinutes:'',observedRuntimeMinutes:''
};
const calc=(patch)=>tool.calculate({...base,...patch});
assert.equal(calc({emergency:true}).status,'emergency');
assert.equal(calc({upsCondition:'swollen'}).status,'stop_use');
assert.equal(calc({upsCondition:'hot'}).status,'stop_use');
assert.equal(calc({installation:'wet'}).status,'stop_use');
assert.equal(calc({installation:'blocked'}).status,'stop_use');
assert.equal(calc({useCase:'medical'}).status,'professional');
assert.equal(calc({useCase:'industrial'}).status,'professional');
assert.equal(calc({hardwired:'yes'}).status,'professional');
assert.equal(calc({loadEvidence:'psu_rating'}).status,'evidence_required');
assert.equal(calc({computerW:'0',monitorW:'0',networkW:'0',nasW:'0'}).status,'evidence_required');
assert.equal(calc({computerW:'3100',monitorW:'0',networkW:'0',nasW:'0'}).status,'professional');
assert.equal(calc({targetMinutes:'2'}).status,'evidence_required');
const candidate=calc({existingType:'none'});
assert.equal(candidate.status,'conditional_purchase');
assert.equal(candidate.commercialAllowed,true);
assert.equal(candidate.totalLoadW,550);
assert.equal(candidate.requiredContinuousW,700);
assert.equal(candidate.requiredPeakW,850);
assert.equal(candidate.requiredVA,900);
assert.equal(candidate.requiredNominalWh,500);
assert.ok(tool.affiliateUrl(candidate).includes('tag=alo186rehber-21'));
assert.equal(calc({activeOutage:'yes'}).status,'active_outage');
assert.equal(calc({existingType:'line_interactive',existingVA:'700',existingW:'500'}).status,'replace_candidate');
assert.equal(calc({existingType:'line_interactive',existingVA:'1000',existingW:'800',pureSine:'no'}).status,'replace_candidate');
assert.equal(calc({existingType:'line_interactive',existingVA:'1000',existingW:'800',pureSine:'yes',certification:'no'}).status,'evidence_required');
assert.equal(calc({existingType:'power_station',existingVA:'1000',existingW:'800',pureSine:'yes',certification:'yes',upsModeCertified:'no'}).status,'evidence_required');
assert.equal(calc({existingType:'line_interactive',existingVA:'1000',existingW:'800',pureSine:'yes',certification:'yes',transferTest:'not_tested'}).status,'test_existing');
assert.equal(calc({existingType:'line_interactive',existingVA:'1000',existingW:'800',pureSine:'yes',certification:'yes',transferTest:'no'}).status,'replace_candidate');
assert.equal(calc({existingType:'line_interactive',existingVA:'1000',existingW:'800',pureSine:'yes',certification:'yes',transferTest:'yes',batterySelfTest:'no'}).status,'battery_service');
assert.equal(calc({existingType:'line_interactive',existingVA:'1000',existingW:'800',pureSine:'yes',certification:'yes',transferTest:'yes',batterySelfTest:'yes',batteryAgeYears:'4',observedRuntimeMinutes:'40'}).status,'battery_service');
assert.equal(calc({existingType:'line_interactive',existingVA:'1000',existingW:'800',pureSine:'yes',certification:'yes',transferTest:'yes',batterySelfTest:'yes'}).status,'test_existing');
assert.equal(calc({existingType:'line_interactive',existingVA:'1000',existingW:'800',pureSine:'yes',certification:'yes',transferTest:'yes',batterySelfTest:'yes',observedRuntimeMinutes:'20'}).status,'replace_candidate');
const noBuy=calc({existingType:'line_interactive',existingVA:'1000',existingW:'800',pureSine:'yes',certification:'yes',transferTest:'yes',batterySelfTest:'yes',batteryAgeYears:'2',observedRuntimeMinutes:'40'});
assert.equal(noBuy.status,'no_buy');
assert.equal(noBuy.commercialAllowed,false);
assert.equal(tool.affiliateUrl(noBuy),null);
console.log(JSON.stringify({ok:true,scenarios:27,totalLoadW:candidate.totalLoadW,requiredW:candidate.requiredContinuousW,requiredVA:candidate.requiredVA,requiredWh:candidate.requiredNominalWh,noBuy:true,affiliateGate:true,personalData:false}));
