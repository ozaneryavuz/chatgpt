'use strict';

const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const catalog=require('../urun-eslestirme/catalog-car-charger-run54.js');

const root=path.resolve(__dirname,'..');
const indexHtml=fs.readFileSync(path.join(root,'urun-eslestirme','index.html'),'utf8');
const appJs=fs.readFileSync(path.join(root,'urun-eslestirme','app.js'),'utf8');

assert.equal(catalog.affiliateTag,'alo186rehber-21');
assert.equal(catalog.verificationMaxAgeDays,45);

const category=catalog.getCategory('car_charger');
assert.ok(category,'Araç içi şarj kategorisi eksik.');
assert.equal(category.mode,'direct');
assert.equal(category.risk,'consumer');
assert.equal(category.affiliatePolicy,'verified_direct');
assert.ok(catalog.categoryNeeds.car_charger.includes('vehicle-device-charging'));
assert.ok(catalog.categoryRelations.car_charger.tools.length>0);
assert.ok(catalog.categoryRelations.car_charger.guides.length>0);
assert.ok(catalog.categoryRelations.car_charger.evidence.length>=4);

const expected=[
  ['belkin-ccb001-24w-dual-usba','B08558MGST','CCB001btBK'],
  ['belkin-cca004-30w-usbc','B0BTP9GF27','CCA004btBK'],
  ['bix-bxac65c-65w','B0BT4GWMS3','BXAC65C']
];
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

const now=new Date('2026-07-30T12:00:00Z');
const staleNow=new Date('2026-09-20T12:00:00Z');
const forbidden=['price','stock','seller','rating','aggregateRating','review','warranty','offers','availability','priceCurrency'];

for(const [id,asin,mpn] of expected){
  const product=catalog.products.find((item)=>item.id===id);
  assert.ok(product,`Ürün eksik: ${id}`);
  assert.equal(product.category,'car_charger');
  assert.equal(product.asin,asin);
  assert.equal(product.mpn,mpn);
  assert.equal(product.status,'verified_listing');
  assert.equal(product.verifiedAt,'2026-07-30');
  assert.equal(product.url,`https://www.amazon.com.tr/dp/${asin}?tag=alo186rehber-21`);
  assert.match(product.technicalSource,/^https:\/\//);
  assert.ok(product.needIds.includes('vehicle-device-charging'));
  assert.ok(product.relatedTools.length>0&&product.relatedGuides.length>0);
  assert.ok(product.requiredEvidence.length>=4);
  assert.ok(product.strengths.some((item)=>item.startsWith('Kullanıcı ihtiyacı:')));
  assert.ok(product.limits.some((item)=>item.startsWith('Satın almama koşulu:')));
  assert.ok(catalog.publicAffiliateEligible(product,{now}));
  assert.ok(!catalog.publicAffiliateEligible(product,{now:staleNow}));
  for(const field of forbidden)assert.ok(!(field in product),`Yasak ürün alanı ${field}: ${id}`);
}

const graph=catalog.knowledgeGraph({now})['@graph'];
const selectedNodes=graph.filter((node)=>node['@type']==='Product'&&expected.some(([id])=>id===node.sku));
assert.equal(selectedNodes.length,3);
for(const node of selectedNodes){
  const expectedItem=expected.find(([id])=>id===node.sku);
  assert.ok(node.identifier.some((item)=>item.propertyID==='ASIN'&&item.value===expectedItem[1]));
  assert.ok(node.identifier.some((item)=>item.propertyID==='MPN'&&item.value===expectedItem[2]));
  assert.equal(node.sameAs,`https://www.amazon.com.tr/dp/${expectedItem[1]}?tag=alo186rehber-21`);
  assert.ok(node.brand&&node.brand['@id']);
  assert.ok(node.category&&node.category['@id'].includes('car_charger'));
  assert.ok(node.additionalProperty.some((item)=>item.name==='Teknik doğrulama tarihi'&&item.value==='2026-07-30'));
  assert.ok(node.additionalProperty.some((item)=>item.name==='Ticari ilişki'));
  for(const field of forbidden)assert.ok(!(field in node),`Yasak KG alanı ${field}: ${node.sku}`);
}
const directList=graph.find((node)=>node['@type']==='ItemList'&&String(node['@id']).endsWith('/urun-bilgi-grafigi/#public-products'));
assert.ok(directList,'Doğrudan affiliate ItemList düğümü eksik.');
const directIds=new Set(directList.itemListElement.map((item)=>item.item['@id']));
for(const [id] of expected)assert.ok([...directIds].some((value)=>value.includes(`/urun/${id}#product`)),`Direct ItemList ürünü eksik: ${id}`);

const staleGraph=catalog.knowledgeGraph({now:staleNow})['@graph'];
for(const [id] of expected)assert.ok(!staleGraph.some((node)=>node['@type']==='Product'&&node.sku===id),`Eski ürün KG'de kaldı: ${id}`);

assert.equal((indexHtml.match(/rel="canonical"/g)||[]).length,1);
assert.match(indexHtml,/<link rel="canonical" href="https:\/\/www\.alo186\.com\/akilli-urun-secimi">/);
assert.ok(indexHtml.indexOf('catalog-car-charger-run54.js')<indexHtml.indexOf('matcher-core.js'));
assert.match(indexHtml,/Reklam \/ satış ortaklığı:/);
assert.match(appJs,/rel="sponsored nofollow noopener"/);
assert.ok(!/amazon\.com\.tr\/s\?k=/.test(appJs),'Genel Amazon araması doğrudan ürün kartına sızdı.');

console.log(JSON.stringify({
  ok:true,
  category:category.id,
  products:expected.map(([,asin])=>asin),
  affiliateTag:catalog.affiliateTag,
  publicNodes:selectedNodes.length,
  staleFailClosed:true
},null,2));
