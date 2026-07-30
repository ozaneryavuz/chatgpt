'use strict';
const assert=require('assert');
const {calculate,metrics,buildSearchUrl}=require('./app.js');

const valid={
  emergency:false,activeProblem:'no',useCase:'router',connection:'wall',grounded:'yes',
  loadEvidence:'measured',loadW:40,loadA:'',hoursPerDay:24,purpose:'energy',
  manufacturerPermission:'yes',existingType:'none',existingCondition:'unknown',
  existingA:'',existingW:'',certification:'unknown',softwareSupport:'unknown',
  recallChecked:'unknown',loadTest:'unknown',energyFeature:'yes',existingEnergy:'unknown'
};
const run=(extra={})=>calculate({...valid,...extra});

assert.equal(run({emergency:true}).status,'emergency');
assert.equal(run({activeProblem:'yes'}).status,'stop_use');
assert.equal(run({useCase:'heater'}).status,'professional');
assert.equal(run({useCase:'fridge'}).commercialAllowed,false);
assert.equal(run({useCase:'medical'}).status,'professional');
assert.equal(run({connection:'extension'}).status,'stop_use');
assert.equal(run({grounded:'no'}).status,'stop_use');
assert.equal(run({manufacturerPermission:'no'}).status,'no_buy');
assert.equal(run({loadEvidence:'guess'}).status,'evidence_required');
assert.equal(run({loadW:1800,loadA:8}).status,'professional');

const fresh=run();
assert.equal(fresh.status,'conditional_purchase');
assert.equal(fresh.commercialAllowed,true);
assert.equal(fresh.requiredW,50);
assert.ok(fresh.monthlyKwh>28&&fresh.monthlyKwh<30);

const existing={
  existingType:'smart',existingCondition:'sound',existingA:16,existingW:3680,
  certification:'yes',softwareSupport:'yes',recallChecked:'yes',loadTest:'yes',existingEnergy:'yes'
};
assert.equal(run({...existing,existingA:0.1,existingW:20}).status,'replace_candidate');
assert.equal(run({...existing,recallChecked:'recalled'}).status,'stop_use');
const unsupported=run({...existing,softwareSupport:'no'});
assert.equal(unsupported.status,'planned_replace');
assert.equal(unsupported.commercialAllowed,true);
assert.equal(run({...existing,existingEnergy:'no'}).status,'feature_gap');
assert.equal(run({...existing,loadTest:'no'}).status,'stop_use');
assert.equal(run({...existing,loadTest:'unknown'}).status,'test_existing');
const enough=run(existing);
assert.equal(enough.status,'no_buy');
assert.equal(enough.commercialAllowed,false);
assert.match(enough.title,/yeni ürün almayın/i);

const m=metrics({loadW:100,hoursPerDay:5});
assert.equal(m.requiredW,150);
assert.equal(m.monthlyKwh,15);
assert.match(buildSearchUrl('akıllı priz'),/alo186rehber-21/);

console.log(JSON.stringify({ok:true,scenarios:18,noBuy:true,affiliateTripleGate:true,highRiskBlocked:true,monthlyEnergy:true},null,2));
