'use strict';
const assert=require('node:assert/strict');
const catalog=require('./catalog-sales-extension.js');
const now=new Date('2026-07-30T12:00:00Z');

assert.equal(catalog.affiliateTag,'alo186rehber-21');
assert.equal(catalog.needs.length,18);
assert.equal(catalog.categories.length,18);
assert.equal(catalog.products.length,30);
assert.deepEqual(catalog.knowledgeGraphSummary({now}),{
  version:'2026-07-30-run50',generatedAt:'2026-07-30',needCount:18,categoryCount:18,
  productCount:30,exactListingCount:20,manufacturerSearchCount:10,
  publicProductCount:13,gatedCandidateCount:17,
  affiliatePolicies:['verified_direct','after_tool','professional_only']
});

const exact=catalog.products.filter(product=>product.status==='verified_listing');
const models=catalog.products.filter(product=>product.status==='manufacturer_verified_search');
assert.equal(exact.length,20);
assert.equal(models.length,10);
for(const product of exact){
  assert.match(product.asin,/^B[A-Z0-9]{9}$/);
  assert(product.url.includes(`/dp/${product.asin}`));
  assert(product.url.includes('tag=alo186rehber-21'));
  assert.equal(product.linkMode,'asin_detail');
  assert(product.needIds.length,`${product.id} ihtiyaç ilişkisi eksik`);
}

const a1289=catalog.getProduct('anker-737-a1289');
assert(a1289);
assert.equal(a1289.asin,'B09VPHVT2Z');
assert.equal(a1289.mpn,'A1289');
assert.equal(a1289.verifiedAt,'2026-07-30');
assert.equal(a1289.attributes.capacityMah,24000);
assert.equal(a1289.attributes.maxOutputW,140);
assert.equal(a1289.attributes.maxSingleDeviceW,140);
assert.equal(a1289.attributes.totalOutputW,140);
assert.match(a1289.sourceNote,/Anker teknik kaynaklarıyla/);
assert.equal(catalog.productLinkLabel(a1289),'Amazon ürün sayfasını aç');

const a1383=catalog.getProduct('anker-a1383-20k-87w');
assert(a1383);
assert.equal(a1383.asin,'B0CXDXP8VR');
assert.equal(a1383.mpn,'A1383');
assert.equal(a1383.verifiedAt,'2026-07-30');
assert.equal(a1383.attributes.capacityMah,20000);
assert.equal(a1383.attributes.maxOutputW,65,'Tek cihaz gücü 65 W olarak korunmalı.');
assert.equal(a1383.attributes.maxSingleDeviceW,65);
assert.equal(a1383.attributes.totalOutputW,87,'87 W yalnız toplam çoklu-port gücüdür.');
assert.match(a1383.sourceNote,/Anker teknik kaynağıyla/);
assert.equal(catalog.productLinkLabel(a1383),'Amazon ürün sayfasını aç');

const modelAdditions={
  'tp-link-tapo-p110':{source:'tp-link.com',maxCurrentA:16,maxPowerW:3680},
  'tp-link-tapo-p110m':{source:'tp-link.com',maxCurrentA:16,maxPowerW:3680,matter:true},
  'ecoflow-river-2':{source:'ecoflow.com.tr',capacityWh:256,continuousW:300},
  'x-sense-xs01':{source:'x-sense.com.tr',alarmDb:85,standard:'EN 14604'},
  'ugreen-nexode-100w-4port':{source:'ugreen.com',maxOutputW:100,usbCPorts:3},
  'tp-link-tapo-p115':{source:'tp-link.com',maxCurrentA:16,maxPowerW:3680},
  'tp-link-tapo-p115m':{source:'tp-link.com',maxCurrentA:16,maxPowerW:3680,matter:true},
  'ecoflow-river-2-max':{source:'ecoflow.com.tr',capacityWh:512,continuousW:500},
  'ecoflow-delta-2-max':{source:'ecoflow.com.tr',capacityWh:2048,continuousW:2400},
  'x-sense-xc01-r':{source:'x-sense.com.tr',alarmDb:85,sensor:'electrochemical'}
};
for(const[id,checks]of Object.entries(modelAdditions)){
  const product=catalog.getProduct(id);
  assert(product,id);
  assert.equal(product.asin,null);
  assert.equal(product.status,'manufacturer_verified_search');
  assert.equal(product.linkMode,'exact_model_search');
  assert(product.url.startsWith('https://www.amazon.com.tr/s?k='));
  assert(product.url.includes('tag=alo186rehber-21'));
  assert(product.technicalSource.includes(checks.source));
  assert(product.needIds.length);
  assert(product.relatedTools.length);
  assert(product.requiredEvidence.length>=3);
  for(const[key,value]of Object.entries(checks)){
    if(key==='source')continue;
    assert.equal(product.attributes[key],value,`${id}.${key}`);
  }
  assert.equal(catalog.productLinkLabel(product),'Amazon’da tam model araması');
}

assert.equal(catalog.productsFor('smart_plug').length,0,'Model arama düğümleri matcher tarafından doğrudan ürün sayılmamalı.');
assert.equal(catalog.allProductsFor('smart_plug').length,4);
assert.equal(catalog.allProductsFor('power_station').length,3);
assert.equal(catalog.graphForCategory('co_alarm').products.length,1);
for(const category of ['usb_c_charger','usb_c_cable','usb_c_hub','display_cable']){
  assert.equal(catalog.graphForCategory(category).needs.length,1,`${category} ihtiyaç düğümüne bağlanmalı`);
}

const publicProducts=catalog.products.filter(product=>catalog.publicAffiliateEligible(product,{now}));
const gatedProducts=catalog.products.filter(product=>catalog.isCatalogProduct(product)&&!catalog.publicAffiliateEligible(product,{now,freshOnly:false}));
assert.equal(publicProducts.length,13);
assert.equal(gatedProducts.length,17);
assert(publicProducts.includes(a1289));
assert(publicProducts.includes(a1383));
assert(!publicProducts.some(product=>product.status==='manufacturer_verified_search'));

const graph=catalog.knowledgeGraph({now})['@graph'];
const productNodes=graph.filter(node=>node['@type']==='Product');
const termNodes=graph.filter(node=>node['@type']==='DefinedTerm');
const candidateNodes=termNodes.filter(node=>node.inDefinedTermSet&&node.inDefinedTermSet['@id'].endsWith('/gated-product-candidates#termset'));
assert.equal(productNodes.length,13);
assert.equal(termNodes.length,53);
assert.equal(candidateNodes.length,17);
assert.equal(graph.filter(node=>node['@type']==='Offer').length,0);
for(const node of productNodes){
  assert(!('offers'in node));
  assert(!('aggregateRating'in node));
  assert(Array.isArray(node.identifier)&&node.identifier.some(item=>item.propertyID==='ASIN'));
  assert(catalog.publicAffiliateEligible(catalog.getProduct(node.sku),{now}));
}
for(const product of gatedProducts){
  assert(!productNodes.some(node=>node.sku===product.id),`Kapılı ürün Product schema'ya sızdı: ${product.id}`);
  assert(candidateNodes.some(node=>node.termCode===product.id),`Kapılı aday eksik: ${product.id}`);
}
for(const id of Object.keys(modelAdditions)){
  const node=candidateNodes.find(item=>item.termCode===id);
  assert(node&&node.sameAs,`${id} üretici kaynağı schema'da eksik`);
}
const itemList=graph.find(node=>node['@type']==='ItemList');
assert.equal(itemList.numberOfItems,13);
assert.equal(itemList.itemListElement.length,13);

const stale=catalog.knowledgeGraph({now:new Date('2027-01-01T12:00:00Z')})['@graph'];
assert.equal(stale.filter(node=>node['@type']==='Product').length,0);
assert.equal(stale.filter(node=>node['@type']==='DefinedTerm'&&node.inDefinedTermSet&&node.inDefinedTermSet['@id'].endsWith('/gated-product-candidates#termset')).length,0);

console.log(JSON.stringify({ok:true,affiliateTag:catalog.affiliateTag,needs:18,categories:18,totalProducts:30,publicProducts:13,gatedCandidates:17,exactAsins:20,manufacturerModels:10,newManufacturerModels:6,existingExactProductsEnriched:2},null,2));
