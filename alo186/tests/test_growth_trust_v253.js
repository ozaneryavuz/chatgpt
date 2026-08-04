'use strict';

const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..');
const PAGE = path.join(ROOT, 'amazon-elektrik-urunleri', 'akilli-priz-enerji-olcer-secimi', 'index.html');
const CATALOG = path.join(ROOT, 'amazon-elektrik-urunleri', 'akilli-priz-enerji-olcer-secimi', 'catalog-v253.js');
const APP = path.join(ROOT, 'amazon-elektrik-urunleri', 'akilli-priz-enerji-olcer-secimi', 'app-v253.js');
const TRACK = path.join(ROOT, 'assets', 'alo186-track-v253.js');

const html = fs.readFileSync(PAGE, 'utf8');
const catalogSource = fs.readFileSync(CATALOG, 'utf8');
const appSource = fs.readFileSync(APP, 'utf8');
const trackSource = fs.readFileSync(TRACK, 'utf8');

const canonicalUrl = 'https://alo186.com/amazon-elektrik-urunleri/akilli-priz-enerji-olcer-secimi';
assert.ok(html.includes(`<link rel="canonical" href="${canonicalUrl}">`));
assert.ok(!html.includes(`<link rel="canonical" href="${canonicalUrl}/">`));
assert.ok(!html.includes('https://www.alo186.com/amazon-elektrik-urunleri/akilli-priz-enerji-olcer-secimi'));
assert.ok(html.includes(`"@id":"${canonicalUrl}#page"`));
assert.ok(html.includes(`"url":"${canonicalUrl}"`));
assert.ok(html.includes(`"@id":"${canonicalUrl}#product-list"`));
assert.ok(!html.includes(`${canonicalUrl}/#`), 'JSON-LD must not split the canonical route with a slash');
assert.ok(!html.toLowerCase().includes('amazon.com.tr'), 'source HTML must not contain a static store URL');

const expectedAsins = ['B0C4LHP7G3', 'B0BTJ1DTBX', 'B07Z5JD3T4'];
expectedAsins.forEach((asin) => {
  assert.strictEqual((html.match(new RegExp(asin, 'g')) || []).length >= 2, true, `${asin} page and schema presence`);
  assert.match(catalogSource, new RegExp(`https://www\\.amazon\\.com\\.tr/dp/${asin}`));
});
assert.strictEqual((html.match(/data-affiliate-asin=/g) || []).length, 3);
assert.strictEqual((html.match(/rel="sponsored nofollow noopener"/g) || []).length, 3);
assert.strictEqual((html.match(/"@type":"Product"/g) || []).length, 3);
assert.ok(!html.includes('data-fresh-products'));

const forbiddenCommercialClaims = [
  /"@type"\s*:\s*"Offer"/i,
  /aggregateRating/i,
  /ratingValue/i,
  /priceCurrency/i,
  /"price"\s*:/i,
  /availability/i
];
forbiddenCommercialClaims.forEach((pattern) => assert.ok(!pattern.test(html), `forbidden field: ${pattern}`));

const gates = [
  'gateConsumerUse', 'gateGrounded', 'gateLoad', 'gateNoHighRisk', 'gateCondition',
  'gateIndoor', 'gateFeature', 'gateVariant', 'gateNeed', 'gateAffiliate'
];
gates.forEach((id) => assert.match(html, new RegExp(`id="${id}"`)));
assert.match(html, /id="noBuySmartPlug"/);
assert.match(html, /id="smartPlugReminder90"/);
assert.match(html, /Mevcut çözümüm yeterli — satın almayacağım/);
assert.match(html, /ALO186 bağımsız bilgilendirme platformudur|Bağımsız bilgilendirme platformudur/);
assert.match(html, /Amazon Türkiye bağlantıları satış ortaklığı bağlantısıdır|Amazon Türkiye bağlantıları satış ortaklığı/);
assert.match(html, /Fiyat, stok, satıcı, teslimat, puan, yorum ve garanti yalnız mağazanın güncel sayfasında doğrulanır/);
assert.match(html, /src="\/assets\/alo186-track-v253\.js"/);
assert.match(html, /src="\.\/catalog-v253\.js"/);
assert.match(html, /src="\.\/app-v253\.js"/);

assert.ok(!/fetch\s*\(/.test(trackSource));
assert.ok(!/XMLHttpRequest/.test(trackSource));
assert.ok(!/localStorage|sessionStorage|document\.cookie/.test(trackSource));
assert.match(trackSource, /blockedKeyPattern/);
assert.match(trackSource, /email\|mail\|phone\|telefon\|address\|adres/);
assert.match(trackSource, /window\.dataLayer\.push/);
assert.match(trackSource, /CustomEvent\('alo186:analytics'/);

const sandbox = { module: { exports: {} }, exports: {}, globalThis: {} };
vm.runInNewContext(catalogSource, sandbox, { filename: CATALOG });
const catalog = sandbox.module.exports;
assert.strictEqual(catalog.version, 253);
assert.strictEqual(catalog.affiliateTag, 'alo186rehber-21');
assert.strictEqual(catalog.category.affiliatePolicy, 'after_tool');
assert.strictEqual(catalog.category.professionalOnly, false);
assert.strictEqual(catalog.category.highRiskDirectCta, false);
assert.strictEqual(catalog.products.length, 3);
assert.deepStrictEqual(Array.from(catalog.products, (product) => product.asin), expectedAsins);
assert.ok(catalog.products.every((product) => product.noBuyWhen && product.limitations.length >= 3));
assert.ok(catalog.products.every((product) => catalog.verificationStatus(product, new Date('2026-09-17T00:00:00Z')).fresh));
assert.ok(catalog.products.every((product) => !catalog.verificationStatus(product, new Date('2026-09-18T00:00:00Z')).fresh));
assert.ok(catalog.products.every((product) => catalog.amazonProductUrl(product, new Date('2026-08-03T12:00:00Z')).includes('tag=alo186rehber-21')));

assert.match(appSource, /affiliate_no_buy_selected/);
assert.match(appSource, /affiliate_gate_passed/);
assert.match(appSource, /affiliate_product_clicked/);
assert.match(appSource, /return_visit_reminder_downloaded/);
assert.match(appSource, /90 günlük kontrol/);
assert.ok(!/localStorage|sessionStorage|fetch\s*\(/.test(appSource));

console.log('ALO186 growth and trust v253 checks passed.');