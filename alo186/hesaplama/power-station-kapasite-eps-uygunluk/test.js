'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {analyze,nextCapacity}=require('./core.js');

const base={loadType:'electronics',ownership:'candidate',continuousPowerW:180,surgePowerW:320,targetHours:4,capacityWh:1000,acContinuousW:1200,acSurgeW:1600,efficiency:.85,reservePct:15,transferRequired:true,requiredTransferMs:25,transferMs:20,bypassPowerW:1200,epsSupported:true,pureSine:true,acTimeoutDisable:true,labelVerified:true,manufacturerLoadApproved:true,damageFree:true,indoorDryVentilated:true,directConnection:true,needsEarth:true,earthVerified:true,unattendedUse:false};
const run=patch=>analyze({...base,...patch});

const compatible=run({});
assert.equal(compatible.status,'compatible');
assert.equal(compatible.commercialAllowed,true);
assert.equal(compatible.noPurchaseNeeded,false);
assert.equal(compatible.recommendedCapacityWh,1000);
assert.ok(compatible.estimatedRuntimeHours>=4);

const owned=run({ownership:'owned'});
assert.equal(owned.status,'compatible');
assert.equal(owned.noPurchaseNeeded,true);
assert.equal(owned.commercialAllowed,false);

const shortRuntime=run({capacityWh:500});
assert.equal(shortRuntime.status,'incompatible');
assert.ok(shortRuntime.blockerCodes.includes('runtime_short'));

const server=run({loadType:'server',requiredTransferMs:0,transferMs:20});
assert.equal(server.professionalRequired,true);
assert.ok(server.blockerCodes.includes('server'));
assert.ok(server.blockerCodes.includes('transfer_slow'));

const noEps=run({epsSupported:false});
assert.ok(noEps.blockerCodes.includes('eps_missing'));

const slowTransfer=run({requiredTransferMs:20,transferMs:30});
assert.ok(slowTransfer.blockerCodes.includes('transfer_slow'));

const bypass=run({bypassPowerW:100});
assert.ok(bypass.blockerCodes.includes('bypass_power'));

const fridgeBlocked=run({loadType:'fridge',continuousPowerW:150,surgePowerW:900,targetHours:8,capacityWh:2000,acContinuousW:1800,acSurgeW:2700,requiredTransferMs:100,transferMs:30,bypassPowerW:1800,acTimeoutDisable:false});
assert.ok(fridgeBlocked.blockerCodes.includes('ac_timeout'));

const fridgeCompatible=run({loadType:'fridge',continuousPowerW:150,surgePowerW:900,targetHours:8,capacityWh:2000,acContinuousW:1800,acSurgeW:2700,requiredTransferMs:100,transferMs:30,bypassPowerW:1800,acTimeoutDisable:true});
assert.equal(fridgeCompatible.status,'compatible');
assert.equal(fridgeCompatible.commercialAllowed,true);

assert.ok(run({continuousPowerW:1300,surgePowerW:1400}).blockerCodes.includes('continuous_power'));
assert.ok(run({surgePowerW:2000}).blockerCodes.includes('surge_power'));
assert.ok(run({pureSine:false}).blockerCodes.includes('waveform'));
assert.ok(run({loadType:'medical'}).blockerCodes.includes('medical'));
assert.ok(run({loadType:'fixed'}).blockerCodes.includes('fixed'));
assert.ok(run({loadType:'ev'}).blockerCodes.includes('ev'));
assert.ok(run({directConnection:false}).blockerCodes.includes('connection'));
assert.ok(run({needsEarth:true,earthVerified:false}).blockerCodes.includes('earth'));
assert.ok(run({loadType:'resistive',unattendedUse:true,pureSine:false}).blockerCodes.includes('unattended_heat'));
assert.throws(()=>run({surgePowerW:100}),/küçük olamaz/);
assert.equal(nextCapacity(1001),1500);
assert.equal(nextCapacity(10001),null);

const repoRoot=path.resolve(__dirname,'../../..');
const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
const center=fs.readFileSync(path.join(__dirname,'..','index.html'),'utf8');
const manifest=fs.readFileSync(path.join(repoRoot,'alo186/deployment/routing-manifest.json'),'utf8');
const sitemap=fs.readFileSync(path.join(repoRoot,'alo186/sitemap.xml'),'utf8');
const catalog=fs.readFileSync(path.join(repoRoot,'alo186/urun-eslestirme/catalog.js'),'utf8');

assert.match(html,/https:\/\/www\.alo186\.com\/hesaplama\/power-station-kapasite-eps-uygunluk\//);
assert.match(html,/WebApplication/);
assert.match(html,/FAQPage/);
assert.match(html,/Reklam \/ satış ortaklığı açıklaması/);
assert.match(html,/Kişisel veri yok/);
assert.match(html,/Satın almama sonucu/);
assert.match(html,/href="\/akilli-urun-secimi\?kategori=power_station"/);
assert.doesNotMatch(html,/amazon\.(com\.tr|com)\//i);
assert.doesNotMatch(html,/type="(?:email|tel|text)"/i);
assert.doesNotMatch(html,/name="(?:address|phone|email|subscription|plate|serial|note)"/i);
assert.match(center,/[3-9][0-9]* çekirdek araç/);
assert.match(center,/\.\/power-station-kapasite-eps-uygunluk\//);
assert.match(manifest,/alo186\/hesaplama\/power-station-kapasite-eps-uygunluk\/index\.html/);
assert.match(sitemap,/https:\/\/alo186\.com\/hesaplama\/power-station-kapasite-eps-uygunluk\//);
assert.match(catalog,/nextStepUrl:'https:\/\/www\.alo186\.com\/hesaplama\/power-station-kapasite-eps-uygunluk\/'/);

console.log('Power station kapasite/EPS uygunluğu: hesap, no-buy, güvenlik, gizlilik, affiliate ve entegrasyon testleri başarılı.');
