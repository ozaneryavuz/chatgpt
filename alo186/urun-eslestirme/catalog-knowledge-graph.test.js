'use strict';

const assert = require('node:assert/strict');
const catalog = require('./catalog.js');

const forbidden = new Set(['price','stock','rating','seller','delivery','warranty','affiliateCommission']);
function collectKeys(value, result = new Set()) {
  if (Array.isArray(value)) value.forEach((item) => collectKeys(item, result));
  else if (value && typeof value === 'object') Object.entries(value).forEach(([key, nested]) => { result.add(key); collectKeys(nested, result); });
  return result;
}

assert.equal(catalog.categories.length, 14, 'Kategori sayısı beklenenden farklı.');
assert.equal(catalog.needs.length, 14, 'İhtiyaç düğümü sayısı beklenenden farklı.');
assert.equal(catalog.products.length, 11, 'Ürün düğümü sayısı beklenenden farklı.');
assert.deepEqual(catalog.knowledgeGraphSummary(), {
  version: '2026-07-29-run34',
  generatedAt: '2026-07-29',
  needCount: 14,
  categoryCount: 14,
  productCount: 11,
  exactListingCount: 7,
  manufacturerSearchCount: 4,
  affiliatePolicies: ['verified_direct','after_tool','professional_only']
});

for (const category of catalog.categories) {
  assert(category.graph, `Kategori graph ilişkisi eksik: ${category.id}`);
  assert(Array.isArray(category.graph.needIds) && category.graph.needIds.length >= 1, category.id);
  assert(Array.isArray(category.graph.relatedTools) && category.graph.relatedTools.length >= 1, category.id);
  assert(Array.isArray(category.graph.requiredEvidence) && category.graph.requiredEvidence.length >= 3, category.id);
  for (const needId of category.graph.needIds) assert(catalog.needs.some((need) => need.id === needId), `${category.id} → ${needId}`);
}

const expectedNew = {
  'tp-link-tapo-p110': { category: 'smart_plug', source: 'tp-link.com', maxCurrentA: 16, maxPowerW: 3680 },
  'tp-link-tapo-p110m': { category: 'smart_plug', source: 'tp-link.com', maxCurrentA: 16, maxPowerW: 3680, matter: true },
  'ecoflow-river-2': { category: 'power_station', source: 'ecoflow.com.tr', capacityWh: 256, continuousW: 300, pureSine: true },
  'x-sense-xs01': { category: 'smoke_alarm', source: 'x-sense.com.tr', alarmDb: 85, standard: 'EN 14604' }
};

for (const [id, expected] of Object.entries(expectedNew)) {
  const product = catalog.getProduct(id);
  assert(product, `Yeni ürün düğümü eksik: ${id}`);
  assert.equal(product.status, 'manufacturer_verified_search');
  assert.equal(product.linkMode, 'exact_model_search');
  assert.equal(product.asin, null);
  assert.equal(product.verifiedAt, '2026-07-29');
  assert(product.technicalSource.includes(expected.source));
  assert(product.url.startsWith('https://www.amazon.com.tr/s?k='));
  assert(product.url.includes(`tag=${catalog.affiliateTag}`));
  assert.equal(product.category, expected.category);
  for (const [key, value] of Object.entries(expected)) {
    if (['category','source'].includes(key)) continue;
    assert.equal(product.attributes[key], value, `${id}.${key}`);
  }
  assert(product.graph.useCaseIds.length >= 1);
  assert(product.graph.relatedTools.length >= 1);
  assert(product.graph.requiredEvidence.length >= 3);
  assert(catalog.verificationStatus(product, new Date('2026-07-29T12:00:00Z')).fresh);
  assert.equal(catalog.productLinkLabel(product), 'Amazon’da tam model araması');
}

const direct = catalog.products.filter((product) => product.status === 'verified_listing');
assert.equal(direct.length, 7);
for (const product of direct) {
  assert(product.asin);
  assert.equal(product.linkMode, 'asin_detail');
  assert(product.url.includes(`/dp/${product.asin}`));
  assert.equal(catalog.productLinkLabel(product), 'Amazon ürün sayfasını aç');
}

assert.equal(catalog.productsFor('smart_plug', { freshOnly: false }).length, 2);
assert.equal(catalog.productsFor('power_station', { freshOnly: false }).length, 1);
assert.equal(catalog.productsFor('smoke_alarm', { freshOnly: false }).length, 1);
assert.equal(catalog.graphForCategory('smart_plug').products.length, 2);
assert.equal(catalog.graphForCategory('power_station').needs[0].id, 'portable-backup-energy');
assert.equal(catalog.getCategory('outlet_tester').affiliatePolicy, 'professional_only');

const foundForbidden = [...collectKeys({ categories: catalog.categories, products: catalog.products })].filter((key) => forbidden.has(key));
assert.deepEqual(foundForbidden, [], `Yasak ticari alanlar bulundu: ${foundForbidden.join(', ')}`);

console.log('ALO186 affiliate Product Knowledge Graph: 14 ihtiyaç, 14 kategori, 11 ürün ve 4 yeni üretici kaynaklı model doğrulandı.');
