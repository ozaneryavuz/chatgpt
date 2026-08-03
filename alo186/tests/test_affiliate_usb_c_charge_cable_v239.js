'use strict';

const assert = require('assert');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
const ROUTE = 'amazon-elektrik-urunleri/usb-c-sarj-kablosu-guc-uygunluk-secimi';
const routeDir = path.join(ROOT, 'alo186', ROUTE);
const catalog = require(path.join(routeDir, 'catalog-v239.js'));
const html = fs.readFileSync(path.join(routeDir, 'index.html'), 'utf8');
const app = fs.readFileSync(path.join(routeDir, 'app-v239.js'), 'utf8');
const overlay = JSON.parse(fs.readFileSync(path.join(ROOT, 'alo186/deployment/routing-overlays/239-affiliate-usb-c-charge-cable.json'), 'utf8'));

assert.strictEqual(catalog.version, 239);
assert.strictEqual(catalog.affiliateTag, 'alo186rehber-21');
assert.strictEqual(catalog.verificationMaxAgeDays, 45);
assert.strictEqual(catalog.verifiedAt, '2026-08-03');
assert.strictEqual(catalog.category.affiliatePolicy, 'after_tool');
assert.strictEqual(catalog.category.requiredTool, 'embedded-usb-c-charge-cable-power-compatibility-v239');
assert.strictEqual(catalog.category.professionalOnly, false);
assert.strictEqual(catalog.category.risk, 'consumer-low');
assert.strictEqual(catalog.products.length, 3);

const expected = new Map([
  ['B0B46N4SK5', 'CAJY000601'],
  ['B0B46PHW14', 'CAJY000701'],
  ['B0144AE0V6', 'CATKLF-GG1']
]);
assert.deepStrictEqual(new Set(catalog.products.map((item) => item.asin)), new Set(expected.keys()));

for (const item of catalog.products) {
  assert.strictEqual(item.mpn, expected.get(item.asin));
  assert.strictEqual(item.brand, 'Baseus');
  assert.ok(item.userNeed.length > 40);
  assert.ok(item.strengths.length >= 3);
  assert.ok(item.limitations.length >= 3);
  assert.match(item.noBuyWhen, /satın alma yapmayın/i);
  assert.match(item.technicalSource, /^https:\/\/cz\.baseus\.com\//);
  assert.strictEqual(item.verifiedAt, '2026-08-03');
  assert.strictEqual(catalog.amazonProductUrl(item.asin), `https://www.amazon.com.tr/dp/${item.asin}?tag=alo186rehber-21`);
}

assert.strictEqual(catalog.verificationStatus(new Date('2026-09-17T00:00:00Z')).fresh, true);
assert.strictEqual(catalog.verificationStatus(new Date('2026-09-18T00:00:00Z')).fresh, false);

const canonical = 'https://alo186.com/amazon-elektrik-urunleri/usb-c-sarj-kablosu-guc-uygunluk-secimi/';
assert.ok(html.includes(`<link rel="canonical" href="${canonical}">`));
assert.ok(html.includes('"@type":"Product"'));
assert.ok(html.includes('"@type":"Brand"'));
assert.ok(html.includes('"@type":"ItemList"'));
assert.ok(html.includes('"propertyID":"ASIN"'));
assert.ok(html.includes('"propertyID":"MPN"'));
assert.ok(html.includes('"additionalProperty"'));
assert.ok(html.includes('rel="sponsored nofollow noopener"'));
assert.ok(html.includes('Reklam / satış ortaklığı açıklaması'));
assert.ok(html.includes('Mevcut kablo sağlam ve ihtiyacı karşılıyorsa satın alma yapmayın.'));
assert.ok(html.includes('data-commercial-scope="after-tool"'));
assert.ok(html.includes('professional_only: false'));
assert.ok(app.includes("catalog.category.professionalOnly === false"));
assert.ok(app.includes("catalog.category.affiliatePolicy === 'after_tool'"));
assert.ok(app.includes('catalog.verificationStatus(new Date())'));

for (const forbidden of [
  '"@type":"Offer"',
  'priceCurrency',
  'aggregateRating',
  'ratingValue',
  'stokta',
  'satıcı:',
  'garanti:',
  'hemen satın al',
  'en ucuz'
]) {
  assert.ok(!html.toLocaleLowerCase('tr-TR').includes(forbidden.toLocaleLowerCase('tr-TR')), `forbidden publication token: ${forbidden}`);
}

assert.ok(!/href="https:\/\/www\.amazon\.com\.tr/i.test(html), 'Amazon href must remain locked before tool');
assert.strictEqual(overlay.version, 239);
assert.strictEqual(overlay.routes[0].canonicalPath, '/amazon-elektrik-urunleri/usb-c-sarj-kablosu-guc-uygunluk-secimi/');
assert.strictEqual(overlay.routes[0].source, 'alo186/amazon-elektrik-urunleri/usb-c-sarj-kablosu-guc-uygunluk-secimi/index.html');

const catalogFiles = [];
function walk(dir) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full);
    else if (/catalog[^/]*\.js$/i.test(entry.name)) catalogFiles.push(full);
  }
}
walk(path.join(ROOT, 'alo186/amazon-elektrik-urunleri'));
for (const asin of expected.keys()) {
  let count = 0;
  for (const file of catalogFiles) {
    const text = fs.readFileSync(file, 'utf8');
    count += [...text.matchAll(new RegExp(`asin\\s*:\\s*['"]${asin}['"]`, 'g'))].length;
  }
  assert.strictEqual(count, 1, `duplicate ASIN in catalog files: ${asin}`);
}

console.log(JSON.stringify({
  ok: true,
  version: catalog.version,
  route: canonical,
  asins: [...expected.keys()],
  checks: [
    'canonical',
    'affiliate-tag',
    'sponsored-nofollow-noopener',
    'duplicate-asin',
    'stale-45-46',
    'knowledge-graph',
    'after-tool',
    'professional-only',
    'no-commercial-dynamic-fields'
  ]
}));
