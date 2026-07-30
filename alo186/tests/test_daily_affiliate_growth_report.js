'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const repoRoot = path.resolve(__dirname, '../..');
const script = path.join(repoRoot, 'alo186/deployment/daily_affiliate_growth_report.js');
const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'alo186-affiliate-growth-'));
const jsonPath = path.join(temp, 'report.json');
const markdownPath = path.join(temp, 'report.md');

const result = spawnSync(process.execPath, [script, '--json', jsonPath, '--markdown', markdownPath], {
  cwd: repoRoot,
  env: { ...process.env, ALO186_REPORT_NOW: '2026-07-30T06:15:00.000Z' },
  encoding: 'utf8'
});

assert.equal(result.status, 0, `${result.stdout}\n${result.stderr}`);
const report = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
const markdown = fs.readFileSync(markdownPath, 'utf8');

assert.equal(report.schemaVersion, 2);
assert.equal(report.trackingIssue, 301);
assert.equal(report.timezone, 'Europe/Istanbul');
assert.equal(report.schedule, 'Her gün 09:15');
assert.equal(report.generatedAt, '2026-07-30T06:15:00.000Z');
assert.ok(report.categories.length >= 18);
assert.equal(report.topActions.length, 3, 'Her çalıştırma tam üç öncelikli satış aksiyonu üretmeli.');
assert.ok(report.summary.totalVerifiedProducts >= 21, 'Run53 doğrulanmış ürünü günlük rapora dahil edilmeli.');
assert.ok(report.summary.publicDirectProducts >= 14, 'Run53 doğrudan affiliate ürünü raporda sayılmalı.');
assert.ok(report.summary.manufacturerVerifiedCandidates >= 10, 'Üretici kaynağı doğrulanmış Amazon kimlik kuyruğu görünür olmalı.');
assert.equal(report.summary.freshProducts, report.summary.publicDirectProducts + report.summary.toolGatedProducts);
assert.equal(report.canonicalAudit.canonicalOrigin, 'https://alo186.com');
assert.equal(report.canonicalAudit.legacyOriginFound, false);
assert.equal(report.canonicalAudit.forbiddenCommerceNodeFound, false);
assert.equal(report.canonicalAudit.forbiddenCommercialFieldFound, false);

const categoryById = new Map(report.categories.map((category) => [category.id, category]));
for (const action of report.topActions) {
  const category = categoryById.get(action.categoryId);
  assert.ok(category, `Kategori bulunamadı: ${action.categoryId}`);
  assert.notEqual(category.affiliatePolicy, 'professional_only');
  assert.ok(action.safetyGate && action.implementation && action.minimumNeeded >= 0);
  assert.ok(Number.isInteger(action.marketplaceVerificationQueue));
  assert.ok(Array.isArray(action.candidateModels));
  if (category.affiliatePolicy === 'verified_direct') {
    assert.deepEqual(action.preferredBatch, { min: 8, max: 15, type: 'verified_direct' });
  } else {
    assert.deepEqual(action.preferredBatch, { min: 3, max: 8, type: 'tool_gated' });
  }
}

const charger = categoryById.get('usb_c_charger');
const cable = categoryById.get('usb_c_cable');
assert.ok(charger.freshCount >= 3, 'UGREEN 140 W ürün kaydı şarj cihazı sayımına girmeli.');
assert.ok(charger.marketplaceVerificationQueue >= 2, 'Tam ASIN/model doğrulaması bekleyen şarj cihazları görünmeli.');
assert.ok(cable.marketplaceVerificationQueue >= 1, 'UGREEN 90440 doğrulama kuyruğunda görünmeli.');

assert.equal(report.guardrails.affiliateDisclosureRequired, true);
assert.equal(report.guardrails.sponsoredRelRequired, true);
assert.equal(report.guardrails.noBuyOutcomeRequired, true);
assert.equal(report.guardrails.hazardCommerceClosed, true);
assert.equal(report.guardrails.officialAffiliationClaimed, false);
assert.equal(report.guardrails.offerSchemaAllowed, false);
assert.equal(report.guardrails.unverifiedCommercialFieldsAllowed, false);
assert.equal(report.guardrails.exactAsinRequiredForDirectProduct, true);

const forbiddenKeys = new Set(['price','stock','rating','aggregateRating','review','seller','delivery','warranty','availability','offers']);
function assertNoForbiddenKeys(value, trail = 'report') {
  if (Array.isArray(value)) return value.forEach((item, index) => assertNoForbiddenKeys(item, `${trail}[${index}]`));
  if (!value || typeof value !== 'object') return;
  for (const [key, item] of Object.entries(value)) {
    assert.ok(!forbiddenKeys.has(key), `Yasak ticari anahtar rapora sızdı: ${trail}.${key}`);
    assertNoForbiddenKeys(item, `${trail}.${key}`);
  }
}
assertNoForbiddenKeys(report);

assert.match(markdown, /En yüksek potansiyelli 3 aksiyon/);
assert.match(markdown, /Amazon Türkiye kimliği doğrulanacak üretici adayları/);
assert.match(markdown, /Tam Amazon Türkiye ASIN\/model eşleşmesi/);
assert.match(markdown, /Amazon satış ortaklığı ilişkisi görünür olmalı/);
assert.match(markdown, /satın almama sonucu korunmalı/i);
assert.doesNotMatch(markdown, /kesin kazanç|garantili satış|stokta|en ucuz/i);

fs.rmSync(temp, { recursive: true, force: true });
console.log(JSON.stringify({ ok: true, topActions: report.topActions.map((action) => action.categoryId), summary: report.summary, canonicalAudit: report.canonicalAudit }, null, 2));
