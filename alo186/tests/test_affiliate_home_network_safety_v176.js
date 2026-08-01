'use strict';

const assert=require('assert');
const fs=require('fs');
const path=require('path');

const root=path.resolve(__dirname,'..');
const pageDir=path.join(root,'amazon-elektrik-urunleri','ev-ofis-ag-surekliligi-guvenlik-urunleri');
const data=require(path.join(pageDir,'exact-products-v176.js'));
const page=fs.readFileSync(path.join(pageDir,'index.html'),'utf8');
const app=fs.readFileSync(path.join(pageDir,'app-v176.js'),'utf8');
const css=fs.readFileSync(path.join(pageDir,'styles-v176.css'),'utf8');
const overlay=JSON.parse(fs.readFileSync(path.join(root,'deployment','routing-overlays','176-affiliate-home-network-safety-products.json'),'utf8'));

assert.strictEqual(data.version,176);
assert.strictEqual(data.affiliateTag,'alo186rehber-21');
assert.strictEqual(data.generatedAt,'2026-08-01');
assert.strictEqual(data.verificationMaxAgeDays,45);
assert.strictEqual(data.products.length,5,'5 doğrulanmış exact model bekleniyor');
assert.strictEqual(data.productClasses.length,12,'12 ürün sınıfı bekleniyor');
assert.strictEqual(data.routePath,'/amazon-elektrik-urunleri/ev-ofis-ag-surekliligi-guvenlik-urunleri/');

const ids=new Set();
const asins=new Set();
const requiredAsins=['B0859MDSFX','B00A128S24','B08JLR2751','B07XLML2YS','B07XGJ163F'];
const reference=new Date('2026-08-01T23:59:59Z');
const bannedKeys=new Set(['price','stock','seller','rating','review','reviews','availability','offer','offers','warranty']);

function inspectKeys(value,trail='root'){
  if(Array.isArray(value))return value.forEach((item,index)=>inspectKeys(item,`${trail}[${index}]`));
  if(!value||typeof value!=='object')return;
  for(const [key,item] of Object.entries(value)){
    assert(!bannedKeys.has(key.toLowerCase()),`yasak ticari alan: ${trail}.${key}`);
    inspectKeys(item,`${trail}.${key}`);
  }
}

for(const product of data.products){
  assert(product.id&&!ids.has(product.id),`yinelenen id: ${product.id}`);ids.add(product.id);
  assert(/^[A-Z0-9]{10}$/.test(product.asin),`ASIN biçimi: ${product.asin}`);
  assert(!asins.has(product.asin),`yinelenen ASIN: ${product.asin}`);asins.add(product.asin);
  assert(product.amazonUrl===`https://www.amazon.com.tr/dp/${product.asin}?tag=alo186rehber-21`);
  assert(product.technicalSource.startsWith('https://'));
  assert(!product.technicalSource.includes('amazon.'),'Teknik kaynak Amazon olamaz');
  assert(product.userNeed.length>=20);
  assert(product.facts.length>=3);
  assert(product.bestFor.length>=2);
  assert(product.evidence.length>=3);
  assert(product.noBuyWhen.length>=3);
  const checked=new Date(`${product.verifiedAt}T00:00:00Z`);
  const age=Math.floor((reference-checked)/86400000);
  assert(age>=0&&age<=data.verificationMaxAgeDays,`eski doğrulama: ${product.id}`);
}
for(const asin of requiredAsins)assert(asins.has(asin),`exact ürün eksik: ${asin}`);

for(const item of data.productClasses){
  assert(item.id&&item.name&&item.tool&&item.amazonUrl&&item.verifiedAt);
  assert(item.tool.startsWith('/'));
  assert(item.amazonUrl.startsWith('https://www.amazon.com.tr/s?k='));
  assert(item.amazonUrl.includes('tag=alo186rehber-21'));
  assert(item.evidence.length>=3);
  assert(item.noBuyWhen.length>=25);
}
inspectKeys({products:data.products,productClasses:data.productClasses});

const payload=data.knowledgeGraph(reference);
assert.strictEqual(payload['@context'],'https://schema.org');
assert(Array.isArray(payload['@graph']));
const graph=payload['@graph'];
const types=graph.map(node=>node['@type']);
assert(types.includes('DefinedTermSet'));
assert(types.includes('ItemList'));
assert(types.includes('Brand'));
assert.strictEqual(types.filter(type=>type==='DefinedTerm').length,5);
assert.strictEqual(graph.find(node=>node['@type']==='ItemList').numberOfItems,5);
for(const node of graph.filter(node=>node['@type']==='DefinedTerm')){
  assert(node.identifier.some(item=>item['@type']==='PropertyValue'&&item.propertyID==='ASIN'));
  assert(node.identifier.some(item=>item['@type']==='PropertyValue'&&item.propertyID==='MPN'));
  assert(node.additionalProperty.length>=3);
}
for(const forbidden of ['Product','Offer','AggregateRating'])assert(!types.includes(forbidden),`yasak şema türü: ${forbidden}`);
assert(!JSON.stringify(payload).includes('priceCurrency'));
assert(!JSON.stringify(payload).includes('availability'));
const stale=data.knowledgeGraph(new Date('2026-10-01T12:00:00Z'));
assert.strictEqual(stale['@graph'].filter(node=>node['@type']==='DefinedTerm').length,0,'eski modeller KG dışına çıkmalı');
assert.strictEqual(stale['@graph'].find(node=>node['@type']==='ItemList').numberOfItems,0);

for(const token of [
  'Bir Amazon Gelir Ortağı olarak nitelikli satın alımlar üzerinden kazanç elde ediyorum.',
  'id="gateExisting"','id="gateTechnical"','id="gateAffiliate"',
  'id="exactProducts"','id="productClasses"','id="filters"',
  './exact-products-v176.js','./app-v176.js','./styles-v176.css',
  'CollectionPage','FAQPage','BreadcrumbList',
  'Mevcut ürün yeterliyse yeni ürün satın almayın.'
])assert(page.includes(token),`sayfa sözleşmesi eksik: ${token}`);
assert(!page.includes('amazon.com.tr/dp/'),'Exact Amazon URL statik HTML içinde kapısız kalamaz');
assert(!page.includes('amazon.com.tr/s?k='),'Amazon arama URL statik HTML içinde kapısız kalamaz');
assert(!page.includes('"@type":"Product"'));
assert(!page.includes('"@type":"Offer"'));
assert(!page.includes('aggregateRating'));
assert(!page.includes('availability'));

for(const token of [
  'function gateOpen()','gateExisting','gateTechnical','gateAffiliate',
  'data-affiliate-link','sponsored nofollow noopener',
  'verificationMaxAgeDays','knowledgeGraph(new Date())',
  'affiliate_home_network_collection_viewed','affiliate_home_network_filter',
  'affiliate_home_network_gate','affiliate_home_network_exact_clicked','affiliate_home_network_class_clicked'
])assert(app.includes(token),`runtime sözleşmesi eksik: ${token}`);
for(const forbidden of ['localStorage','sessionStorage','geolocation','window.open(','fetch('])assert(!app.includes(forbidden),`yasak runtime: ${forbidden}`);
assert(css.includes('@media(max-width:640px)'));
assert(css.includes('button:focus-visible'));
assert(css.includes('@media(prefers-reduced-motion:reduce)'));

assert.strictEqual(overlay.version,176);
assert.deepStrictEqual(overlay.routes,[{
  source:'alo186/amazon-elektrik-urunleri/ev-ofis-ag-surekliligi-guvenlik-urunleri/index.html',
  canonicalPath:'/amazon-elektrik-urunleri/ev-ofis-ag-surekliligi-guvenlik-urunleri/',
  type:'collection'
}]);

console.log(JSON.stringify({ok:true,version:data.version,exactProducts:data.products.length,productClasses:data.productClasses.length,uniqueAsins:asins.size,tripleGate:true,staleFailClosed:true,noUngatedAmazonLinks:true}));
