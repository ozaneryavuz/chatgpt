'use strict';

const assert = require('node:assert/strict');
const catalog = require('../urun-eslestirme/catalog-car-charger-run54.js');

assert.equal(catalog.affiliateTag, 'alo186rehber-21');
assert.equal(catalog.__affiliateProductExpansionV104, true);
assert.ok(catalog.productExpansionV104);
assert.equal(catalog.productExpansionV104.version, 104);
assert.equal(catalog.productExpansionV104.generatedAt, '2026-07-30');

const newIds = [
  'spigen-ach08701-20w',
  'ugreen-nexode-140w-90549',
  'apple-140w-a2452',
  'belkin-avc006-4in1',
  'ugreen-hdmi21-25911-3m',
  'veggieg-vz631-dp14-2m',
  'veggieg-vz623-usbc-dp14-2m',
  'daytona-hc01-usbc-hdmi-18m'
];
const expectedAsins = new Map([
  ['spigen-ach08701-20w', 'B0DWT5G6QQ'],
  ['ugreen-nexode-140w-90549', 'B0B127GW4D'],
  ['apple-140w-a2452', 'B0D232C5JJ'],
  ['belkin-avc006-4in1', 'B08X5168HM'],
  ['ugreen-hdmi21-25911-3m', 'B0CFF9T3PS'],
  ['veggieg-vz631-dp14-2m', 'B0DN61ZDBQ'],
  ['veggieg-vz623-usbc-dp14-2m', 'B0DK6QPTFQ'],
  ['daytona-hc01-usbc-hdmi-18m', 'B096G51911']
]);

const allIds = new Set(catalog.products.map((product) => product.id));
const allAsins = catalog.products.map((product) => product.asin).filter(Boolean);
assert.equal(new Set(allAsins).size, allAsins.length, 'ASIN değerleri benzersiz olmalı.');
for (const id of newIds) {
  assert.ok(allIds.has(id), `Yeni ürün eksik: ${id}`);
  const product = catalog.getProduct(id);
  assert.equal(product.status, 'verified_listing');
  assert.equal(product.verifiedAt, '2026-07-30');
  assert.equal(product.asin, expectedAsins.get(id));
  assert.match(product.asin, /^B[A-Z0-9]{9}$/);
  assert.ok(product.mpn && product.brand && product.name && product.technicalSource);
  assert.ok(product.userNeed, `${id} kullanıcı ihtiyacı eksik.`);
  assert.ok(product.bestFor.length >= 2, `${id} kullanım bağlamı eksik.`);
  assert.ok(product.noBuyWhen.length >= 2, `${id} satın almama koşulu eksik.`);
  assert.ok(product.requiredEvidence.length >= 4, `${id} teknik kanıt eksik.`);
  assert.ok(product.intentIds.length >= 1, `${id} kullanıcı niyeti bağlantısı eksik.`);
  assert.ok(product.needIds.length >= 1, `${id} Knowledge Graph ihtiyaç bağlantısı eksik.`);
  assert.match(product.url, new RegExp(`amazon\\.com\\.tr/dp/${product.asin}`));
  assert.match(product.url, /[?&]tag=alo186rehber-21(?:&|$)/);
  for (const forbidden of ['price', 'stock', 'rating', 'aggregateRating', 'review', 'seller', 'warranty', 'availability', 'offers']) {
    assert.ok(!(forbidden in product), `${id} yasak ticari alan içeriyor: ${forbidden}`);
  }
}

const now = new Date('2026-07-30T12:00:00Z');
for (const id of newIds) {
  const product = catalog.getProduct(id);
  assert.equal(catalog.verificationStatus(product, now).fresh, true);
  assert.equal(catalog.publicAffiliateEligible(product, { now }), true, `${id} doğrudan yayın kapısından geçmeli.`);
}

const displayCategory = catalog.getCategory('display_cable');
assert.match(displayCategory.name, /HDMI/);
assert.match(displayCategory.name, /DisplayPort/);
assert.ok(catalog.getCategory('car_charger'));
assert.ok(catalog.getCategory('portable_evse'));
for (const needId of ['phone-fast-charging', 'high-power-usbc-laptop', 'portable-workstation', 'high-refresh-display', 'usbc-video-output']) {
  assert.ok(catalog.needs.some((need) => need.id === needId), `Yeni ihtiyaç düğümü eksik: ${needId}`);
}

const payload = catalog.knowledgeGraph({ now });
assert.equal(payload['@context'], 'https://schema.org');
const graph = payload['@graph'];
assert.ok(Array.isArray(graph));
const productNodes = graph.filter((node) => node['@type'] === 'Product');
const offerNodes = graph.filter((node) => node['@type'] === 'Offer');
assert.equal(offerNodes.length, 0);
for (const id of newIds) {
  const product = catalog.getProduct(id);
  const node = productNodes.find((item) => item.sku === id);
  assert.ok(node, `Product düğümü eksik: ${id}`);
  assert.equal(node.sameAs, product.url);
  assert.equal(node.dateModified, '2026-07-30');
  assert.ok(node.identifier.some((item) => item.propertyID === 'ASIN' && item.value === product.asin));
  assert.ok(node.identifier.some((item) => item.propertyID === 'MPN' && item.value === product.mpn));
  assert.ok(node.audience && node.audience['@type'] === 'Audience');
  assert.match(node.keywords, /,/);
  for (const propertyName of ['Kullanıcı ihtiyacı', 'En uygun kullanım', 'Satın almama koşulu', 'Satın alma öncesi kanıt']) {
    assert.ok(node.additionalProperty.some((item) => item.name === propertyName), `${id} KG alanı eksik: ${propertyName}`);
  }
}

for (const node of graph) {
  for (const forbidden of ['offers', 'aggregateRating', 'review', 'price', 'priceCurrency', 'availability', 'seller', 'warranty']) {
    assert.ok(!(forbidden in node), `Yasak ticari alan Knowledge Graph'a sızdı: ${forbidden}`);
  }
}

const summary = catalog.knowledgeGraphSummary();
assert.equal(summary.version, '2026-07-30-v104');
assert.ok(summary.exactListingCount >= 28, `Doğrulanmış ASIN sayısı düşük: ${summary.exactListingCount}`);
assert.ok(summary.productCount >= summary.exactListingCount);
assert.ok(summary.userFocusedProductCount >= 11);

const stalePayload = catalog.knowledgeGraph({ now: new Date('2026-09-20T12:00:00Z') });
assert.equal(stalePayload['@graph'].filter((node) => node['@type'] === 'Product').length, 0);

console.log(JSON.stringify({
  ok: true,
  version: catalog.productExpansionV104.version,
  exactProductsAddedInExtension: newIds.length,
  totalCatalogProducts: catalog.products.length,
  exactListingCount: summary.exactListingCount,
  publicProductNodes: productNodes.length,
  offerNodes: offerNodes.length,
  userFocusedProductCount: summary.userFocusedProductCount
}, null, 2));
