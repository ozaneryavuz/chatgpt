'use strict';
const assert=require('assert');
const fs=require('fs');
const path=require('path');
const core=require('./core.js');

const base={
  evaluationMode:'existing',voltage:230,loadPower:300,powerFactor:0.95,loadType:'electronic',startMultiplier:'',usage:'short',intendedUse:'portable',
  length:15,area:1.5,ratedCurrent:16,reelState:'none',woundMaxPower:'',unwoundMaxPower:'',environment:'indoor',
  applianceClass:'classI',factoryAssembled:true,labelVerified:true,damageFree:true,earthPresent:true,outdoorRated:false,thermalProtection:false,daisyChain:false,recallChecked:true
};
const run=overrides=>core.analyze({...base,...overrides});

const office=run({});
assert.equal(office.status,'no_buy');
assert.equal(office.purchaseDecision,'no_buy');
assert.equal(office.commercialAllowed,false);
assert(office.dropPercent<3);
assert(office.checks.some(x=>x.includes('yeni ürün aramayın')));

const planned=run({evaluationMode:'planned'});
assert.equal(planned.status,'compatible');
assert.equal(planned.commercialAllowed,true);
assert.equal(planned.purchaseDecision,'conditional_purchase');
assert.equal(planned.repeatDays,180);

const recallMissing=run({evaluationMode:'planned',recallChecked:false});
assert.equal(recallMissing.status,'conditional');
assert.equal(recallMissing.commercialAllowed,false);
assert(recallMissing.warnings.some(x=>x.includes('geri çağırma')));

const longThin=run({loadPower:1800,powerFactor:1,length:100,area:.75,ratedCurrent:16});
assert.equal(longThin.status,'incompatible');
assert(longThin.dropPercent>5);
assert(longThin.blockers.some(x=>x.includes('gerilim düşümü')));

const overCurrent=run({loadPower:2500,powerFactor:.8,ratedCurrent:10});
assert.equal(overCurrent.status,'incompatible');
assert.equal(overCurrent.commercialAllowed,false);

const wound=run({loadPower:1200,powerFactor:1,reelState:'wound',woundMaxPower:800,thermalProtection:true});
assert.equal(wound.status,'incompatible');
assert(wound.blockers.some(x=>x.includes('sarılı durumdaki')));

assert.equal(run({environment:'outdoor',outdoorRated:false}).status,'incompatible');
assert.equal(run({applianceClass:'classI',earthPresent:false}).status,'incompatible');
for(const intendedUse of ['ev','generatorBackfeed','fixed']){
  const result=run({intendedUse});
  assert.equal(result.status,'incompatible');
  assert.equal(result.commercialAllowed,false);
}

for(const intendedUse of ['medical','heater','cooling']){
  const result=run({evaluationMode:'planned',intendedUse});
  assert.equal(result.commercialAllowed,false);
  assert.equal(result.professionalRequired,true);
}
assert.equal(run({daisyChain:true}).status,'incompatible');

const motor=run({evaluationMode:'planned',loadPower:900,powerFactor:.8,loadType:'motor',startMultiplier:5,length:30,area:1.5,ratedCurrent:16});
assert(motor.startCurrent>motor.operatingCurrent);
assert(motor.warnings.some(x=>x.includes('kalkış')));
assert.equal(motor.commercialAllowed,false);

assert.throws(()=>run({loadType:'motor',startMultiplier:''}),/kalkış akımı katsayısını/);
assert.throws(()=>run({area:1.2}),/0,75/);

const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
assert(html.includes('https://alo186.com/hesaplama/uzatma-kablosu-uygunluk/'));
assert(html.includes('Amazon satış ortaklığı'));
assert(html.includes('IEC 60884-2-7:2025'));
assert(html.includes('IEC 61242'));
assert(!/amazon\.(com|com\.tr)/i.test(html));
assert(!html.includes('"@type":"Offer"'));
assert(html.includes('id="jsonButton"'));
assert(html.includes('id="icsButton"'));
for(const id of ['affiliateNeedAck','affiliateSpecAck','affiliateDisclosureAck'])assert(html.includes(`id="${id}"`));
const formFieldIds=[...html.matchAll(/<(?:input|select|textarea)\b[^>]*(?:id|name)="([^"]+)"/gi)].map(match=>match[1]);
assert(!formFieldIds.some(field=>/(^|[-_])(name|email|phone|telefon|address|adres|abonelik|tc|identity)([-_]|$)/i.test(field)));
assert(html.includes('aria-live="polite"'));
assert(html.includes('type="application/ld+json"'));

console.log(JSON.stringify({ok:true,scenarios:18,noBuy:office.status,plannedPurchase:planned.commercialAllowed,recallGate:true,tripleAffiliateGate:true,repeatDays:planned.repeatDays,personalData:false},null,2));
