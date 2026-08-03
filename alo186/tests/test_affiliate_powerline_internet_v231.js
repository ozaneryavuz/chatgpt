'use strict';

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const ROOT = path.resolve(__dirname, '..');
const ROUTE = path.join(ROOT, 'amazon-elektrik-urunleri', 'priz-hatti-powerline-internet-olcum-secimi');
const HTML = fs.readFileSync(path.join(ROUTE, 'index.html'), 'utf8');
const APP = fs.readFileSync(path.join(ROUTE, 'app-v231.js'), 'utf8');
const catalog = require(path.join(ROUTE, 'catalog-v231.js'));
const EXPECTED = new Map([
  ['B0859MDSFX', 'TL-PA7017P KIT'],
  ['B08XNLZLJ3', 'TL-WPA7617 KIT'],
  ['B00C2ICYPC', 'TL-WPA4220 KIT'],
]);

function walk(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const full = path.join(dir, entry.name);
    return entry.isDirectory() ? walk(full) : [full];
  });
}

assert.strictEqual(catalog.version, 231);
assert.strictEqual(catalog.affiliateTag, 'alo186rehber-21');
assert.strictEqual(catalog.verificationMaxAgeDays, 45);
assert.strictEqual(catalog.category.risk, 'consumer-medium');
assert.strictEqual(catalog.category.affiliatePolicy, 'after_tool');
assert.strictEqual(catalog.category.professionalOnly, false);
assert.strictEqual(catalog.category.requiredTool, 'embedded-powerline-circuit-and-speed-check-v231');
assert.ok(catalog.category.excludes.includes('damaged-hot-loose-or-ungrounded-outlet'));
assert.ok(catalog.category.excludes.includes('medical-or-life-safety-network'));
assert.ok(catalog.category.excludes.includes('industrial-control-or-building-automation'));
assert.strictEqual(catalog.products.length, 3);
assert.strictEqual(new Set(catalog.products.map((item) => item.asin)).size, 3);

for (const product of catalog.products) {
  assert.strictEqual(EXPECTED.get(product.asin), product.mpn, `ASIN/MPN mismatch: ${product.asin}`);
  for (const field of ['userNeed', 'strengths', 'limitations', 'noBuyWhen', 'technicalSource', 'verifiedAt']) assert.ok(product[field], `${product.asin} missing ${field}`);
  assert.ok(product.strengths.length >= 3);
  assert.ok(product.limitations.length >= 3);
  assert.ok(/^https:\/\/www\.tp-link\.com\/tr\/home-networking\/powerline\//.test(product.technicalSource));
  const url = catalog.amazonProductUrl(product.asin);
  assert.ok(url.startsWith(`https://www.amazon.com.tr/dp/${product.asin}?`));
  assert.ok(url.includes('tag=alo186rehber-21'));
}

assert.strictEqual(catalog.verificationStatus(new Date('2026-09-17T12:00:00Z')).fresh, true);
assert.strictEqual(catalog.verificationStatus(new Date('2026-09-18T12:00:00Z')).fresh, false);

const canonical = 'https://alo186.com/amazon-elektrik-urunleri/priz-hatti-powerline-internet-olcum-secimi/';
assert.strictEqual((HTML.match(new RegExp(`<link rel="canonical" href="${canonical}">`, 'g')) || []).length, 1);
for (const token of ['data-commercial-scope="after-tool"', 'data-risk="consumer-medium"', 'Affiliate / satış ortaklığı açıklaması', 'Satın almama koşulu', 'rel="sponsored nofollow noopener"']) assert.ok(HTML.includes(token), token);
assert.ok(!/href="https:\/\/www\.amazon\.com\.tr\/(?:dp|s\?k=)/i.test(HTML));
for (const token of ["affiliatePolicy === 'after_tool'", 'professionalOnly === false', 'verificationStatus(new Date())', "link.removeAttribute('href')"]) assert.ok(APP.includes(token), token);

const jsonLd = [...HTML.matchAll(/<script type="application\/ld\+json">\s*(.*?)\s*<\/script>/gs)];
assert.strictEqual(jsonLd.length, 1);
const graph = JSON.parse(jsonLd[0][1])['@graph'];
const products = graph.filter((node) => node['@type'] === 'Product');
const itemLists = graph.filter((node) => node['@type'] === 'ItemList');
assert.strictEqual(products.length, 3);
assert.strictEqual(itemLists.length, 1);
assert.strictEqual(itemLists[0].numberOfItems, 3);
for (const product of products) {
  assert.strictEqual(product.brand['@type'], 'Brand');
  assert.ok(product.identifier.length >= 2);
  assert.ok(product.additionalProperty.length >= 3);
  assert.ok(!Object.prototype.hasOwnProperty.call(product, 'offers'));
}
const serialized = JSON.stringify(graph);
for (const forbidden of ['"Offer"', 'aggregateRating', 'priceCurrency', 'availability', 'seller', 'review', 'warranty']) assert.ok(!serialized.includes(forbidden), forbidden);

const duplicateHits = [];
for (const file of walk(ROOT)) {
  if (!['.html', '.js', '.json'].includes(path.extname(file))) continue;
  if (file.startsWith(path.join(ROOT, 'tests')) || file.startsWith(ROUTE)) continue;
  const text = fs.readFileSync(file, 'utf8');
  for (const asin of EXPECTED.keys()) if (text.includes(asin)) duplicateHits.push(`${asin}:${path.relative(ROOT, file)}`);
}
assert.deepStrictEqual(duplicateHits, [], `Duplicate ASIN outside route: ${duplicateHits.join(', ')}`);

console.log(JSON.stringify({ok:true,route:'/amazon-elektrik-urunleri/priz-hatti-powerline-internet-olcum-secimi/',products:[...EXPECTED.keys()],knowledgeGraph:['Product','Brand','ItemList','identifier','additionalProperty'],affiliatePolicy:'after_tool',professionalOnlyBypass:false,staleBoundary:'45-open-46-closed',duplicateAsin:false}));
