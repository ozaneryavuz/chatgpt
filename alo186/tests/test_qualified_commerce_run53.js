'use strict';
const assert=require('node:assert/strict');
const catalog=require('../urun-eslestirme/catalog-qualified-commerce-run53.js');

const now=new Date('2026-07-30T12:00:00Z');
const product=catalog.products.find((item)=>item.id==='ugreen-nexode-140w-90322');
assert.ok(product,'UGREEN 140 W ürün kaydı eksik.');
assert.equal(product.status,'verified_listing');
assert.equal(product.asin,'B0B127GW4D');
assert.equal(product.mpn,'90322');
assert.equal(product.category,'usb_c_charger');
assert.equal(product.attributes.maxSingleDeviceW,140);
assert.equal(product.attributes.totalOutputW,140);
assert.equal(product.attributes.usbCPorts,2);
assert.equal(product.attributes.usbAPorts,1);
assert.equal(product.attributes.pd31,true);
assert.equal(product.attributes.pps,true);
assert.equal(catalog.publicAffiliateEligible(product,{now}),true);
assert.match(product.url,/amazon\.com\.tr\/dp\/B0B127GW4D/);
assert.match(product.url,/[?&]tag=alo186rehber-21(?:&|$)/);

for(const forbidden of ['price','stock','rating','aggregateRating','review','seller','delivery','warranty','availability','offers']){
  assert.ok(!(forbidden in product),`Yasak ürün alanı: ${forbidden}`);
}

const payload=catalog.knowledgeGraph({now});
const graph=payload['@graph'];
const node=graph.find((item)=>item['@type']==='Product'&&item.sku===product.id);
assert.ok(node,'Yeni ürün Product Knowledge Graph içine alınmadı.');
assert.equal(node.sameAs,product.url);
assert.ok(node.identifier.some((item)=>item.propertyID==='ASIN'&&item.value==='B0B127GW4D'));
assert.ok(node.identifier.some((item)=>item.propertyID==='MPN'&&item.value==='90322'));
assert.ok(node.additionalProperty.some((item)=>item.name==='maxSingleDeviceW'&&item.value===140));
assert.ok(node.additionalProperty.some((item)=>item.name==='totalOutputW'&&item.value===140));
for(const forbidden of ['offers','price','priceCurrency','availability','aggregateRating','review','seller']){
  assert.ok(!(forbidden in node),`Yasak KG alanı: ${forbidden}`);
}

const directList=graph.find((item)=>item['@id']==='https://www.alo186.com/akilli-urun-secimi#direct-affiliate-products');
assert.ok(directList.itemListElement.some((item)=>item.item&&item.item['@id']===node['@id']));
const summary=catalog.knowledgeGraphSummary({now});
assert.equal(summary.version,'2026-07-30-run53');
assert.equal(summary.qualifiedCommerce.verifiedChargerAdded,product.id);
assert.equal(summary.qualifiedCommerce.directAffiliateLinksAdded,1);
assert.deepEqual(summary.qualifiedCommerce.commercialFieldsExcluded,['price','stock','rating','review','seller','delivery','warranty','availability']);

console.log(JSON.stringify({
  ok:true,
  product:product.id,
  asin:product.asin,
  singleDeviceW:product.attributes.maxSingleDeviceW,
  publicAffiliateEligible:true,
  offerNodes:graph.filter((item)=>item['@type']==='Offer').length
},null,2));
