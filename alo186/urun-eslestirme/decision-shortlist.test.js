const assert=require('assert');
const fs=require('fs');
const path=require('path');
const core=require('./decision-shortlist-core.js');

const now=new Date('2026-07-28T08:00:00Z');
const snapshot=core.sanitizeSnapshot({
  productId:'anker-prime-a1336',asin:'B0BYNZXFM2',categoryId:'powerbank',productName:'Anker Prime 20.000 mAh',brand:'Anker',score:96,confidence:'Yüksek',verifiedAt:'2026-07-27',sourceNote:'Teknik alanlar kontrol edildi.',unknowns:['Garanti satıcı sayfasında doğrulanmalı'],attributes:{capacityMah:20000,energyWh:72,maxOutputW:200,wireless:false,usbCPorts:2}
},now);
assert(snapshot,'Geçerli ürün özeti oluşturulmalı.');
assert.strictEqual(snapshot.schemaVersion,1);
assert.strictEqual(snapshot.productId,'anker-prime-a1336');
assert.strictEqual(snapshot.attributes.capacityMah,20000);
assert(!('email' in snapshot));
assert(!('phone' in snapshot));
assert(!('address' in snapshot));
assert.strictEqual(core.hasForbiddenData(snapshot),false);
assert.strictEqual(core.hasForbiddenData({email:'x@example.com'}),true);

let vault=core.upsert([],snapshot);
assert.strictEqual(vault.length,1);
const second=core.sanitizeSnapshot({productId:'viko-multilet-6',asin:'B08L9KVRP1',categoryId:'surge_strip',productName:'Viko Multilet',brand:'Viko',score:88,verifiedAt:'2026-07-27',attributes:{outlets:6,joules:282,maxCurrentA:16,maxPowerW:3500}},now);
const third=core.sanitizeSnapshot({productId:'tuncmatik-tsk6136',asin:'B07CST4766',categoryId:'surge_strip',productName:'Tunçmatik PowerSurge',brand:'Tunçmatik',score:91,verifiedAt:'2026-07-27',attributes:{outlets:5,joules:1050,maxCurrentA:10}},now);
const fourth=core.sanitizeSnapshot({productId:'cata-ct9186',asin:'B09YTYTZ4J',categoryId:'surge_strip',productName:'Cata CT-9186',brand:'Cata',score:80,verifiedAt:'2026-07-27',attributes:{outlets:1,joules:918,maxPowerW:4000}},now);
vault=core.upsert(vault,second);
vault=core.upsert(vault,third);
assert.strictEqual(vault.length,3);
vault=core.upsert(vault,fourth);
assert.strictEqual(vault.length,3,'Kısa liste en fazla üç ürün tutmalı.');
assert.strictEqual(vault[0].productId,'cata-ct9186');
assert(!vault.some(item=>item.productId==='anker-prime-a1336'),'En eski kayıt limit aşımında düşmeli.');

const rows=core.comparisonRows([snapshot,second]);
assert(rows.some(row=>row.key==='capacityMah'&&row.values[0]==='20.000'));
assert(rows.some(row=>row.key==='outlets'&&row.values[0]==='Bilinmiyor'&&row.values[1]==='6'));
assert.strictEqual(core.gateAllowed({needConfirmed:true,technicalConfirmed:true,affiliateConfirmed:true}),true);
assert.strictEqual(core.gateAllowed({needConfirmed:true,technicalConfirmed:false,affiliateConfirmed:true}),false);

const expired={...snapshot,expiresAt:'2026-07-27T00:00:00Z'};
assert.strictEqual(core.normalizeVault([expired],now).length,0,'Süresi dolmuş kayıt temizlenmeli.');
assert.strictEqual(core.remove([snapshot,second],snapshot.productId).length,1);
assert.strictEqual(core.daysUntilExpiry(snapshot,now),30);

const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
const js=fs.readFileSync(path.join(__dirname,'decision-shortlist.js'),'utf8');
const css=fs.readFileSync(path.join(__dirname,'styles.css'),'utf8');
assert(html.includes('id="productShortlist"'));
assert(html.includes('decision-shortlist-core.js'));
assert(html.includes('decision-shortlist.js'));
assert(html.includes('satın almamak geçerli sonuçtur')||html.includes('satın almamak geçerli bir sonuçtur'));
assert(html.includes('Fiyat, stok, satıcı, teslimat, garanti veya kişisel veri kaydedilmez'));
assert(js.includes('rel="sponsored nofollow noopener"'));
assert(js.includes('affiliate_no_purchase_selected'));
assert(js.includes('affiliate_verified_product_gate_opened'));
assert(js.includes('product_shortlist_added'));
for(const key of ['name','email','phone','address','subscription','identity','plate','serialNumber','freeText'])assert(!Object.prototype.hasOwnProperty.call(snapshot,key),`Saklanan snapshot ${key} anahtarını içermemeli.`);
assert(css.includes('.product-shortlist'));
assert(css.includes('.affiliate-decision-gate'));
assert(css.includes('@media(max-width:680px)'));

console.log('ALO186 ürün kısa listesi: 3 ürün limiti, 30 gün saklama, teknik karşılaştırma, PII yasağı ve üç adımlı affiliate kapısı testleri geçti.');
