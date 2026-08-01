'use strict';

const assert=require('assert');
const fs=require('fs');
const path=require('path');

const root=path.resolve(__dirname,'..');
const pageDir=path.join(root,'amazon-elektrik-urunleri','tasinabilir-enerji-sarj-urunleri');
const data=require(path.join(pageDir,'exact-products-v175.js'));
const page=fs.readFileSync(path.join(pageDir,'index.html'),'utf8');
const app=fs.readFileSync(path.join(pageDir,'app-v175.js'),'utf8');

assert.strictEqual(data.version,175);
assert.strictEqual(data.affiliateTag,'alo186rehber-21');
assert.strictEqual(data.products.length,10,'10 exact model bekleniyor');
assert.strictEqual(data.productClasses.length,10,'10 ürün sınıfı bekleniyor');

const ids=new Set();
const asins=new Set();
const requiredNewAsins=['B0DWT5G6QQ','B0B127GW4D','B0D232C5JJ','B08X5168HM'];
const reference=new Date('2026-08-01T23:59:59Z');
const bannedKeys=new Set(['price','stock','seller','rating','review','reviews','availability','offer','offers']);

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
  assert(product.userNeed.length>=20);
  assert(product.facts.length>=3);
  assert(product.bestFor.length>=2);
  assert(product.evidence.length>=3);
  assert(product.noBuyWhen.length>=2);
  const checked=new Date(`${product.verifiedAt}T00:00:00Z`);
  const age=Math.floor((reference-checked)/86400000);
  assert(age>=0&&age<=data.verificationMaxAgeDays,`eski doğrulama: ${product.id}`);
}
for(const asin of requiredNewAsins)assert(asins.has(asin),`yeni exact ürün eksik: ${asin}`);

for(const item of data.productClasses){
  assert(item.id&&item.name&&item.tool&&item.amazonUrl);
  assert(item.amazonUrl.includes('https://www.amazon.com.tr/s?k='));
  assert(item.amazonUrl.includes('tag=alo186rehber-21'));
  assert(item.evidence.length>=3);
  assert(item.noBuyWhen.length>=15);
}
inspectKeys({products:data.products,productClasses:data.productClasses});

for(const token of [
  'Bir Amazon Gelir Ortağı olarak nitelikli satın alımlar üzerinden kazanç elde ediyorum.',
  'id="gateExisting"','id="gateTechnical"','id="gateAffiliate"',
  'id="exactProducts"','id="productClasses"',
  './exact-products-v175.js','./app-v175.js',
  'CollectionPage','FAQPage','BreadcrumbList'
])assert(page.includes(token),`sayfa sözleşmesi eksik: ${token}`);

assert(!page.includes('amazon.com.tr/dp/'),'Amazon exact URL HTML içinde kapısız kalamaz');
assert(!page.includes('amazon.com.tr/s?k='),'Amazon arama URL HTML içinde kapısız kalamaz');
assert(!page.includes('"@type":"Product"'));
assert(!page.includes('"@type":"Offer"'));
assert(!page.includes('aggregateRating'));
assert(!page.includes('availability'));

for(const token of [
  'function gateOpen()','gateExisting','gateTechnical','gateAffiliate',
  'data-affiliate-link','sponsored nofollow noopener',
  'verificationMaxAgeDays','DefinedTermSet','affiliate_exact_product_clicked'
])assert(app.includes(token),`runtime güven sözleşmesi eksik: ${token}`);

assert(!/href=["']https:\/\/www\.amazon\.com\.tr/.test(page));
console.log(JSON.stringify({ok:true,version:data.version,exactProducts:data.products.length,productClasses:data.productClasses.length,newExactProducts:requiredNewAsins.length,tripleGate:true,noUngatedAmazonLinks:true}));
