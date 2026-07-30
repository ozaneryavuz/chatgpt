'use strict';
const assert=require('node:assert/strict');
const {evaluateModemBackup,AFFILIATE_URLS}=require('./app.js');

const base={
  electricalHazard:false,criticalUse:false,scenario:'planning',connection:'fiber',serviceEvidence:'yes',
  modemW:12,modemV:12,ontW:8,ontV:12,hours:4,efficiency:85,reserve:20,
  voltageVerified:'yes',currentVerified:'yes',jackVerified:'yes',polarityVerified:'yes',
  sourceStatus:'none',existingW:30,existingWh:100,realTest:'unknown'
};

const commerce=evaluateModemBackup(base);
assert.equal(commerce.state,'commerce');
assert.equal(commerce.commerceAllowed,true);
assert.equal(commerce.productClass,'mini');
assert.match(commerce.affiliateUrl,/amazon\.com\.tr/);
assert.match(commerce.affiliateUrl,/alo186rehber-21/);
assert.ok(commerce.requiredWh>100&&commerce.requiredWh<120);

const active=evaluateModemBackup({...base,scenario:'active'});
assert.equal(active.state,'active');
assert.equal(active.commerceAllowed,false);

const hazard=evaluateModemBackup({...base,electricalHazard:true});
assert.equal(hazard.state,'hazard');
assert.equal(hazard.commerceAllowed,false);

const critical=evaluateModemBackup({...base,criticalUse:true});
assert.equal(critical.state,'professional');
assert.equal(critical.commerceAllowed,false);

const serviceGap=evaluateModemBackup({...base,serviceEvidence:'no'});
assert.equal(serviceGap.state,'service_gap');
assert.equal(serviceGap.commerceAllowed,false);

const evidence=evaluateModemBackup({...base,polarityVerified:'unknown'});
assert.equal(evidence.state,'evidence');
assert.equal(evidence.commerceAllowed,false);

const noBuy=evaluateModemBackup({...base,sourceStatus:'existing',existingW:40,existingWh:150,realTest:'yes'});
assert.equal(noBuy.state,'no_buy');
assert.equal(noBuy.commerceAllowed,false);

const testFirst=evaluateModemBackup({...base,sourceStatus:'existing',existingW:40,existingWh:150,realTest:'unknown'});
assert.equal(testFirst.state,'test_first');
assert.equal(testFirst.commerceAllowed,false);

const insufficient=evaluateModemBackup({...base,sourceStatus:'existing',existingW:15,existingWh:40,realTest:'failed'});
assert.equal(insufficient.state,'commerce');
assert.equal(insufficient.commerceAllowed,true);

const splitVoltage=evaluateModemBackup({...base,ontV:9});
assert.equal(splitVoltage.differentVoltages,true);
assert.ok(splitVoltage.outputs.some(line=>line.includes('tek sabit voltaj')));

const dsl=evaluateModemBackup({...base,connection:'dsl',ontW:90,ontV:24});
assert.equal(dsl.totalW,12);
assert.equal(dsl.ontA,0);

assert.deepEqual(Object.keys(AFFILIATE_URLS).sort(),['backup','mini']);
assert.equal(commerce.revisitDays,90);
console.log(JSON.stringify({ok:true,scenarios:11,states:['commerce','active','hazard','professional','service_gap','evidence','no_buy','test_first'],tripleGate:true,affiliateDisclosure:true,revisitDays:90}));
