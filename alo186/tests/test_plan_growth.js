'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'../..');
const read=relative=>fs.readFileSync(path.join(root,relative),'utf8');

const html=read('alo186/hesaplama/elektrik-planim/index.html');
const css=read('alo186/hesaplama/elektrik-planim/growth.css');
const app=read('alo186/hesaplama/elektrik-planim/growth.js');
const core=read('alo186/hesaplama/elektrik-planim/growth-core.js');

for(const token of ['id="seasonalList"','id="procurementBrief"','id="sharePlanBtn"','Marka bağımsız teknik alım kartı','Paylaşılan plan kişisel veri içerir mi?'])assert(html.includes(token),`Elektrik Planım büyüme entegrasyonu eksik: ${token}`);
assert(html.includes('<script src="./growth-core.js"></script><script src="./growth.js"></script>'),'Büyüme runtime scriptleri eksik.');
assert(!/type="(?:email|tel|text)"|<textarea/i.test(html),'Yeni büyüme alanında kişisel veri veya serbest metin alanı bulunmamalı.');
assert(!/amazon\.(?:com|com\.tr)/i.test(html),'Elektrik Planım doğrudan Amazon URL’si içermemeli.');
assert(!/fiyat[^.]{0,30}(?:₺|TL|TRY)|stokta|yıldız|garanti süresi/i.test(html),'Doğrulanmamış ticari iddia bulunmamalı.');

assert(app.includes('navigator.share'),'Web Share API progressive enhancement eksik.');
assert(app.includes('navigator.clipboard.writeText'),'Paylaşım fallback’i eksik.');
assert(app.includes("alo186:seasonal-readiness:v1"),'Mevsimsel tekrar ziyaret local store eksik.');
assert(app.includes('vendor_neutral_brief_rendered'),'Marka bağımsız brief ölçüm olayı eksik.');
assert(app.includes('seasonal_readiness_saved'),'Mevsimsel tekrar ziyaret olayı eksik.');
assert(!/localStorage\.setItem\([^\n]*(?:email|phone|address|serial|price|seller|asin)/i.test(app),'Büyüme runtimeı kişisel veya ticari veri saklamamalı.');

for(const token of ['summer','winter','storm','spring','affiliateAllowed','professional','sharePayload','reviewRecord'])assert(core.includes(token),`Büyüme çekirdeği sözleşmesi eksik: ${token}`);
assert(core.includes("status='no_buy'"),'Satın almama karar durumu eksik.');
assert(core.includes("affiliateAllowed=false"),'Satın almama ve profesyonel sonuçlarda affiliate kapısı kapanmalı.');
assert(core.includes('ALO186 EDAŞ veya kamu kurumu değildir'),'Resmî kurum sınırı paylaşım metninde eksik.');
assert(!/amazon\.(?:com|com\.tr)|ASIN|seller|price|stock|warranty/i.test(core),'Büyüme çekirdeği haricî ürün veya doğrulanmamış ticari alan içermemeli.');

for(const token of ['.growth-grid','.season-card','.procurement[data-status="no_buy"]','.share-panel','@media(max-width:640px)'])assert(css.includes(token),`Mobil büyüme stili eksik: ${token}`);

console.log('ALO186 Elektrik Planım büyüme entegrasyonu: mevsimsel koç, marka bağımsız alım kartı, paylaşım, gizlilik ve mobil sözleşmeler başarılı.');
