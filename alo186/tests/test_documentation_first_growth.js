'use strict';

const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');

const root=path.resolve(__dirname,'../..');
const read=relative=>fs.readFileSync(path.join(root,relative),'utf8');

const common=read('alo186/hesaplama/common.js');
const core=read('alo186/urun-eslestirme/documentation-growth-core.js');
const ui=read('alo186/urun-eslestirme/documentation-growth.js');
const supplier=read('alo186/tedarikci-isbirligi/app.js');
const productHtml=read('alo186/urun-eslestirme/index.html');

assert(common.includes('documentation-growth-core.js'),'Ortak runtime belge güven core dosyasını yüklemiyor.');
assert(common.includes('documentation-growth.js'),'Ortak runtime belge güven arayüzünü yüklemiyor.');
assert(common.includes("document.addEventListener('DOMContentLoaded',loadDocumentationLayer"),'Belge katmanı katalog ve DOM hazır olmadan yüklenmemeli.');
assert(common.includes('data-alo186-documentation-core'),'Tekrarlı core yükleme koruması eksik.');
assert(common.includes('data-alo186-documentation-ui'),'Tekrarlı UI yükleme koruması eksik.');

for(const category of ['powerbank','surge_strip','mini_ups','emergency_light','smoke_alarm','power_station','smart_plug','ev_cable','ups_battery','generator','inverter','outlet_tester']){
  assert(core.includes(`${category}:`),`Belge profili eksik: ${category}`);
}
assert(core.includes("reviewStorageKey='alo186:documentation-reviews:v1'"),'Yerel tekrar kontrol anahtarı eksik.');
assert(core.includes('const reviewLimit=6'),'Belge kontrol kayıt sınırı eksik.');
assert(core.includes('const reviewDays=14'),'14 günlük tekrar ziyaret süresi eksik.');
assert(core.includes('const retentionDays=45'),'Belge kontrol saklama süresi eksik.');
assert(core.includes("source:'documentation_gap'"),'Tedarikçi veri boşluğu handoff kaynağı eksik.');
assert(core.includes("type:'document'"),'Doküman kalite kontrolü handoff türü eksik.');
assert(core.includes('Fiyat, stok, puan, garanti, satıcı, ASIN'),'Dışa aktarma gizlilik açıklaması eksik.');

assert(ui.includes('Teknik belge kapsamı ve satıcı soru paketi'),'Belge laboratuvarı görünür başlığı eksik.');
assert(ui.includes('documentation_affiliate_blocked'),'Kritik belge eksikliğinde affiliate engelleme olayı eksik.');
assert(ui.includes("window.addEventListener('click',interceptAffiliate,true)"),'Affiliate belge kapısı document gate öncesi çalışmıyor.');
assert(ui.includes('Soru paketini kopyala'),'Satıcı/üretici soru paketi kopyalama CTA’sı eksik.');
assert(ui.includes('14 günlük yeniden kontrol oluştur'),'Tekrar ziyaret CTA’sı eksik.');
assert(ui.includes('Teknik veri hazırlık skorunu aç'),'B2B teknik veri hizmeti CTA’sı eksik.');
assert(!/amazon\.(?:com|com\.tr)\/dp\//i.test(ui),'Belge katmanı doğrudan ürün URL’si içermemeli.');
assert(!/type="(?:email|tel|text)"|<textarea/i.test(ui),'Belge katmanı kişisel veri veya serbest metin alanı oluşturmamalı.');

assert(supplier.includes("params.get('source') !== 'documentation_gap'"),'Tedarikçi sayfası belge boşluğu kaynağını okumuyor.');
assert(supplier.includes("byId('type').value = type"),'Tedarikçi iş birliği türü otomatik doldurulmuyor.');
assert(supplier.includes('Bu bağlantı ürün, fiyat, ASIN, iletişim veya kişisel veri taşımaz.'),'Prefill gizlilik açıklaması görünür değil.');
assert(supplier.includes('supplier_documentation_gap_prefilled'),'B2B prefill ölçüm olayı eksik.');

assert(productHtml.includes('<script src="../hesaplama/common.js"></script>'),'Akıllı Ürün Merkezi ortak runtimeı yüklemiyor.');
assert(productHtml.includes('productShortlist'),'Mevcut kısa liste entegrasyonu korunmalı.');
assert(productHtml.includes('Reklam / satış ortaklığı'),'Affiliate açıklaması korunmalı.');
assert(productHtml.includes('Mevcut ürün yeterliyse'),'Satın almama sınırı korunmalı.');

console.log('ALO186 belge öncelikli büyüme: 12 kategori, belge skoru, soru paketi, affiliate kapısı, tekrar ziyaret ve tedarikçi hizmeti entegrasyonları başarılı.');
