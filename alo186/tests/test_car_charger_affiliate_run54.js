'use strict';

const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const catalog=require('../urun-eslestirme/catalog-car-charger-run54.js');

const root=path.resolve(__dirname,'..');
const indexHtml=fs.readFileSync(path.join(root,'urun-eslestirme','index.html'),'utf8');
const appJs=fs.readFileSync(path.join(root,'urun-eslestirme','app.js'),'utf8');
const extensionJs=fs.readFileSync(path.join(root,'urun-eslestirme','catalog-car-charger-run54.js'),'utf8');

assert.equal(catalog.affiliateTag,'alo186rehber-21');
assert.equal(catalog.verificationMaxAgeDays,45);

const category=catalog.getCategory('car_charger');
assert.ok(category,'Araç içi şarj kategorisi eksik.');
assert.equal(category.mode,'direct');
assert.equal(category.risk,'consumer');
assert.equal(category.affiliatePolicy,'verified_direct');
assert.notEqual(category.affiliatePolicy,'after_tool');
assert.notEqual(category.affiliatePolicy,'professional_only');
assert.ok(catalog.categoryNeeds.car_charger.includes('vehicle-device-charging'));
assert.ok(catalog.categoryRelations.car_charger.tools.length>0);
assert.ok(catalog.categoryRelations.car_charger.guides.length>0);
assert.ok(catalog.categoryRelations.car_charger.evidence.length>=4);

const portableEvse=catalog.getCategory('portable_evse');
assert.ok(portableEvse,'Taşınabilir EVSE kategorisi ürün merkezine kaydedilmedi.');
assert.equal(portableEvse.mode,'guide');
assert.equal(portableEvse.risk,'safety');
assert.equal(portableEvse.affiliatePolicy,'after_tool');
assert.equal(portableEvse.nextStepUrl,'https://alo186.com/hesaplama/tasinabilir-ev-sarj-priz-uygunluk/');
assert.match(portableEvse.nextStepLabel,/priz.*PE.*RCD\/DC.*akım/i);
assert.match(portableEvse.description,/etiketi.*kanıtlamaz/i);
assert.match(extensionJs,/searchParams\.get\('niyet'\)==='portable_evse'/);
assert.match(extensionJs,/searchParams\.set\('kategori','portable_evse'\)/);
assert.match(extensionJs,/history\.replaceState/);

const expected=[
  {id:'belkin-ccb001-24w-dual-usba',asin:'B08558MGST',mpn:'CCB001btBK',brand:'Belkin',verifiedAt:'2026-07-30'},
  {id:'belkin-cca004-30w-usbc',asin:'B0BTP9GF27',mpn:'CCA004btBK',brand:'Belkin',verifiedAt:'2026-07-30'},
  {id:'bix-bxac65c-65w',asin:'B0BT4GWMS3',mpn:'BXAC65C',brand:'Bix',verifiedAt:'2026-07-30'},
  {id:'anker-323-a2735-52w',asin:'B0BPGSRYFH',mpn:'A2735',brand:'Anker',verifiedAt:'2026-07-31'},
  {id:'ugreen-60980-52w',asin:'B082WZ139M',mpn:'60980',brand:'UGREEN',verifiedAt:'2026-07-31'},
  {id:'ugreen-70594-dual-usbc-40w',asin:'B07Z1NPFWC',mpn:'70594',brand:'UGREEN',verifiedAt:'2026-07-31'}
];
const newAsins=new Set(['B0BPGSRYFH','B082WZ139M','B07Z1NPFWC']);
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
  for(const field of forbidden)assert.ok(!(field in value),`Yasak alan ${field}: ${context}`);
  for(const [key,nested] of Object.entries(value)){
    if(nested&&typeof nested==='object')assertForbiddenFieldsAbsent(nested,`${context}.${key}`);
  }
}

for(const item of expected){
  const product=catalog.products.find((current)=>current.id===item.id);
  assert.ok(product,`Ürün eksik: ${item.id}`);
  assert.equal(product.category,'car_charger');
  assert.equal(product.asin,item.asin);
  assert.equal(product.mpn,item.mpn);
  assert.equal(product.brand,item.brand);
  assert.equal(product.status,'verified_listing');
  assert.equal(product.verifiedAt,item.verifiedAt);
  assert.equal(product.url,`https://www.amazon.com.tr/dp/${item.asin}?tag=alo186rehber-21`);
  assert.match(product.technicalSource,/^https:\/\//);
  assert.ok(product.needIds.includes('vehicle-device-charging'));
  assert.ok(product.relatedTools.length>0&&product.relatedGuides.length>0);
  assert.ok(product.requiredEvidence.length>=4);
  assert.ok(product.strengths.some((value)=>value.startsWith('Kullanıcı ihtiyacı:')));
  assert.ok(product.limits.some((value)=>value.startsWith('Satın almama koşulu:')));
  assert.match(product.sourceNote,/Amazon Türkiye/);
  assert.match(product.sourceNote,/Fiyat, stok, satıcı, puan, yorum ve garanti yayımlanmaz\./);
  assert.ok(catalog.publicAffiliateEligible(product,{now}));
  assert.ok(!catalog.publicAffiliateEligible(product,{now:staleNow}));
  assertForbiddenFieldsAbsent(product,item.id);
}

assert.equal([...newAsins].filter((asin)=>asins.has(asin)).length,3);
assert.match(extensionJs,/version:'2026-07-31-run76'/);
assert.match(extensionJs,/data\.generated='alo186-affiliate-knowledge-graph-run76'|dataset\.generated='alo186-affiliate-knowledge-graph-run76'/);
assert.ok(!extensionJs.includes('amazonSearchUrl('),'Doğrudan ürün uzantısında genel Amazon araması kullanılamaz.');

const graph=catalog.knowledgeGraph({now})['@graph'];
const selectedNodes=graph.filter((node)=>node['@type']==='Product'&&expected.some((item)=>item.id===node.sku));
assert.equal(selectedNodes.length,expected.length);
for(const node of selectedNodes){
  const item=expected.find((current)=>current.id===node.sku);
  assert.ok(node.identifier.some((identifier)=>identifier.propertyID==='ASIN'&&identifier.value===item.asin));
  assert.ok(node.identifier.some((identifier)=>identifier.propertyID==='MPN'&&identifier.value===item.mpn));
  assert.equal(node.sameAs,`https://www.amazon.com.tr/dp/${item.asin}?tag=alo186rehber-21`);
  assert.ok(node.brand&&node.brand['@id']);
  assert.ok(node.category&&node.category['@id'].includes('car_charger'));
  assert.ok(Array.isArray(node.additionalProperty)&&node.additionalProperty.length>0);
  assert.ok(node.additionalProperty.some((property)=>property.name==='Teknik doğrulama tarihi'&&property.value===item.verifiedAt));
  assert.ok(node.additionalProperty.some((property)=>property.name==='Ticari ilişki'));
  assertForbiddenFieldsAbsent(node,`kg.${node.sku}`);
}

const brandNodes=graph.filter((node)=>node['@type']==='Brand');
for(const brand of new Set(expected.map((item)=>item.brand))){
  assert.ok(brandNodes.some((node)=>node.name===brand),`Brand düğümü eksik: ${brand}`);
}
const portableEvseNode=graph.find((node)=>node['@type']==='DefinedTerm'&&node.termCode==='portable_evse');
assert.ok(portableEvseNode,'Taşınabilir EVSE kategori düğümü Knowledge Graph içinde eksik.');
assert.match(portableEvseNode.description,/Priz sınıfı/);
const directList=graph.find((node)=>node['@type']==='ItemList'&&String(node['@id']).endsWith('/urun-bilgi-grafigi/#public-products'));
assert.ok(directList,'Doğrudan affiliate ItemList düğümü eksik.');
const directIds=new Set(directList.itemListElement.map((entry)=>entry.item['@id']));
for(const item of expected){
  assert.ok([...directIds].some((value)=>value.includes(`/urun/${item.id}#product`)),`Direct ItemList ürünü eksik: ${item.id}`);
}

const staleGraph=catalog.knowledgeGraph({now:staleNow})['@graph'];
for(const item of expected){
  assert.ok(!staleGraph.some((node)=>node['@type']==='Product'&&node.sku===item.id),`Eski ürün KG'de kaldı: ${item.id}`);
}

assert.equal((indexHtml.match(/rel="canonical"/g)||[]).length,1);
assert.match(indexHtml,/<link rel="canonical" href="https:\/\/www\.alo186\.com\/akilli-urun-secimi">/);
assert.ok(indexHtml.indexOf('catalog-car-charger-run54.js')<indexHtml.indexOf('matcher-core.js'));
assert.match(indexHtml,/Reklam \/ satış ortaklığı:/);
assert.match(appJs,/rel="sponsored nofollow noopener"/);
assert.ok(!/amazon\.com\.tr\/s\?k=/.test(appJs),'Genel Amazon araması doğrudan ürün kartına sızdı.');

console.log(JSON.stringify({
  ok:true,
  category:category.id,
  portableEvseCategory:portableEvse.id,
  products:expected.map(({asin})=>asin),
  newProducts:[...newAsins],
  affiliateTag:catalog.affiliateTag,
  productNodes:selectedNodes.length,
  brandNodes:brandNodes.length,
  itemList:true,
  canonical:true,
  sponsoredNofollow:true,
  duplicateAsinGuard:true,
  staleFailClosed:true,
  forbiddenCommercialFieldsAbsent:true
},null,2));
