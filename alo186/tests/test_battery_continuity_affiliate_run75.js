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
assert.ok(!extensionJs.includes('amazonSearchUrl('),'Doğrudan ürün uzantısında genel Amazon araması kullanılamaz.');

const expected=[
  ['duracell-cef14-aa-aaa-set','B07BFDVNSJ','CEF14','nimh_battery_charger','Duracell'],
  ['gp-recyko-e411-2700-aa-set','B09DPKNDBX','E411-270AAHCCS-2CR1','nimh_battery_charger','GP Batteries'],
  ['duracell-aaa-750-2pack','B00DDEVU36','5000394107939','rechargeable_nimh_battery','Duracell']
];

for(const categoryId of ['nimh_battery_charger','rechargeable_nimh_battery']){
  const category=catalog.getCategory(categoryId);
  assert.ok(category,`Kategori eksik: ${categoryId}`);
  assert.equal(category.mode,'direct');
  assert.equal(category.risk,'consumer');
  assert.equal(category.affiliatePolicy,'verified_direct');
  assert.notEqual(category.affiliatePolicy,'after_tool');
  assert.notEqual(category.affiliatePolicy,'professional_only');
  assert.ok(catalog.categoryNeeds[categoryId].includes('reusable-battery-continuity'));
  assert.ok(catalog.categoryRelations[categoryId].tools.length>0);
  assert.ok(catalog.categoryRelations[categoryId].guides.length>0);
  assert.ok(catalog.categoryRelations[categoryId].evidence.length>=4);
}

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

const now=new Date('2026-07-31T09:00:00Z');
const staleNow=new Date('2026-09-20T09:00:00Z');
const forbidden=['price','stock','seller','rating','aggregateRating','review','reviews','warranty','offers','availability','priceCurrency'];

function assertForbiddenFieldsAbsent(value,context){
  if(!value||typeof value!=='object')return;
  for(const key of forbidden)assert.ok(!(key in value),`Yasak alan ${key}: ${context}`);
  for(const [key,nested] of Object.entries(value)){
    if(nested&&typeof nested==='object')assertForbiddenFieldsAbsent(nested,`${context}.${key}`);
  }
}

for(const [id,asin,mpn,categoryId,brand] of expected){
  const product=catalog.products.find((item)=>item.id===id);
  assert.ok(product,`Ürün eksik: ${id}`);
  assert.equal(product.category,categoryId);
  assert.equal(product.asin,asin);
  assert.equal(product.mpn,mpn);
  assert.equal(product.brand,brand);
  assert.equal(product.status,'verified_listing');
  assert.equal(product.verifiedAt,'2026-07-31');
  assert.equal(product.url,`https://www.amazon.com.tr/dp/${asin}?tag=alo186rehber-21`);
  assert.match(product.technicalSource,/^https:\/\//);
  assert.ok(product.needIds.includes('reusable-battery-continuity'));
  assert.ok(product.relatedTools.length>0&&product.relatedGuides.length>0);
  assert.ok(product.requiredEvidence.length>=4);
  assert.ok(product.strengths.some((item)=>item.startsWith('Kullanıcı ihtiyacı:')),`Kullanıcı ihtiyacı eksik: ${id}`);
  assert.ok(product.strengths.some((item)=>item.startsWith('Satış ortaklığı açıklaması:')),`Kart açıklaması eksik: ${id}`);
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
  assert.ok(node.category&&node.category['@id'].includes(expectedItem[3]));
  assert.ok(node.additionalProperty.some((item)=>item.name==='Teknik doğrulama tarihi'&&item.value==='2026-07-31'));
  assert.ok(node.additionalProperty.some((item)=>item.name==='Ticari ilişki'));
  assert.ok(!node.potentialAction,'Doğrudan tüketici ürünü after_tool kapısına yanlış bağlandı.');
  assertForbiddenFieldsAbsent(node,`kg.${node.sku}`);
}

const lists=graph.filter((node)=>node['@type']==='ItemList');
assert.ok(lists.length>=2,'ItemList düğümleri eksik.');
const listedProductIds=new Set(lists.flatMap((list)=>list.itemListElement||[]).map((item)=>item.item&&item.item['@id']).filter(Boolean));
for(const node of productNodes)assert.ok(listedProductIds.has(node['@id']),`ItemList ürünü eksik: ${node.sku}`);

const staleGraph=catalog.knowledgeGraph({now:staleNow})['@graph'];
for(const [id] of expected){
  assert.ok(!staleGraph.some((node)=>node['@type']==='Product'&&node.sku===id),`Eski ürün Knowledge Graph'ta kaldı: ${id}`);
}

assert.equal((indexHtml.match(/rel="canonical"/g)||[]).length,1);
assert.match(indexHtml,/<link rel="canonical" href="https:\/\/www\.alo186\.com\/akilli-urun-secimi">/);
assert.equal((indexHtml.match(/catalog-battery-continuity-run75\.js/g)||[]).length,1);
assert.ok(indexHtml.indexOf('catalog-battery-continuity-run75.js')<indexHtml.indexOf('matcher-core.js'));
assert.match(indexHtml,/Reklam \/ satış ortaklığı:/);
assert.match(appJs,/rel="sponsored nofollow noopener"/);
assert.ok(!/amazon\.com\.tr\/s\?k=/.test(extensionJs),'Yeni ürün uzantısında Amazon arama CTA’sı bulunamaz.');

console.log(JSON.stringify({
  ok:true,
  categories:['nimh_battery_charger','rechargeable_nimh_battery'],
  products:expected.map(([,asin])=>asin),
  affiliateTag:catalog.affiliateTag,
  productNodes:productNodes.length,
  brandNodes:new Set(productNodes.map((node)=>node.brand['@id'])).size,
  itemLists:lists.length,
  duplicateAsinGuard:true,
  staleFailClosed:true,
  forbiddenCommercialFields:true,
  safetyGatesPreserved:true
},null,2));
