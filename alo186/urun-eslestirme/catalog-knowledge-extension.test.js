'use strict';
const assert=require('node:assert/strict');
const base=require('./catalog.js');
assert.equal(base.products.length,24,'Ana katalogdaki 24 doğrulanmış ASIN düğümü korunmalı.');
assert.equal(base.affiliateTag,'alo186rehber-21');
const catalog=require('../akilli-urun-secimi/catalog-knowledge-extension.js');
assert.equal(catalog.products.length,28);
assert.equal(catalog.needs.length,19);
assert.equal(catalog.categories.length,18);
assert.deepEqual(catalog.knowledgeGraphSummary(),{version:'2026-07-29-run39',generatedAt:'2026-07-29',needCount:19,categoryCount:18,productCount:28,exactListingCount:24,manufacturerSearchCount:4,publicProductCount:17,gatedCandidateCount:11,affiliatePolicies:['verified_direct','after_tool','professional_only']});
const exact=catalog.products.filter(product=>product.status==='verified_listing');
const models=catalog.products.filter(product=>product.status==='manufacturer_verified_search');
assert.equal(exact.length,24);assert.equal(models.length,4);
for(const product of exact){assert.match(product.asin,/^B[A-Z0-9]{9}$/);assert(product.url.includes(`/dp/${product.asin}`));assert(product.url.includes('tag=alo186rehber-21'));assert.equal(product.linkMode,'asin_detail');assert(product.needIds.length,`${product.id} ihtiyaç ilişkisi eksik`);}
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
for(const category of ['usb_c_charger','usb_c_cable','usb_c_hub'])assert.equal(catalog.graphForCategory(category).needs.length,1,`${category} ihtiyaç düğümüne bağlanmalı`);
assert.deepEqual(new Set(catalog.graphForCategory('display_cable').needs.map(need=>need.id)),new Set(['usb-c-display-output','display-link-compatibility']));
const usbDisplayIds=['ugreen-usbc-dp14-2m','ugreen-usbc-dp14-3m','daytona-hc01-usbc-hdmi-18m'];
const nativeDisplayIds=['ugreen-dp14-2m','ugreen-hdmi21-3m'];
for(const id of usbDisplayIds){const product=catalog.getProduct(id);assert.deepEqual(product.needIds,['usb-c-display-output']);assert(product.relatedTools.includes('/hesaplama/usb-c-urun-kabul-testi/'));assert(product.requiredEvidence.some(item=>item.includes('Alt Mode')));}
for(const id of nativeDisplayIds){const product=catalog.getProduct(id);assert.deepEqual(product.needIds,['display-link-compatibility']);assert(!product.relatedTools.includes('/hesaplama/usb-c-urun-kabul-testi/'));assert(!product.requiredEvidence.some(item=>item.includes('Alt Mode')));assert(product.requiredEvidence.some(item=>item.includes('konektör')));}
const now=new Date('2026-07-29T12:00:00Z');
const publicProducts=catalog.products.filter(product=>catalog.publicAffiliateEligible(product,{now}));
const gatedProducts=catalog.products.filter(product=>catalog.isCatalogProduct(product)&&!catalog.publicAffiliateEligible(product,{now,freshOnly:false}));
assert.equal(publicProducts.length,17);
assert.deepEqual(new Set(publicProducts.map(product=>product.category)),new Set(['powerbank','usb_c_charger','usb_c_cable','usb_c_hub','display_cable']));
assert.equal(gatedProducts.length,11);
const payload=catalog.knowledgeGraph({now});
const graph=payload['@graph'];
const productNodes=graph.filter(node=>node['@type']==='Product');
const termNodes=graph.filter(node=>node['@type']==='DefinedTerm');
const candidateNodes=termNodes.filter(node=>node.inDefinedTermSet&&node.inDefinedTermSet['@id'].endsWith('/gated-product-candidates#termset'));
assert.equal(productNodes.length,17);
assert.equal(termNodes.length,48);
assert.equal(candidateNodes.length,11);
assert.equal(graph.filter(node=>node['@type']==='Offer').length,0);
for(const node of productNodes){assert(!('offers'in node));assert(!('aggregateRating'in node));assert(Array.isArray(node.identifier)&&node.identifier.some(item=>item.propertyID==='ASIN'));assert(Array.isArray(node.isRelatedTo)&&node.isRelatedTo.length);const product=catalog.getProduct(node.sku);assert(catalog.publicAffiliateEligible(product,{now}));}
for(const product of gatedProducts){assert(!productNodes.some(node=>node.sku===product.id),`Kapılı ürün Product schema'ya sızdı: ${product.id}`);assert(candidateNodes.some(node=>node.termCode===product.id),`Kapılı aday DefinedTerm olarak eksik: ${product.id}`);}
for(const id of Object.keys(expected)){const node=candidateNodes.find(item=>item.termCode===id);assert(node&&node.sameAs);assert(node.additionalProperty.some(item=>item.name==='Model'));}
const itemList=graph.find(node=>node['@type']==='ItemList');
assert.equal(itemList.numberOfItems,17);
assert.equal(itemList.itemListElement.length,17);
const stale=catalog.knowledgeGraph({now:new Date('2027-01-01T12:00:00Z')})['@graph'];
assert.equal(stale.filter(node=>node['@type']==='Product').length,0);
assert.equal(stale.filter(node=>node['@type']==='DefinedTerm'&&node.inDefinedTermSet&&node.inDefinedTermSet['@id'].endsWith('/gated-product-candidates#termset')).length,0);
const audit=catalog.knowledgeGraph({now:new Date('2027-01-01T12:00:00Z'),freshOnly:false})['@graph'];
assert.equal(audit.filter(node=>node['@type']==='Product').length,17);
assert.equal(audit.filter(node=>node['@type']==='DefinedTerm'&&node.inDefinedTermSet&&node.inDefinedTermSet['@id'].endsWith('/gated-product-candidates#termset')).length,11);
console.log(JSON.stringify({ok:true,affiliateTag:catalog.affiliateTag,needs:19,categories:18,totalProducts:28,publicProducts:17,gatedCandidates:11,exactAsins:24,manufacturerModels:4,connectorSpecificDisplayRelations:true},null,2));
