'use strict';

const assert=require('assert');
const fs=require('fs');
const path=require('path');

const root=path.resolve(__dirname,'..');
const pageDir=path.join(root,'amazon-elektrik-urunleri','harici-ssd-hdd-usb-yedekleme-urun-secici');
const dataPath=path.join(pageDir,'exact-products-v186.js');
const appPath=path.join(pageDir,'exact-products-v186-app.js');
const stylePath=path.join(pageDir,'exact-products-v186.css');
const pagePath=path.join(pageDir,'index.html');
const data=require(dataPath);
const app=fs.readFileSync(appPath,'utf8');
const css=fs.readFileSync(stylePath,'utf8');
const page=fs.readFileSync(pagePath,'utf8');

assert.strictEqual(data.version,186);
assert.strictEqual(data.affiliateTag,'alo186rehber-21');
assert.strictEqual(data.verifiedAt,'2026-08-01');
assert.strictEqual(data.verificationMaxAgeDays,45);
assert.strictEqual(data.products.length,4,'Dört exact yedekleme modeli bekleniyor');

const expected=new Map([
  ['B09VLK9W3S','MU-PE1T0S/WW'],
  ['B06W55K9N6','WDBU6Y0020BBK-WESN'],
  ['B0B57T5G5L','DTMAX/256GB'],
  ['B07YYJL21Z','SDDDC3-256G-G46']
]);
const ids=new Set();
const asins=new Set();
const forbiddenKeys=new Set(['price','stock','seller','rating','review','reviews','warranty','offer','offers','availability','aggregateRating']);

function inspectKeys(value,trail='root'){
  if(Array.isArray(value))return value.forEach((item,index)=>inspectKeys(item,`${trail}[${index}]`));
  if(!value||typeof value!=='object')return;
  for(const [key,item] of Object.entries(value)){
    assert(!forbiddenKeys.has(key),`Yasak ticari alan: ${trail}.${key}`);
    inspectKeys(item,`${trail}.${key}`);
  }
}

for(const product of data.products){
  assert(product.id&&!ids.has(product.id),`Yinelenen ürün id: ${product.id}`);ids.add(product.id);
  assert(/^[A-Z0-9]{10}$/.test(product.asin),`ASIN biçimi: ${product.asin}`);
  assert(!asins.has(product.asin),`Yinelenen ASIN: ${product.asin}`);asins.add(product.asin);
  assert.strictEqual(expected.get(product.asin),product.mpn,`ASIN/MPN eşleşmesi: ${product.asin}`);
  assert.strictEqual(product.amazonUrl,`https://www.amazon.com.tr/dp/${product.asin}?tag=alo186rehber-21`);
  assert(product.technicalSource.startsWith('https://'));
  assert(!product.technicalSource.includes('amazon.'),'Teknik kaynak Amazon olamaz');
  assert(product.userNeed.length>=40);
  assert(product.facts.length>=4);
  assert(product.bestFor.length>=2);
  assert(product.evidence.length>=4);
  assert(product.noBuyWhen.length>=4);
  assert(data.verificationStatus(product,new Date('2026-08-01T12:00:00Z')).fresh);
}
assert.deepStrictEqual([...asins].sort(),[...expected.keys()].sort());
inspectKeys(data.products);

function walk(directory){
  const files=[];
  for(const entry of fs.readdirSync(directory,{withFileTypes:true})){
    if(['.git','node_modules'].includes(entry.name))continue;
    const full=path.join(directory,entry.name);
    if(entry.isDirectory())files.push(...walk(full));
    else if(/\.(?:js|json|html)$/.test(entry.name))files.push(full);
  }
  return files;
}
const duplicateFiles=walk(root).filter(file=>file!==dataPath&&file!==__filename);
for(const asin of expected.keys()){
  const collisions=duplicateFiles.filter(file=>fs.readFileSync(file,'utf8').includes(asin));
  assert.deepStrictEqual(collisions,[],`ASIN başka katalogda tekrarlandı: ${asin} ${collisions.join(', ')}`);
}

const graph=data.knowledgeGraph(new Date('2026-08-01T12:00:00Z'));
assert.strictEqual(graph['@context'],'https://schema.org');
assert(Array.isArray(graph['@graph']));
const types=graph['@graph'].map(node=>node['@type']);
for(const type of ['DefinedTermSet','ItemList','Brand','DefinedTerm'])assert(types.includes(type),`KG türü eksik: ${type}`);
assert.strictEqual(types.filter(type=>type==='DefinedTerm').length,4);
assert.strictEqual(graph['@graph'].find(node=>node['@type']==='ItemList').numberOfItems,4);
for(const node of graph['@graph'].filter(node=>node['@type']==='DefinedTerm')){
  assert(node.identifier.some(item=>item['@type']==='PropertyValue'&&item.propertyID==='ASIN'));
  assert(node.identifier.some(item=>item['@type']==='PropertyValue'&&item.propertyID==='MPN'));
  assert(node.additionalProperty.length>=4);
  assert(!('sameAs' in node),'Ticari kapı KG üzerinden aşılmamalı');
}
for(const forbidden of ['Product','Offer','AggregateRating'])assert(!types.includes(forbidden),`Yasak şema türü: ${forbidden}`);
assert(!JSON.stringify(graph).includes('priceCurrency'));
assert(!JSON.stringify(graph).includes('availability'));

const stale=data.knowledgeGraph(new Date('2026-10-01T12:00:00Z'));
assert.strictEqual(stale['@graph'].filter(node=>node['@type']==='DefinedTerm').length,0);
assert.strictEqual(stale['@graph'].find(node=>node['@type']==='ItemList').numberOfItems,0);

for(const token of [
  'id="exactBackupProducts"','id="exactNeedConfirm"','id="exactSpecConfirm"','id="exactAffiliateConfirm"',
  'id="exactGateStatus"','id="exactFreshCount"','./exact-products-v186.js','./exact-products-v186-app.js','./exact-products-v186.css',
  'Bir Amazon Gelir Ortağı olarak nitelikli satın alımlar üzerinden kazanç elde ediyorum.',
  'Mevcut disk kapasite, sağlık ve gerçek geri yükleme testini karşılıyorsa yeni ürün almayın.',
  'slice(0,3)','needConfirm','specConfirm','adConfirm','sponsored nofollow noopener','alo186rehber-21'
])assert(page.includes(token),`Sayfa sözleşmesi eksik: ${token}`);
assert(!/href=["']https:\/\/www\.amazon\.com\.tr\/dp\//i.test(page),'Kapısız exact Amazon bağlantısı statik HTML içinde olamaz');
assert(!page.includes('"@type":"Product"'));
assert(!page.includes('"@type":"Offer"'));

for(const token of [
  'function gateOpen()','exactNeedConfirm','exactSpecConfirm','exactAffiliateConfirm',
  'data-exact-affiliate','sponsored nofollow noopener','verificationStatus',
  'knowledgeGraph(new Date())','affiliate_backup_exact_viewed','affiliate_backup_exact_gate','affiliate_backup_exact_clicked'
])assert(app.includes(token),`Runtime sözleşmesi eksik: ${token}`);
for(const forbidden of ['localStorage','sessionStorage','geolocation','window.open(','fetch('])assert(!app.includes(forbidden),`Yasak runtime: ${forbidden}`);
assert(css.includes('@media(max-width:800px)'));
assert(css.includes('.exact-shop[aria-disabled=true]'));
assert(css.includes('@media(prefers-reduced-motion:reduce)'));

console.log(JSON.stringify({ok:true,version:data.version,exactModels:data.products.length,uniqueAsins:asins.size,tripleGate:true,staleFailClosed:true,noDuplicateAsin:true,noCommercialSchema:true}));
