'use strict';
const assert = require('assert');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
const ROUTE = 'amazon-elektrik-urunleri/buzdolabi-dondurucu-sicaklik-olcum-termometre-secimi';
const routeDir = path.join(ROOT, 'alo186', ROUTE);
const catalog = require(path.join(routeDir, 'catalog-v238.js'));
const html = fs.readFileSync(path.join(routeDir, 'index.html'), 'utf8');
const app = fs.readFileSync(path.join(routeDir, 'app-v238.js'), 'utf8');
const overlay = JSON.parse(fs.readFileSync(path.join(ROOT, 'alo186/deployment/routing-overlays/238-affiliate-cold-temperature-thermometer.json'), 'utf8'));

assert.strictEqual(catalog.version, 238);
assert.strictEqual(catalog.affiliateTag, 'alo186rehber-21');
assert.strictEqual(catalog.verificationMaxAgeDays, 45);
assert.strictEqual(catalog.verifiedAt, '2026-08-03');
assert.strictEqual(catalog.category.affiliatePolicy, 'after_tool');
assert.strictEqual(catalog.category.requiredTool, 'embedded-cold-temperature-measurement-safety-v238');
assert.strictEqual(catalog.category.professionalOnly, false);
assert.strictEqual(catalog.category.risk, 'consumer-low');
assert.strictEqual(catalog.products.length, 3);
assert.ok(catalog.category.excludes.includes('medical-or-pharmaceutical-cold-chain'));
assert.ok(catalog.category.excludes.includes('laboratory-or-regulated-monitoring'));

const expected = new Map([
  ['B004A0UPTW', '30.1042'],
  ['B001F8MRFM', '14.4006'],
  ['B001386MUK', '30.1034']
]);
assert.deepStrictEqual(new Set(catalog.products.map((item) => item.asin)), new Set(expected.keys()));
for (const item of catalog.products) {
  assert.strictEqual(item.mpn, expected.get(item.asin));
  assert.strictEqual(item.brand, 'TFA Dostmann');
  assert.ok(item.userNeed.length > 40);
  assert.ok(item.strengths.length >= 3);
  assert.ok(item.limitations.length >= 3);
  assert.match(item.noBuyWhen, /satın alma yapmayın/i);
  assert.match(item.technicalSource, /^https:\/\/www\.tfa-dostmann\.de\//);
  assert.strictEqual(item.verifiedAt, '2026-08-03');
  assert.strictEqual(catalog.amazonProductUrl(item.asin), `https://www.amazon.com.tr/dp/${item.asin}?tag=alo186rehber-21`);
}

assert.strictEqual(catalog.verificationStatus(new Date('2026-09-17T00:00:00Z')).fresh, true);
assert.strictEqual(catalog.verificationStatus(new Date('2026-09-18T00:00:00Z')).fresh, false);

const canonical = 'https://alo186.com/amazon-elektrik-urunleri/buzdolabi-dondurucu-sicaklik-olcum-termometre-secimi/';
assert.ok(html.includes(`<link rel="canonical" href="${canonical}">`));
assert.ok(html.includes('"@type":"Product"'));
assert.ok(html.includes('"@type":"Brand"'));
assert.ok(html.includes('"@type":"ItemList"'));
assert.ok(html.includes('"propertyID":"ASIN"'));
assert.ok(html.includes('"propertyID":"MPN"'));
assert.ok(html.includes('"additionalProperty"'));
assert.ok(html.includes('rel="sponsored nofollow noopener"'));
assert.ok(html.includes('Reklam / satış ortaklığı açıklaması'));
assert.ok(html.includes('satın alma yapmayın'));
assert.ok(html.includes('data-commercial-scope="after-tool"'));
assert.ok(html.includes('professional_only=false'));
assert.ok(app.includes("catalog.category.professionalOnly === false"));
assert.ok(app.includes("catalog.category.affiliatePolicy === 'after_tool'"));
assert.ok(app.includes('catalog.verificationStatus(new Date())'));

for (const forbidden of [
  '"@type":"Offer"', 'priceCurrency', 'aggregateRating', 'ratingValue',
  'stokta', 'satıcı:', 'garanti:', 'hemen satın al', 'en ucuz'
]) {
  assert.ok(!html.toLocaleLowerCase('tr-TR').includes(forbidden.toLocaleLowerCase('tr-TR')), `forbidden publication token: ${forbidden}`);
}
assert.ok(!/href="https:\/\/www\.amazon\.com\.tr/i.test(html), 'Amazon href must remain locked before tool');
assert.strictEqual(overlay.version, 238);
assert.strictEqual(overlay.routes[0].canonicalPath, '/amazon-elektrik-urunleri/buzdolabi-dondurucu-sicaklik-olcum-termometre-secimi/');

const catalogFiles = [];
function walk(dir) {
  if (!fs.existsSync(dir)) return;
  for (const entry of fs.readdirSync(dir, {withFileTypes: true})) {
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
  checks: ['canonical','affiliate-tag','sponsored-nofollow-noopener','duplicate-asin','stale-45-46','knowledge-graph','after-tool','professional-only']
}));
