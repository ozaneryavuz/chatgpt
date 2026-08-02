'use strict';

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const root = path.resolve(__dirname, '..');
const routeDir = path.join(root, 'amazon-elektrik-urunleri', 'ev-ofis-gigabit-switch-secimi');
const html = fs.readFileSync(path.join(routeDir, 'index.html'), 'utf8');
const catalogSource = fs.readFileSync(path.join(routeDir, 'catalog-v222.js'), 'utf8');
const catalog = require(path.join(routeDir, 'catalog-v222.js'));
const expected = new Map([
  ['B00A128S24', 'TL-SG105'],
  ['B00A121WN6', 'TL-SG108'],
  ['B00N0OHEMA', 'TL-SG105E'],
]);

assert.strictEqual(catalog.version, 222);
assert.strictEqual(catalog.affiliateTag, 'alo186rehber-21');
assert.strictEqual(catalog.verificationMaxAgeDays, 45);
assert.strictEqual(catalog.category.affiliatePolicy, 'after_tool');
assert.strictEqual(catalog.category.professionalOnly, false);
assert.strictEqual(catalog.category.risk, 'consumer-medium');
assert.strictEqual(catalog.products.length, 3);
assert.deepStrictEqual(new Set(catalog.products.map((p) => p.asin)), new Set(expected.keys()));

for (const product of catalog.products) {
  assert.strictEqual(expected.get(product.asin), product.mpn);
  assert.ok(product.brand && product.name && product.userNeed);
  assert.ok(product.strengths.length >= 3);
  assert.ok(product.limitations.length >= 3);
  assert.ok(product.noBuyWhen.includes('satın almayın'));
  assert.ok(product.technicalSource.startsWith('https://www.tp-link.com/'));
  const url = catalog.amazonProductUrl(product.asin);
  assert.ok(url === `https://www.amazon.com.tr/dp/${product.asin}?tag=alo186rehber-21`);
}

assert.strictEqual(catalog.verificationStatus(new Date('2026-09-16T00:00:00Z')).fresh, true, '45. gün açık olmalı');
assert.strictEqual(catalog.verificationStatus(new Date('2026-09-17T00:00:00Z')).fresh, false, '46. gün stale fail-closed olmalı');
assert.throws(() => catalog.amazonProductUrl('B000000000'), /Unknown ASIN/);

const canonical = 'https://alo186.com/amazon-elektrik-urunleri/ev-ofis-gigabit-switch-secimi/';
assert.strictEqual((html.match(new RegExp(`<link rel="canonical" href="${canonical}">`, 'g')) || []).length, 1);
assert.ok(html.includes('Reklam / satış ortaklığı açıklaması'));
assert.ok(html.includes('data-commercial-scope="after-tool"'));
assert.ok(html.includes('rel="sponsored nofollow noopener"'));
assert.ok(!/href=["']https:\/\/www\.amazon\.com\.tr\//i.test(html), 'İlk DOM içinde kapısız Amazon href olamaz');
assert.ok(html.includes('professional') || html.includes('Profesyonel'));
assert.ok(html.includes('doğrudan satın alma CTA’sı açılmaz'));

const scripts = [...html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)];
assert.strictEqual(scripts.length, 1);
const graph = JSON.parse(scripts[0][1])['@graph'];
const products = graph.filter((node) => node['@type'] === 'Product');
const itemLists = graph.filter((node) => node['@type'] === 'ItemList');
assert.strictEqual(products.length, 3);
assert.strictEqual(itemLists.length, 1);
assert.strictEqual(itemLists[0].numberOfItems, 3);
for (const product of products) {
  assert.strictEqual(product.brand['@type'], 'Brand');
  const identifiers = Object.fromEntries(product.identifier.map((x) => [x.propertyID, x.value]));
  assert.strictEqual(expected.get(identifiers.ASIN), identifiers.MPN);
  assert.ok(product.additionalProperty.length >= 4);
  assert.strictEqual(product.offers, undefined);
}
const jsonLd = scripts[0][1];
for (const forbidden of ['"offers"', '"Offer"', '"price"', '"priceCurrency"', '"availability"', '"aggregateRating"', '"review"', '"seller"', '"warranty"']) {
  assert.ok(!jsonLd.includes(forbidden), `Yasak yapılandırılmış alan: ${forbidden}`);
}

function walk(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) return walk(full);
    return [full];
  });
}
const allowedPrefix = `${routeDir}${path.sep}`;
for (const file of walk(root)) {
  if (file.startsWith(allowedPrefix) || file === __filename) continue;
  if (!/\.(?:html|js|json|py|md|yml|yaml)$/i.test(file)) continue;
  const body = fs.readFileSync(file, 'utf8');
  for (const asin of expected.keys()) {
    assert.ok(!body.includes(asin), `Duplicate ASIN başka dosyada bulundu: ${asin} -> ${path.relative(root, file)}`);
  }
}

assert.ok(catalogSource.includes("verificationMaxAgeDays = 45"));
console.log(JSON.stringify({ ok: true, version: 222, products: [...expected.keys()], staleGate: '45-pass/46-block', directHighRiskCta: false }));
