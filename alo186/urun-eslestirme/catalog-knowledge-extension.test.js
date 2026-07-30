'use strict';
const assert=require('node:assert/strict');
const catalog=require('./catalog-growth-run7.js');
const now=new Date('2026-07-30T12:00:00Z');

assert.equal(catalog.affiliateTag,'alo186rehber-21');
assert.equal(catalog.needs.length,23);
assert.equal(catalog.categories.length,23);
assert.equal(catalog.products.length,55);
assert.deepEqual(catalog.knowledgeGraphSummary({now}),{
  version:'2026-07-30-run7-user-growth',generatedAt:'2026-07-30',needCount:23,categoryCount:23,
  productCount:55,exactListingCount:20,manufacturerSearchCount:35,
  publicProductCount:13,gatedCandidateCount:42,
  affiliatePolicies:['verified_direct','after_tool','professional_only']
});

const exact=catalog.products.filter(product=>product.status==='verified_listing');
const models=catalog.products.filter(product=>product.status==='manufacturer_verified_search');
assert.equal(exact.length,20);
assert.equal(models.length,35);
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

const modelChecks={
  'tp-link-tapo-p110':{source:'tp-link.com',maxCurrentA:16,maxPowerW:3680},
  'tp-link-tapo-p110m':{source:'tp-link.com',maxCurrentA:16,maxPowerW:3680,matter:true},
  'ecoflow-river-2':{source:'ecoflow.com.tr',capacityWh:256,continuousW:300},
  'x-sense-xs01':{source:'x-sense.com.tr',alarmDb:85,standard:'EN 14604'},
  'ugreen-nexode-100w-4port':{source:'ugreen.com',maxOutputW:100,usbCPorts:3},
  'tp-link-tapo-p115':{source:'tp-link.com',maxCurrentA:16,maxPowerW:3680},
  'tp-link-tapo-p115m':{source:'tp-link.com',maxCurrentA:16,maxPowerW:3680,matter:true},
  'ecoflow-river-2-max':{source:'ecoflow.com.tr',capacityWh:512,continuousW:500},
  'ecoflow-delta-2-max':{source:'ecoflow.com.tr',capacityWh:2048,continuousW:2400},
  'x-sense-xc01-r':{source:'x-sense.com.tr',alarmDb:85,sensor:'electrochemical'},
  'samsung-eb-p4520-20k-45w':{source:'samsung.com',capacityMah:20000,maxOutputW:45,usbCPorts:3},
  'ugreen-nexode-x-65w-3port':{source:'ugreen.com',maxOutputW:65,maxSingleDeviceW:65,usbCPorts:2},
  'ugreen-90440-240w-usb-c':{source:'ugreen.com',maxPowerW:240,maxCurrentA:5,videoSupport:false},
  'ecoflow-river-3':{source:'ecoflow.com.tr',capacityWh:245,continuousW:300,epsTransferMs:20},
  'ecoflow-river-3-plus':{source:'ecoflow.com.tr',capacityWh:286,continuousW:600,epsTransferMs:10},
  'ecoflow-delta-3-plus':{source:'ecoflow.com.tr',capacityWh:1024,continuousW:1800,surgeW:3600},
  'bluetti-ac70p':{source:'bluettipower.eu',capacityWh:864,continuousW:1000,powerLiftingW:2000},
  'honda-eu22i':{source:'honda.co.uk',ratedW:1800,maxW:2200,weightKg:21},
  'victron-phoenix-vedirect-12-1200':{source:'victronenergy.com',continuousW25C:1150,peakW:1600,transferSwitchBuiltIn:false},
  'x-sense-sc07-mr':{source:'x-sense.com.tr',alarmDb:85,standardSmoke:'EN 14604',standardCo:'EN 50291'},
  'anker-735-a2668-65w':{source:'anker.com',maxOutputW:65,singlePortMaxW:65,usbCPorts:2},
  'anker-341-a8346-hub':{source:'anker.com',ports:7,pdPassThroughW:85,maxResolution:'4K@30Hz'},
  'ugreen-90871-usbc-100w':{source:'ugreen.com',maxPowerW:100,maxCurrentA:5,eMarker:true},
  'anker-prime-a88e2-240w':{source:'anker.com',maxPowerW:240,usbPdEpr:true,video:false},
  'ugreen-50571-usbc-hdmi':{source:'ugreen.com',maxResolution:'4K@60Hz',direction:'USB-C source to HDMI display'},
  'apc-bx1600mi-gr':{source:'se.com',capacityVA:1600,capacityW:900,outletsSchuko:4,avr:true},
  'cyberpower-cp1500epfclcd':{source:'cyberpower.com',capacityVA:1500,capacityW:900,pureSine:true,activePfcCompatible:true},
  'fluke-117':{source:'fluke.com',trueRms:true,maxVoltageV:600,currentContinuousA:10,nonContactVoltage:true},
  'fluke-325':{source:'fluke.com',trueRms:true,acCurrentMaxA:400,dcCurrentMaxA:400,jawMaxMm:30},
  'flir-c5':{source:'flir.com',thermalResolution:'160x120',temperatureMaxC:400,radiometric:true,ipRating:'IP54'},
  'bosch-universaltemp-06036831z0':{source:'bosch-diy.com',temperatureMinC:-30,temperatureMaxC:500,opticalRatio:'12:1'},
  'ctek-mxs-5-0-eu':{source:'ctek.com',batteryVoltageV:12,chargingCurrentA:5,chargingCapacityAhMax:110,maintenanceCapacityAhMax:160},
  'noco-genius5':{source:'no.co',chargingCurrentA:5,capacityAhMax:120,ipRating:'IP65'},
  'bosch-procore18v-5-5ah-1600a02149':{source:'bosch-professional.com',voltageV:18,capacityAh:5.5,weightKg:0.955},
  'milwaukee-m18-hb5-5-4932464712':{source:'milwaukeetool.eu',voltageV:18,capacityAh:5.5,highOutput:true,redlink:true}
};
assert.equal(Object.keys(modelChecks).length,35);
for(const[id,checks]of Object.entries(modelChecks)){
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
assert.equal(catalog.allProductsFor('power_station').length,7);
assert.equal(catalog.allProductsFor('generator').length,1);
assert.equal(catalog.allProductsFor('inverter').length,1);
assert.equal(catalog.allProductsFor('smoke_alarm').length,2);
assert.ok(catalog.allProductsFor('usb_c_charger').some(product=>product.id==='anker-735-a2668-65w'));
assert.ok(catalog.allProductsFor('usb_c_cable').some(product=>product.id==='anker-prime-a88e2-240w'));
assert.ok(catalog.allProductsFor('usb_c_hub').some(product=>product.id==='anker-341-a8346-hub'));
assert.ok(catalog.allProductsFor('display_cable').some(product=>product.id==='ugreen-50571-usbc-hdmi'));
for(const category of ['computer_ups','multimeter','thermal_imager','battery_charger','tool_battery']){
  assert.equal(catalog.allProductsFor(category).length,2,`${category} iki kullanıcı odaklı model taşımalı`);
  assert.equal(catalog.graphForCategory(category).needs.length,1,`${category} ihtiyaç düğümüne bağlanmalı`);
  assert(catalog.categoryRelations[category].tools.length,`${category} ücretsiz araca bağlanmalı`);
}
for(const category of ['usb_c_charger','usb_c_cable','usb_c_hub','display_cable']){
  assert.equal(catalog.graphForCategory(category).needs.length,1,`${category} ihtiyaç düğümüne bağlanmalı`);
}
const combined=catalog.getProduct('x-sense-sc07-mr');
assert.deepEqual(combined.needIds,['fire-early-warning','carbon-monoxide-warning']);
assert(combined.relatedTools.length);
assert(combined.requiredEvidence.length>=4);

const publicProducts=catalog.products.filter(product=>catalog.publicAffiliateEligible(product,{now}));
const gatedProducts=catalog.products.filter(product=>catalog.isCatalogProduct(product)&&!catalog.publicAffiliateEligible(product,{now,freshOnly:false}));
assert.equal(publicProducts.length,13);
assert.equal(gatedProducts.length,42);
assert(publicProducts.includes(a1289));
assert(publicProducts.includes(a1383));
assert(!publicProducts.some(product=>product.status==='manufacturer_verified_search'));

const graph=catalog.knowledgeGraph({now})['@graph'];
const productNodes=graph.filter(node=>node['@type']==='Product');
const termNodes=graph.filter(node=>node['@type']==='DefinedTerm');
const candidateNodes=termNodes.filter(node=>node.inDefinedTermSet&&node.inDefinedTermSet['@id'].endsWith('/gated-product-candidates#termset'));
assert.equal(productNodes.length,13);
assert.equal(termNodes.length,88);
assert.equal(candidateNodes.length,42);
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
for(const id of Object.keys(modelChecks)){
  const node=candidateNodes.find(item=>item.termCode===id);
  assert(node&&node.sameAs,`${id} üretici kaynağı schema'da eksik`);
}
const itemList=graph.find(node=>node['@type']==='ItemList');
assert.equal(itemList.numberOfItems,13);
assert.equal(itemList.itemListElement.length,13);

const stale=catalog.knowledgeGraph({now:new Date('2027-01-01T12:00:00Z')})['@graph'];
assert.equal(stale.filter(node=>node['@type']==='Product').length,0);
assert.equal(stale.filter(node=>node['@type']==='DefinedTerm'&&node.inDefinedTermSet&&node.inDefinedTermSet['@id'].endsWith('/gated-product-candidates#termset')).length,0);

console.log(JSON.stringify({
  ok:true,affiliateTag:catalog.affiliateTag,needs:23,categories:23,totalProducts:55,
  publicProducts:13,gatedCandidates:42,exactAsins:20,manufacturerModels:35,
  run7ManufacturerModels:10,userJourneys:5
},null,2));
