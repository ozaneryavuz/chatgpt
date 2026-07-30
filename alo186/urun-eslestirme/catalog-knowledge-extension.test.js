'use strict';
const assert=require('node:assert/strict');
const base=require('./catalog.js');
const now=new Date('2026-07-30T12:00:00Z');
const baseCount=base.products.length;
const basePublicCount=base.products.filter(product=>base.publicAffiliateEligible(product,{now})).length;
assert(baseCount>=18,'Ana doğrulanmış ASIN kataloğu beklenenden küçük.');
assert.equal(base.affiliateTag,'alo186rehber-21');
const catalog=require('./catalog-sales-extension.js');
const summary=catalog.knowledgeGraphSummary({now});
assert.equal(catalog.needs.length,18);assert.equal(catalog.categories.length,18);assert.equal(catalog.products.length,baseCount+12);
assert.deepEqual(summary,{version:'2026-07-30-run50',generatedAt:'2026-07-30',needCount:18,categoryCount:18,productCount:baseCount+12,exactListingCount:baseCount+2,manufacturerSearchCount:10,publicProductCount:basePublicCount+2,gatedCandidateCount:(baseCount+12)-(basePublicCount+2),affiliatePolicies:['verified_direct','after_tool','professional_only']});
const exact=catalog.products.filter(product=>product.status==='verified_listing');const models=catalog.products.filter(product=>product.status==='manufacturer_verified_search');
assert.equal(exact.length,baseCount+2);assert.equal(models.length,10);
for(const product of exact){assert.match(product.asin,/^B[A-Z0-9]{9}$/);assert(product.url.includes(`/dp/${product.asin}`));assert(product.url.includes('tag=alo186rehber-21'));assert.equal(product.linkMode,'asin_detail');assert(product.needIds.length,`${product.id} ihtiyaç ilişkisi eksik`);}
const exactAdditions={'anker-737-a1289':{asin:'B09VPHVT2Z',capacityMah:24000,maxOutputW:140,source:'anker.com'},'anker-a1383-20k-87w':{asin:'B0CXDXP8VR',capacityMah:20000,maxOutputW:87,source:'anker.com'}};
for(const[id,expected]of Object.entries(exactAdditions)){const product=catalog.getProduct(id);assert(product,id);assert.equal(product.asin,expected.asin);assert.equal(product.status,'verified_listing');assert.equal(product.verifiedAt,'2026-07-30');assert.equal(product.attributes.capacityMah,expected.capacityMah);assert.equal(product.attributes.maxOutputW,expected.maxOutputW);assert(product.technicalSource.includes(expected.source));assert.equal(catalog.productLinkLabel(product),'Amazon ürün sayfasını aç');}
const modelAdditions={
 'tp-link-tapo-p110':{category:'smart_plug',source:'tp-link.com',maxCurrentA:16,maxPowerW:3680},
 'tp-link-tapo-p110m':{category:'smart_plug',source:'tp-link.com',maxCurrentA:16,maxPowerW:3680,matter:true},
 'ecoflow-river-2':{category:'power_station',source:'ecoflow.com.tr',capacityWh:256,continuousW:300},
 'x-sense-xs01':{category:'smoke_alarm',source:'x-sense.com.tr',alarmDb:85,standard:'EN 14604'},
 'ugreen-nexode-100w-4port':{category:'usb_c_charger',source:'ugreen.com',maxOutputW:100,usbCPorts:3},
 'tp-link-tapo-p115':{category:'smart_plug',source:'tp-link.com',maxCurrentA:16,maxPowerW:3680},
 'tp-link-tapo-p115m':{category:'smart_plug',source:'tp-link.com',maxCurrentA:16,maxPowerW:3680,matter:true},
 'ecoflow-river-2-max':{category:'power_station',source:'ecoflow.com.tr',capacityWh:512,continuousW:500},
 'ecoflow-delta-2-max':{category:'power_station',source:'ecoflow.com.tr',capacityWh:2048,continuousW:2400},
 'x-sense-xc01-r':{category:'co_alarm',source:'x-sense.com.tr',alarmDb:85,sensor:'electrochemical'}
};
for(const[id,checks]of Object.entries(modelAdditions)){const product=catalog.getProduct(id);assert(product,id);assert.equal(product.asin,null);assert.equal(product.status,'manufacturer_verified_search');assert.equal(product.linkMode,'exact_model_search');assert(product.url.startsWith('https://www.amazon.com.tr/s?k='));assert(product.url.includes('tag=alo186rehber-21'));assert(product.technicalSource.includes(checks.source));assert(product.needIds.length);assert(product.relatedTools.length);assert(product.requiredEvidence.length>=3);for(const[key,value]of Object.entries(checks)){if(['category','source'].includes(key))continue;assert.equal(product.attributes[key],value,`${id}.${key}`);}assert.equal(catalog.productLinkLabel(product),'Amazon’da tam model araması');}
assert.equal(catalog.productsFor('smart_plug').length,0,'Üretici arama düğümleri matcher tarafından doğrudan ürün sayılmamalı.');assert.equal(catalog.allProductsFor('smart_plug').length,4);assert.equal(catalog.allProductsFor('power_station').length,4);assert.equal(catalog.graphForCategory('co_alarm').products.length,1);
for(const category of ['usb_c_charger','usb_c_cable','usb_c_hub','display_cable'])assert.equal(catalog.graphForCategory(category).needs.length,1,`${category} ihtiyaç düğümüne bağlanmalı`);
const publicProducts=catalog.products.filter(product=>catalog.publicAffiliateEligible(product,{now}));const gatedProducts=catalog.products.filter(product=>catalog.isCatalogProduct(product)&&!catalog.publicAffiliateEligible(product,{now,freshOnly:false}));
assert.equal(publicProducts.length,basePublicCount+2);assert.equal(gatedProducts.length,catalog.products.length-publicProducts.length);assert(publicProducts.some(product=>product.id==='anker-737-a1289'));assert(publicProducts.some(product=>product.id==='anker-a1383-20k-87w'));assert(!publicProducts.some(product=>product.status==='manufacturer_verified_search'));
const graph=catalog.knowledgeGraph({now})['@graph'];const productNodes=graph.filter(node=>node['@type']==='Product');const termNodes=graph.filter(node=>node['@type']==='DefinedTerm');const candidateNodes=termNodes.filter(node=>node.inDefinedTermSet&&node.inDefinedTermSet['@id'].endsWith('/gated-product-candidates#termset'));
assert.equal(productNodes.length,publicProducts.length);assert.equal(termNodes.length,18+18+gatedProducts.length);assert.equal(candidateNodes.length,gatedProducts.length);assert.equal(graph.filter(node=>node['@type']==='Offer').length,0);
for(const node of productNodes){assert(!('offers'in node));assert(!('aggregateRating'in node));assert(Array.isArray(node.identifier)&&node.identifier.some(item=>item.propertyID==='ASIN'));assert(catalog.publicAffiliateEligible(catalog.getProduct(node.sku),{now}));}
for(const product of gatedProducts){assert(!productNodes.some(node=>node.sku===product.id),`Kapılı ürün Product schema'ya sızdı: ${product.id}`);assert(candidateNodes.some(node=>node.termCode===product.id),`Kapılı aday eksik: ${product.id}`);}
for(const id of Object.keys(modelAdditions)){const node=candidateNodes.find(item=>item.termCode===id);assert(node&&node.sameAs,`${id} üretici kaynağı schema'da eksik`);}
const itemList=graph.find(node=>node['@type']==='ItemList');assert.equal(itemList.numberOfItems,publicProducts.length);assert.equal(itemList.itemListElement.length,publicProducts.length);
const stale=catalog.knowledgeGraph({now:new Date('2027-01-01T12:00:00Z')})['@graph'];assert.equal(stale.filter(node=>node['@type']==='Product').length,0);assert.equal(stale.filter(node=>node['@type']==='DefinedTerm'&&node.inDefinedTermSet&&node.inDefinedTermSet['@id'].endsWith('/gated-product-candidates#termset')).length,0);
const audit=catalog.knowledgeGraph({now:new Date('2027-01-01T12:00:00Z'),freshOnly:false})['@graph'];assert.equal(audit.filter(node=>node['@type']==='Product').length,publicProducts.length);assert.equal(audit.filter(node=>node['@type']==='DefinedTerm'&&node.inDefinedTermSet&&node.inDefinedTermSet['@id'].endsWith('/gated-product-candidates#termset')).length,gatedProducts.length);
console.log(JSON.stringify({ok:true,affiliateTag:catalog.affiliateTag,needs:18,categories:18,totalProducts:catalog.products.length,publicProducts:publicProducts.length,gatedCandidates:gatedProducts.length,exactAsins:exact.length,manufacturerModels:models.length,newProducts:8},null,2));
