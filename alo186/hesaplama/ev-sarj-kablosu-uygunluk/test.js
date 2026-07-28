'use strict';
const assert=require('assert');
const fs=require('fs');
const path=require('path');
const core=require('./core.js');
const base={stationType:'socketed',vehicleInlet:'type2',vehiclePhases:'three',vehicleMaxKw:11,stationPhases:'three',stationMaxCurrent:32,ownership:'candidate',cableConnector:'type2-type2',cablePhases:'three',cableRatedCurrent:16,cableLength:5,labelVerified:true,vehicleSpecVerified:true,stationSpecVerified:true,damageFree:true,storageOk:true,manufacturerCompatibility:true,noExtension:true,lockingWorks:true};
const run=o=>core.analyze({...base,...o});

const eleven=run({});
assert.equal(eleven.status,'compatible');
assert.equal(eleven.recommendedCurrent,16);
assert.equal(eleven.commercialAllowed,true);
assert.equal(eleven.targetPowerKw,11);

const owned=run({ownership:'owned'});
assert.equal(owned.noPurchaseNeeded,true);
assert.equal(owned.commercialAllowed,false);

const overSpecified=run({cableRatedCurrent:32});
assert.equal(overSpecified.overSpecified,true);
assert.equal(overSpecified.status,'conditional');
assert.equal(overSpecified.commercialAllowed,false);
assert(overSpecified.warnings.some(x=>x.includes('Gereksiz yüksek sınıf için ürün yönlendirmesi açılmaz')));

const fullPower=run({vehicleMaxKw:22,cableRatedCurrent:32});
assert.equal(fullPower.recommendedCurrent,32);
assert.equal(fullPower.overSpecified,false);
assert.equal(fullPower.commercialAllowed,true);

const single=run({vehicleMaxKw:22,cablePhases:'single',cableRatedCurrent:32});
assert(single.blockerCodes.includes('phase_capacity'));
assert.equal(single.commercialAllowed,true);

const low=run({vehiclePhases:'single',stationPhases:'single',vehicleMaxKw:7.4,cablePhases:'single',cableRatedCurrent:16});
assert(low.blockerCodes.includes('current_capacity'));
assert.equal(low.commercialAllowed,true);

assert.equal(run({stationType:'tethered'}).status,'not-needed');
for(const item of [{vehicleInlet:'type1'},{damageFree:false},{noExtension:false},{lockingWorks:false},{cableConnector:'unknown'}]){
  const result=run(item);
  assert.equal(result.status,'incompatible');
  assert.equal(result.commercialAllowed,false);
}
assert.equal(run({stationPhases:'unknown'}).commercialAllowed,false);
assert.equal(run({labelVerified:false}).status,'conditional');
assert(run({cableLength:15}).warnings.some(x=>x.includes('10 m üzerindeki')));
assert(Math.abs(core.powerFor('single',32)-7.36)<.01);
assert(Math.abs(core.powerFor('three',16)-11.09)<.02);

const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
assert(html.includes('https://www.alo186.com/hesaplama/ev-sarj-kablosu-uygunluk/'));
assert(html.includes('Şeffaf satış ortaklığı'));
assert(html.includes('Phoenix Contact'));
assert(html.includes('Volvo Support'));
assert(html.includes('28 Temmuz 2026'));
assert(!/amazon\.(com|com\.tr)/i.test(html));
const fields=[...html.matchAll(/<(?:input|select|textarea)\b[^>]*(?:id|name)="([^"]+)"/gi)].map(m=>m[1]);
assert(!fields.some(field=>/(^|[-_])(name|email|phone|telefon|address|adres|abonelik|tc|identity|plaka)([-_]|$)/i.test(field)));
assert(html.includes('aria-live="polite"'));
assert(html.includes('type="application/ld+json"'));
assert(html.includes('Satın almama sonucu'));
console.log('EV şarj kablosu uygunluk testleri başarılı.');