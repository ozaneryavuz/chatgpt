'use strict';
const fs=require('fs'); const path=require('path'); const assert=require('assert');
const ROOT=path.resolve(__dirname,'..');
const ROUTE=path.join(ROOT,'amazon-elektrik-urunleri','usb-c-pd-pps-sarj-gucu-olcum-secimi');
const HTML=fs.readFileSync(path.join(ROUTE,'index.html'),'utf8');
const APP=fs.readFileSync(path.join(ROUTE,'app-v233.js'),'utf8');
const catalog=require(path.join(ROUTE,'catalog-v233.js'));
const EXPECTED=new Map([['B0DFX1N74Z','ACH08448'],['B0B4K26Z58','ACH03717'],['B09W2HP21R','EP-T6530NBEGWW']]);
function walk(dir){return fs.readdirSync(dir,{withFileTypes:true}).flatMap((entry)=>{const full=path.join(dir,entry.name);return entry.isDirectory()?walk(full):[full];});}
assert.strictEqual(catalog.version,233);
assert.strictEqual(catalog.affiliateTag,'alo186rehber-21');
assert.strictEqual(catalog.verificationMaxAgeDays,45);
assert.strictEqual(catalog.category.risk,'consumer-medium');
assert.strictEqual(catalog.category.affiliatePolicy,'after_tool');
assert.strictEqual(catalog.category.professionalOnly,false);
assert.strictEqual(catalog.category.requiredTool,'embedded-usbc-pd-pps-charger-measurement-v233');
assert.strictEqual(catalog.products.length,3);
assert.strictEqual(new Set(catalog.products.map((item)=>item.asin)).size,3);
assert.strictEqual(new Set(catalog.products.map((item)=>item.mpn)).size,3);
for(const product of catalog.products){
  assert.strictEqual(EXPECTED.get(product.asin),product.mpn,`ASIN/MPN mismatch: ${product.asin}`);
  for(const field of ['userNeed','strengths','limitations','noBuyWhen','technicalSource','verifiedAt']) assert.ok(product[field],`${product.asin} missing ${field}`);
  assert.ok(product.strengths.length>=3); assert.ok(product.limitations.length>=3);
  const url=catalog.amazonProductUrl(product.asin);
  assert.ok(url.startsWith(`https://www.amazon.com.tr/dp/${product.asin}?`));
  assert.ok(url.includes('tag=alo186rehber-21'));
}
assert.strictEqual(catalog.verificationStatus(new Date('2026-09-17T12:00:00Z')).fresh,true,'45th day must remain fresh');
assert.strictEqual(catalog.verificationStatus(new Date('2026-09-18T12:00:00Z')).fresh,false,'46th day must fail closed');
const canonical='https://alo186.com/amazon-elektrik-urunleri/usb-c-pd-pps-sarj-gucu-olcum-secimi/';
assert.strictEqual((HTML.match(new RegExp(`<link rel="canonical" href="${canonical}">`,'g'))||[]).length,1);
assert.ok(HTML.includes('data-commercial-scope="after-tool"'));
assert.ok(HTML.includes('data-risk="consumer-medium"'));
assert.ok(HTML.includes('Reklam / satış ortaklığı açıklaması'));
assert.ok(HTML.includes('Satın almama koşulu'));
assert.strictEqual((HTML.match(/rel="sponsored nofollow noopener"/g)||[]).length,3);
assert.ok(HTML.includes('mevcut') && HTML.includes('satın alma'));
assert.ok(!/href="https:\/\/www\.amazon\.com\.tr\/(?:dp|s\?k=)/i.test(HTML),'Initial HTML must not contain an enabled Amazon href');
assert.ok(APP.includes("affiliatePolicy === 'after_tool'"));
assert.ok(APP.includes('professionalOnly === false'));
assert.ok(APP.includes('verificationStatus(new Date())'));
assert.ok(APP.includes("link.removeAttribute('href')"));
assert.ok(APP.includes("category.risk === 'consumer-medium'"));
const jsonLd=[...HTML.matchAll(/<script type="application\/ld\+json">\s*(.*?)\s*<\/script>/gs)];
assert.strictEqual(jsonLd.length,1);
const graph=JSON.parse(jsonLd[0][1])['@graph'];
const products=graph.filter((node)=>node['@type']==='Product');
const lists=graph.filter((node)=>node['@type']==='ItemList');
assert.strictEqual(products.length,3); assert.strictEqual(lists.length,1); assert.strictEqual(lists[0].numberOfItems,3);
for(const product of products){
  assert.strictEqual(product.brand['@type'],'Brand');
  assert.ok(Array.isArray(product.identifier)&&product.identifier.length>=2);
  assert.ok(Array.isArray(product.additionalProperty)&&product.additionalProperty.length>=5);
  assert.ok(!Object.prototype.hasOwnProperty.call(product,'offers'));
}
const serialized=JSON.stringify(graph);
for(const forbidden of ['"Offer"','aggregateRating','priceCurrency','availability','seller','review','warranty']) assert.ok(!serialized.includes(forbidden),`Forbidden structured field: ${forbidden}`);
const hits=[]; const exts=new Set(['.html','.js','.json']);
for(const file of walk(ROOT)){
  if(!exts.has(path.extname(file))||file.startsWith(path.join(ROOT,'tests'))||file.startsWith(ROUTE)) continue;
  const text=fs.readFileSync(file,'utf8');
  for(const asin of EXPECTED.keys()) if(text.includes(asin)) hits.push(`${asin}:${path.relative(ROOT,file)}`);
}
assert.deepStrictEqual(hits,[],`Duplicate ASIN outside route: ${hits.join(', ')}`);
console.log(JSON.stringify({ok:true,route:'/amazon-elektrik-urunleri/usb-c-pd-pps-sarj-gucu-olcum-secimi/',products:[...EXPECTED.keys()],knowledgeGraph:['Product','Brand','ItemList','identifier','additionalProperty'],affiliatePolicy:'after_tool',professionalOnlyBypass:false,staleBoundary:'45-open-46-closed',duplicateAsin:false}));