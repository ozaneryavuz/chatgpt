'use strict';

const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {analyze}=require('./core.js');

const base={
  useCase:'home_room',ownership:'candidate',areaM2:20,targetLux:20,lumensPerUnit:300,units:3,placement:'average',targetHours:6,declaredRuntimeHours:8,
  lumensVerified:true,runtimeVerified:true,physicalSwitch:true,chargeIndicator:true,handsFreeMount:true,autoOnRequired:false,autoOnSupported:false,weatherRated:false,damageFree:true,drySafeEnvironment:true,candlesPlanned:false
};

const compatible=analyze(base);
assert.equal(compatible.status,'compatible');
assert.equal(compatible.commercialAllowed,true);
assert.equal(compatible.requiredUnits,3);
assert.equal(compatible.approximateLux,20.3);

const owned=analyze({...base,ownership:'owned'});
assert.equal(owned.noPurchaseNeeded,true);
assert.equal(owned.commercialAllowed,false);

const tooDark=analyze({...base,units:1});
assert.equal(tooDark.status,'incompatible');
assert.ok(tooDark.blockerCodes.includes('illumination'));

const tooShort=analyze({...base,declaredRuntimeHours:4});
assert.ok(tooShort.blockerCodes.includes('runtime'));
assert.equal(tooShort.commercialAllowed,false);

const workplace=analyze({...base,useCase:'workplace_exit'});
assert.equal(workplace.status,'professional');
assert.equal(workplace.professionalRequired,true);
assert.equal(workplace.commercialAllowed,false);

const outdoor=analyze({...base,useCase:'outdoor',weatherRated:false});
assert.ok(outdoor.blockerCodes.includes('weather'));

const autoOn=analyze({...base,autoOnRequired:true,autoOnSupported:false});
assert.ok(autoOn.blockerCodes.includes('auto_on'));

const damaged=analyze({...base,damageFree:false});
assert.ok(damaged.blockerCodes.includes('damage'));

const candles=analyze({...base,candlesPlanned:true});
assert.ok(candles.blockerCodes.includes('candles'));

const unverified=analyze({...base,lumensVerified:false,runtimeVerified:false});
assert.equal(unverified.status,'conditional');
assert.equal(unverified.commercialAllowed,false);

assert.throws(()=>analyze({...base,areaM2:0}),/Alan/);
assert.throws(()=>analyze({...base,targetHours:100}),/Hedef süre/);

const repoRoot=path.resolve(__dirname,'../../..');
const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
const manifest=fs.readFileSync(path.join(repoRoot,'alo186','deployment','routing-manifest.json'),'utf8');
const sitemap=fs.readFileSync(path.join(repoRoot,'alo186','sitemap.xml'),'utf8');
const catalog=require(path.join(repoRoot,'alo186','urun-eslestirme','catalog.js'));

assert.match(html,/https:\/\/www\.alo186\.com\/hesaplama\/acil-aydinlatma-sure-uygunluk\//);
assert.match(html,/Satış ortaklığı açıklaması/);
assert.match(html,/Kişisel veri yok/);
assert.match(html,/İşyeri kaçış yolu/);
assert.match(html,/mum yerine/i);
assert.doesNotMatch(html,/amazon\.(com|com\.tr)\//i);
assert.doesNotMatch(html,/type="(?:email|tel|text)"/i);
assert.match(manifest,/alo186\/hesaplama\/acil-aydinlatma-sure-uygunluk\/index\.html/);
assert.match(sitemap,/https:\/\/alo186\.com\/hesaplama\/acil-aydinlatma-sure-uygunluk\//);
assert.equal(catalog.getCategory('emergency_light').affiliatePolicy,'after_tool');
assert.match(catalog.getCategory('emergency_light').nextStepUrl,/acil-aydinlatma-sure-uygunluk/);

console.log('Acil aydınlatma uygunluğu: hesap, süre, güvenlik, satın almama, affiliate ve yayın entegrasyonu testleri başarılı.');
