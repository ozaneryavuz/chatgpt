'use strict';
const assert=require('node:assert/strict');
const base=require('./catalog.js');
const summaryNow=new Date('2026-07-29T12:00:00Z');
const baseExactCount=base.products.filter(product=>product.status==='verified_listing').length;
const basePublicCount=base.products.filter(product=>base.publicAffiliateEligible(product,{now:summaryNow})).length;
assert(baseExactCount>=24,`Ana katalog en az 24 doğrulanmış ASIN düğümü içermeli; bulunan=${baseExactCount}`);
assert(basePublicCount>=17,`Ana katalog en az 17 doğrudan düşük riskli ürün içermeli; bulunan=${basePublicCount}`);
assert.equal(base.affiliateTag,'alo186rehber-21');
const catalog=require('../akilli-urun-secimi/catalog-knowledge-extension.js');
const expectedManufacturerCount=4;
const expectedTotalCount=baseExactCount+expectedManufacturerCount;
const expectedGatedCount=expectedTotalCount-basePublicCount;
assert.equal(catalog.products.length,expectedTotalCount);
assert.equal(catalog.needs.length,19);
assert.equal(catalog.categories.length,18);
assert.deepEqual(catalog.knowledgeGraphSummary(),{version:'2026-07-29-run39',generatedAt:'2026-07-29',needCount:19,categoryCount:18,productCount:expectedTotalCount,exactListingCount:baseExactCount,manufacturerSearchCount:expectedManufacturerCount,publicProductCount:basePublicCount,gatedCandidateCount:expectedGatedCount,affiliatePolicies:['verified_direct','after_tool','professional_only']});
const exact=catalog.products.filter(product=>product.status==='verified_listing');
const models=catalog.products.filter(product=>product.status==='manufacturer_verified_search');
assert.equal(exact.length,baseExactCount);assert.equal(models.length,expectedManufacturerCount);
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
const publicProducts=catalog.products.filter(product=>catalog.publicAffiliateEligible(product,{now:summaryNow}));
const gatedProducts=catalog.products.filter(product=>catalog.isCatalogProduct(product)&&!catalog.publicAffiliateEligible(product,{now:summaryNow,freshOnly:false}));
assert.equal(publicProducts.length,basePublicCount);
assert.deepEqual(new Set(publicProducts.map(product=>product.category)),new Set(['powerbank','usb_c_charger','usb_c_cable','usb_c_hub','display_cable']));
assert.equal(gatedProducts.length,expectedGatedCount);
const payload=catalog.knowledgeGraph({now:summaryNow});
const graph=payload['@graph'];
const productNodes=graph.filter(node=>node['@type']==='Product');
const termNodes=graph.filter(node=>node['@type']==='DefinedTerm');
const candidateNodes=termNodes.filter(node=>node.inDefinedTermSet&&node.inDefinedTermSet['@id'].endsWith('/gated-product-candidates#termset'));
assert.equal(productNodes.length,basePublicCount);
assert.equal(termNodes.length,catalog.needs.length+catalog.categories.length+expectedGatedCount);
assert.equal(candidateNodes.length,expectedGatedCount);
assert.equal(graph.filter(node=>node['@type']==='Offer').length,0);
for(const node of productNodes){assert(!('offers'in node));assert(!('aggregateRating'in node));assert(Array.isArray(node.identifier)&&node.identifier.some(item=>item.propertyID==='ASIN'));assert(Array.isArray(node.isRelatedTo)&&node.isRelatedTo.length);const product=catalog.getProduct(node.sku);assert(catalog.publicAffiliateEligible(product,{now:summaryNow}));}
for(const product of gatedProducts){assert(!productNodes.some(node=>node.sku===product.id),`Kapılı ürün Product schema'ya sızdı: ${product.id}`);assert(candidateNodes.some(node=>node.termCode===product.id),`Kapılı aday DefinedTerm olarak eksik: ${product.id}`);}
for(const id of Object.keys(expected)){const node=candidateNodes.find(item=>item.termCode===id);assert(node&&node.sameAs);assert(node.additionalProperty.some(item=>item.name==='Model'));}
const itemList=graph.find(node=>node['@type']==='ItemList');
assert.equal(itemList.numberOfItems,basePublicCount);
assert.equal(itemList.itemListElement.length,basePublicCount);
const stale=catalog.knowledgeGraph({now:new Date('2027-01-01T12:00:00Z')})['@graph'];
assert.equal(stale.filter(node=>node['@type']==='Product').length,0);
assert.equal(stale.filter(node=>node['@type']==='DefinedTerm'&&node.inDefinedTermSet&&node.inDefinedTermSet['@id'].endsWith('/gated-product-candidates#termset')).length,0);
const audit=catalog.knowledgeGraph({now:new Date('2027-01-01T12:00:00Z'),freshOnly:false})['@graph'];
assert.equal(audit.filter(node=>node['@type']==='Product').length,basePublicCount);
assert.equal(audit.filter(node=>node['@type']==='DefinedTerm'&&node.inDefinedTermSet&&node.inDefinedTermSet['@id'].endsWith('/gated-product-candidates#termset')).length,expectedGatedCount);
console.log(JSON.stringify({ok:true,affiliateTag:catalog.affiliateTag,needs:catalog.needs.length,categories:catalog.categories.length,totalProducts:expectedTotalCount,publicProducts:basePublicCount,gatedCandidates:expectedGatedCount,exactAsins:baseExactCount,manufacturerModels:expectedManufacturerCount,connectorSpecificDisplayRelations:true},null,2));
