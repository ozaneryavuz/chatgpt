'use strict';
const assert=require('node:assert/strict');
const catalog=require('../urun-eslestirme/catalog.js');

assert.equal(catalog.affiliateTag,'alo186rehber-21');
assert.equal(catalog.verifiedAt,'2026-07-29');
assert.ok(catalog.products.length>=10);

const ids=new Set();
const asins=new Set();
for(const product of catalog.products){
  assert.ok(product.id&&!ids.has(product.id),`Tekrarlanan ürün id: ${product.id}`);ids.add(product.id);
  assert.ok(product.asin&&!asins.has(product.asin),`Tekrarlanan ASIN: ${product.asin}`);asins.add(product.asin);
  assert.match(product.url,/amazon\.com\.tr\/dp\//);
  assert.match(product.url,/[?&]tag=alo186rehber-21(?:&|$)/);
  assert.ok(product.brand&&product.category&&product.name);
  assert.equal(product.status,'verified_listing');
}
for(const id of ['philips-spn7040wa-62','tuncmatik-tsk6134','brennenstuhl-eco-line-6'])assert.ok(ids.has(id),`Yeni ürün eksik: ${id}`);

const now=new Date('2026-07-29T12:00:00Z');
const publicProducts=catalog.products.filter(product=>catalog.publicAffiliateEligible(product,{now}));
const gatedProducts=catalog.products.filter(product=>!catalog.publicAffiliateEligible(product,{now,freshOnly:false}));
assert.ok(publicProducts.length>0);
assert.ok(gatedProducts.length>0);
assert.deepEqual(new Set(publicProducts.map(product=>product.category)),new Set(['powerbank']));
for(const product of publicProducts){
  const category=catalog.getCategory(product.category);
  assert.equal(category.mode,'direct');
  assert.equal(category.affiliatePolicy,'verified_direct');
}
for(const product of gatedProducts){
  const category=catalog.getCategory(product.category);
  assert.ok(category.mode!=='direct'||category.affiliatePolicy!=='verified_direct');
}

const payload=catalog.knowledgeGraph({now});
assert.equal(payload['@context'],'https://schema.org');
assert.ok(Array.isArray(payload['@graph']));
const graph=payload['@graph'];
const types=new Set(graph.flatMap(node=>Array.isArray(node['@type'])?node['@type']:[node['@type']]));
for(const type of ['Organization','WebSite','DefinedTermSet','DefinedTerm','Brand','ItemList','Product'])assert.ok(types.has(type),`KG türü eksik: ${type}`);
const productNodes=graph.filter(node=>node['@type']==='Product');
assert.equal(productNodes.length,publicProducts.length);
assert.equal(graph.filter(node=>node['@type']==='Brand').length,new Set(publicProducts.map(product=>product.brand)).size);
assert.equal(graph.filter(node=>node['@type']==='Offer').length,0);
for(const node of graph){
  for(const forbidden of ['offers','aggregateRating','review','price','priceCurrency','availability','seller'])assert.ok(!(forbidden in node),`Yasak ticari alan: ${forbidden}`);
}
for(const product of publicProducts){
  const node=productNodes.find(item=>item.sku===product.id);
  assert.ok(node,`Doğrudan ürün grafikte eksik: ${product.id}`);
  assert.match(node['@id'],/^https:\/\/www\.alo186\.com\/akilli-urun-secimi\/urun\//);
  assert.ok(node.subjectOf&&node.subjectOf['@id'].endsWith('#webpage'));
  assert.ok(node.mainEntityOfPage&&node.mainEntityOfPage['@id'].endsWith('#webpage'));
  assert.ok(node.brand&&node.brand['@id']);
  assert.ok(node.category&&node.category['@id']);
  assert.ok(Array.isArray(node.additionalProperty)&&node.additionalProperty.length>0);
  assert.ok(node.identifier.some(item=>item.propertyID==='ASIN'&&item.value===product.asin));
}
for(const product of gatedProducts){
  assert.ok(!productNodes.some(node=>node.sku===product.id),`Araç kapısı arkasındaki ürün public Product grafiğine sızdı: ${product.id}`);
}
const itemList=graph.find(node=>node['@type']==='ItemList');
assert.equal(itemList.numberOfItems,publicProducts.length);
assert.equal(itemList.itemListElement.length,publicProducts.length);
assert.deepEqual(itemList.itemListElement.map(item=>item.position),publicProducts.map((_,index)=>index+1));

const staleGraph=catalog.knowledgeGraph({now:new Date('2027-01-01T12:00:00Z')});
assert.equal(staleGraph['@graph'].filter(node=>node['@type']==='Product').length,0);
assert.equal(staleGraph['@graph'].find(node=>node['@type']==='ItemList').numberOfItems,0);

const auditGraph=catalog.knowledgeGraph({now:new Date('2027-01-01T12:00:00Z'),freshOnly:false});
const auditProducts=auditGraph['@graph'].filter(node=>node['@type']==='Product');
assert.equal(auditProducts.length,publicProducts.length);
for(const product of gatedProducts)assert.ok(!auditProducts.some(node=>node.sku===product.id));

console.log(JSON.stringify({ok:true,totalProducts:catalog.products.length,publicProducts:publicProducts.length,gatedProducts:gatedProducts.length,graphNodes:graph.length},null,2));
