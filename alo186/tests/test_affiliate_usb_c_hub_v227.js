'use strict';

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const ROOT = path.resolve(__dirname, '..');
const ROUTE = path.join(ROOT, 'amazon-elektrik-urunleri', 'usb-c-hub-port-uygunluk-secimi');
const HTML = fs.readFileSync(path.join(ROUTE, 'index.html'), 'utf8');
const APP = fs.readFileSync(path.join(ROUTE, 'app-v227.js'), 'utf8');
const catalog = require(path.join(ROUTE, 'catalog-v227.js'));
const EXPECTED = new Map([
  ['B093FKT9BF', '60515'],
  ['B0DCZY52K3', 'UH6120C'],
  ['B08XNG4ZKN', 'AVC009BTSGY'],
]);

function walk(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) return walk(full);
    return [full];
  });
}

assert.strictEqual(catalog.version, 227);
assert.strictEqual(catalog.affiliateTag, 'alo186rehber-21');
assert.strictEqual(catalog.verificationMaxAgeDays, 45);
assert.strictEqual(catalog.category.risk, 'consumer-medium');
assert.strictEqual(catalog.category.affiliatePolicy, 'after_tool');
assert.strictEqual(catalog.category.professionalOnly, false);
assert.strictEqual(catalog.category.requiredTool, 'embedded-usb-c-hub-port-fit-v227');
assert.strictEqual(catalog.products.length, 3);
assert.strictEqual(new Set(catalog.products.map((item) => item.asin)).size, 3);

for (const product of catalog.products) {
  assert.strictEqual(EXPECTED.get(product.asin), product.mpn, `ASIN/MPN mismatch: ${product.asin}`);
  for (const field of ['userNeed', 'strengths', 'limitations', 'noBuyWhen', 'technicalSource', 'amazonSource', 'verifiedAt']) {
    assert.ok(product[field], `${product.asin} missing ${field}`);
  }
  assert.ok(product.strengths.length >= 3);
  assert.ok(product.limitations.length >= 3);
  assert.strictEqual(product.amazonSource, `https://www.amazon.com.tr/dp/${product.asin}`);
  const url = catalog.amazonProductUrl(product.asin);
  assert.ok(url.startsWith(`https://www.amazon.com.tr/dp/${product.asin}?`));
  assert.ok(url.includes('tag=alo186rehber-21'));
}

assert.strictEqual(catalog.verificationStatus(new Date('2026-09-17T12:00:00Z')).fresh, true, '45th day must remain fresh');
assert.strictEqual(catalog.verificationStatus(new Date('2026-09-18T12:00:00Z')).fresh, false, '46th day must fail closed');

const canonical = 'https://alo186.com/amazon-elektrik-urunleri/usb-c-hub-port-uygunluk-secimi/';
assert.strictEqual((HTML.match(new RegExp(`<link rel="canonical" href="${canonical}">`, 'g')) || []).length, 1);
assert.ok(HTML.includes('data-commercial-scope="after-tool"'));
assert.ok(HTML.includes('data-risk="consumer-medium"'));
assert.ok(HTML.includes('Reklam / satış ortaklığı açıklaması'));
assert.ok(HTML.includes('Satın almama koşulu'));
assert.strictEqual((HTML.match(/rel="sponsored nofollow noopener"/g) || []).length, 3);
assert.ok(!/href="https:\/\/www\.amazon\.com\.tr\/(?:dp|s\?k=)/i.test(HTML), 'Initial HTML must not contain an enabled Amazon href');
assert.ok(APP.includes("affiliatePolicy === 'after_tool'"));
assert.ok(APP.includes('professionalOnly === false'));
assert.ok(APP.includes('verificationStatus(new Date())'));
assert.ok(APP.includes("link.removeAttribute('href')"));

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
  assert.ok(Array.isArray(product.identifier) && product.identifier.length >= 2);
  assert.ok(Array.isArray(product.additionalProperty) && product.additionalProperty.length >= 3);
  assert.ok(!Object.prototype.hasOwnProperty.call(product, 'offers'));
}
const serialized = JSON.stringify(graph);
for (const forbidden of ['"Offer"', 'aggregateRating', 'priceCurrency', 'availability', 'seller', 'review', 'warranty']) {
  assert.ok(!serialized.includes(forbidden), `Forbidden structured field: ${forbidden}`);
}

const sourceExtensions = new Set(['.html', '.js', '.json']);
const duplicateHits = [];
for (const file of walk(ROOT)) {
  if (!sourceExtensions.has(path.extname(file))) continue;
  if (file.startsWith(path.join(ROOT, 'tests'))) continue;
  if (file.startsWith(ROUTE)) continue;
  const text = fs.readFileSync(file, 'utf8');
  for (const asin of EXPECTED.keys()) {
    if (text.includes(asin)) duplicateHits.push(`${asin}:${path.relative(ROOT, file)}`);
  }
}
assert.deepStrictEqual(duplicateHits, [], `Duplicate ASIN outside route: ${duplicateHits.join(', ')}`);

console.log(JSON.stringify({
  ok: true,
  route: '/amazon-elektrik-urunleri/usb-c-hub-port-uygunluk-secimi/',
  products: [...EXPECTED.keys()],
  knowledgeGraph: ['Product', 'Brand', 'ItemList', 'identifier', 'additionalProperty'],
  affiliatePolicy: 'after_tool',
  professionalOnlyBypass: false,
  staleBoundary: '45-open-46-closed',
  duplicateAsin: false,
}));
