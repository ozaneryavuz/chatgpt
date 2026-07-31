'use strict';
const assert = require('assert');
const { evaluate } = require('./app.js');

const noBuy = evaluate({
  deviceClass:'remote',manual:'yes',size:'AAA',deviceCount:2,cellsPerDevice:2,
  downtime:'yes',currentSet:'healthy',existingSpare:2,slots:4,chargerMode:'individual',
  chargeHours:8,serviceDays:14,chargerStatus:'good'
});
assert.equal(noBuy.status,'no-buy');
assert.equal(noBuy.requiredAdditional,0);
assert.equal(noBuy.affiliateAllowed,false);

const needCells = evaluate({
  deviceClass:'toy',manual:'yes',size:'AA',deviceCount:3,cellsPerDevice:4,
  downtime:'no',currentSet:'healthy',existingSpare:4,slots:4,chargerMode:'pair',
  chargeHours:6,serviceDays:7,chargerStatus:'good',
  confirmNeed:true,confirmSpecs:true,confirmAffiliate:true
});
assert.equal(needCells.status,'recommend');
assert.equal(needCells.activeCells,12);
assert.equal(needCells.targetBackup,12);
assert.equal(needCells.requiredAdditional,8);
assert(needCells.categories.includes('rechargeable_nimh_battery'));
assert.equal(needCells.affiliateAllowed,true);

const blocked = evaluate({
  deviceClass:'smoke',manual:'unknown',size:'AA',deviceCount:1,cellsPerDevice:2,
  downtime:'no',currentSet:'unknown',existingSpare:0,slots:2,chargerMode:'unknown',
  chargeHours:8,serviceDays:30,chargerStatus:'unknown',damage:false,
  confirmNeed:true,confirmSpecs:true,confirmAffiliate:true
});
assert.equal(blocked.status,'professional');
assert.equal(blocked.affiliateAllowed,false);
console.log('şarjlı pil döngü testleri geçti');