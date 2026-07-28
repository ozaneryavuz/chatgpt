'use strict';
const assert=require('assert');
const {analyze}=require('./core.js');
const base={totalPower:350,peakPower:450,length:10,section:1.5,productType:'lead',reelState:'unwound',labelUnwoundA:16,labelWoundA:'',loadType:'electronics',environment:'indoor',outdoorRated:false,rcdProtection:'yes',earthRequirement:'class1',earthPresent:'yes',thermalCutout:'unknown',manufacturerVerified:true,daisyChain:false,permanentUse:false,damageOrHeat:false};
const run=overrides=>analyze({...base,...overrides});
{
  const result=run({});
  assert.strictEqual(result.status,'compatible');
  assert.strictEqual(result.commercialAllowed,true);
  assert(result.voltageDropPct<3);
}
{
  const result=run({productType:'reel',reelState:'wound',labelWoundA:5,totalPower:1800,peakPower:1800,thermalCutout:'yes',loadType:'resistive'});
  assert.strictEqual(result.status,'incompatible');
  assert(result.blockers.some(item=>item.includes('etiket sınırını aşıyor')));
  assert.strictEqual(result.commercialAllowed,false);
}
{
  assert.throws(()=>run({productType:'reel',reelState:'wound',labelWoundA:''}),/sarılı durum etiket akımı/);
}
{
  const result=run({damageOrHeat:true});
  assert.strictEqual(result.status,'incompatible');
  assert(result.blockers.some(item=>item.includes('kullanımdan çıkarın')));
}
{
  const result=run({daisyChain:true});
  assert.strictEqual(result.status,'incompatible');
  assert.strictEqual(result.commercialAllowed,false);
}
{
  const result=run({environment:'outdoor',outdoorRated:false,rcdProtection:'unknown'});
  assert.strictEqual(result.status,'incompatible');
  assert(result.blockers.some(item=>item.includes('Dış ortam')));
}
{
  const result=run({earthRequirement:'class1',earthPresent:'unknown'});
  assert.strictEqual(result.status,'incompatible');
}
{
  const result=run({length:100,section:.75,totalPower:2000,peakPower:2000,labelUnwoundA:16,loadType:'resistive'});
  assert.strictEqual(result.status,'incompatible');
  assert(result.voltageDropPct>5);
}
{
  const result=run({manufacturerVerified:false});
  assert.strictEqual(result.status,'conditional');
  assert.strictEqual(result.commercialAllowed,false);
}
{
  const result=run({permanentUse:true});
  assert.strictEqual(result.professionalRequired,true);
  assert.strictEqual(result.commercialAllowed,false);
}
{
  assert.throws(()=>run({peakPower:100}),/küçük olamaz/);
}
console.log('Uzatma kablosu uygunluk testleri geçti.');