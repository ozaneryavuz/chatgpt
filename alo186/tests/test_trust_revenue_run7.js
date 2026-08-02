'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
const read=relative=>fs.readFileSync(path.join(root,relative),'utf8');
const catalogHtml=read('katalog-guven-durumu/index.html');
const catalogApp=read('katalog-guven-durumu/app.js');
const corporateHtml=read('kurumsal-on-degerlendirme/index.html');
const corporateApp=read('kurumsal-on-degerlendirme/app.js');
const supplierHtml=read('tedarikci-isbirligi/index.html');
const supplierApp=read('tedarikci-isbirligi/app.js');
const routing=JSON.parse(read('deployment/routing-manifest.json'));
const sitemap=read('sitemap.xml');
const productCatalog=require(path.join(root,'urun-eslestirme','catalog.js'));
const corporateCore=require(path.join(root,'kurumsal-on-degerlendirme','core.js'));
const supplierCore=require(path.join(root,'tedarikci-isbirligi','core.js'));

assert.match(catalogHtml,/rel="canonical" href="https:\/\/www\.alo186\.com\/katalog-guven-durumu"/);
assert.match(catalogHtml,/Katalog Güven Durumu/);
assert.match(catalogHtml,/Reklam \/ satış ortaklığı açıklaması/);
assert.match(catalogHtml,/45 günlük doğrulama sınırı/);
assert.match(catalogHtml,/\/akilli-urun-secimi\/catalog\.js/);
assert.match(catalogApp,/catalog_trust_status_viewed/);
assert.match(catalogApp,/catalog_trust_category_opened/);
assert.doesNotMatch(catalogHtml,/amazon\.(com|com\.tr)\//i);
assert.doesNotMatch(catalogHtml,/"@type"\s*:\s*"Product"/);
assert(productCatalog.categories.length>=14,`Kategori envanteri geriledi: ${productCatalog.categories.length}`);
assert(productCatalog.products.length>=10,`Doğrulanmış ASIN envanteri geriledi: ${productCatalog.products.length}`);
assert.equal(productCatalog.verificationMaxAgeDays,45);
for(const id of ['smart_plug','ev_cable','ups_battery']){
  const category=productCatalog.getCategory(id);
  assert(category&&category.affiliatePolicy==='after_tool');
  assert.equal(productCatalog.productsFor(id).length,0);
}

const corporateReady=corporateCore.assess({facility:'hotel',problem:'backup',backup:'both',scope:'site',urgency:'urgent',evidence:'ready'});
const corporatePrepare=corporateCore.assess({facility:'office',problem:'outage',backup:'none',scope:'remote',urgency:'planning',evidence:'none'});
assert(corporateReady.score>=80);
assert.equal(corporateReady.band,'ready');
assert(corporatePrepare.score<corporateReady.score);
assert(corporateReady.docs.some(item=>/kritik yük/i.test(item)));
assert.match(corporateHtml,/Hazırlık skorunu ve talep özetini oluştur/);
assert.match(corporateHtml,/Kapsam özetini kopyala/);
assert.match(corporateApp,/paid_assessment_readiness_scored/);
assert.doesNotMatch(corporateHtml,/type="(?:email|tel|text|file)"/i);
assert.doesNotMatch(corporateHtml,/amazon\.(com|com\.tr)\//i);

const allSupplierDocs=supplierCore.documents.map(item=>item.id);
const supplierReady=supplierCore.assess({category:'ups',type:'data',readiness:'complete',goal:'accuracy',documents:allSupplierDocs});
const supplierPrepare=supplierCore.assess({category:'ev',type:'sponsored',readiness:'unknown',goal:'visibility',documents:[]});
assert.equal(supplierReady.score,100);
assert.equal(supplierReady.band,'ready');
assert(supplierPrepare.score<supplierReady.score);
assert.equal(supplierPrepare.missing.length,supplierCore.documents.length);
assert.match(supplierHtml,/Teknik hazırlık skorunu ve talebi oluştur/);
assert.match(supplierHtml,/Ödeme; organik teknik sıralamayı/);
assert.match(supplierApp,/supplier_data_readiness_scored/);
assert.doesNotMatch(supplierHtml,/type="(?:email|tel|text|file)"/i);
assert.doesNotMatch(supplierHtml,/amazon\.(com|com\.tr)\//i);

for(const[name,text]of[['catalog',catalogHtml],['corporate',corporateHtml],['supplier',supplierHtml]]){
  assert.doesNotMatch(text,/stokta|kargo|teslimat süresi|satıcı puanı|garanti süresi\s*:\s*\d/i,`${name}: unverified commercial claim found`);
  assert.match(text,/Bağımsız|bağımsız/i,`${name}: independence wording missing`);
}
assert(routing.routes.some(route=>route.source==='alo186/katalog-guven-durumu/index.html'&&route.canonicalPath==='/katalog-guven-durumu'&&route.type==='collection'));
assert.match(sitemap,/https:\/\/alo186\.com\/katalog-guven-durumu/);
console.log(`ALO186 güvenli büyüme: ${productCatalog.categories.length} kategorilik katalog güveni, ${productCatalog.products.length} doğrulanmış ASIN, kurumsal lead ve tedarikçi hazırlığı başarılı.`);
