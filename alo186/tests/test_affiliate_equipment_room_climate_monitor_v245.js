const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ROOT = path.resolve(__dirname, "..", "..");
const route = path.join(ROOT, "alo186", "amazon-elektrik-urunleri", "elektrik-ekipman-odasi-sicaklik-nem-olcum-alarm-secimi");
const html = fs.readFileSync(path.join(route, "index.html"), "utf8");
const catalogText = fs.readFileSync(path.join(route, "catalog-v245.js"), "utf8");
const appText = fs.readFileSync(path.join(route, "app-v245.js"), "utf8");
const overlay = JSON.parse(fs.readFileSync(path.join(ROOT, "alo186", "deployment", "routing-overlays", "245-affiliate-equipment-room-climate-monitor.json"), "utf8"));

const sandbox = { module: { exports: {} }, exports: {}, globalThis: {} };
vm.runInNewContext(catalogText, sandbox, { filename: "catalog-v245.js" });
const catalog = sandbox.module.exports;

assert.strictEqual(catalog.version, 245);
assert.strictEqual(catalog.affiliateTag, "alo186rehber-21");
assert.strictEqual(catalog.category.affiliatePolicy, "after_tool");
assert.strictEqual(catalog.category.professionalOnly, false);
assert.strictEqual(catalog.products.length, 3);

const expectedAsins = ["B01H1R0K68", "B0BNYSVV3J", "B07D37FKGY"];
assert.deepStrictEqual(Array.from(catalog.products, p => p.asin), expectedAsins);
assert.strictEqual(new Set(catalog.products.map(p => p.asin)).size, 3, "duplicate ASIN");
assert.strictEqual(new Set(catalog.products.map(p => p.mpn)).size, 3, "duplicate MPN");

for (const product of catalog.products) {
  assert.match(product.asin, /^[A-Z0-9]{10}$/);
  assert.ok(product.mpn);
  assert.ok(product.brand);
  assert.ok(product.userNeed);
  assert.ok(product.strengths.length >= 3);
  assert.ok(product.limitations.length >= 3);
  assert.match(product.noBuyWhen, /Mevcut|mevcut/);
  assert.match(product.noBuyWhen, /satın alma|satın almayın/);
  assert.ok(product.technicalSource.startsWith("https://"));
  assert.strictEqual(catalog.verificationStatus(product, new Date("2026-09-17T00:00:00Z")).fresh, true, "45 gün taze olmalı");
  assert.strictEqual(catalog.verificationStatus(product, new Date("2026-09-18T00:00:00Z")).fresh, false, "46 gün stale olmalı");
  const url = catalog.amazonProductUrl(product, new Date("2026-08-03T12:00:00Z"));
  assert.ok(url.includes("/dp/" + product.asin));
  assert.ok(url.endsWith("?tag=alo186rehber-21"));
  assert.strictEqual(catalog.amazonProductUrl(product, new Date("2026-09-18T00:00:00Z")), null);
}

const canonical = "https://alo186.com/amazon-elektrik-urunleri/elektrik-ekipman-odasi-sicaklik-nem-olcum-alarm-secimi/";
assert.ok(html.includes(`<link rel="canonical" href="${canonical}">`));
assert.ok(html.includes('data-commercial-scope="after_tool"'));
assert.ok(html.includes('data-professional-only="false"'));
assert.ok(html.includes('Görünür satış ortaklığı açıklaması'));
assert.ok(html.includes("Mevcut BMS"));
assert.ok(html.includes('rel="sponsored nofollow noopener"'));
assert.ok(!/href="https:\/\/www\.amazon\.com\.tr\/dp\//.test(html), "affiliate links initially locked");
assert.ok(!/"@type"\s*:\s*"Offer"|priceCurrency|aggregateRating|ratingValue/.test(html));
assert.ok(!/\b(en ucuz|stokta|son fırsat|hemen satın al)\b/i.test(html));

for (const type of ["Product", "Brand", "ItemList", "PropertyValue"]) {
  assert.ok(html.includes(`"@type": "${type}"`), `missing KG type ${type}`);
}
for (const asin of expectedAsins) {
  assert.ok(html.includes(`"propertyID": "ASIN"`));
  assert.ok(html.includes(`"value": "${asin}"`));
  assert.ok(html.includes(`data-affiliate-asin="${asin}"`));
}
assert.ok(html.includes('"propertyID": "MPN"'));
assert.ok(html.includes('"additionalProperty"'));
assert.ok(appText.includes('catalog.category.affiliatePolicy !== "after_tool"'));
assert.ok(appText.includes("catalog.category.professionalOnly"));
assert.ok(appText.includes('link.rel = "sponsored nofollow noopener"'));
assert.ok(appText.includes('link.removeAttribute("href")'));
assert.ok(appText.includes('catalog.amazonProductUrl'));

assert.strictEqual(overlay.version, 245);
assert.strictEqual(overlay.routes.length, 1);
assert.strictEqual(overlay.routes[0].canonicalPath, "/amazon-elektrik-urunleri/elektrik-ekipman-odasi-sicaklik-nem-olcum-alarm-secimi/");
assert.strictEqual(overlay.routes[0].source, "alo186/amazon-elektrik-urunleri/elektrik-ekipman-odasi-sicaklik-nem-olcum-alarm-secimi/index.html");

console.log(JSON.stringify({
  ok: true,
  version: catalog.version,
  products: catalog.products.map(p => ({ asin: p.asin, mpn: p.mpn })),
  checks: [
    "canonical",
    "affiliate-tag",
    "sponsored-nofollow-noopener",
    "duplicate-ASIN",
    "stale-45-46",
    "Knowledge-Graph",
    "after_tool",
    "professional_only"
  ]
}, null, 2));
