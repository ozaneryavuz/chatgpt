'use strict';
const assert=require('assert');
const fs=require('fs');
const path=require('path');
const core=require('./core.js');

const base={
  deviceType:'phone',deviceEnergyMode:'wh',deviceWh:18,deviceMah:'',deviceVoltage:'',targetCharges:2,deviceMinW:10,devicePreferredW:25,
  bankEnergyMode:'mah',bankWh:'',bankMah:20000,cellVoltage:3.7,transferEfficiency:70,singlePortW:25,totalOutputW:25,simultaneousDevices:1,cableW:60,ownership:'candidate',
  capacityLabelVerified:true,usbPdConfirmed:true,cableRated:true,sharedOutputConfirmed:true,manufacturerInstructionsChecked:true,damageFree:true,recallChecked:true,medicalDevice:false
};
const run=overrides=>core.analyze({...base,...overrides});

const phone=run({});
assert.equal(phone.status,'compatible');
assert.equal(phone.commercialAllowed,true);
assert(phone.estimatedCharges>2);
assert.equal(phone.bankStoredWh,74);
assert(phone.requiredStoredWh<phone.bankStoredWh);
assert(phone.negotiatedW===25);

const energy=core.energyWh('mah','',10000,3.7,'Test');
assert.equal(energy,37);

const ownedEnough=run({ownership:'owned'});
assert.equal(ownedEnough.noPurchaseNeeded,true);
assert.equal(ownedEnough.commercialAllowed,false);

const ownedInsufficient=run({ownership:'owned',bankMah:10000,targetCharges:3});
assert.equal(ownedInsufficient.status,'incompatible');
assert(ownedInsufficient.blockerCodes.includes('capacity'));
assert.equal(ownedInsufficient.commercialAllowed,true);

const laptopNoPd=run({deviceType:'laptop',deviceWh:60,targetCharges:1,deviceMinW:45,devicePreferredW:65,bankMah:27000,singlePortW:65,totalOutputW:65,cableW:100,usbPdConfirmed:false});
assert.equal(laptopNoPd.status,'incompatible');
assert(laptopNoPd.blockerCodes.includes('pd'));
assert.equal(laptopNoPd.commercialAllowed,false);

const shared=run({deviceType:'tablet',deviceWh:30,targetCharges:1,deviceMinW:18,devicePreferredW:30,singlePortW:30,totalOutputW:30,simultaneousDevices:2,sharedOutputConfirmed:false});
assert.equal(shared.status,'incompatible');
assert(shared.blockerCodes.includes('power'));
assert(shared.warnings.some(text=>text.includes('portlar arasında')));

const slow=run({deviceMinW:10,devicePreferredW:65,singlePortW:25,totalOutputW:25,cableW:60});
assert.equal(slow.status,'conditional');
assert(slow.warnings.some(text=>text.includes('daha yavaş')));

assert.equal(run({medicalDevice:true}).commercialAllowed,false);
assert(run({medicalDevice:true}).blockerCodes.includes('medical'));
assert(run({damageFree:false}).blockerCodes.includes('damage'));
assert(run({recallChecked:false}).blockerCodes.includes('recall'));
assert.equal(run({devicePreferredW:140,singlePortW:140,totalOutputW:140,cableW:240}).commercialAllowed,false);
assert(run({transferEfficiency:95}).warnings.some(text=>text.includes('iyimser')));
assert.throws(()=>run({deviceMinW:65,devicePreferredW:45}),/küçük olamaz/);
assert.throws(()=>run({bankMah:0}),/Powerbank kapasitesi/);

const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
assert(html.includes('https://www.alo186.com/hesaplama/powerbank-usb-c-uygunluk/'));
assert(/Amazon[^<]{0,100}satış ortaklığı/i.test(html));
assert(html.includes('USB-IF'));
assert(html.includes('FAA PackSafe'));
assert(html.includes('28 Temmuz 2026'));
assert(!/amazon\.(com|com\.tr)/i.test(html));
const formFieldIds=[...html.matchAll(/<(?:input|select|textarea)\b[^>]*(?:id|name)="([^"]+)"/gi)].map(match=>match[1]);
assert(!formFieldIds.some(field=>/(^|[-_])(name|email|phone|telefon|address|adres|abonelik|tc|identity)([-_]|$)/i.test(field)));
assert(html.includes('aria-live="polite"'));
assert(html.includes('type="application/ld+json"'));
assert(html.includes('Satın alma zorunlu sonuç değildir'));

const root=path.resolve(__dirname,'../..');
const routing=JSON.parse(fs.readFileSync(path.join(root,'deployment/routing-manifest.json'),'utf8'));
assert(routing.version>=14);
assert(routing.routes.some(route=>route.canonicalPath==='/hesaplama/powerbank-usb-c-uygunluk/'));
const sitemap=fs.readFileSync(path.join(root,'sitemap.xml'),'utf8');
assert(sitemap.includes('/hesaplama/powerbank-usb-c-uygunluk/'));
const center=fs.readFileSync(path.join(__dirname,'../index.html'),'utf8');
const toolCount=Number((center.match(/(\d+) çekirdek araç/)||[])[1]);
assert(toolCount>=21);
assert(center.includes('./powerbank-usb-c-uygunluk/'));

console.log('Powerbank ve USB-C uygunluk testleri başarılı.');