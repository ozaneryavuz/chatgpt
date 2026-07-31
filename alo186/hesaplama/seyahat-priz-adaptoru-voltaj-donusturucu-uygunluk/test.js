'use strict';
const assert=require('assert');
const {evaluate}=require('./app.js');

const noBuy=evaluate({destV:230,minV:100,maxV:240,powerW:65,destHz:'50',deviceHz:'both',plugMatch:'yes',official:'yes',deviceClass:'electronics'});
assert.equal(noBuy.status,'no-buy');
assert.equal(noBuy.affiliateAllowed,false);

const recommend=evaluate({destV:120,minV:100,maxV:240,powerW:65,destHz:'60',deviceHz:'both',plugMatch:'no',official:'yes',deviceClass:'electronics',existing:'none',earth:'notNeeded',confirmNeed:true,confirmSpecs:true,confirmAffiliate:true});
assert.equal(recommend.status,'recommend');
assert.equal(recommend.affiliateAllowed,true);
assert.deepEqual(recommend.categories,['travel_adapter']);

const blocked=evaluate({destV:120,minV:220,maxV:240,powerW:1800,destHz:'60',deviceHz:'50',plugMatch:'no',official:'yes',deviceClass:'heating',confirmNeed:true,confirmSpecs:true,confirmAffiliate:true});
assert.equal(blocked.status,'stop');
assert.equal(blocked.affiliateAllowed,false);
console.log('seyahat adaptörü karar testleri geçti');
