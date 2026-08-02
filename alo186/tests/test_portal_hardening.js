const assert = require('assert');
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const portal = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const css = fs.readFileSync(path.join(root, 'styles.css'), 'utf8');
const htaccess = fs.readFileSync(path.join(root, 'deployment', 'apache-production.htaccess'), 'utf8');
const deadlinePolicy = fs.readFileSync(path.join(root, 'deployment', 'device_damage_deadline.py'), 'utf8');

assert(portal.includes('class="legal-alert"'), 'Portal cihaz hasarı hukukî uyarı alanını taşımalı.');
assert(portal.includes('ALO186 başvuru veya hasar kaydı almaz'), 'ALO186 başvuru almadığını açıkça söylemeli.');
assert(deadlinePolicy.includes('CURRENT_DEADLINE = "30 gün"'), 'Canonical yayın politikası Madde 26/1 kapsamındaki 30 günü kullanmalı.');
assert(deadlinePolicy.includes('elektrik-portali/index.html'), 'Portal hukukî metni production normalizasyon kapsamına alınmalı.');
assert(deadlinePolicy.includes('20201229M1-1.htm'), 'Bağlayıcı Kalite Yönetmeliği kaynağı production politikasında bulunmalı.');

assert(portal.includes('rel="canonical" href="https://www.alo186.com/elektrik-portali"'), 'Portal www canonical kullanmalı.');
assert(portal.includes('class="skip-link" href="#main-content"'), 'Skip link eksik.');
assert(portal.includes('<main id="main-content"'), 'Skip link ana hedefi eksik.');
assert(portal.includes('data-alo186-user-first="true"'), 'Portal kullanıcı öncelikli yayın işareti taşımalı.');
assert(portal.includes('data-alo186-toc-disabled="true"'), 'Portalın kapalı kaynak kataloğu otomatik içerik haritasına karışmamalı.');
assert(portal.includes('önce doğru ve güvenli adımı bulun'), 'Portal H1 kullanıcı sorununu güvenlik önceliğiyle anlatmalı.');
assert(portal.includes('kaynak doğrulamalı rehberler'), 'Portal kaynak doğrulamalı rehber ailesini göstermeli.');
assert(portal.includes('kişisel veri istemeyen araçlar'), 'Portal kişisel veri istemeyen araç ailesini göstermeli.');
assert(!/\b\d+\s+(?:kişisel veri istemeyen (?:araç|hesaplama ve karar aracı)|kaynak doğrulamalı (?:teknik )?rehber)\b/iu.test(portal), 'Hızla değişen araç/rehber envanteri sabit sayıyla pazarlanmamalı.');

assert(portal.includes('class="task-start"'), 'Kullanıcının dört ana niyetini ayıran başlangıç alanı eksik.');
assert.strictEqual((portal.match(/data-alo186-primary-task=/g) || []).length, 4, 'İlk ekranda tam dört birincil görev bulunmalı.');
for (const task of ['emergency', 'official', 'decision', 'tools']) {
  assert(portal.includes(`data-alo186-primary-task="${task}"`), `Birincil görev eksik: ${task}`);
}
assert(portal.includes('<details class="resource-library"'), 'Uzun araç ve rehber kataloğu progresif açılım içinde olmalı.');
assert(portal.includes('Tüm ücretsiz araç ve teknik rehberler'), 'Kaynak kataloğunun kullanıcı dostu özeti eksik.');
assert(!portal.includes('gelire dönüştüren'), 'Kullanıcı H1 metninde iç gelir hedefi bulunmamalı.');
assert(!portal.includes('ASIN kartı'), 'Kullanıcı metninde iç katalog jargonu bulunmamalı.');
assert(!portal.includes('local-first'), 'Kullanıcı metninde ürün geliştirme jargonu bulunmamalı.');
assert(!portal.toLowerCase().includes('affiliate'), 'Türkçe portal görünür ve yapılandırılmış metninde affiliate jargonu yerine satış ortaklığı kullanılmalı.');

const taskIndex = portal.indexOf('class="task-start"');
const legalIndex = portal.indexOf('class="legal-alert"');
const libraryIndex = portal.indexOf('class="resource-library"');
const revenueIndex = portal.indexOf('class="revenue-sprint"');
const principlesIndex = portal.indexOf('class="principles"');
assert(taskIndex > 0 && taskIndex < legalIndex, 'Birincil görevler cihaz hasarı uyarısından önce gelmeli.');
assert(legalIndex < libraryIndex, 'Hak ve süre bilgisi kaynak kataloğundan önce gelmeli.');
assert(libraryIndex < revenueIndex, 'Ücretsiz kaynaklar ticari seçeneklerden önce gelmeli.');
assert(revenueIndex < principlesIndex, 'Ticari seçenekleri güven ve şeffaflık ilkeleri izlemeli.');

assert(portal.includes('Akıllı Priz ve Enerji Ölçer Uygunluğu'), 'Akıllı priz/enerji ölçer aracı portalda bulunmalı.');
assert(portal.includes('Kaçak akım rölesi kaç amper ve kaç mA?'), 'RCD etiketi rehberi portalda bulunmalı.');
assert(portal.includes('Nötr ile toprak arası kaç volt olmalı?'), 'Nötr-toprak rehberi portalda bulunmalı.');
assert(portal.includes('GES inverter AFCI alarmı nedir?'), 'AFCI/DC ark rehberi portalda bulunmalı.');

const staleRoutes = [
  'href="./turkiye-arama/"',
  'href="./karar-motoru/"',
  'href="./urun-eslestirme/"',
  'href="./sureklilik-paneli/"',
  'href="./fatura-analizi/"',
  'href="./yedek-guc-hesaplayici/"',
  'href="./kesinti-maliyet-hesaplayici/"'
];
for (const route of staleRoutes) {
  assert(!portal.includes(route), `Eski kaynak-klasör rotası kaldı: ${route}`);
}

const requiredRoutes = [
  '/acil-numaralar/',
  '/elektrik-durum-merkezi/',
  '/edas-bul',
  '/karar-motoru',
  '/hesaplama/',
  '/akilli-urun-secimi',
  '/isletme-surekliligi',
  '/fatura-analizi',
  '/hesaplama/yedek-guc',
  '/hesaplama/kesinti-maliyeti',
  '/hesaplama/elektrik-surekliligi-pasaportu/',
  '/hesaplama/elektrik-kesintisi-tatbikati/',
  '/hesaplama/modem-internet-yedekleme/',
  '/hesaplama/powerbank-usb-c-uygunluk/',
  '/hesaplama/akilli-priz-enerji-olcer-uygunluk/',
  '/hesaplama/gunes-paneli-power-station-uygunluk/',
  '/hesaplama/ev-sarj-kablosu-uygunluk/',
  '/kesintiye-hazirlik-atolyesi',
  '/kurumsal-elektrik-surekliligi-on-degerlendirme',
  '/tedarikci-ve-uretici-isbirligi'
];
for (const route of requiredRoutes) {
  assert(portal.includes(`href="${route}"`), `Portal kartı/rota eksik: ${route}`);
}

for (const label of ['Satış ortaklığı', 'Ücretli profesyonel hizmet', 'Sponsorlu iş birliği']) {
  assert(portal.includes(label), `Ticari ilişki etiketi eksik: ${label}`);
}
assert(portal.includes('Ödeme organik teknik sıralamayı satın alamaz'), 'Sponsorlu iş birliğinde organik sıralama koruması görünür olmalı.');

for (const token of [
  '.skip-link',
  'a:focus-visible',
  'min-height:44px',
  '.legal-alert',
  '.task-start',
  '.task-grid',
  '.task-card.emergency',
  '.resource-library',
  '.resource-library:not([open]) .grid',
  '.revenue-sprint',
  '.money-tag',
  'overflow-wrap:anywhere',
  '@media(prefers-reduced-motion:reduce)'
]) {
  assert(css.includes(token), `Portal CSS koruması eksik: ${token}`);
}
assert(!/overflow\s*:\s*hidden/.test(css), 'Bilgi kartlarında metni kırpabilecek overflow:hidden kullanılmamalı.');
assert(!/line-clamp/.test(css), 'Güvenlik ve hak bilgisi line-clamp ile gizlenmemeli.');

assert(htaccess.includes('RewriteCond %{HTTP_HOST} !^alo186\\.com$ [NC]'), 'Non-apex host koşulu eksik.');
assert(htaccess.includes('RewriteRule ^ https://alo186.com%{REQUEST_URI} [R=301,L,NE]'), 'www → apex canonical yönlendirmesi eksik.');
assert(!htaccess.includes('RewriteRule ^ https://www.alo186.com%{REQUEST_URI} [R=301,L,NE]'), 'Eski apex → www yönlendirmesi kalmamalı.');
for (const header of [
  'Strict-Transport-Security',
  'X-Content-Type-Options',
  'Content-Security-Policy',
  'Referrer-Policy',
  'Permissions-Policy'
]) {
  assert(htaccess.includes(header), `Production güvenlik başlığı eksik: ${header}`);
}
assert(htaccess.includes('Cihaz hasarı başvuru süresi HTML yanıt katmanında değiştirilmez'), 'Hukukî metin response katmanında değiştirilemez sözleşmesi eksik.');
assert(!htaccess.includes('AddOutputFilterByType SUBSTITUTE text/html application/xhtml+xml'), 'Response katmanı hukukî içeriği dönüştürmemeli.');
assert(!htaccess.includes('Substitute "s|'), 'Apache hukukî metin substitution kuralı taşımamalı.');

console.log('ALO186 portal hardening: kullanıcı öncelikli görev sırası, progresif kaynak kataloğu, şeffaf ticari katman, canonical rotalar, Madde 26/1 yayın politikası ve erişilebilirlik sözleşmeleri geçti.');
