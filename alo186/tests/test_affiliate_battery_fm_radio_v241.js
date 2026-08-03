const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..", "..");
const ROUTE = path.join(ROOT, "alo186", "amazon-elektrik-urunleri", "elektrik-kesintisi-pilli-fm-radyo-secimi");
const catalog = require(path.join(ROUTE, "catalog-v241.js"));
const html = fs.readFileSync(path.join(ROUTE, "index.html"), "utf8");
const app = fs.readFileSync(path.join(ROUTE, "app-v241.js"), "utf8");
const overlay = JSON.parse(fs.readFileSync(path.join(ROOT, "alo186", "deployment", "routing-overlays", "241-affiliate-battery-fm-radio.json"), "utf8"));
const canonical = "https://alo186.com/amazon-elektrik-urunleri/elektrik-kesintisi-pilli-fm-radyo-secimi/";
const expected = [
  ["B0089AK54E", "SCD-24 B"],
  ["B004IZKVAW", "SCD-38 USB PINK"],
  ["B013PUUZS8", "SCD-420RD"]
];

assert.equal(catalog.version, 241);
assert.equal(catalog.affiliateTag, "alo186rehber-21");
assert.equal(catalog.maxVerificationAgeDays, 45);
assert.equal(catalog.verifiedAt, "2026-08-03");
assert.equal(catalog.category.affiliatePolicy, "after_tool");
assert.equal(catalog.category.professionalOnly, false);
assert.match(catalog.category.requiredTool, /embedded-battery-fm-radio-readiness-v241/);
assert.match(catalog.amazonTurkeyListingSource, /amazon\.com\.tr/);
assert.equal(catalog.products.length, 3);

const asins = catalog.products.map((product) => product.asin);
assert.equal(new Set(asins).size, 3);
assert.deepEqual(catalog.products.map((product) => [product.asin, product.mpn]), expected);

for (const product of catalog.products) {
  assert.equal(product.brand, "Lenco");
  assert.equal(product.verifiedAt, "2026-08-03");
  assert.ok(product.userNeed.length > 60);
  assert.ok(product.strengths.length >= 3);
  assert.ok(product.limitations.length >= 3);
  assert.match(product.noBuyWhen, /satın alma yapmayın/i);
  assert.match(product.technicalSource, /^https:\/\/(?:catalog\.)?lenco\.com\//);
  assert.match(product.amazonAsinSource, /^https:\/\//);
  assert.ok(Object.keys(product.technical).length >= 4);

  const fresh = catalog.verificationStatus(product, new Date("2026-09-17T00:00:00Z"));
  const stale = catalog.verificationStatus(product, new Date("2026-09-18T00:00:00Z"));
  assert.equal(fresh.ageDays, 45);
  assert.equal(fresh.fresh, true);
  assert.equal(stale.ageDays, 46);
  assert.equal(stale.fresh, false);
  assert.equal(catalog.amazonProductUrl(product, new Date("2026-09-18T00:00:00Z")), null);
  assert.equal(
    catalog.amazonProductUrl(product, new Date("2026-08-03T12:00:00Z")),
    `https://www.amazon.com.tr/dp/${product.asin}?tag=alo186rehber-21`
  );
}

assert.match(html, new RegExp(`<link rel="canonical" href="${canonical.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}">`));
assert.match(html, /"@type": "Product"/);
assert.match(html, /"@type": "Brand"/);
assert.match(html, /"@type": "ItemList"/);
assert.match(html, /"propertyID": "ASIN"/);
assert.match(html, /"propertyID": "MPN"/);
assert.match(html, /"additionalProperty"/);
assert.match(html, /data-commercial-scope="after_tool"/);
assert.match(html, /data-professional-only="false"/);
assert.match(html, /Bir Amazon Gelir Ortağı olarak nitelikli satın alımlar üzerinden kazanç elde ediyorum/);
assert.match(html, /Mevcut.*satın alma yapmayın/is);
assert.match(html, /rel="sponsored nofollow noopener"/);
assert.match(html, /Kullanıcı ihtiyacı/);
assert.match(html, /Güçlü yönler/);
assert.match(html, /Sınırlamalar/);
assert.match(html, /Satın almama koşulu/);
assert.match(html, /FM.*tek.*acil iletişim/is);
assert.match(html, /yaşam güvenliği/is);

for (const [asin, mpn] of expected) {
  assert.match(html, new RegExp(asin));
  assert.match(html, new RegExp(mpn.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
}
assert.doesNotMatch(html, /href="https:\/\/www\.amazon\.com\.tr\/dp\//i);
assert.match(app, /sponsored nofollow noopener/);
for (const id of ["gateDry", "gateBattery", "gateReception", "gateCord", "gateNotCritical", "gateVariant", "gateNeed", "gateAffiliate"]) {
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

assert.equal(overlay.version, 241);
assert.equal(overlay.routes.length, 1);
assert.equal(overlay.routes[0].canonicalPath, "/amazon-elektrik-urunleri/elektrik-kesintisi-pilli-fm-radyo-secimi/");
assert.equal(overlay.routes[0].source, "alo186/amazon-elektrik-urunleri/elektrik-kesintisi-pilli-fm-radyo-secimi/index.html");

function walk(directory) {
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
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
  version: 241,
  products: expected.map(([asin, mpn]) => ({ asin, mpn })),
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
