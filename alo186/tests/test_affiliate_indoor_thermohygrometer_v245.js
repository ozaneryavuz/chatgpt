const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const ROOT = path.resolve(__dirname, "..", "..");
const SLUG = "elektrik-kesintisi-sicaklik-nem-olcum-termometre-secimi";
const ROUTE = path.join(ROOT, "alo186", "amazon-elektrik-urunleri", SLUG);
const catalog = require(path.join(ROUTE, "catalog-v245.js"));
const html = fs.readFileSync(path.join(ROUTE, "index.html"), "utf8");
const app = fs.readFileSync(path.join(ROUTE, "app-v245.js"), "utf8");
const overlay = JSON.parse(fs.readFileSync(path.join(ROOT, "alo186", "deployment", "routing-overlays", "245-affiliate-indoor-thermohygrometer.json"), "utf8"));
const canonical = `https://alo186.com/amazon-elektrik-urunleri/${SLUG}/`;
const expected = [["B07P996ZKJ", "TP50"], ["B079N98K93", "TP53"], ["B06XZYP5FW", "TP55"]];

assert.equal(catalog.version, 245);
assert.equal(catalog.affiliateTag, "alo186rehber-21");
assert.equal(catalog.maxVerificationAgeDays, 45);
assert.equal(catalog.verifiedAt, "2026-08-03");
assert.equal(catalog.category.affiliatePolicy, "after_tool");
assert.equal(catalog.category.professionalOnly, false);
assert.match(catalog.category.requiredTool, /embedded-indoor-thermohygrometer-readiness-v245/);
assert.match(catalog.amazonTurkeyListingSource, /amazon\.com\.tr/);
assert.equal(catalog.products.length, 3);

const asins = catalog.products.map((product) => product.asin);
assert.equal(new Set(asins).size, 3);
assert.deepEqual(catalog.products.map((product) => [product.asin, product.mpn]), expected);

for (const product of catalog.products) {
  assert.equal(product.verifiedAt, "2026-08-03");
  assert.ok(product.userNeed.length > 80);
  assert.ok(product.strengths.length >= 3);
  assert.ok(product.limitations.length >= 3);
  assert.match(product.noBuyWhen, /satın alma yapmayın/i);
  assert.match(product.technicalSource, /^https:\/\//);
  assert.match(product.amazonAsinSource, /^https:\/\/www\.amazon\.com\.tr\//);
  assert.ok(Object.keys(product.technical).length >= 5);
  const fresh = catalog.verificationStatus(product, new Date("2026-09-17T00:00:00Z"));
  const stale = catalog.verificationStatus(product, new Date("2026-09-18T00:00:00Z"));
  assert.deepEqual(fresh, {ageDays: 45, fresh: true});
  assert.deepEqual(stale, {ageDays: 46, fresh: false});
  assert.equal(catalog.amazonProductUrl(product, new Date("2026-09-18T00:00:00Z")), null);
  assert.equal(catalog.amazonProductUrl(product, new Date("2026-08-03T12:00:00Z")), `https://www.amazon.com.tr/dp/${product.asin}?tag=alo186rehber-21`);
}

assert.match(html, new RegExp(`<link rel="canonical" href="${canonical.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}">`));
for (const token of [
  /"@type": "Product"/,
  /"@type": "Brand"/,
  /"@type": "ItemList"/,
  /"propertyID": "ASIN"/,
  /"propertyID": "MPN"/,
  /"additionalProperty"/,
  /data-commercial-scope="after_tool"/,
  /data-professional-only="false"/,
  /Bir Amazon Gelir Ortağı olarak nitelikli satın alımlar üzerinden kazanç elde ediyorum/,
  /Mevcut.*satın alma yapmayın/is,
  /rel="sponsored nofollow noopener"/,
  /Kullanıcı ihtiyacı/,
  /Güçlü yönler/,
  /Sınırlamalar/,
  /Satın almama koşulu/,
  /kalibre edilmiş profesyonel cihaz/,
  /kuru iç mekân/
]) assert.match(html, token);

for (const [asin, mpn] of expected) {
  assert.match(html, new RegExp(asin));
  assert.match(html, new RegExp(mpn));
}
assert.doesNotMatch(html, /href="https:\/\/www\.amazon\.com\.tr\/dp\//i);
assert.match(app, /sponsored nofollow noopener/);
for (const id of ["gateIndoor","gateDry","gatePlacement","gateRange","gateReference","gateNotCritical","gateVariant","gateNeed","gateAffiliate"]) {
  assert.match(app, new RegExp(id));
}

const forbidden = [
  /"@type"\s*:\s*"Offer"/i,
  /priceCurrency/i,
  /aggregateRating/i,
  /ratingValue/i,
  /\bstokta\b/i,
  /\bsatıcı\s*:/i,
  /\bgaranti\s*:/i,
  /hemen satın al/i,
  /en ucuz/i
];
for (const token of forbidden) {
  assert.doesNotMatch(html, token);
  assert.doesNotMatch(JSON.stringify(catalog), token);
}

assert.equal(overlay.version, 245);
assert.equal(overlay.routes.length, 1);
assert.equal(overlay.routes[0].canonicalPath, `/amazon-elektrik-urunleri/${SLUG}/`);
assert.equal(overlay.routes[0].source, `alo186/amazon-elektrik-urunleri/${SLUG}/index.html`);

function walk(directory) {
  if (!fs.existsSync(directory)) return [];
  return fs.readdirSync(directory, {withFileTypes:true}).flatMap((entry) => {
    const target = path.join(directory, entry.name);
    return entry.isDirectory() ? walk(target) : [target];
  });
}
const affiliateRoot = path.join(ROOT, "alo186", "amazon-elektrik-urunleri");
const catalogFiles = walk(affiliateRoot).filter((file) => /catalog.*\.js$/i.test(path.basename(file)));
const allCatalogText = catalogFiles.map((file) => fs.readFileSync(file, "utf8")).join("\n");
for (const asin of asins) {
  const occurrences = allCatalogText.split(asin).length - 1;
  assert.equal(occurrences, 1, `Duplicate ASIN detected: ${asin} (${occurrences})`);
}

console.log(JSON.stringify({
  ok: true,
  version: 245,
  products: expected.map(([asin, mpn]) => ({asin, mpn})),
  checks: [
    "canonical",
    "affiliate-tag",
    "sponsored-nofollow-noopener",
    "duplicate-asin",
    "stale-45-46-days",
    "product-brand-itemlist-identifiers-additional-property",
    "after-tool-and-professional-only",
    "visible-disclosure-and-no-buy",
    "forbidden-commercial-fields"
  ]
}, null, 2));
