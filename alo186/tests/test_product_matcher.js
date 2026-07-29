const assert=require('assert');
const catalog=require('../urun-eslestirme/catalog.js');
const matcher=require('../urun-eslestirme/matcher-core.js');

assert.strictEqual(catalog.affiliateTag,'alo186rehber-21');
assert.strictEqual(catalog.categories.length,16,'On altı ihtiyaç kategorisi bulunmalı.');
assert(catalog.productsFor('powerbank').length>=3,'Powerbank kataloğunda en az üç ürün olmalı.');
assert(catalog.productsFor('usb_c_charger').length>=1,'USB-C şarj cihazı kataloğunda doğrulanmış ürün olmalı.');
assert(catalog.productsFor('usb_c_cable').length>=1,'USB-C kablo kataloğunda doğrulanmış ürün olmalı.');
assert(catalog.productsFor('surge_strip').length>=3,'Grup priz kataloğunda en az üç doğrulanmış ürün korunmalı.');
for(const category of ['generator','inverter','smart_plug','ev_cable','ups_battery','smoke_alarm','co_alarm','extension_cord'])assert.strictEqual(catalog.productsFor(category).length,0,`${category} doğrulanmamış ürün kartı taşımamalı.`);

const asins=catalog.products.map(p=>p.asin);
assert.strictEqual(new Set(asins).size,asins.length,'ASIN değerleri benzersiz olmalı.');
for(const product of catalog.products){
  assert(/^B[A-Z0-9]{9}$/.test(product.asin),`${product.id} ASIN biçimi geçersiz.`);
  assert(product.url.includes(`/dp/${product.asin}`),`${product.id} doğrudan ürün URL'si içermeli.`);
  assert(product.url.includes('tag=alo186rehber-21'),`${product.id} affiliate etiketi içermeli.`);
  assert(product.verifiedAt&&product.sourceNote,`${product.id} doğrulama kaydı içermeli.`);
  assert(!Object.prototype.hasOwnProperty.call(product,'price'),`${product.id} statik fiyat taşımamalı.`);
  assert(!Object.prototype.hasOwnProperty.call(product,'stock'),`${product.id} statik stok taşımamalı.`);
}

let result=matcher.match('powerbank',{capacity:'20000',power:'high',wireless:'no'});
assert(result.products.length>=1,'Powerbank eşleşmesi sonuç üretmeli.');
assert(result.products.every(p=>p.category==='powerbank'));
result=matcher.match('usb_c_charger',{});
assert(result.products.length>=1,'USB-C şarj cihazı eşleşmesi sonuç üretmeli.');
result=matcher.match('usb_c_cable',{});
assert(result.products.length>=1,'USB-C kablo eşleşmesi sonuç üretmeli.');
result=matcher.match('surge_strip',{outlets:'6',joules:'high'});
assert(result.nextStepRequired,true);

const gated={
  generator:'https://www.alo186.com/hesaplama/jenerator-gucu-secimi/',
  inverter:'https://www.alo186.com/hesaplama/inverter-uygunluk/',
  smart_plug:'https://www.alo186.com/hesaplama/akilli-priz-enerji-olcer-uygunluk/',
  ev_cable:'https://www.alo186.com/hesaplama/ev-sarj-kablosu-uygunluk/',
  ups_battery:'https://www.alo186.com/haberler/ups-akusu-ne-zaman-degisir',
  extension_cord:'https://www.alo186.com/hesaplama/uzatma-kablosu-kablo-makarasi-uygunluk/'
};
for(const[category,url]of Object.entries(gated)){
  result=matcher.match(category,{});
  assert.strictEqual(result.nextStepRequired,true,`${category} teknik kapı gerektirmeli.`);
  assert.strictEqual(result.nextStepUrl,url);
}
result=matcher.match('emergency_light',{});
assert.strictEqual(result.professionalSelectionRequired,false);
assert.throws(()=>matcher.match('olmayan-kategori',{}),/Ürün kategorisi bulunamadı/);
console.log('Ürün kataloğu ve eşleştirme testleri: 16 kategori, USB-C doğrudan ürünleri ve güvenli teknik kapılar başarılı.');
