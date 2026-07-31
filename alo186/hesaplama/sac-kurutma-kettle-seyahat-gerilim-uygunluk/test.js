'use strict';
const assert=require('assert');
const {evaluate}=require('./app.js');

const noBuy=evaluate({device:'straightener',powerW:45,minV:100,maxV:240,destV:230,deviceHz:'both',destHz:'50',selector:'none',plugMatch:'yes',official:'yes',place:'dry'});
assert.equal(noBuy.status,'no-buy');
assert.equal(noBuy.affiliateAllowed,false);

const recommend=evaluate({device:'shaver',powerW:12,minV:100,maxV:240,destV:120,deviceHz:'both',destHz:'60',selector:'none',plugMatch:'no',official:'yes',place:'dry',adapter:'none',confirmNeed:true,confirmSpecs:true,confirmAffiliate:true});
assert.equal(recommend.status,'recommend');
assert.equal(recommend.affiliateAllowed,true);

const highPower=evaluate({device:'dryer',powerW:1800,minV:100,maxV:240,destV:120,deviceHz:'both',destHz:'60',selector:'correct',plugMatch:'no',official:'yes',place:'dry',adapter:'none',confirmNeed:true,confirmSpecs:true,confirmAffiliate:true});
assert.equal(highPower.status,'professional');
assert.equal(highPower.affiliateAllowed,false);
console.log('yüksek güçlü seyahat cihazı testleri geçti');
