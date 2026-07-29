const assert=require('assert');
const catalog=require('../urun-eslestirme/catalog.js');
const matcher=require('../urun-eslestirme/matcher-core.js');

assert.strictEqual(catalog.affiliateTag,'alo186hazirlik-21');
assert.strictEqual(catalog.categories.length,14,'On dört ihtiyaç kategorisi bulunmalı.');
assert(catalog.productsFor('powerbank').length>=3,'Powerbank kataloğunda en az üç ürün olmalı.');
assert(catalog.productsFor('surge_strip').length>=3,'Grup priz kataloğunda en az üç doğrulanmış ürün korunmalı.');
for(const category of ['generator','inverter','smart_plug','ev_cable','ups_battery','smoke_alarm','co_alarm','extension_cord'])assert.strictEqual(catalog.productsFor(category).length,0,`${category} doğrulanmamış ürün kartı taşımamalı.`);

const asins=catalog.products.map(p=>p.asin);
assert.strictEqual(new Set(asins).size,asins.length,'ASIN değerleri benzersiz olmalı.');
for(const product of catalog.products){
  assert(/^B[A-Z0-9]{9}$/.test(product.asin),`${product.id} ASIN biçimi geçersiz.`);
  assert(product.url.includes(`/dp/${product.asin}`),`${product.id} doğrudan ürün URL'si içermeli.`);
  assert(product.url.includes('tag=alo186hazirlik-21'),`${product.id} affiliate etiketi içermeli.`);
  assert(product.verifiedAt&&product.sourceNote,`${product.id} doğrulama kaydı içermeli.`);
  assert(!Object.prototype.hasOwnProperty.call(product,'price'),`${product.id} statik fiyat taşımamalı.`);
  assert(!Object.prototype.hasOwnProperty.call(product,'stock'),`${product.id} statik stok taşımamalı.`);
}

let result=matcher.match('powerbank',{minCapacityMah:20000,minOutputW:65,wireless:false});
assert.strictEqual(result.mode,'direct');
assert.strictEqual(result.matches.length,1);
assert.strictEqual(result.matches[0].product.asin,'B0BYNZXFM2');
result=matcher.match('powerbank',{minCapacityMah:10000,minOutputW:10,wireless:true});
assert(result.matches.length>=2);
assert(result.matches.every(x=>x.product.attributes.wireless));

const tuncmatik=catalog.products.find(product=>product.asin==='B07CST4766');
const surgeScore=matcher.scoreSurge(tuncmatik,{minOutlets:5,minJoules:900,usb:false});
assert.strictEqual(surgeScore.eligible,true);
assert(surgeScore.score>0);
const lowJoule=catalog.products.find(product=>product.asin==='B08L9KVRP1');
assert.strictEqual(matcher.scoreSurge(lowJoule,{minOutlets:5,minJoules:900,usb:false}).eligible,false);

const gated={
  surge_strip:'https://www.alo186.com/hesaplama/akim-korumali-grup-priz-uygunluk/',
  mini_ups:'https://www.alo186.com/hesaplama/modem-internet-yedekleme/',
  smoke_alarm:'https://www.alo186.com/hesaplama/duman-alarmi-yerlesim-bakim-uygunluk/',
  co_alarm:'https://www.alo186.com/hesaplama/karbonmonoksit-alarmi-jenerator-guvenligi/',
  generator:'https://www.alo186.com/hesaplama/jenerator-gucu-secimi/',
  inverter:'https://www.alo186.com/hesaplama/inverter-uygunluk/',
  smart_plug:'https://www.alo186.com/hesaplama/akilli-priz-enerji-olcer-uygunluk/',
  ev_cable:'https://www.alo186.com/hesaplama/ev-sarj-kablosu-uygunluk/',
  ups_battery:'https://www.alo186.com/haberler/ups-akusu-ne-zaman-degisir',
  extension_cord:'https://www.alo186.com/hesaplama/uzatma-kablosu-kablo-makarasi-uygunluk/'
};
for(const[category,url]of Object.entries(gated)){
  result=matcher.match(category,{});
  assert.strictEqual(result.mode,'guide');
  assert.strictEqual(result.affiliatePolicy,'after_tool');
  assert.strictEqual(result.nextStep.url,url);
  assert(result.searchUrl.includes('tag=alo186hazirlik-21'));
}
result=matcher.match('emergency_light',{});
assert.strictEqual(result.professionalSelectionRequired,false);
assert.throws(()=>matcher.match('olmayan-kategori',{}),/Ürün kategorisi bulunamadı/);
console.log('Ürün kataloğu ve eşleştirme testleri: 14 kategori, uzatma kablosu ve güvenli teknik kapılar başarılı.');
