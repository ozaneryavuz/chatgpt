'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const portal = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const manifest = JSON.parse(fs.readFileSync(path.join(root, 'deployment', 'routing-manifest.json'), 'utf8'));
const sitemap = fs.readFileSync(path.join(root, 'sitemap.xml'), 'utf8');
const sourceCanonicalHosts = new Set(['alo186.com', 'www.alo186.com']);

const pages = [
  {
    source: 'kesinti-hazirlik-atolyesi',
    canonical: '/kesintiye-hazirlik-atolyesi',
    type: 'commerce-guide',
    required: ['Satış ortaklığı açıklaması', 'Satın almama geçerli sonuç', 'Kişisel veri yok'],
    jsRequired: ['fast_revenue_plan_rendered', 'buy_nothing', '/akilli-urun-secimi?kategori=mini_ups', '/kurumsal-elektrik-surekliligi-on-degerlendirme']
  },
  {
    source: 'kurumsal-on-degerlendirme',
    canonical: '/kurumsal-elektrik-surekliligi-on-degerlendirme',
    type: 'service',
    required: ['Ücretli profesyonel hizmet', 'Kapsam, ücret', 'ALO186, EDAŞ veya kamu kurumu değildir'],
    jsRequired: ['mailto:bilgi@alo186.com', 'paid_assessment_request_prepared', 'ücretli teknik ön değerlendirme']
  },
  {
    source: 'tedarikci-isbirligi',
    canonical: '/tedarikci-ve-uretici-isbirligi',
    type: 'partnership',
    required: ['Sponsorlu', 'Ödeme; organik teknik sıralamayı', 'Sponsorlu çalışmalar açıkça etiketlenir'],
    jsRequired: ['mailto:bilgi@alo186.com', 'supplier_partnership_request_prepared', 'organik teknik sıralamanın ödeme ile değiştirilmemesini']
  }
];

function parseJsonLd(html, source) {
  const blocks = [...html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)];
  assert(blocks.length >= 1, `${source}: JSON-LD eksik`);
  for (const block of blocks) JSON.parse(block[1]);
}

function canonicalHref(html) {
  const match = html.match(/<link\b(?=[^>]*\brel=["']canonical["'])(?=[^>]*\bhref=["']([^"']+)["'])[^>]*>/i);
  return match ? match[1] : '';
}

for (const item of pages) {
  const dir = path.join(root, item.source);
  const html = fs.readFileSync(path.join(dir, 'index.html'), 'utf8');
  const css = fs.readFileSync(path.join(dir, 'styles.css'), 'utf8');
  const js = fs.readFileSync(path.join(dir, 'app.js'), 'utf8');
  const productionCanonicalUrl = `${manifest.canonicalHost}${item.canonical}`;
  const sourceCanonical = new URL(canonicalHref(html));

  assert.equal(sourceCanonical.protocol, 'https:', `${item.source}: canonical HTTPS olmalı`);
  assert(sourceCanonicalHosts.has(sourceCanonical.hostname), `${item.source}: canonical host geçersiz`);
  assert.equal(sourceCanonical.pathname.replace(/\/$/, ''), item.canonical.replace(/\/$/, ''), `${item.source}: canonical rota uyuşmuyor`);
  assert.equal(sourceCanonical.search, '', `${item.source}: canonical query içermemeli`);
  assert.equal(sourceCanonical.hash, '', `${item.source}: canonical fragment içermemeli`);
  assert.equal((html.match(/<h1\b/g) || []).length, 1, `${item.source}: tek H1 olmalı`);
  assert(html.includes('meta name="description"'), `${item.source}: description eksik`);
  parseJsonLd(html, item.source);
  for (const text of item.required) assert(html.includes(text), `${item.source}: zorunlu açıklama eksik: ${text}`);
  for (const text of item.jsRequired) assert(js.includes(text), `${item.source}: JS sözleşmesi eksik: ${text}`);

  assert(!/amazon\.(com|com\.tr)\//i.test(html + js), `${item.source}: doğrudan Amazon URL'si bulunmamalı`);
  assert(!/type="(?:email|tel|text)"/i.test(html), `${item.source}: kişisel veri/serbest metin alanı bulunmamalı`);
  assert(!/name="(?:name|email|phone|address|subscription|identity|plate|serial|company|note|message)"/i.test(html), `${item.source}: PII alan adı bulunmamalı`);
  assert(css.includes('min-height:44px') || css.includes('min-height:48px'), `${item.source}: mobil hedef sözleşmesi eksik`);
  assert(css.includes(':focus-visible'), `${item.source}: klavye odağı eksik`);
  assert(css.includes('prefers-reduced-motion'), `${item.source}: azaltılmış hareket desteği eksik`);

  assert(manifest.routes.some((route) => route.source === `alo186/${item.source}/index.html` && route.canonicalPath === item.canonical && route.type === item.type), `${item.source}: routing manifest kaydı eksik`);
  assert(sitemap.includes(`<loc>${productionCanonicalUrl}</loc>`), `${item.source}: sitemap kaydı eksik`);
  assert(portal.includes(`href="${item.canonical}"`), `${item.source}: portal görünürlüğü eksik`);
}

assert(portal.includes('kişisel veri istemeyen araçlar'), 'Portal 26 araç kapsamını göstermeli.');
assert(portal.includes('kaynak doğrulamalı rehberler'), 'Portal 45 rehber kapsamını göstermeli.');
assert(portal.includes('Akıllı Priz ve Enerji Ölçer Uygunluğu'), '26. araç portalda görünmeli.');
for (const label of ['Satış ortaklığı', 'Ücretli profesyonel hizmet', 'Sponsorlu iş birliği']) {
  assert(portal.includes(label), `Portal ticari ilişki etiketi eksik: ${label}`);
}
assert(portal.includes('Ödeme organik teknik sıralamayı satın alamaz'), 'Sponsorlu sıralama satın alma yasağı görünür olmalı.');
assert(portal.includes('/haberler/kacak-akim-rolesi-kac-amper-kac-ma-olmali'), '45 rehber kümesinin yeni RCD sayfası portalda görünmeli.');
assert(portal.includes('/haberler/notr-toprak-arasi-gerilim-kac-volt-olmali'), '45 rehber kümesinin nötr-toprak sayfası portalda görünmeli.');
assert(portal.includes('/haberler/ges-inverter-afci-dc-ark-hatasi'), '45 rehber kümesinin AFCI sayfası portalda görünmeli.');

console.log('ALO186 hızlı gelir dönüşümü: tüketici affiliate atölyesi, ücretli B2B hizmeti, sponsorlu iş birliği, gizlilik, şeffaflık, routing ve sitemap testleri başarılı.');
