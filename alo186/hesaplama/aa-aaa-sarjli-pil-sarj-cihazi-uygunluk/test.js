'use strict';
const assert = require('assert');
const { evaluate } = require('./app.js');

const noBuy = evaluate({
  deviceClass:'remote',size:'AAA',manual:'yes',voltage:'1.2-ok',deviceCells:2,
  chargePlan:'use',currentChemistry:'nimh',condition:'good',mix:'same',
  chargerType:'nimh-individual',chargerCondition:'good',slots:'4'
});
assert.equal(noBuy.status,'no-buy');
assert.equal(noBuy.affiliateAllowed,false);

const recommend = evaluate({
  deviceClass:'toy',size:'AA',manual:'yes',voltage:'1.2-ok',deviceCells:4,
  chargePlan:'new',currentChemistry:'none',condition:'good',mix:'same',
  chargerType:'none',chargerCondition:'good',slots:'4',
  confirmNeed:true,confirmSpecs:true,confirmAffiliate:true
});
assert.equal(recommend.status,'recommend');
assert.deepEqual(recommend.categories.sort(),['nimh_battery_charger','rechargeable_nimh_battery'].sort());
assert.equal(recommend.affiliateAllowed,true);

const blocked = evaluate({
  deviceClass:'medical',size:'AA',manual:'unknown',voltage:'unknown',
  currentChemistry:'alkaline',chargePlan:'charge',condition:'good',mix:'same',
  chargerType:'nimh-pair',chargerCondition:'good',damage:false,
  confirmNeed:true,confirmSpecs:true,confirmAffiliate:true
});
assert.equal(blocked.status,'stop');
assert.equal(blocked.affiliateAllowed,false);
console.log('aa-aaa uyumluluk testleri geçti');