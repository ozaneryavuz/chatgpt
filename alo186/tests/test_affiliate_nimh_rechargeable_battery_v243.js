const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const ROOT = path.resolve(__dirname, "..", "..");
const ROUTE = path.join(ROOT, "alo186", "amazon-elektrik-urunleri", "elektrik-kesintisi-aa-aaa-nimh-sarjli-pil-secimi");
const catalog = require(path.join(ROUTE, "catalog-v243.js"));
const html = fs.readFileSync(path.join(ROUTE, "index.html"), "utf8");
const app = fs.readFileSync(path.join(ROUTE, "app-v243.js"), "utf8");
const overlay = JSON.parse(fs.readFileSync(path.join(ROOT, "alo186", "deployment", "routing-overlays", "243-affiliate-nimh-rechargeable-battery.json"), "utf8"));
const canonical = "https://alo186.com/amazon-elektrik-urunleri/elektrik-kesintisi-aa-aaa-nimh-sarjli-pil-secimi/";
const expected = [["B007FD5W3K", "5716101402"], ["B07CF47XZ4", "56703101412"], ["B07BFCZ5SW", "HR6/DX1500"]];
assert.equal(catalog.version, 243);
assert.equal(catalog.affiliateTag, "alo186rehber-21");
assert.equal(catalog.maxVerificationAgeDays, 45);
assert.equal(catalog.verifiedAt, "2026-08-03");
assert.equal(catalog.category.affiliatePolicy, "after_tool");
assert.equal(catalog.category.professionalOnly, false);
assert.match(catalog.category.requiredTool, /embedded-nimh-rechargeable-battery-readiness-v243/);
assert.match(catalog.amazonTurkeyListingSource, /amazon\.com\.tr/);
assert.equal(catalog.products.length, 3);
const asins = catalog.products.map((p) => p.asin);
assert.equal(new Set(asins).size, 3);
assert.deepEqual(catalog.products.map((p) => [p.asin, p.mpn]), expected);
for (const product of catalog.products) {
  assert.equal(product.verifiedAt, "2026-08-03");
  assert.ok(product.userNeed.length > 70);
  assert.ok(product.strengths.length >= 3);
  assert.ok(product.limitations.length >= 3);
  assert.match(product.noBuyWhen, /satın alma yapmayın/i);
  assert.match(product.technicalSource, /^https:\/\//);
  assert.match(product.amazonAsinSource, /^https:\/\//);
  assert.ok(Object.keys(product.technical).length >= 4);
  const fresh = catalog.verificationStatus(product, new Date("2026-09-17T00:00:00Z"));
  const stale = catalog.verificationStatus(product, new Date("2026-09-18T00:00:00Z"));
  assert.equal(fresh.ageDays, 45);
  assert.equal(fresh.fresh, true);
  assert.equal(stale.ageDays, 46);
  assert.equal(stale.fresh, false);
  assert.equal(catalog.amazonProductUrl(product, new Date("2026-09-18T00:00:00Z")), null);
  assert.equal(catalog.amazonProductUrl(product, new Date("2026-08-03T12:00:00Z")), `https://www.amazon.com.tr/dp/${product.asin}?tag=alo186rehber-21`);
}
assert.match(html, new RegExp(`<link rel="canonical" href="${canonical.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}">`));
for (const token of [/"@type": "Product"/,/"@type": "Brand"/,/"@type": "ItemList"/,/"propertyID": "ASIN"/,/"propertyID": "MPN"/,/"additionalProperty"/,/data-commercial-scope="after_tool"/,/data-professional-only="false"/,/Bir Amazon Gelir Ortağı olarak nitelikli satın alımlar üzerinden kazanç elde ediyorum/,/Mevcut.*satın alma yapmayın/is,/rel="sponsored nofollow noopener"/,/Kullanıcı ihtiyacı/,/Güçlü yönler/,/Sınırlamalar/,/Satın almama koşulu/,/NiMH/,/alkalin/i,/lityum/i]) assert.match(html, token);
for (const [asin, mpn] of expected) {
  assert.match(html, new RegExp(asin));
  assert.match(html, new RegExp(mpn.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
}
assert.doesNotMatch(html, /href="https:\/\/www\.amazon\.com\.tr\/dp\//i);
assert.match(app, /sponsored nofollow noopener/);
for (const id of ["gateChemistry","gateCondition","gateCharger","gateDevice","gateMatched","gateDry","gateNotCritical","gateVariant","gateNeed","gateAffiliate"]) assert.match(app, new RegExp(id));
const forbidden = [/"@type"\s*:\s*"Offer"/i,/priceCurrency/i,/aggregateRating/i,/ratingValue/i,/\bstokta\b/i,/\bsatıcı\s*:/i,/\bgaranti\s*:/i,/hemen satın al/i,/en ucuz/i];
for (const token of forbidden) { assert.doesNotMatch(html, token); assert.doesNotMatch(JSON.stringify(catalog), token); }
assert.equal(overlay.version, 243);
assert.equal(overlay.routes.length, 1);
assert.equal(overlay.routes[0].canonicalPath, "/amazon-elektrik-urunleri/elektrik-kesintisi-aa-aaa-nimh-sarjli-pil-secimi/");
assert.equal(overlay.routes[0].source, "alo186/amazon-elektrik-urunleri/elektrik-kesintisi-aa-aaa-nimh-sarjli-pil-secimi/index.html");
function walk(directory) {
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
console.log(JSON.stringify({ok:true,version:243,products:expected.map(([asin,mpn])=>({asin,mpn})),checks:["canonical","affiliate-tag","sponsored-nofollow-noopener","duplicate-asin","stale-45-46-days","product-brand-itemlist-identifiers-additional-property","after-tool-and-professional-only","visible-disclosure-and-no-buy","forbidden-commercial-fields"]},null,2));
