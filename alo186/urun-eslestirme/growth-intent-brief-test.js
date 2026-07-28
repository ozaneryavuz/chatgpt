'use strict';

const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');

const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
const script=fs.readFileSync(path.join(__dirname,'growth-intent-brief.js'),'utf8');
const conversion=fs.readFileSync(path.join(__dirname,'conversion-growth.js'),'utf8');
const conversionCore=fs.readFileSync(path.join(__dirname,'conversion-growth-core.js'),'utf8');
const styles=fs.readFileSync(path.join(__dirname,'styles.css'),'utf8');
const app=fs.readFileSync(path.join(__dirname,'app.js'),'utf8');

assert.match(html,/id="intentShortcutsTitle"/,'Arama niyeti kısayolları görünür olmalı.');
assert.equal((html.match(/data-intent-category=/g)||[]).length,6,'Altı yüksek niyetli başlangıç rotası kaynak HTML’de bulunmalı; ek kategoriler katalogdan istemci tarafında tamamlanır.');
assert.match(html,/id="briefVault"/,'Tekrar ziyaret için teknik ihtiyaç dosyası bulunmalı.');
assert.match(html,/id="decisionBrief"/,'Sonuç sonrasında satıcıdan bağımsız teknik özet bulunmalı.');
assert.match(html,/Doğrulanmış ürün bulunamazsa neden hemen arama açılmıyor/,'Affiliate arama kapısı kullanıcıya açıklanmalı.');
assert.match(html,/growth-intent-brief\.js/,'Büyüme modülü sayfaya bağlanmalı.');
assert.match(html,/Reklam \/ satış ortaklığı/,'Affiliate niteliği görünür olmalı.');
assert.match(html,/EDAŞ veya kamu kurumu değildir/,'Resmî kurum izlenimi reddedilmeli.');

assert.match(script,/alo186_product_briefs_v1/,'Teknik ihtiyaç dosyası yalnız yerel depolamada tutulmalı.');
assert.match(script,/vaultLimit=3/,'Yerel dosya en fazla üç kayıt tutmalı.');
assert.match(script,/retentionDays=30/,'Teknik kayıtlar 30 gün sonra geçersiz olmalı.');
assert.match(script,/affiliate_unverified_search_acknowledged/,'Eski teknik özet katmanındaki arama onayı ölçümü korunmalı.');
assert.match(script,/no_verified_match_requires_ack/,'Eşleşme yokken affiliate bağlantısı kapalı başlamalı.');
assert.match(script,/aria-disabled','true'/,'Affiliate erişilebilirlik kapısı bulunmalı.');
assert.match(script,/product_brief_saved/,'Tekrar ziyaret için kayıt olayı ölçülmeli.');
assert.match(script,/product_brief_copied/,'Teknik özet kopyalama olayı ölçülmeli.');
assert.match(script,/product_brief_downloaded/,'Kişisel verisiz dışa aktarım ölçülmeli.');
assert.match(script,/Bu özet fiyat teklifi, uygunluk belgesi veya satın alma önerisi değildir/,'Özet satın alma onayı gibi sunulmamalı.');
assert.doesNotMatch(script,/amazon\.com\.tr/i,'Teknik özet katmanı doğrudan Amazon URL üretmemeli.');
assert.doesNotMatch(html,/<input[^>]+(?:name|id)="(?:name|email|phone|address|tc|abonelik)/i,'Kişisel veri alanı bulunmamalı.');

assert.match(styles,/\.intent-grid/,'Niyet kısayolları responsive tasarıma sahip olmalı.');
assert.match(styles,/\.brief-vault-list/,'Teknik ihtiyaç dosyası responsive tasarıma sahip olmalı.');
assert.match(styles,/@media print/,'Teknik özet yazdırma ve PDF görünümü bulunmalı.');
assert.match(styles,/conversion-growth\.css/,'Nitelikli arama dönüşüm stili yüklenmeli.');
assert.doesNotMatch(app,/data-filtered-search/,'Doğrulanmış kart yokken tek tıklamalı genel affiliate araması kaldırılmalı.');
assert.doesNotMatch(app,/data-guide-amazon/,'Kontrol listesi sonrasında tek onaylı genel affiliate araması kaldırılmalı.');
assert.match(conversion,/qualifiedExistingInsufficient/,'Mevcut ürün yetersizliği ayrıca onaylanmalı.');
assert.match(conversion,/qualifiedAffiliateAccepted/,'Affiliate ilişkisi ayrıca onaylanmalı.');
assert.match(conversion,/Şimdilik satın alma/,'Satın almama görünür seçenek olmalı.');
assert.match(conversionCore,/gateStatus/,'Yeni nitelikli arama fail-closed kapısı bulunmalı.');

console.log('ALO186 niyet, teknik özet, tekrar ziyaret ve nitelikli affiliate kapısı testleri başarılı.');
