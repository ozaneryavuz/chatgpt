'use strict';

const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const catalog=require('../urun-eslestirme/catalog-battery-continuity-run75.js');

const root=path.resolve(__dirname,'..');
const indexHtml=fs.readFileSync(path.join(root,'urun-eslestirme','index.html'),'utf8');
const appJs=fs.readFileSync(path.join(root,'urun-eslestirme','app.js'),'utf8');
const extensionJs=fs.readFileSync(path.join(root,'urun-eslestirme','catalog-battery-continuity-run75.js'),'utf8');

assert.equal(catalog.affiliateTag,'alo186rehber-21');
assert.equal(catalog.verificationMaxAgeDays,45);
assert.ok(catalog.__batteryContinuityAffiliateRun75,'Önceki NiMH katalog sözleşmesi kayboldu.');
assert.ok(catalog.__wiredNetworkAffiliateRun76,'Kablolu ağ affiliate uzantısı yüklenmedi.');
assert.ok(!extensionJs.includes('amazonSearchUrl('),'Doğrudan ürün kaydında genel Amazon araması kullanılamaz.');

const categoryId='usb_gigabit_ethernet_adapter';
const needId='stable-wired-network-access';
const expected=[
  ['tp-link-ue300-usb-gigabit','B00V4BGDKU','UE300','TP-Link'],
  ['tp-link-ue300c-usbc-gigabit','B08FYB5HHK','UE300C','TP-Link'],
  ['tp-link-ue330-usb-hub-gigabit','B01M6C9DPK','UE330','TP-Link']
];

const category=catalog.getCategory(categoryId);
assert.ok(category,'USB Gigabit Ethernet kategorisi eksik.');
assert.equal(category.mode,'direct');
assert.equal(category.risk,'consumer');
assert.equal(category.affiliatePolicy,'verified_direct');
assert.notEqual(category.affiliatePolicy,'after_tool');
assert.notEqual(category.affiliatePolicy,'professional_only');
assert.deepEqual(catalog.categoryNeeds[categoryId],[needId]);
assert.ok(catalog.categoryRelations[categoryId].tools.length>0);
assert.ok(catalog.categoryRelations[categoryId].guides.length>0);
assert.ok(catalog.categoryRelations[categoryId].evidence.length>=5);

const ids=new Set();
const asins=new Set();
for(const product of catalog.products){
  assert.ok(product.id&&!ids.has(product.id),`Tekrarlanan ürün kimliği: ${product.id}`);
  ids.add(product.id);
  if(product.asin){
    assert.ok(!asins.has(product.asin),`Tekrarlanan ASIN: ${product.asin}`);
    asins.add(product.asin);
  }
}

const now=new Date('2026-08-01T06:30:00Z');
const staleNow=new Date('2026-09-20T06:30:00Z');
const forbidden=['price','stock','seller','rating','aggregateRating','review','reviews','warranty','offers','availability','priceCurrency'];

function assertForbiddenFieldsAbsent(value,context){
  if(!value||typeof value!=='object')return;
  for(const key of forbidden)assert.ok(!(key in value),`Yasak alan ${key}: ${context}`);
  for(const [key,nested] of Object.entries(value)){
    if(nested&&typeof nested==='object')assertForbiddenFieldsAbsent(nested,`${context}.${key}`);
  }
}

for(const [id,asin,mpn,brand] of expected){
  const product=catalog.products.find((item)=>item.id===id);
  assert.ok(product,`Ürün eksik: ${id}`);
  assert.equal(product.category,categoryId);
  assert.equal(product.asin,asin);
  assert.equal(product.mpn,mpn);
  assert.equal(product.brand,brand);
  assert.equal(product.status,'verified_listing');
  assert.equal(product.verifiedAt,'2026-08-01');
  assert.equal(product.url,`https://www.amazon.com.tr/dp/${asin}?tag=alo186rehber-21`);
  assert.match(product.technicalSource,/^https:\/\/www\.tp-link\.com\//);
  assert.match(product.listingSource,/^https:\/\//);
  assert.ok(product.needIds.includes(needId));
  assert.ok(product.relatedTools.length>0&&product.relatedGuides.length>0);
  assert.ok(product.requiredEvidence.length>=5);
  assert.ok(Object.keys(product.attributes).length>=7,`Teknik özellik alanı yetersiz: ${id}`);
  assert.ok(product.strengths.some((item)=>item.startsWith('Kullanıcı ihtiyacı:')),`Kullanıcı ihtiyacı eksik: ${id}`);
  assert.ok(product.strengths.length>=4,`Güçlü yönler eksik: ${id}`);
  assert.ok(product.strengths.some((item)=>item.startsWith('Satış ortaklığı açıklaması:')),`Satış ortaklığı açıklaması eksik: ${id}`);
  assert.ok(product.limits.length>=4,`Sınırlamalar eksik: ${id}`);
  assert.ok(product.limits.some((item)=>item.startsWith('Satın almama koşulu:')),`Satın almama koşulu eksik: ${id}`);
  assert.ok(catalog.publicAffiliateEligible(product,{now}),`Güncel doğrudan ürün kapalı: ${id}`);
  assert.ok(!catalog.publicAffiliateEligible(product,{now:staleNow}),`Eski ürün fail-closed olmadı: ${id}`);
  assertForbiddenFieldsAbsent(product,id);
}

const graph=catalog.knowledgeGraph({now})['@graph'];
const productNodes=graph.filter((node)=>node['@type']==='Product'&&expected.some(([id])=>id===node.sku));
assert.equal(productNodes.length,3);
for(const node of productNodes){
  const expectedItem=expected.find(([id])=>id===node.sku);
  assert.ok(node.identifier.some((item)=>item.propertyID==='ASIN'&&item.value===expectedItem[1]));
  assert.ok(node.identifier.some((item)=>item.propertyID==='MPN'&&item.value===expectedItem[2]));
  assert.equal(node.mpn,expectedItem[2]);
  assert.equal(node.sameAs,`https://www.amazon.com.tr/dp/${expectedItem[1]}?tag=alo186rehber-21`);
  assert.ok(node.brand&&node.brand['@id']);
  assert.ok(graph.some((candidate)=>candidate['@type']==='Brand'&&candidate['@id']===node.brand['@id']));
  assert.ok(node.category&&node.category['@id'].includes(categoryId));
  assert.ok(Array.isArray(node.additionalProperty)&&node.additionalProperty.length>=5);
  assert.ok(node.additionalProperty.some((item)=>item.name==='Teknik doğrulama tarihi'&&item.value==='2026-08-01'));
  assert.ok(node.additionalProperty.some((item)=>item.name==='Ticari ilişki'));
  assert.ok(!node.potentialAction,'Düşük riskli ürün yanlışlıkla after_tool kapısına bağlandı.');
  assertForbiddenFieldsAbsent(node,`kg.${node.sku}`);
}

const itemList=graph.find((node)=>node['@type']==='ItemList'&&node['@id'].endsWith(`#itemlist-${categoryId}`));
assert.ok(itemList,'Kategori ItemList düğümü eksik.');
assert.equal(itemList.numberOfItems,3);
const listedProductIds=new Set((itemList.itemListElement||[]).map((item)=>item.item&&item.item['@id']).filter(Boolean));
for(const node of productNodes)assert.ok(listedProductIds.has(node['@id']),`ItemList ürünü eksik: ${node.sku}`);

const staleGraph=catalog.knowledgeGraph({now:staleNow})['@graph'];
for(const [id] of expected){
  assert.ok(!staleGraph.some((node)=>node['@type']==='Product'&&node.sku===id),`Eski ürün Knowledge Graph'ta kaldı: ${id}`);
}

for(const protectedCategory of catalog.categories.filter((item)=>['after_tool','professional_only'].includes(item.affiliatePolicy))){
  assert.notEqual(protectedCategory.id,categoryId,'Yeni kategori mevcut yüksek risk kapısının üzerine yazıldı.');
}
assert.equal((indexHtml.match(/rel="canonical"/g)||[]).length,1);
assert.match(indexHtml,/<link rel="canonical" href="https:\/\/www\.alo186\.com\/akilli-urun-secimi">/);
assert.equal((indexHtml.match(/catalog-battery-continuity-run75\.js/g)||[]).length,1);
assert.ok(indexHtml.indexOf('catalog-battery-continuity-run75.js')<indexHtml.indexOf('matcher-core.js'));
assert.match(indexHtml,/Reklam \/ satış ortaklığı:/);
assert.match(appJs,/rel="sponsored nofollow noopener"/);
assert.ok(!/amazon\.com\.tr\/s\?k=/.test(extensionJs),'Yeni ürün kayıtlarında Amazon arama CTA’sı bulunamaz.');

console.log(JSON.stringify({
  ok:true,
  category:categoryId,
  products:expected.map(([,asin])=>asin),
  affiliateTag:catalog.affiliateTag,
  productNodes:productNodes.length,
  brandNodes:new Set(productNodes.map((node)=>node.brand['@id'])).size,
  itemListItems:itemList.numberOfItems,
  duplicateAsinGuard:true,
  staleFailClosed:true,
  forbiddenCommercialFields:true,
  afterToolAndProfessionalOnlyPreserved:true,
  canonical:true,
  sponsoredNofollow:true
},null,2));
