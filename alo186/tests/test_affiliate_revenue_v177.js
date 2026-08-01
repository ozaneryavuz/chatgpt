'use strict';

const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');

const root=path.resolve(__dirname,'..');
const hubRoot=path.join(root,'amazon-elektrik-urunleri','dogrulanmis-tak-calistir-urunler');
const catalog=require('../urun-eslestirme/catalog-battery-continuity-run75.js');
const engine=require('../amazon-elektrik-urunleri/dogrulanmis-tak-calistir-urunler/catalog-revenue-v177.js');
const opportunities=JSON.parse(fs.readFileSync(path.join(hubRoot,'opportunities-v177.json'),'utf8'));
const page=fs.readFileSync(path.join(hubRoot,'index.html'),'utf8');
const app=fs.readFileSync(path.join(hubRoot,'app-v177.js'),'utf8');
const parentApp=fs.readFileSync(path.join(root,'amazon-elektrik-urunleri','tasinabilir-enerji-sarj-urunleri','app-v175.js'),'utf8');

const now=new Date('2026-08-01T12:00:00Z');
const data=engine.build(catalog,opportunities,now);

assert.equal(engine.version,177);
assert.equal(data.affiliateTag,'alo186rehber-21');
assert.equal(data.verificationMaxAgeDays,45);
assert.ok(data.products.length>=12,`Güncel doğrulanmış model sayısı yetersiz: ${data.products.length}`);
assert.ok(data.productClasses.length>=30,`Ürün sınıfı sayısı yetersiz: ${data.productClasses.length}`);
assert.equal(data.bundles.length,7);
assert.equal(opportunities.productClasses.length,25);
assert.equal(data.stats.exactProducts,data.products.length);
assert.equal(data.stats.productClasses,data.productClasses.length);

const asins=new Set();
const ids=new Set();
const forbiddenDirectCategories=new Set(['surge_strip','mini_ups','emergency_light','smoke_alarm','co_alarm','power_station','generator','inverter','outlet_tester','smart_plug','ev_cable','ups_battery','extension_cord','portable_evse','rccb','rcbo','mcb','spd','wallbox']);
for(const product of data.products){
  assert.ok(product.id&&!ids.has(product.id),`Tekrarlanan ürün kimliği: ${product.id}`);
  ids.add(product.id);
  assert.ok(product.asin&&!asins.has(product.asin),`Tekrarlanan ASIN: ${product.asin}`);
  asins.add(product.asin);
  assert.ok(catalog.publicAffiliateEligible(catalog.products.find(item=>item.id===product.id),{now}),`Doğrudan ürün kapısı kapalı: ${product.id}`);
  assert.ok(!forbiddenDirectCategories.has(product.rawCategory),`Yüksek riskli kategori doğrudan açıldı: ${product.rawCategory}`);
  assert.match(product.amazonUrl,/^https:\/\/www\.amazon\.com\.tr\/dp\/[A-Z0-9]+\?tag=alo186rehber-21$/);
  assert.ok(product.evidence.length>=3,`Kanıt alanı yetersiz: ${product.id}`);
  assert.ok(product.noBuyWhen.length>=1,`Satın almama sınırı eksik: ${product.id}`);
}

const classIds=new Set();
for(const item of data.productClasses){
  assert.ok(item.id&&!classIds.has(item.id),`Tekrarlanan ürün sınıfı: ${item.id}`);
  classIds.add(item.id);
  assert.match(item.amazonUrl,/^https:\/\/www\.amazon\.com\.tr\/s\?k=.*[?&]tag=alo186rehber-21$/);
  assert.ok(item.tool&&item.tool.startsWith('/'),`Ücretsiz araç rotası eksik: ${item.id}`);
  assert.ok(Array.isArray(item.evidence)&&item.evidence.length>=1,`Sınıf kanıtı eksik: ${item.id}`);
  assert.ok(item.noBuyWhen,`Sınıf satın almama sınırı eksik: ${item.id}`);
}

const requiredManual=['qi2-manyetik-powerbank','gan-100-140w-pd31','usb-c-240w-epr','usb-c-hub-hdmi-ethernet','hdmi21-4k120','arac-65w-pd','toprakli-seyahat-adaptoru','nimh-bagimsiz-kanal','usb-c-guc-olcer'];
for(const id of requiredManual)assert.ok(classIds.has(id),`Yüksek niyetli ürün sınıfı eksik: ${id}`);
for(const bundle of data.bundles){
  assert.ok(bundle.id&&bundle.name&&bundle.description);
  assert.ok(bundle.categories.length>=1);
  assert.ok(bundle.categories.every(category=>engine.categoryLabels[category]),`Bilinmeyen paket kategorisi: ${bundle.id}`);
}

assert.match(page,/<link rel="canonical" href="https:\/\/alo186\.com\/amazon-elektrik-urunleri\/dogrulanmis-tak-calistir-urunler\/">/);
assert.match(page,/Bir Amazon Gelir Ortağı olarak/);
assert.ok(!/href=["']https?:\/\/(?:www\.)?(?:amazon\.com\.tr|amzn\.to)/i.test(page),'Kaynak HTML doğrudan Amazon bağlantısı taşımamalı.');
for(const id of ['gateExisting','gateTechnical','gateAffiliate','bundles','filters','exactProducts','productClasses','catalogSearch'])assert.match(page,new RegExp(`id=["']${id}["']`));
for(const script of ['catalog.js','catalog-knowledge-extension.js','catalog-sales-extension.js','catalog-car-charger-run54.js','catalog-battery-continuity-run75.js','catalog-revenue-v177.js','app-v177.js'])assert.ok(page.includes(script),`Script eksik: ${script}`);
assert.match(app,/rel=\"sponsored nofollow noopener\"/);
assert.match(app,/affiliate_revenue_v177_click/);
assert.match(app,/data-product-title/);
assert.match(app,/data-product-category/);
assert.match(app,/exactCommitReceiptAvailable|ItemList|DefinedTermSet/);
assert.match(parentApp,/dogrulanmis-tak-calistir-urunler/);
assert.match(parentApp,/25\+ ürün sınıfını/);

for(const forbidden of ['price','stock','rating','seller','warranty','aggregateRating','availability','priceCurrency']){
  assert.ok(!(forbidden in opportunities),`Yasak ticari kök alan: ${forbidden}`);
}

console.log(JSON.stringify({
  ok:true,
  version:data.version,
  exactProducts:data.products.length,
  productClasses:data.productClasses.length,
  bundles:data.bundles.length,
  directCategories:data.stats.directCategories,
  duplicateAsinGuard:true,
  highRiskDirectAffiliate:false,
  tripleGate:true,
  affiliateTag:data.affiliateTag
},null,2));
