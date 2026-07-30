'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const repoRoot=path.resolve(__dirname,'../..');
const catalog=require(path.join(repoRoot,'alo186/urun-eslestirme/catalog-trust-growth-run54.js'));
const ui=require(path.join(repoRoot,'alo186/hesaplama/usb-c-set-kisa-listesi/trust-growth-run54.js'));

const now=new Date('2026-07-30T06:15:00.000Z');
const graph=catalog.knowledgeGraph({now});
const graphText=JSON.stringify(graph);
const audit=catalog.canonicalAudit({now});
const ugreenNode=(graph['@graph']||[]).find((node)=>node&&node['@type']==='Product'&&node.sku==='ugreen-nexode-140w-90322');

assert.equal(catalog.__trustGrowthRun54,true);
assert.equal(catalog.canonicalOrigin,'https://alo186.com');
assert.ok(catalog.products.some((product)=>product.id==='ugreen-nexode-140w-90322'&&product.asin==='B0B127GW4D'));
assert.ok(ugreenNode,'Run53 ürünü normalize edilmiş Product grafiğinde korunmalı.');
assert.equal(audit.legacyOriginFound,false);
assert.equal(audit.forbiddenCommerceNodeFound,false);
assert.equal(audit.forbiddenCommercialFieldFound,false);
assert.ok(audit.productCount>=20,'Taze ve doğrulanmış Product düğümleri korunmalı.');
assert.doesNotMatch(graphText,/https:\/\/www\.alo186\.com/);
assert.doesNotMatch(graphText,/"@type":"(?:Offer|AggregateOffer)"/);
assert.doesNotMatch(graphText,/"(?:offers|aggregateRating|review)"\s*:/);
assert.match(graphText,/https:\/\/alo186\.com\/akilli-urun-secimi/);

const fields={
  useCase:{value:'desk',options:[{value:'phone'},{value:'desk'}]},
  requiredW:{value:'100',options:[{value:'65'},{value:'100'}]},
  cableRole:{value:'high_speed',options:[{value:'charge'},{value:'high_speed'}]},
  needPortable:{checked:false},needMultiPortCharging:{checked:true},needHub:{checked:true},needDisplay:{checked:true},
  needHubEthernet:{checked:true},needHubCardReader:{checked:false},needHub4k60:{checked:true},needHub10Gbps:{checked:true}
};
const fakeDocument={getElementById:(id)=>fields[id]||null};
const data=new Map();
const storage={
  getItem:(key)=>data.has(key)?data.get(key):null,
  setItem:(key,value)=>data.set(key,String(value)),
  removeItem:(key)=>data.delete(key)
};
const profile=ui.saveProfile(storage,fakeDocument,now);
assert.equal(profile.expiresAt,'2026-08-29T06:15:00.000Z');
assert.deepEqual(Object.keys(profile.values).sort(),['cableRole','requiredW','useCase']);
assert.equal(profile.flags.needHub,true);
assert.equal(Object.prototype.hasOwnProperty.call(profile.values,'devicePowerKnown'),false);
assert.equal(Object.prototype.hasOwnProperty.call(profile.flags,'hazard'),false);
assert.equal(Object.prototype.hasOwnProperty.call(profile.flags,'existing-usb_c_charger'),false);
assert.deepEqual(ui.loadProfile(storage,new Date('2026-08-28T06:15:00.000Z')),profile);
assert.equal(ui.loadProfile(storage,new Date('2026-08-30T06:15:00.000Z')),null);
assert.equal(data.has(ui.PROFILE_KEY),false,'Süresi dolan profil storage içinden kalıcı silinmeli.');

const loader=fs.readFileSync(path.join(repoRoot,'alo186/hesaplama/usb-c-set-kisa-listesi/catalog-loader.js'),'utf8');
const app=fs.readFileSync(path.join(repoRoot,'alo186/hesaplama/usb-c-set-kisa-listesi/app.js'),'utf8');
const runtime=fs.readFileSync(path.join(repoRoot,'alo186/hesaplama/usb-c-set-kisa-listesi/trust-growth-run54.js'),'utf8');
const report=fs.readFileSync(path.join(repoRoot,'alo186/deployment/daily_affiliate_growth_report.js'),'utf8');

assert.ok(loader.indexOf('catalog-qualified-commerce-run53.js')<loader.indexOf('catalog-trust-growth-run54.js'));
assert.match(loader,/trust-growth-run54\.js/);
assert.match(app,/rel="sponsored nofollow noopener"/);
assert.match(app,/Mevcut şarj zinciri ihtiyacı karşılıyor\. Yeni ürün satın almak gerekli değildir/);
assert.match(app,/Ticari rota kapalıdır/);
assert.match(runtime,/Minimum yeterli başlangıç/);
assert.match(runtime,/fiyatına veya komisyonuna göre değil/);
assert.match(runtime,/Kanıt kutuları, tehlike durumu ve mevcut ürün yeterliliği özellikle geri yüklenmedi/);
assert.doesNotMatch(runtime,/email|telefon|adres|konum|abonelik/i);
assert.match(report,/catalog-trust-growth-run54\.js/);
assert.match(report,/manufacturer_verified_search/);
assert.match(report,/exactAsinRequiredForDirectProduct/);

console.log(JSON.stringify({
  ok:true,
  productCount:audit.productCount,
  canonicalOrigin:audit.canonicalOrigin,
  profileFields:Object.keys(profile.values),
  profileFlags:Object.keys(profile.flags)
},null,2));
