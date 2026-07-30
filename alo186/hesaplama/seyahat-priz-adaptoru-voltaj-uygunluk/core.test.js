'use strict';

const assert=require('node:assert/strict');
const {evaluate}=require('./core.js');

const base={destination:'uk',deviceType:'electronics',minV:100,maxV:240,frequency:'50_60',deviceW:65,earthClass:'class2',existingAdapter:'none',hazard:false,adapterDamaged:false};
const run=(patch)=>evaluate({...base,...patch});

assert.equal(run({destination:'eu'}).status,'no_buy','C/F ve çift gerilimli cihazda yeni adaptör gerekmemeli.');
let result=run({destination:'uk'});
assert.equal(result.status,'conditional_purchase');
assert.equal(result.commerceAllowed,true);
assert.match(result.affiliateQuery,/Type G/);
assert.ok(result.requiredW>=82);

result=run({destination:'uk',existingAdapter:'yes',adapterMaxV:250,adapterMaxA:3,adapterMaxW:0,adapterEarth:'unknown',safetyEvidence:'yes',recallChecked:'yes'});
assert.equal(result.status,'no_buy','Yeterli mevcut Class II adaptör yeni alışverişi kapatmalı.');

result=run({destination:'us',minV:220,maxV:240});
assert.equal(result.status,'voltage_mismatch');
assert.equal(result.commerceAllowed,false);
assert.match(result.summary,/voltaj|dönüştürmez/i);

result=run({destination:'us',minV:100,maxV:240,frequency:'50_60'});
assert.equal(result.status,'conditional_purchase');

result=run({destination:'japan',frequency:'50',deviceType:'motor'});
assert.equal(result.status,'evidence','Japonya 50/60 Hz bölge farkında tek frekanslı motor için hedef bölge kanıtı istenmeli.');

result=run({destination:'japan',frequency:'50_60'});
assert.equal(result.status,'conditional_purchase','50/60 Hz elektronik Japonya için voltaj uyumundan sonra adaptör yoluna gidebilmeli.');

result=run({destination:'us',deviceType:'heater',deviceW:1800,minV:100,maxV:240});
assert.equal(result.status,'professional');
assert.equal(result.commerceAllowed,false);

result=run({destination:'uk',deviceType:'medical'});
assert.equal(result.status,'professional');

result=run({destination:'unknown'});
assert.equal(result.status,'evidence');

result=run({hazard:true});
assert.equal(result.status,'emergency');

result=run({adapterDamaged:true});
assert.equal(result.status,'emergency');

result=run({existingAdapter:'yes',adapterMaxV:250,adapterMaxA:3,safetyEvidence:'yes',recallChecked:'no'});
assert.equal(result.status,'emergency','Olumsuz geri çağırma sonucu mevcut adaptörü kullanmayı durdurmalı.');

result=run({existingAdapter:'yes',adapterMaxV:250,adapterMaxA:.1,safetyEvidence:'yes',recallChecked:'yes'});
assert.equal(result.status,'conditional_purchase');
assert.ok(result.reasons.some((item)=>/güç|akım/.test(item)));

result=run({earthClass:'earth_required',existingAdapter:'yes',adapterMaxV:250,adapterMaxA:3,adapterEarth:'no',safetyEvidence:'yes',recallChecked:'yes'});
assert.equal(result.status,'conditional_purchase');
assert.ok(result.reasons.some((item)=>/topraklama/.test(item)));

result=run({earthClass:'unknown'});
assert.equal(result.status,'evidence');

result=run({frequency:'unknown'});
assert.equal(result.status,'evidence');

result=run({destination:'us',deviceType:'motor',frequency:'50'});
assert.equal(result.status,'professional','Motorlu yüksek riskli yük tüketici affiliate rotasına açılmamalı.');

result=run({deviceW:0});
assert.equal(result.status,'invalid');

console.log('Seyahat priz adaptörü uygunluğu: voltaj, frekans, topraklama, no-buy, geri çağırma ve affiliate kapıları başarılı.');
