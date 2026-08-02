'use strict';

const assert = require('assert');
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const pageDir = path.join(root, 'amazon-elektrik-urunleri', 'kamera-kayit-yuksek-dayanim-microsd-secimi');
const pagePath = path.join(pageDir, 'index.html');
const appPath = path.join(pageDir, 'app-v200.js');
const catalogPath = path.join(pageDir, 'catalog-v200.js');
const overlayPath = path.join(root, 'deployment', 'routing-overlays', '200-affiliate-endurance-microsd.json');
const catalog = require(catalogPath);
const page = fs.readFileSync(pagePath, 'utf8');
const app = fs.readFileSync(appPath, 'utf8');
const overlay = JSON.parse(fs.readFileSync(overlayPath, 'utf8'));

assert.strictEqual(catalog.version, 200);
assert.strictEqual(catalog.affiliateTag, 'alo186rehber-21');
assert.strictEqual(catalog.verifiedAt, '2026-08-02');
assert.strictEqual(catalog.maxAgeDays, 45);
assert.strictEqual(catalog.products.length, 3);

const expected = new Map([
  ['B07NY23WBG', 'SDSQQNR-128G-GN6IA'],
  ['B07PGBYMVH', 'SDCE/128GB'],
  ['B084CJ9T2R', 'SDSQQVR-128G-GN6IA'],
]);
const asins = new Set();
for (const product of catalog.products) {
  assert(/^[A-Z0-9]{10}$/.test(product.asin), `ASIN biçimi geçersiz: ${product.asin}`);
  assert.strictEqual(expected.get(product.asin), product.mpn, `ASIN/MPN eşleşmesi: ${product.asin}`);
  assert(!asins.has(product.asin), `Duplicate ASIN: ${product.asin}`);
  asins.add(product.asin);
  assert.strictEqual(
    catalog.amazonProductUrl(product.asin),
    `https://www.amazon.com.tr/dp/${product.asin}?tag=alo186rehber-21`
  );
}
assert.throws(() => catalog.amazonProductUrl('B000000000'), /Katalog dışı ASIN/);

assert.deepStrictEqual(catalog.verificationStatus(new Date('2026-08-02T12:00:00Z')), { fresh: true, ageDays: 0 });
assert.deepStrictEqual(catalog.verificationStatus(new Date('2026-09-16T12:00:00Z')), { fresh: true, ageDays: 45 });
assert.deepStrictEqual(catalog.verificationStatus(new Date('2026-09-17T12:00:00Z')), { fresh: false, ageDays: 46 });

const jsonLdMatches = [...page.matchAll(/<script type="application\/ld\+json">\s*([\s\S]*?)\s*<\/script>/g)];
assert.strictEqual(jsonLdMatches.length, 1, 'Tek JSON-LD graph bekleniyor');
const graph = JSON.parse(jsonLdMatches[0][1])['@graph'];
const products = graph.filter(node => node['@type'] === 'Product');
const itemLists = graph.filter(node => node['@type'] === 'ItemList');
assert.strictEqual(products.length, 3);
assert.strictEqual(itemLists.length, 1);
assert.strictEqual(itemLists[0].numberOfItems, 3);
assert(graph.some(node => node['@type'] === 'CollectionPage'));
assert(graph.some(node => node['@type'] === 'FAQPage'));
assert(graph.some(node => node['@type'] === 'BreadcrumbList'));

const kgAsins = new Set();
for (const product of products) {
  assert.strictEqual(product.brand['@type'], 'Brand');
  assert(product.brand.name);
  assert(product.additionalProperty.length >= 5);
  const identifiers = new Map(product.identifier.map(item => [item.propertyID, item.value]));
  const asin = identifiers.get('ASIN');
  const mpn = identifiers.get('MPN');
  assert.strictEqual(expected.get(asin), mpn);
  assert.strictEqual(product.mpn, mpn);
  assert(!kgAsins.has(asin));
  kgAsins.add(asin);
  for (const forbidden of ['offers', 'aggregateRating', 'review', 'price', 'availability', 'seller', 'warranty']) {
    assert(!(forbidden in product), `Yasak Product alanı: ${forbidden}`);
  }
}
assert.deepStrictEqual([...kgAsins].sort(), [...asins].sort());
const serializedGraph = JSON.stringify(graph);
for (const forbidden of ['"@type":"Offer"', 'priceCurrency', 'aggregateRating', 'availability', 'seller']) {
  assert(!serializedGraph.includes(forbidden), `Yasak ticari şema: ${forbidden}`);
}

const canonical = 'https://alo186.com/amazon-elektrik-urunleri/kamera-kayit-yuksek-dayanim-microsd-secimi/';
assert.strictEqual((page.match(new RegExp(`<link rel="canonical" href="${canonical}">`, 'g')) || []).length, 1);
assert.strictEqual((page.match(/data-affiliate-asin=/g) || []).length, 3);
assert.strictEqual((page.match(/rel="sponsored nofollow noopener"/g) || []).length, 3);
assert(!/href="https:\/\/www\.amazon\.com\.tr\/dp\//i.test(page), 'Kapısız Amazon href statik HTML’de olamaz');
for (const token of [
  'gateNeed', 'gateCompatibility', 'gateAffiliate',
  'Reklam / satış ortaklığı açıklaması', 'Satın almama koşulu',
  'professional_only', 'after_tool', 'Mevcut kart',
  './app-v200.js'
]) assert(page.includes(token), `Sayfa sözleşmesi eksik: ${token}`);

for (const token of [
  'Alo186EnduranceMicroSDCatalogV200', 'verificationStatus(new Date())',
  'amazonProductUrl(asin)', 'removeAttribute(\'href\')',
  'affiliate_endurance_microsd_clicked', 'catalog-v200.js'
]) assert(app.includes(token), `Runtime sözleşmesi eksik: ${token}`);
for (const forbidden of ['localStorage', 'sessionStorage', 'window.open(', 'geolocation']) {
  assert(!app.includes(forbidden), `Yasak runtime: ${forbidden}`);
}

assert.strictEqual(overlay.version, 200);
assert.strictEqual(overlay.routes.length, 1);
assert.strictEqual(overlay.routes[0].canonicalPath, '/amazon-elektrik-urunleri/kamera-kayit-yuksek-dayanim-microsd-secimi/');
assert.strictEqual(overlay.routes[0].source, 'alo186/amazon-elektrik-urunleri/kamera-kayit-yuksek-dayanim-microsd-secimi/index.html');
assert.strictEqual(overlay.routes[0].type, 'collection');

function walk(directory) {
  const files = [];
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    if (['.git', 'node_modules'].includes(entry.name)) continue;
    const full = path.join(directory, entry.name);
    if (entry.isDirectory()) files.push(...walk(full));
    else if (/\.(?:html|js|json|py)$/.test(entry.name)) files.push(full);
  }
  return files;
}
const exclusions = new Set([pagePath, appPath, catalogPath, __filename]);
for (const asin of asins) {
  const collisions = walk(root).filter(file => !exclusions.has(file) && fs.readFileSync(file, 'utf8').includes(asin));
  assert.deepStrictEqual(collisions, [], `ASIN başka katalogda tekrarlandı: ${asin}: ${collisions.join(', ')}`);
}

console.log(JSON.stringify({
  ok: true,
  version: catalog.version,
  products: catalog.products.length,
  uniqueAsins: asins.size,
  productSchema: true,
  offerSchema: false,
  tripleGate: true,
  staleFailClosed: true,
  duplicateAsin: false,
}));
