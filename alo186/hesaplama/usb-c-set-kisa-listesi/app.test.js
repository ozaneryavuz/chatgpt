'use strict';
const assert=require('node:assert/strict');
const tool=require('./app.js');
const catalog=require('../../urun-eslestirme/catalog-sales-extension.js');
const now=new Date('2026-07-30T09:00:00Z');

const base={useCase:'travel',requiredW:45,needPortable:true,needHub:false,needDisplay:false,devicePowerKnown:true,hostDataKnown:true,hostVideoKnown:true,hazard:false,existing:{usb_c_charger:false,usb_c_cable:false,powerbank:false,usb_c_hub:false,display_cable:false}};

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

console.log(JSON.stringify({ok:true,categories:tool.requiredCategories(base),directMatches:Object.fromEntries(Object.entries(tool.evaluate(base,now).products).map(([key,value])=>[key,value.length])),shortlistLimit:tool.LIMIT,ttlDays:tool.TTL_MS/86400000},null,2));