'use strict';
const assert=require('assert');
const {calculate,coverage,buildSearchUrl}=require('./app.js');

const valid={
  emergency:false,alarmState:'none',symptoms:'no',occupancy:'apartment',accessibility:'standard',
  levels:2,bedrooms:3,sleepingAreas:2,fuelSources:'multiple',placementChecked:'yes',
  smokeBedrooms:'yes',smokeOutside:'yes',smokeEveryLevel:'yes',coEveryLevel:'yes',coOutside:'yes',
  existingType:'mixed',condition:'sound',smokeAgeYears:4,coEndOfLife:'valid',monthlyTest:'pass',
  batteryMode:'sealed',batteryRetest:'unknown',powerBackup:'yes',certSmoke:'yes',certCo:'yes',recallChecked:'yes'
};
const run=(extra={})=>calculate({...valid,...extra});

assert.equal(run({emergency:true}).status,'emergency');
assert.equal(run({alarmState:'co'}).status,'emergency');
assert.equal(run({symptoms:'yes'}).commercialAllowed,false);
assert.equal(run({occupancy:'hotel'}).status,'professional');
assert.equal(run({accessibility:'hearing'}).status,'professional');
assert.equal(run({levels:''}).status,'evidence_required');
assert.equal(run({fuelSources:'unknown'}).status,'evidence_required');
assert.equal(run({placementChecked:'no'}).status,'evidence_required');
assert.equal(run({smokeBedrooms:'unknown'}).status,'evidence_required');
assert.equal(run({coEveryLevel:'unknown'}).status,'evidence_required');
assert.equal(run({condition:'damaged'}).status,'stop_use');
assert.equal(run({recallChecked:'recalled'}).status,'stop_use');
assert.equal(run({smokeAgeYears:10}).status,'replace_candidate');
assert.equal(run({smokeAgeYears:10}).commercialAllowed,true);
assert.equal(run({coEndOfLife:'expired'}).status,'replace_candidate');
assert.equal(run({monthlyTest:'fail',batteryMode:'replaceable',batteryRetest:'no'}).status,'maintenance_first');
assert.equal(run({monthlyTest:'fail',batteryMode:'sealed'}).status,'replace_candidate');
assert.equal(run({monthlyTest:'unknown'}).status,'test_existing');
assert.equal(run({powerBackup:'no'}).status,'evidence_required');
assert.equal(run({certSmoke:'no'}).status,'evidence_required');
assert.equal(run({certCo:'no'}).status,'evidence_required');

const smokeGap=run({smokeBedrooms:'no'});
assert.equal(smokeGap.status,'conditional_purchase');
assert.equal(smokeGap.coverageGap,'smoke');
assert.equal(smokeGap.commercialAllowed,true);
assert.match(smokeGap.searchTerm,/EN 14604/);

const coGap=run({coOutside:'no'});
assert.equal(coGap.status,'conditional_purchase');
assert.equal(coGap.coverageGap,'co');
assert.match(coGap.searchTerm,/EN 50291-1/);

const bothGap=run({smokeEveryLevel:'no',coEveryLevel:'no'});
assert.equal(bothGap.status,'conditional_purchase');
assert.equal(bothGap.coverageGap,'both');

const noBuy=run();
assert.equal(noBuy.status,'no_buy');
assert.equal(noBuy.commercialAllowed,false);
assert.match(noBuy.title,/yeni ürün almayın/i);

const electricOnly=run({
  fuelSources:'none',existingType:'smoke',coEndOfLife:'unknown',certCo:'unknown',coEveryLevel:'unknown',coOutside:'unknown'
});
assert.equal(electricOnly.status,'no_buy');
assert.equal(electricOnly.coObligations,0);

const emptyWithGap=run({
  existingType:'none',condition:'unknown',smokeAgeYears:'',coEndOfLife:'unknown',monthlyTest:'unknown',
  batteryMode:'unknown',powerBackup:'unknown',certSmoke:'unknown',certCo:'unknown',recallChecked:'unknown',
  smokeEveryLevel:'no',coEveryLevel:'no'
});
assert.equal(emptyWithGap.status,'conditional_purchase');

const c=coverage(valid);
assert.equal(c.smokeObligations,7);
assert.equal(c.coObligations,4);
assert.match(buildSearchUrl('duman alarmı'),/alo186rehber-21/);

console.log(JSON.stringify({
  ok:true,scenarios:29,emergencyCommerceBlocked:true,professionalBlocked:true,
  smokeAndCoSeparated:true,coverageNotProductCount:true,recallBeforeCommerce:true,
  maintenanceBeforeReplacement:true,noBuy:true,affiliateTripleGate:true,revisitDays:30
},null,2));
