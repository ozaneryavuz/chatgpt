'use strict';
const assert=require('node:assert/strict');
const catalog=require('../urun-eslestirme/catalog.js');

assert.equal(catalog.affiliateTag,'alo186rehber-21');
assert.equal(catalog.verifiedAt,'2026-07-29');
assert.ok(catalog.products.length>=12);

const ids=new Set();
const asins=new Set();
for(const product of catalog.products){
  assert.ok(product.id&&!ids.has(product.id),`Tekrarlanan ürün id: ${product.id}`);ids.add(product.id);
  assert.ok(product.asin&&!asins.has(product.asin),`Tekrarlanan ASIN: ${product.asin}`);asins.add(product.asin);
  assert.match(product.url,/amazon\.com\.tr\/dp\//);
  assert.match(product.url,/[?&]tag=alo186rehber-21(?:&|$)/);
  assert.ok(product.brand&&product.category&&product.name);
  assert.equal(product.status,'verified_listing');
  for(const forbidden of ['price','stock','rating','aggregateRating','review','warranty','seller'])assert.ok(!(forbidden in product),`Yasak ürün alanı: ${forbidden}`);
}
for(const id of ['philips-spn7040wa-62','tuncmatik-tsk6134','brennenstuhl-eco-line-6','anker-737-a1289','anker-a1383-20000-87w'])assert.ok(ids.has(id),`Yeni ürün eksik: ${id}`);

const anker737=catalog.products.find(product=>product.id==='anker-737-a1289');
assert.equal(anker737.asin,'B09VPHVT2Z');
assert.equal(anker737.mpn,'A1289');
assert.equal(anker737.attributes.capacityMah,24000);
assert.equal(anker737.attributes.maxOutputW,140);
const anker87=catalog.products.find(product=>product.id==='anker-a1383-20000-87w');
assert.equal(anker87.asin,'B0CXDXP8VR');
assert.equal(anker87.mpn,'A1383');
assert.equal(anker87.attributes.maxOutputW,87);
assert.equal(anker87.attributes.singlePortMaxOutputW,65);
assert.equal(anker87.attributes.builtInUsbCCable,true);

const now=new Date('2026-07-29T12:00:00Z');
const publicProducts=catalog.products.filter(product=>catalog.publicAffiliateEligible(product,{now}));
const gatedProducts=catalog.products.filter(product=>!catalog.publicAffiliateEligible(product,{now,freshOnly:false}));
assert.deepEqual([...new Set(publicProducts.map(product=>product.category))],['powerbank']);
assert.ok(gatedProducts.some(product=>product.category==='surge_strip'));

const payload=catalog.knowledgeGraph({now});
assert.equal(payload['@context'],'https://schema.org');
assert.ok(Array.isArray(payload['@graph']));
const graph=payload['@graph'];
const types=new Set(graph.flatMap(node=>Array.isArray(node['@type'])?node['@type']:[node['@type']]));
for(const type of ['Organization','WebSite','DefinedTermSet','DefinedTerm','Brand','ItemList','Product'])assert.ok(types.has(type),`KG türü eksik: ${type}`);
const productNodes=graph.filter(node=>node['@type']==='Product');
assert.equal(productNodes.length,publicProducts.length);
assert.equal(graph.filter(node=>node['@type']==='Brand').length,new Set(publicProducts.map(p=>p.brand)).size);
assert.equal(graph.filter(node=>node['@type']==='Offer').length,0);
for(const node of graph){
  for(const forbidden of ['offers','aggregateRating','review','price','priceCurrency','availability','seller'])assert.ok(!(forbidden in node),`Yasak ticari alan: ${forbidden}`);
}
for(const node of productNodes){
  const product=publicProducts.find(item=>item.id===node.sku);
  assert.ok(product,`Public kapısı olmayan ürün KG'ye sızdı: ${node.sku}`);
  assert.match(node['@id'],/^https:\/\/www\.alo186\.com\/akilli-urun-secimi\/urun\//);
  assert.equal(node.sameAs,product.url);
  assert.match(node.sameAs,/^https:/);
  assert.ok(node.subjectOf&&node.subjectOf['@id'].endsWith('#webpage'));
  assert.ok(node.mainEntityOfPage&&node.mainEntityOfPage['@id'].endsWith('#webpage'));
  assert.ok(node.brand&&node.brand['@id']);
  assert.ok(node.category&&node.category['@id']);
  assert.ok(Array.isArray(node.additionalProperty)&&node.additionalProperty.length>0);
  assert.ok(node.identifier.some(item=>item.propertyID==='ASIN'));
  if(product.mpn){
    assert.equal(node.mpn,product.mpn);
    assert.ok(node.identifier.some(item=>item.propertyID==='MPN'&&item.value===product.mpn));
  }
  assert.ok(node.additionalProperty.some(item=>item.name==='Teknik doğrulama tarihi'));
  assert.ok(node.additionalProperty.some(item=>item.name==='Ticari ilişki'));
}
for(const product of gatedProducts)assert.ok(!productNodes.some(node=>node.sku===product.id),`Guide ürün public Product düğümüne sızdı: ${product.id}`);
const itemList=graph.find(node=>node['@type']==='ItemList');
assert.equal(itemList.numberOfItems,publicProducts.length);
assert.equal(itemList.itemListElement.length,publicProducts.length);
assert.ok(productNodes.some(node=>node.sku==='anker-737-a1289'&&node.mpn==='A1289'));
assert.ok(productNodes.some(node=>node.sku==='anker-a1383-20000-87w'&&node.mpn==='A1383'));

const stalePayload=catalog.knowledgeGraph({now:new Date('2026-09-20T12:00:00Z')});
assert.equal(stalePayload['@graph'].filter(node=>node['@type']==='Product').length,0);
const health=catalog.catalogHealth({now});
assert.equal(health.publicDirect,publicProducts.length);
assert.equal(health.gatedVerified,gatedProducts.length);
assert.equal(health.reviewBy,'2026-08-28');
assert.equal(health.staleAfter,'2026-09-13');
console.log(JSON.stringify({ok:true,affiliateTag:catalog.affiliateTag,totalProducts:catalog.products.length,publicProducts:productNodes.length,gatedProducts:gatedProducts.length},null,2));