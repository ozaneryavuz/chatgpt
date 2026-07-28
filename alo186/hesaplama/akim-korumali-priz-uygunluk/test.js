const assert=require('assert');
const fs=require('fs');
const path=require('path');
const core=require('./core.js');

const base={problemType:'transient',loadType:'electronics',ownership:'candidate',totalPowerW:650,powerFactor:.9,startupPowerW:900,dailyHours:6,requiredOutlets:5,requiredUsbPorts:0,neededCableM:1.2,candidateOutlets:6,candidateUsbPorts:0,candidateCurrentA:16,candidatePowerW:3500,candidateJoules:1050,candidateCableM:1.5,surgeClaimVerified:true,jouleVerified:true,currentPowerVerified:true,labelVerified:true,protectionIndicator:true,indicatorActive:true,autoShutoff:false,breakerOrFuse:true,manufacturerLoadApproved:true,groundedWallSocket:true,earthContinuityKnown:true,directWallConnection:true,damageFree:true,indoorDry:true,daisyChainPlanned:false,extensionPlanned:false};
const run=overrides=>core.analyze({...base,...overrides});

const compatible=run({});
assert.equal(compatible.status,'compatible');
assert.equal(compatible.commercialAllowed,true);
assert.equal(compatible.targetJoules,1000);
assert.equal(compatible.outletSpare,1);
assert.equal(compatible.noPurchaseNeeded,false);
assert(compatible.currentA>3&&compatible.currentA<4);

const owned=run({ownership:'owned'});
assert.equal(owned.noPurchaseNeeded,true);
assert.equal(owned.commercialAllowed,false);

const basic=run({loadType:'lighting',totalPowerW:100,powerFactor:1,startupPowerW:100,dailyHours:5,requiredOutlets:2,candidateJoules:540});
assert.equal(basic.targetJoules,400);
assert.equal(basic.status,'compatible');
assert.equal(basic.commercialAllowed,true);

const lowJoule=run({candidateJoules:282});
assert.equal(lowJoule.status,'conditional');
assert.equal(lowJoule.commercialAllowed,false);
assert(lowJoule.warnings.some(item=>item.includes('1.000 J')));

const unknownJoule=run({candidateJoules:'',jouleVerified:false});
assert.equal(unknownJoule.status,'conditional');
assert.equal(unknownJoule.commercialAllowed,false);

const plainStrip=run({surgeClaimVerified:false});
assert.equal(plainStrip.status,'conditional');
assert.equal(plainStrip.commercialAllowed,false);

const extraOutlets=run({problemType:'extra_outlets',candidateJoules:'',jouleVerified:false,surgeClaimVerified:false});
assert.equal(extraOutlets.targetJoules,0);
assert.equal(extraOutlets.status,'conditional');
assert.equal(extraOutlets.commercialAllowed,false);

for(const problemType of ['ongoing_voltage','neutral_fault','outage_backup']){
  const result=run({problemType});
  assert.equal(result.status,'incompatible');
  assert.equal(result.commercialAllowed,false);
  assert(result.blockerCodes.includes(problemType));
}

for(const loadType of ['medical','ev','fixed','heater']){
  const result=run({loadType});
  assert.equal(result.status,'incompatible');
  assert.equal(result.commercialAllowed,false);
  assert.equal(result.professionalRequired,true);
}

const motor=run({loadType:'motor_compressor',manufacturerLoadApproved:false});
assert(motor.blockerCodes.includes('motor'));
assert.equal(motor.commercialAllowed,false);

const daisy=run({daisyChainPlanned:true});
assert(daisy.blockerCodes.includes('daisy_chain'));
const extension=run({extensionPlanned:true});
assert(extension.blockerCodes.includes('extension'));
const noGround=run({groundedWallSocket:false});
assert(noGround.blockerCodes.includes('ground'));
const unknownEarth=run({earthContinuityKnown:false});
assert(unknownEarth.blockerCodes.includes('ground'));
const notDirect=run({directWallConnection:false});
assert(notDirect.blockerCodes.includes('direct_wall'));
const damaged=run({damageFree:false});
assert(damaged.blockerCodes.includes('damage'));

const overload=run({totalPowerW:3000,powerFactor:.8,startupPowerW:3500,dailyHours:1,candidateCurrentA:10,candidatePowerW:2300});
assert(overload.blockerCodes.includes('current_rating'));
assert(overload.blockerCodes.includes('power_rating'));
assert(overload.blockerCodes.includes('startup'));

const longRun=run({totalPowerW:3000,powerFactor:1,startupPowerW:3000,dailyHours:8,candidateCurrentA:16,candidatePowerW:3500});
assert(longRun.blockerCodes.includes('continuous_current')||longRun.blockerCodes.includes('continuous_power'));

const outletGap=run({requiredOutlets:8,candidateOutlets:6});
assert(outletGap.blockerCodes.includes('outlets'));
const cableGap=run({neededCableM:3,candidateCableM:1.5});
assert(cableGap.blockerCodes.includes('cable'));
const indicatorOff=run({ownership:'owned',indicatorActive:false});
assert(indicatorOff.blockerCodes.includes('indicator_off'));
assert.equal(indicatorOff.noPurchaseNeeded,false);

const usbGap=run({requiredUsbPorts:2,candidateUsbPorts:0});
assert.equal(usbGap.status,'conditional');
assert.equal(usbGap.commercialAllowed,false);

const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
assert(html.includes('https://www.alo186.com/hesaplama/akim-korumali-priz-uygunluk/'));
assert(html.includes('Şeffaf satış ortaklığı'));
assert(html.includes('/akilli-urun-secimi?kategori=surge_strip'));
assert(html.includes('Satın almama sonucu'));
assert(html.includes('ALO186 EDAŞ, kamu kurumu'));
assert(html.includes('Eaton'));
assert(html.includes('APC'));
assert(html.includes('28 Temmuz 2026'));
assert(html.includes('aria-live="polite"'));
assert(html.includes('type="application/ld+json"'));
assert(!/amazon\.(com|com\.tr)\//i.test(html));
const fields=[...html.matchAll(/<(?:input|select|textarea)\b[^>]*(?:id|name)="([^"]+)"/gi)].map(match=>match[1]);
assert(!fields.some(field=>/(^|[-_])(name|email|phone|telefon|address|adres|abonelik|tc|identity|plaka|serial|seri|freeText)([-_]|$)/i.test(field)));
assert(!/fiyatı\s+\d|stokta|puanı\s+\d|garanti\s+\d/i.test(html));

console.log('Akım korumalı grup priz uygunluk: hesap, güvenlik, satın almama, gizlilik ve affiliate kapıları başarılı.');
