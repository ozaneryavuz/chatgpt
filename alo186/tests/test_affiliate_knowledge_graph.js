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

const payload=catalog.knowledgeGraph({now:new Date('2026-07-29T12:00:00Z')});
assert.equal(payload['@context'],'https://schema.org');
assert.ok(Array.isArray(payload['@graph']));
const graph=payload['@graph'];
const types=new Set(graph.flatMap(node=>Array.isArray(node['@type'])?node['@type']:[node['@type']]));
for(const type of ['Organization','WebSite','DefinedTermSet','DefinedTerm','Brand','ItemList','Product'])assert.ok(types.has(type),`KG türü eksik: ${type}`);
const productNodes=graph.filter(node=>node['@type']==='Product');
assert.equal(productNodes.length,catalog.products.length);
assert.equal(graph.filter(node=>node['@type']==='Brand').length,new Set(catalog.products.map(p=>p.brand)).size);
assert.equal(graph.filter(node=>node['@type']==='Offer').length,0);
for(const node of graph){
  for(const forbidden of ['offers','aggregateRating','review','price','priceCurrency','availability','seller'])assert.ok(!(forbidden in node),`Yasak ticari alan: ${forbidden}`);
}
for(const node of productNodes){
  assert.match(node['@id'],/^https:\/\/www\.alo186\.com\/akilli-urun-secimi\/urun\//);
  assert.ok(node.subjectOf&&node.subjectOf['@id'].endsWith('#webpage'));
  assert.ok(node.mainEntityOfPage&&node.mainEntityOfPage['@id'].endsWith('#webpage'));
  assert.ok(node.brand&&node.brand['@id']);
  assert.ok(node.category&&node.category['@id']);
  assert.ok(Array.isArray(node.additionalProperty)&&node.additionalProperty.length>0);
  assert.ok(node.identifier.some(item=>item.propertyID==='ASIN'));
}
const itemList=graph.find(node=>node['@type']==='ItemList');
assert.equal(itemList.numberOfItems,catalog.products.length);
assert.equal(itemList.itemListElement.length,catalog.products.length);
console.log(JSON.stringify({ok:true,affiliateTag:catalog.affiliateTag,products:catalog.products.length,graphNodes:graph.length,productNodes:productNodes.length},null,2));
