const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ROOT = path.resolve(__dirname, "..", "..");
const slug = "usb-c-goruntu-cikisi-displayport-hdmi-uyumluluk-secimi";
const route = path.join(ROOT, "alo186", "amazon-elektrik-urunleri", slug);
const html = fs.readFileSync(path.join(route, "index.html"), "utf8");
const catalogText = fs.readFileSync(path.join(route, "catalog-v254.js"), "utf8");
const appText = fs.readFileSync(path.join(route, "app-v254.js"), "utf8");
const overlay = JSON.parse(fs.readFileSync(path.join(ROOT, "alo186", "deployment", "routing-overlays", "254-affiliate-usbc-display.json"), "utf8"));

const sandbox = { module: { exports: {} }, exports: {}, globalThis: {} };
vm.runInNewContext(catalogText, sandbox, { filename: "catalog-v254.js" });
const catalog = sandbox.module.exports;

assert.strictEqual(catalog.version, 254);
assert.strictEqual(catalog.affiliateTag, "alo186rehber-21");
assert.strictEqual(catalog.verifiedAt, "2026-08-03");
assert.strictEqual(catalog.maxVerificationAgeDays, 45);
assert.strictEqual(catalog.category.slug, slug);
assert.strictEqual(catalog.category.risk, "consumer-low");
assert.strictEqual(catalog.category.affiliatePolicy, "after_tool");
assert.strictEqual(catalog.category.professionalOnly, false);
assert.strictEqual(catalog.category.highRiskDirectCta, false);
assert.strictEqual(catalog.products.length, 3);

const expectedAsins = ["B0C4DB8MLL", "B0DK6QPTFQ", "B096G51911"];
const expectedMpns = ["25158", "V-Z623", "HC-01"];
assert.deepStrictEqual(Array.from(catalog.products, p => p.asin), expectedAsins);
assert.deepStrictEqual(Array.from(catalog.products, p => p.mpn), expectedMpns);
assert.strictEqual(new Set(expectedAsins).size, 3);
assert.strictEqual(new Set(expectedMpns).size, 3);

for (const product of catalog.products) {
  assert.match(product.asin, /^[A-Z0-9]{10}$/);
  assert.ok(product.brand && product.userNeed && product.noBuyWhen);
  assert.ok(product.strengths.length >= 3);
  assert.ok(product.limitations.length >= 3);
  assert.match(product.noBuyWhen, /satın alma|satın almayın/);
  assert.strictEqual(product.amazonAsinSource, `https://www.amazon.com.tr/dp/${product.asin}`);
  assert.match(product.technicalSource, /^https:\/\/(www\.ugreenindia\.com|www\.teknostore\.com|www\.epey\.com)\//);
  assert.strictEqual(catalog.verificationStatus(product, new Date("2026-09-17T00:00:00Z")).fresh, true);
  assert.strictEqual(catalog.verificationStatus(product, new Date("2026-09-18T00:00:00Z")).fresh, false);
  const url = catalog.amazonProductUrl(product, new Date("2026-08-03T12:00:00Z"));
  assert.ok(url.includes("/dp/" + product.asin));
  assert.ok(url.endsWith("?tag=alo186rehber-21"));
  assert.strictEqual(catalog.amazonProductUrl(product, new Date("2026-09-18T00:00:00Z")), null);
}

const canonical = "https://alo186.com/amazon-elektrik-urunleri/usb-c-goruntu-cikisi-displayport-hdmi-uyumluluk-secimi/";
assert.ok(html.includes(`<link rel="canonical" href="${canonical}">`));
assert.ok(html.includes('data-commercial-scope="after_tool"'));
assert.ok(html.includes('data-professional-only="false"'));
assert.strictEqual((html.match(/Görünür satış ortaklığı açıklaması/g) || []).length, 3);
assert.strictEqual((html.match(/rel="sponsored nofollow noopener"/g) || []).length, 3);
assert.ok(!/href="https:\/\/www\.amazon\.com\.tr\/dp\/[^\"]+\?tag=/.test(html));
assert.ok(!/"@type"\s*:\s*"Offer"|priceCurrency|aggregateRating|ratingValue|reviewCount/.test(html));
assert.ok(html.includes("DP Alt Mode"));
assert.ok(html.includes("tek yönlü"));
assert.ok(html.includes("satın almayın"));

const ids = Array.from(html.matchAll(/\sid="([^"]+)"/g), match => match[1]);
assert.strictEqual(new Set(ids).size, ids.length, "duplicate HTML id");
for (const anchor of ["urun-ugreen-cm556-25158", "urun-veggieg-z623", "urun-daytona-hc-01"]) assert.ok(ids.includes(anchor));

const kgMatch = html.match(/<script id="knowledge-graph" type="application\/ld\+json">\s*([\s\S]*?)\s*<\/script>/);
assert.ok(kgMatch);
const graph = JSON.parse(kgMatch[1])["@graph"];
assert.strictEqual(graph.filter(node => node["@type"] === "Product").length, 3);
assert.strictEqual(graph.filter(node => node["@type"] === "Brand").length, 3);
assert.strictEqual(graph.filter(node => node["@type"] === "ItemList").length, 1);
assert.strictEqual(graph.filter(node => node["@type"] === "BreadcrumbList").length, 1);
const graphIds = graph.map(node => node["@id"]).filter(Boolean);
assert.strictEqual(new Set(graphIds).size, graphIds.length, "duplicate JSON-LD @id");
for (const productNode of graph.filter(node => node["@type"] === "Product")) {
  assert.ok(productNode.identifier.some(item => item.propertyID === "ASIN"));
  assert.ok(productNode.identifier.some(item => item.propertyID === "MPN"));
  assert.ok(productNode.additionalProperty.length >= 3);
}
for (const asin of expectedAsins) {
  assert.ok(html.includes(`"value":"${asin}"`));
  assert.ok(html.includes(`data-affiliate-asin="${asin}"`));
}

assert.ok(appText.includes('catalog.category.affiliatePolicy !== "after_tool"'));
assert.ok(appText.includes("catalog.category.professionalOnly"));
assert.ok(appText.includes("catalog.category.highRiskDirectCta"));
assert.ok(appText.includes('link.rel = "sponsored nofollow noopener"'));
assert.ok(appText.includes('link.removeAttribute("href")'));
for (const gate of ["gateConsumerUse","gatePortCondition","gateAltMode","gateDirection","gateDisplayPort","gateResolution","gateNoHighRisk","gateVariant","gateNeed","gateAffiliate"]) assert.ok(html.includes(`id="${gate}"`));

function walk(directory) {
  if (!fs.existsSync(directory)) return [];
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap(entry => {
    const full = path.join(directory, entry.name);
    return entry.isDirectory() ? walk(full) : [full];
  });
}
const catalogFiles = walk(path.join(ROOT, "alo186", "amazon-elektrik-urunleri")).filter(file => /catalog-v\d+\.js$/.test(file));
for (const asin of expectedAsins) {
  let occurrences = 0;
  for (const file of catalogFiles) {
    const matches = fs.readFileSync(file, "utf8").match(new RegExp(`asin\\s*:\\s*["']${asin}["']`, "g"));
    occurrences += matches ? matches.length : 0;
  }
  assert.strictEqual(occurrences, 1, `global duplicate ASIN: ${asin}`);
}

assert.strictEqual(overlay.version, 254);
assert.strictEqual(overlay.routes.length, 1);
assert.strictEqual(overlay.routes[0].canonicalPath, "/amazon-elektrik-urunleri/usb-c-goruntu-cikisi-displayport-hdmi-uyumluluk-secimi/");
assert.strictEqual(overlay.routes[0].source, "alo186/amazon-elektrik-urunleri/usb-c-goruntu-cikisi-displayport-hdmi-uyumluluk-secimi/index.html");

console.log(JSON.stringify({ ok: true, version: 254, products: catalog.products.map(p => ({ asin: p.asin, mpn: p.mpn })), checks: ["canonical","affiliate-tag","sponsored-nofollow-noopener","duplicate-ASIN-global","stale-45-46","Knowledge-Graph","duplicate-id","after_tool","professional_only","high-risk-direct-cta"] }, null, 2));
