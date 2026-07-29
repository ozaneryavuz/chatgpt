'use strict';
const assert=require('node:assert/strict');
const base=require('./catalog.js');
assert.equal(base.products.length,10,'Ana katalogdaki 10 ASIN düğümü korunmalı.');
assert.equal(base.affiliateTag,'alo186rehber-21');
const catalog=require('./catalog-knowledge-extension.js');
assert.equal(catalog.products.length,14);
assert.equal(catalog.needs.length,14);
assert.equal(catalog.categories.length,14);
assert.deepEqual(catalog.knowledgeGraphSummary(),{version:'2026-07-29-run34b',generatedAt:'2026-07-29',needCount:14,categoryCount:14,productCount:14,exactListingCount:10,manufacturerSearchCount:4,affiliatePolicies:['verified_direct','after_tool','professional_only']});
const exact=catalog.products.filter(product=>product.status==='verified_listing');
const models=catalog.products.filter(product=>product.status==='manufacturer_verified_search');
assert.equal(exact.length,10);assert.equal(models.length,4);
for(const product of exact){assert.match(product.asin,/^B[A-Z0-9]{9}$/);assert(product.url.includes(`/dp/${product.asin}`));assert(product.url.includes('tag=alo186rehber-21'));assert.equal(product.linkMode,'asin_detail');}
const expected={
 'tp-link-tapo-p110':{category:'smart_plug',source:'tp-link.com',maxCurrentA:16,maxPowerW:3680},
 'tp-link-tapo-p110m':{category:'smart_plug',source:'tp-link.com',maxCurrentA:16,maxPowerW:3680,matter:true},
 'ecoflow-river-2':{category:'power_station',source:'ecoflow.com.tr',capacityWh:256,continuousW:300,pureSine:true},
 'x-sense-xs01':{category:'smoke_alarm',source:'x-sense.com.tr',alarmDb:85,standard:'EN 14604'}
};
for(const[id,checks]of Object.entries(expected)){const product=catalog.getProduct(id);assert(product,id);assert.equal(product.asin,null);assert.equal(product.linkMode,'exact_model_search');assert(product.url.startsWith('https://www.amazon.com.tr/s?k='));assert(product.url.includes('tag=alo186rehber-21'));assert(product.technicalSource.includes(checks.source));assert(product.needIds.length);assert(product.relatedTools.length);assert(product.requiredEvidence.length>=3);for(const[key,value]of Object.entries(checks)){if(['category','source'].includes(key))continue;assert.equal(product.attributes[key],value,`${id}.${key}`);}assert.equal(catalog.productLinkLabel(product),'Amazon’da tam model araması');}
assert.equal(catalog.productsFor('smart_plug').length,0,'Mevcut matcher davranışı üretici arama düğümlerini doğrudan eşleştirmemeli.');
assert.equal(catalog.allProductsFor('smart_plug').length,2);
assert.equal(catalog.graphForCategory('power_station').products.length,1);
const payload=catalog.knowledgeGraph({now:new Date('2026-07-29T12:00:00Z')});
const graph=payload['@graph'];
const productNodes=graph.filter(node=>node['@type']==='Product');
assert.equal(productNodes.length,14);
assert.equal(graph.filter(node=>node['@type']==='DefinedTerm').length,28);
assert.equal(graph.filter(node=>node['@type']==='Offer').length,0);
for(const node of productNodes){assert(!('offers'in node));assert(!('aggregateRating'in node));assert(Array.isArray(node.identifier)&&node.identifier.length);assert(Array.isArray(node.isRelatedTo)&&node.isRelatedTo.length);}
for(const id of Object.keys(expected)){const node=productNodes.find(item=>item['@id'].endsWith(`/${id}#product`));assert(node&&node.sameAs);assert(node.identifier.some(item=>item.propertyID==='Model'));}
console.log(JSON.stringify({ok:true,affiliateTag:catalog.affiliateTag,needs:14,categories:14,products:14,exactAsins:10,manufacturerModels:4},null,2));
