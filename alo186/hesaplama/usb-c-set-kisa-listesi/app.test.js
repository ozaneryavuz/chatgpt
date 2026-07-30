'use strict';
const assert=require('node:assert/strict');
const tool=require('./app.js');
const catalog=require('../../urun-eslestirme/catalog-qualified-commerce-run53.js');
const now=new Date('2026-07-30T09:00:00Z');

const base={
  useCase:'travel',requiredW:45,cableRole:'charge_sync',needPortable:true,needMultiPortCharging:false,
  needHub:false,needDisplay:false,needHubEthernet:false,needHubCardReader:false,needHub4k60:false,needHub10Gbps:false,
  devicePowerKnown:true,hostDataKnown:true,hostVideoKnown:true,hazard:false,
  existing:{usb_c_charger:false,usb_c_cable:false,powerbank:false,usb_c_hub:false,display_cable:false}
};

assert.deepEqual(tool.requiredCategories(base),['usb_c_charger','usb_c_cable','powerbank']);
let result=tool.evaluate(base,now);
assert.equal(result.status,'qualified');
assert.deepEqual(result.missing,['usb_c_charger','usb_c_cable','powerbank']);
for(const category of result.missing){
  assert.ok(Array.isArray(result.products[category]));
  for(const product of result.products[category]){
    assert.equal(product.status,'verified_listing');
    assert.equal(catalog.publicAffiliateEligible(product,{now}),true);
    assert.match(product.url,/amazon\.com\.tr\/dp\//);
    assert.match(product.url,/[?&]tag=alo186rehber-21/);
    assert.ok(tool.productPower(product)>=45);
  }
}
assert.ok(result.products.usb_c_cable.length>=1);
assert.ok(result.products.powerbank.length>=1);

const charger140=tool.eligibleProducts('usb_c_charger',{...base,requiredW:140,needMultiPortCharging:true},now);
assert.deepEqual(charger140.map((product)=>product.id),['ugreen-nexode-140w-90322']);
assert.equal(tool.productPower(charger140[0]),140);
assert.equal(tool.totalPorts(charger140[0]),3);
assert.equal(charger140[0].asin,'B0B127GW4D');
assert.equal(charger140[0].mpn,'90322');
assert.match(charger140[0].url,/B0B127GW4D/);

const multiPort65=tool.eligibleProducts('usb_c_charger',{...base,requiredW:65,needMultiPortCharging:true},now);
assert.ok(multiPort65.some((product)=>product.id==='samsung-ep-t6530-trio-65w'));
assert.ok(multiPort65.some((product)=>product.id==='ugreen-nexode-140w-90322'));
assert.ok(!multiPort65.some((product)=>product.id==='anker-313-a2677'),'Tek portlu adaptör çoklu port ihtiyacına sızmamalı.');

const desk={...base,useCase:'desk',needPortable:false,needHub:true,needDisplay:false,requiredW:65,needHubEthernet:true,needHubCardReader:true,needHub4k60:true};
result=tool.evaluate(desk,now);
assert.equal(result.status,'qualified');
assert.ok(result.products.usb_c_hub.length>=1);
assert.equal(result.products.usb_c_hub[0].id,'ugreen-7in1-60515','10 Gbps gerekmiyorsa daha sade uygun hub önce gelmeli.');

const tenGbHub=tool.eligibleProducts('usb_c_hub',{...desk,needHub10Gbps:true},now);
assert.deepEqual(tenGbHub.map((product)=>product.id),['anker-555-8in1']);
assert.equal(tool.dataGbps(tenGbHub[0]),10);

result=tool.evaluate({...base,cableRole:'high_speed',hostDataKnown:false},now);
assert.equal(result.status,'evidence_required');
assert.match(result.message,/veri standardı/);
result=tool.evaluate({...base,cableRole:'high_speed',hostDataKnown:true},now);
assert.equal(result.status,'qualified');
assert.deepEqual(result.products.usb_c_cable,[],'Yalnız şarj/USB2 kabloları 10 Gbps ihtiyacına gösterilmemeli.');
assert.match(tool.featureGapMessage('usb_c_cable',{cableRole:'high_speed'}),/10 Gbps/);

result=tool.evaluate({...base,existing:{usb_c_charger:true,usb_c_cable:true,powerbank:true,usb_c_hub:false,display_cable:false}},now);
assert.equal(result.status,'no_buy');
assert.match(result.message,/satın almak gerekli değildir/i);

result=tool.evaluate({...base,devicePowerKnown:false},now);
assert.equal(result.status,'evidence_required');
assert.equal(Object.keys(result.products).length,0);

result=tool.evaluate({...base,useCase:'desk',needDisplay:true,hostVideoKnown:false},now);
assert.equal(result.status,'evidence_required');
assert.match(result.message,/DisplayPort Alt Mode|Thunderbolt/);

result=tool.evaluate({...base,hazard:true},now);
assert.equal(result.status,'hazard');
assert.equal(result.missing.length,0);

class MemoryStorage{
  constructor(){this.map=new Map();}
  getItem(key){return this.map.has(key)?this.map.get(key):null;}
  setItem(key,value){this.map.set(key,String(value));}
  removeItem(key){this.map.delete(key);}
}
const storage=new MemoryStorage();
const ids=catalog.products.filter((product)=>product.status==='verified_listing').slice(0,8).map((product)=>product.id);
const stored=tool.saveShortlist(storage,ids,now);
assert.equal(stored.ids.length,tool.LIMIT);
assert.equal(tool.loadShortlist(storage,new Date('2026-08-15T09:00:00Z')).ids.length,tool.LIMIT);
assert.equal(tool.loadShortlist(storage,new Date('2026-09-01T09:00:00Z')),null);
const fresh=tool.saveShortlist(storage,ids.slice(0,2),now);
const ics=tool.createIcs(fresh,now);
assert.match(ics,/BEGIN:VCALENDAR/);
assert.match(ics,/DTSTART;VALUE=DATE:20260829/);
assert.match(ics,/Mevcut sistem yeterliyse yeni ürün almayın/);
assert.doesNotMatch(ics,/mailto:|ATTENDEE|ORGANIZER/);

console.log(JSON.stringify({
  ok:true,
  actions:['140W PD 3.1 charger','feature-qualified hub','charging-vs-high-speed cable gate'],
  charger140:charger140.map((product)=>product.id),
  hub10Gbps:tenGbHub.map((product)=>product.id),
  shortlistLimit:tool.LIMIT,
  ttlDays:tool.TTL_MS/86400000
},null,2));
