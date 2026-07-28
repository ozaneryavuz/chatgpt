const assert = require('assert');
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const portal = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const css = fs.readFileSync(path.join(root, 'styles.css'), 'utf8');
const htaccess = fs.readFileSync(path.join(root, 'deployment', 'apache-production.htaccess'), 'utf8');
const oldDuration = ['3', '0', ' gün'].join('');
const oldLivePhrase = ['3', '0 gün içinde EDAŞ kaydı açın'].join('');

assert(portal.includes('Cihaz hasarında başvuru süresi 10 iş günüdür'), 'Portal 10 iş günü başlığını göstermeli.');
assert(portal.includes('zararın ortaya çıktığı tarihten itibaren <strong>10 iş günü içinde</strong>'), 'Görünür metinde 10 iş günü bulunmalı.');
assert(portal.includes('ALO186 başvuru veya hasar kaydı almaz'), 'ALO186 başvuru almadığını açıkça söylemeli.');
assert(portal.includes('https://www.epdk.gov.tr/Detay/Icerik/12-3/elektrik-piyasasi'), 'Doğru EPDK elektrik piyasası SSS kaynağına görünür bağlantı olmalı.');
assert(!new RegExp(`zararın ortaya çıktığı tarihten itibaren\\s*${oldDuration}`, 'i').test(portal), 'Cihaz hasarı bağlamında eski süre kaynak portalda bulunmamalı.');

assert(portal.includes('rel="canonical" href="https://www.alo186.com/elektrik-portali"'), 'Portal www canonical kullanmalı.');
assert(portal.includes('class="skip-link" href="#main-content"'), 'Skip link eksik.');
assert(portal.includes('<main id="main-content"'), 'Skip link ana hedefi eksik.');
assert(portal.includes('42 kaynak doğrulamalı teknik rehber'), 'Portal güncel 42 rehber kapsamını göstermeli.');
assert(portal.includes('24 kişisel veri istemeyen araç'), 'Portal güncel 24 araç kapsamını göstermeli.');

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
  '/hesaplama/powerbank-usb-c-uygunluk/',
  '/hesaplama/gunes-paneli-power-station-uygunluk/',
  '/hesaplama/ev-sarj-kablosu-uygunluk/'
];
for (const route of requiredRoutes) {
  assert(portal.includes(`href="${route}"`), `Portal kartı/rota eksik: ${route}`);
}

for (const token of [
  '.skip-link',
  'a:focus-visible',
  'min-height:44px',
  '.legal-alert',
  'overflow-wrap:anywhere',
  '@media(prefers-reduced-motion:reduce)'
]) {
  assert(css.includes(token), `Portal CSS koruması eksik: ${token}`);
}
assert(!/overflow\s*:\s*hidden/.test(css), 'Bilgi kartlarında metni kırpabilecek overflow:hidden kullanılmamalı.');
assert(!/line-clamp/.test(css), 'Güvenlik ve hak bilgisi line-clamp ile gizlenmemeli.');

assert(htaccess.includes('RewriteRule ^ https://www.alo186.com%{REQUEST_URI} [R=301,L,NE]'), 'www canonical yönlendirmesi eksik.');
for (const header of [
  'Strict-Transport-Security',
  'X-Content-Type-Options',
  'Content-Security-Policy',
  'Referrer-Policy',
  'Permissions-Policy'
]) {
  assert(htaccess.includes(header), `Production güvenlik başlığı eksik: ${header}`);
}
assert(htaccess.includes('AddOutputFilterByType SUBSTITUTE text/html application/xhtml+xml'), 'Aktif live-copy substitute filtresi eksik.');
assert(htaccess.includes(oldLivePhrase), 'Bilinen yanlış canlı cümle fail-safe eşleşmesinde bulunmalı.');
assert(htaccess.includes('10 iş günü içinde ilgili dağıtım şirketinin resmî kanalına başvurun'), 'Fail-safe doğru 10 iş günü metnini üretmeli.');

console.log('ALO186 portal hardening: 42 rehber, 24 araç, canonical rotalar, 10 iş günü, erişilebilirlik ve aktif production korumaları geçti.');
