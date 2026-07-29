'use strict';
const assert=require('node:assert/strict');
const catalog=require('../urun-eslestirme/catalog.js');

assert.equal(catalog.affiliateTag,'alo186rehber-21');
assert.equal(catalog.verifiedAt,'2026-07-29');
assert.ok(catalog.products.length>=16);

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
for(const id of ['philips-spn7040wa-62','tuncmatik-tsk6134','brennenstuhl-eco-line-6','anker-313-a2677','baseus-cafule-catklf-gg1','baseus-crystal-shine-100w-2m','ugreen-7in1-60515','anker-555-8in1','ugreen-usbc-dp14-2m','ugreen-usbc-dp14-3m'])assert.ok(ids.has(id),`Yeni ürün eksik: ${id}`);

const now=new Date('2026-07-29T12:00:00Z');
const verifiedProducts=catalog.products.filter(product=>product.status==='verified_listing'&&catalog.verificationStatus(product,now).fresh);
const publicProducts=verifiedProducts.filter(product=>catalog.publicAffiliateEligible(product,{now}));
const gatedProducts=verifiedProducts.filter(product=>!catalog.publicAffiliateEligible(product,{now,freshOnly:false}));
assert.deepEqual([...new Set(publicProducts.map(product=>product.category))],['powerbank','usb_c_charger','usb_c_cable','usb_c_hub','display_cable']);
assert.ok(gatedProducts.some(product=>product.category==='surge_strip'));

const payload=catalog.knowledgeGraph({now});
assert.equal(payload['@context'],'https://schema.org');
assert.ok(Array.isArray(payload['@graph']));
const graph=payload['@graph'];
const types=new Set(graph.flatMap(node=>Array.isArray(node['@type'])?node['@type']:[node['@type']]));
for(const type of ['Organization','WebSite','DefinedTermSet','DefinedTerm','Brand','ItemList','Product','ProductGroup'])assert.ok(types.has(type),`KG türü eksik: ${type}`);
const productNodes=graph.filter(node=>node['@type']==='Product');
const productGroupNodes=graph.filter(node=>node['@type']==='ProductGroup');
assert.equal(productNodes.length,verifiedProducts.length);
assert.equal(productGroupNodes.length,2);
assert.equal(graph.filter(node=>node['@type']==='Brand').length,new Set(verifiedProducts.map(p=>p.brand)).size);
assert.equal(graph.filter(node=>node['@type']==='Offer').length,0);
for(const node of graph){
  for(const forbidden of ['offers','aggregateRating','review','price','priceCurrency','availability','seller'])assert.ok(!(forbidden in node),`Yasak ticari alan: ${forbidden}`);
}
for(const node of productNodes){
  const product=verifiedProducts.find(item=>item.id===node.sku);
  assert.ok(product,`Doğrulanmamış ürün KG'ye sızdı: ${node.sku}`);
  assert.match(node['@id'],/^https:\/\/www\.alo186\.com\/akilli-urun-secimi\/urun\//);
  assert.ok(node.subjectOf&&node.subjectOf['@id'].endsWith('#webpage'));
  assert.ok(node.mainEntityOfPage&&node.mainEntityOfPage['@id'].endsWith('#webpage'));
  assert.ok(node.brand&&node.brand['@id']);
  assert.ok(node.category&&node.category['@id']);
  assert.ok(Array.isArray(node.additionalProperty)&&node.additionalProperty.length>0);
  assert.ok(node.identifier.some(item=>item.propertyID==='ASIN'));
  assert.ok(node.additionalProperty.some(item=>item.name==='Teknik doğrulama tarihi'));
  assert.ok(node.additionalProperty.some(item=>item.name==='Ticari ilişki'));
  if(product.variantGroup)assert.ok(node.isVariantOf&&node.isVariantOf['@id'].includes(product.variantGroup));
  if(publicProducts.some(item=>item.id===product.id)){
    assert.equal(node.sameAs,product.url);
    assert.match(node.sameAs,/^https:/);
    assert.ok(!node.potentialAction);
  }else{
    assert.ok(!('sameAs' in node),`Teknik kapılı ürünün affiliate URL'si schema içine sızdı: ${node.sku}`);
    assert.equal(node.potentialAction['@type'],'ViewAction');
    assert.match(node.potentialAction.target,/^https:\/\/www\.alo186\.com\//);
  }
}
for(const id of ['anker-313-a2677','baseus-cafule-catklf-gg1','ugreen-7in1-60515','ugreen-usbc-dp14-2m']){
  const node=productNodes.find(item=>item.sku===id);
  assert.ok(node,`Yeni Product düğümü eksik: ${id}`);
  assert.ok(node.identifier.some(item=>item.propertyID==='MPN'));
}
for(const group of productGroupNodes){
  assert.ok(Array.isArray(group.hasVariant)&&group.hasVariant.length===2);
  assert.ok(Array.isArray(group.variesBy)&&group.variesBy.includes('https://schema.org/size'));
}
const allList=graph.find(node=>node['@id']==='https://www.alo186.com/akilli-urun-secimi#verified-products');
const directList=graph.find(node=>node['@id']==='https://www.alo186.com/akilli-urun-secimi#direct-affiliate-products');
const gatedList=graph.find(node=>node['@id']==='https://www.alo186.com/akilli-urun-secimi#tool-gated-products');
assert.equal(allList.numberOfItems,verifiedProducts.length);
assert.equal(directList.numberOfItems,publicProducts.length);
assert.equal(gatedList.numberOfItems,gatedProducts.length);
assert.equal(allList.itemListElement.length,verifiedProducts.length);
assert.equal(directList.itemListElement.length,publicProducts.length);
assert.equal(gatedList.itemListElement.length,gatedProducts.length);

const stalePayload=catalog.knowledgeGraph({now:new Date('2026-09-20T12:00:00Z')});
assert.equal(stalePayload['@graph'].filter(node=>node['@type']==='Product').length,0);
assert.equal(stalePayload['@graph'].filter(node=>node['@type']==='ProductGroup').length,0);
const health=catalog.catalogHealth({now});
assert.equal(health.totalVerified,verifiedProducts.length);
assert.equal(health.publicDirect,publicProducts.length);
assert.equal(health.gatedVerified,gatedProducts.length);
assert.equal(health.variantGroups,2);
assert.equal(health.reviewBy,'2026-08-28');
assert.equal(health.staleAfter,'2026-09-13');
console.log(JSON.stringify({ok:true,affiliateTag:catalog.affiliateTag,totalProducts:catalog.products.length,knowledgeGraphProducts:productNodes.length,productGroups:productGroupNodes.length,publicProducts:publicProducts.length,gatedProducts:gatedProducts.length},null,2));