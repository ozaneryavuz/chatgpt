'use strict';
const assert=require('node:assert/strict');

global.window=global;
global.document={
  getElementById(){return null;},
  addEventListener(){},
  querySelector(){return null;},
  body:{appendChild(){}},
};
global.location={search:''};

const catalog=require('../urun-eslestirme/catalog.js');
const matcher=require('../urun-eslestirme/matcher-core.js');
require('../urun-eslestirme/generator-guide-extension.js');

const newCategoryIds=['hdmi_cable','displayport_cable','usb_c_hdmi_cable'];
const newProductIds=[
  'xiaomi-bhr4996gl-33w',
  'samsung-ep-ta800n-25w',
  'baseus-pudding-100w-12m',
  'ugreen-dp14-2m',
  'ugreen-hdmi21-3m',
  'daytona-hc01-usbc-hdmi-18m',
  'veggieg-z623-usbc-dp14-2m',
  'veggieg-dp14-2m',
];
for(const id of newCategoryIds){
  const category=catalog.getCategory(id);
  assert.ok(category,`Yeni kategori eksik: ${id}`);
  assert.equal(category.mode,'direct');
  assert.equal(category.risk,'consumer');
  assert.equal(category.affiliatePolicy,'verified_direct');
}

const ids=new Set(catalog.products.map(product=>product.id));
const asins=new Set();
for(const product of catalog.products){
  assert.ok(!asins.has(product.asin),`Tekrarlanan ASIN: ${product.asin}`);
  asins.add(product.asin);
}
for(const id of newProductIds){
  assert.ok(ids.has(id),`Yeni ürün eksik: ${id}`);
  const product=catalog.products.find(item=>item.id===id);
  assert.equal(product.verifiedAt,'2026-07-30');
  assert.match(product.url,/amazon\.com\.tr\/dp\/[A-Z0-9]{10}\?tag=alo186rehber-21/);
  assert.ok(product.sourceNote.includes('fiyat, stok, puan, satıcı ve garanti yayımlanmaz'));
}

const now=new Date('2026-07-30T12:00:00Z');
const payload=catalog.knowledgeGraph({now});
const graph=payload['@graph'];
const productNodes=graph.filter(node=>node['@type']==='Product');
for(const id of newProductIds){
  const node=productNodes.find(item=>item.sku===id);
  assert.ok(node,`Knowledge Graph Product düğümü eksik: ${id}`);
  assert.ok(node.sameAs&&node.sameAs.includes('tag=alo186rehber-21'));
  assert.ok(node.identifier.some(item=>item.propertyID==='ASIN'));
}
const collectionNodes=graph.filter(node=>node['@type']==='ItemList'&&String(node['@id']).includes('#collection-'));
assert.equal(collectionNodes.length,5);
for(const node of collectionNodes){
  assert.ok(node.numberOfItems>=2);
  assert.equal(node.itemListElement.length,node.numberOfItems);
}
assert.equal(graph.filter(node=>node['@type']==='Offer').length,0);
for(const node of graph){
  for(const forbidden of ['offers','aggregateRating','review','price','priceCurrency','availability','seller'])assert.ok(!(forbidden in node),`Yasak ticari alan: ${forbidden}`);
}

const charger=catalog.products.find(item=>item.id==='xiaomi-bhr4996gl-33w');
assert.equal(matcher.scoreCharger(charger,{minOutputW:33,minUsbCPorts:1}).eligible,true);
assert.equal(matcher.scoreCharger(charger,{minOutputW:65,minUsbCPorts:1}).eligible,false);
const usbCable=catalog.products.find(item=>item.id==='baseus-pudding-100w-12m');
assert.equal(matcher.scoreUsbCable(usbCable,{minPowerW:100,minLengthM:1.2,dataTransfer:true}).eligible,true);
const dpCable=catalog.products.find(item=>item.id==='ugreen-dp14-2m');
assert.equal(matcher.scoreDisplay(dpCable,{minLengthM:2,need4k:true}).eligible,true);
const hdmiCable=catalog.products.find(item=>item.id==='ugreen-hdmi21-3m');
assert.equal(matcher.scoreDisplay(hdmiCable,{minLengthM:3,need4k:true}).eligible,true);

const extensionSource=require('node:fs').readFileSync(require('node:path').join(__dirname,'../urun-eslestirme/generator-guide-extension.js'),'utf8');
for(const token of [
  'Bir Amazon Gelir Ortağı olarak nitelikli satın alımlar üzerinden kazanç elde ediyorum.',
  'Satış ortaklığı bağlantısı',
  'sales_collection_product_clicked',
  'sales_cross_sell_clicked',
  'Port, güç ve protokol uyumunu ürün sayfasında yeniden doğrulayacağım.',
])assert.ok(extensionSource.includes(token),`Satış sözleşmesi eksik: ${token}`);
for(const forbidden of ['stokta son','hemen satın al','kaçırma','fiyat düştü'])assert.ok(!extensionSource.toLocaleLowerCase('tr-TR').includes(forbidden),`Manipülatif satış ifadesi: ${forbidden}`);

console.log(JSON.stringify({
  ok:true,
  addedCategories:newCategoryIds.length,
  addedProducts:newProductIds.length,
  purchaseCollections:collectionNodes.length,
  knowledgeGraphProducts:productNodes.length,
},null,2));
