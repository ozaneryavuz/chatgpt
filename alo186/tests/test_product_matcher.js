const assert=require('assert');
const fs=require('fs');
const path=require('path');
const catalog=require('../urun-eslestirme/catalog.js');
const matcher=require('../urun-eslestirme/matcher-core.js');

assert.strictEqual(catalog.affiliateTag,'alo186rehber-21');
assert.strictEqual(catalog.categories.length,18,'On sekiz ihtiyaç kategorisi bulunmalı.');
assert(catalog.productsFor('powerbank').length>=5,'Powerbank kataloğunda en az beş ürün olmalı.');
assert(catalog.productsFor('usb_c_charger').length>=2,'USB-C şarj cihazı kataloğunda en az iki doğrulanmış ürün olmalı.');
assert(catalog.productsFor('usb_c_cable').length>=2,'USB-C kablo kataloğunda en az iki doğrulanmış ürün olmalı.');
assert(catalog.productsFor('usb_c_hub').length>=2,'USB-C hub kataloğunda en az iki doğrulanmış ürün olmalı.');
assert(catalog.productsFor('display_cable').length>=2,'Görüntü kablosu kataloğunda en az iki doğrulanmış ürün olmalı.');
assert(catalog.productsFor('surge_strip').length>=3,'Grup priz kataloğunda en az üç doğrulanmış ürün korunmalı.');
for(const category of ['generator','inverter','smart_plug','ev_cable','ups_battery','smoke_alarm','co_alarm','extension_cord'])assert.strictEqual(catalog.productsFor(category).length,0,`${category} doğrulanmamış ürün kartı taşımamalı.`);

const asins=catalog.products.map(p=>p.asin);
assert.strictEqual(new Set(asins).size,asins.length,'ASIN değerleri benzersiz olmalı.');
for(const product of catalog.products){
  assert(/^B[A-Z0-9]{9}$/.test(product.asin),`${product.id} ASIN biçimi geçersiz.`);
  assert(product.url.includes(`/dp/${product.asin}`),`${product.id} doğrudan ürün URL'si içermeli.`);
  assert(product.url.includes('tag=alo186rehber-21'),`${product.id} affiliate etiketi içermeli.`);
  assert(product.verifiedAt&&product.sourceNote,`${product.id} doğrulama kaydı içermeli.`);
  for(const key of ['price','stock','rating','aggregateRating','review','seller','delivery','warranty','availability','offers'])assert(!Object.prototype.hasOwnProperty.call(product,key),`${product.id} yasak ticari alan taşımamalı: ${key}`);
}

let result=matcher.match('powerbank',{minCapacityMah:20000,minOutputW:65,wireless:false});
assert.strictEqual(result.mode,'direct');
assert.strictEqual(result.matches.length,3);
assert(result.matches.every(item=>item.product.attributes.maxOutputW>=65));
assert(result.matches.some(item=>item.product.asin==='B0CXDXP8VR'),'65 W dahili kablolu seçenek görünmeli.');

result=matcher.match('powerbank',{minCapacityMah:20000,minOutputW:100,wireless:false});
assert.strictEqual(result.matches.length,2);
assert(result.matches.every(item=>item.product.attributes.maxOutputW>=100));
assert(result.matches.some(item=>item.product.asin==='B09VPHVT2Z'));
assert(result.matches.some(item=>item.product.asin==='B0BYNZXFM2'));
assert(!result.matches.some(item=>item.product.asin==='B0CXDXP8VR'),'87 W toplam / 65 W tek cihaz ürünü 100 W ihtiyacına sızmamalı.');

result=matcher.match('powerbank',{minCapacityMah:20000,minOutputW:140,wireless:false});
assert.strictEqual(result.matches.length,1);
assert.strictEqual(result.matches[0].product.asin,'B09VPHVT2Z');

result=matcher.match('powerbank',{minCapacityMah:10000,minOutputW:10,wireless:true});
assert(result.matches.length>=2);
assert(result.matches.every(x=>x.product.attributes.wireless));

const tuncmatik=catalog.products.find(product=>product.asin==='B07CST4766');
const surgeScore=matcher.scoreSurge(tuncmatik,{minOutlets:5,minJoules:900,usb:false});
assert.strictEqual(surgeScore.eligible,true);
assert(surgeScore.score>0);
const lowJoule=catalog.products.find(product=>product.asin==='B08L9KVRP1');
assert.strictEqual(matcher.scoreSurge(lowJoule,{minOutlets:5,minJoules:900,usb:false}).eligible,false);

// 1. USB-C şarj cihazı: güç, port ve protokol niyeti birlikte uygulanmalı.
result=matcher.match('usb_c_charger',{minOutputW:65,minUsbCPorts:2,multiPort:true});
assert.strictEqual(result.mode,'direct');
assert.strictEqual(result.matches.length,1,'65 W ve iki USB-C isteyen kullanıcıya yalnız uygun çok portlu adaptör gösterilmeli.');
assert.strictEqual(result.matches[0].product.asin,'B09W2HP21R');
result=matcher.match('usb_c_charger',{minOutputW:100,minUsbCPorts:1});
assert.strictEqual(result.matches.length,0,'100 W gereksinimi için daha düşük güçlü ürün gösterilmemeli.');
result=matcher.match('usb_c_charger',{minOutputW:45,requirePps:true});
assert.strictEqual(result.matches.length,0,'PPS teknik kayıtta doğrulanmadıysa sonuç fail-closed olmalı.');
result=matcher.match('usb_c_charger',{minOutputW:140,requirePd31:true});
assert.strictEqual(result.matches.length,0,'PD 3.1 doğrulanmış adaptör yoksa genel ürün araması açılmamalı.');

// 2. USB-C kablo: şarj gücü ile veri hızı aynı özellik sayılmamalı.
result=matcher.match('usb_c_cable',{minPowerW:100,minLengthM:2,minDataGbps:0});
assert.strictEqual(result.matches.length,1);
assert.strictEqual(result.matches[0].product.asin,'B0B46PHW14');
result=matcher.match('usb_c_cable',{minPowerW:60,minLengthM:1,minDataGbps:10});
assert.strictEqual(result.matches.length,0,'Yüksek hızlı veri kanıtı olmayan şarj kablosu 10 Gbps sonucuna sızmamalı.');
result=matcher.match('usb_c_cable',{minPowerW:240,minLengthM:1,requireEpr:true});
assert.strictEqual(result.matches.length,0,'240 W EPR doğrulanmamış kablo gösterilmemeli.');

// 3. USB-C hub: kullanılacak özellikler ve satın almama/güvenlik kapıları ayrılmalı.
result=matcher.match('usb_c_hub',{needHdmi:true,needEthernet:true,minPdPassThroughW:65,needCardReader:true,minDataGbps:0});
assert.strictEqual(result.matches.length,2,'HDMI, Ethernet, kart okuyucu ve PD ihtiyacını karşılayan iki doğrulanmış hub korunmalı.');
result=matcher.match('usb_c_hub',{needHdmi:true,minPdPassThroughW:65,minDataGbps:10});
assert.strictEqual(result.matches.length,1,'10 Gbps kanıtı bulunan hub tek başına gösterilmeli.');
assert.strictEqual(result.matches[0].product.asin,'B0DJN3NDCP');
for(const category of ['usb_c_charger','usb_c_cable','usb_c_hub']){
  result=matcher.match(category,{existingSufficient:true});
  assert.strictEqual(result.mode,'direct');
  assert.strictEqual(result.blockReason,'no_buy');
  assert.strictEqual(result.matches.length,0,'Mevcut ürün yeterliyse affiliate sonucu olmamalı.');
  result=matcher.match(category,{hazard:true});
  assert.strictEqual(result.blockReason,'hazard');
  assert.strictEqual(result.matches.length,0,'Fiziksel riskte bütün ticari sonuçlar kapanmalı.');
  const markup=matcher.intentMarkup(category);
  assert(markup.includes('existingSufficient')&&markup.includes('hazard'),`${category} kullanıcı arayüzünde satın almama ve güvenlik kapıları görünür olmalı.`);
}
assert(matcher.intentMarkup('usb_c_charger').includes('requirePd31'));
assert(matcher.intentMarkup('usb_c_cable').includes('minDataGbps'));
assert(matcher.intentMarkup('usb_c_hub').includes('needCardReader'));
assert.match(matcher.requirementsSummary('usb_c_charger',{minOutputW:65,minUsbCPorts:2,requirePd31:true}),/65 W\+.*2 USB-C.*PD 3\.1/);
assert.match(matcher.requirementsSummary('usb_c_cable',{minPowerW:100,minLengthM:2,minDataGbps:10}),/10 Gbps/);
assert.match(matcher.requirementsSummary('usb_c_hub',{minPdPassThroughW:65,needEthernet:true,needCardReader:true}),/Ethernet.*kart okuyucu/);

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
  assert(result.searchUrl.includes('tag=alo186rehber-21'));
}
result=matcher.match('emergency_light',{});
assert.strictEqual(result.professionalSelectionRequired,false);
assert.throws(()=>matcher.match('olmayan-kategori',{}),/Ürün kategorisi bulunamadı/);

const matcherSource=fs.readFileSync(path.join(__dirname,'../urun-eslestirme/matcher-core.js'),'utf8');
assert(matcherSource.includes('Amazon')===false,'Matcher güven kapıları Amazon marka baskısı üretmemeli.');
assert(!/price|stock|aggregateRating|warranty/i.test(JSON.stringify({directIntentCategories:[...matcher.directIntentCategories]})));
console.log('Ürün kataloğu ve eşleştirme testleri: USB-C adaptör, kablo ve hub teknik niyetleri; satın almama ve fiziksel risk kapıları başarılı.');
