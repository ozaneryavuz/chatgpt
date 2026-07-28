const assert = require('assert');
const fs = require('fs');
const path = require('path');
const core = require('../hesaplama/elektrik-surekliligi-pasaportu/core.js');

function evidence(status) {
  return Object.fromEntries(core.EVIDENCE_FIELDS.map((field) => [field.id, status]));
}

const complete = core.evaluatePassport({
  facilityType: 'hotel',
  criticalLoads: ['life-safety', 'it-comms'],
  backupSources: ['generator', 'ups'],
  evidence: evidence('current')
}, { now: '2026-07-28T08:00:00Z' });
assert.strictEqual(complete.valid, true);
assert.strictEqual(complete.score, 100);
assert.strictEqual(complete.priorities.P0.length, 0);
assert.strictEqual(complete.priorities.P1.length, 0);
assert.strictEqual(complete.priorities.P2.length, 0);
assert.strictEqual(complete.revenueAllowed, true);

const noBackup = core.evaluatePassport({
  facilityType: 'business',
  criticalLoads: ['operations'],
  backupSources: ['none'],
  evidence: { ...evidence('current'), critical_load_inventory: 'missing' }
});
assert.strictEqual(noBackup.valid, true);
assert(noBackup.priorities.P0.some((item) => item.id === 'critical_load_without_backup'));
assert(noBackup.priorities.P0.some((item) => item.id === 'critical_load_not_documented'));
assert.strictEqual(noBackup.professionalPlanRequired, true);

const emergency = core.evaluatePassport({ immediateDanger: true });
assert.strictEqual(emergency.valid, false);
assert.strictEqual(emergency.emergency, true);
assert.strictEqual(emergency.revenueAllowed, false);
assert.strictEqual(emergency.route, '112');

const invalid = core.evaluatePassport({
  facilityType: 'site',
  criticalLoads: [],
  backupSources: [],
  evidence: evidence('current')
});
assert.strictEqual(invalid.valid, false);
assert.strictEqual(invalid.errors.length, 2);

const lifeSupport = core.evaluatePassport({
  facilityType: 'other',
  criticalLoads: ['life-safety'],
  backupSources: ['ups'],
  evidence: evidence('current'),
  lifeSupport: true
});
assert.strictEqual(lifeSupport.professionalPlanRequired, true);
assert.strictEqual(lifeSupport.lifeSupportSelected, true);

const exported = core.createExport(lifeSupport, {
  generatedAt: '2026-07-28T08:00:00Z',
  importedMaturity: {
    facilityType: 'hotel',
    score: 72,
    band: '<script>Gelişen</script>',
    dimensions: [{ id: 'backup<script>', score: 120 }],
    medical: true,
    email: 'should-not-pass@example.com'
  }
});
assert.strictEqual(exported.schemaVersion, 1);
assert.strictEqual(exported.privacy.containsPersonalData, false);
assert.strictEqual(exported.privacy.lifeSupportFlagIncluded, false);
assert.strictEqual(exported.privacy.immediateDangerFlagIncluded, false);
assert.deepStrictEqual(exported.privacy.personalFieldsCollected, []);
assert(!JSON.stringify(exported).includes('should-not-pass@example.com'));
assert(!JSON.stringify(exported).includes('medical'));
assert.strictEqual(exported.importedMaturity.score, 72);
assert.strictEqual(exported.importedMaturity.dimensions[0].score, 100);
assert(!exported.importedMaturity.band.includes('<'));

const stored = core.sanitizeStorage({
  facilityType: 'hotel',
  criticalLoads: ['life-safety', 'invalid'],
  backupSources: ['generator'],
  evidence: { ...evidence('due'), unknown: 'current' },
  lifeSupport: true,
  immediateDanger: true,
  name: 'Kişisel veri'
}, '2026-07-28T08:00:00Z');
assert.strictEqual(stored.privacy.containsPersonalData, false);
assert.strictEqual(stored.privacy.lifeSupportFlagIncluded, false);
assert.strictEqual(stored.privacy.immediateDangerFlagIncluded, false);
assert.deepStrictEqual(stored.criticalLoads, ['life-safety']);
assert(!Object.prototype.hasOwnProperty.call(stored, 'name'));
assert(!Object.prototype.hasOwnProperty.call(stored, 'lifeSupport'));
assert(!Object.prototype.hasOwnProperty.call(stored, 'immediateDanger'));
assert.strictEqual(core.isStoredPayloadFresh(stored, '2026-08-26T08:00:00Z'), true);
assert.strictEqual(core.isStoredPayloadFresh(stored, '2026-08-28T08:00:01Z'), false);

const dueReview = core.nextReviewDate(evidence('due'), new Date('2026-07-28T08:00:00Z'));
assert.strictEqual(dueReview.toISOString(), '2026-08-27T08:00:00.000Z');

const schema = JSON.parse(fs.readFileSync(path.join(__dirname, '../hesaplama/elektrik-surekliligi-pasaportu/passport.schema.json'), 'utf8'));
assert.strictEqual(schema.$id, 'https://www.alo186.com/schemas/electric-continuity-passport-v1.json');
assert(schema.required.includes('privacy'));
assert.strictEqual(schema.properties.privacy.properties.containsPersonalData.const, false);
assert.strictEqual(schema.properties.evidence.minItems, 10);
assert.strictEqual(schema.properties.evidence.maxItems, 10);

const analytics = JSON.parse(fs.readFileSync(path.join(__dirname, '../hesaplama/elektrik-surekliligi-pasaportu/analytics-events.json'), 'utf8'));
assert(analytics.events.some((item) => item.name === 'continuity_passport_completed'));
assert(analytics.events.some((item) => item.name === 'continuity_passport_panel_handoff_created'));
assert(analytics.privacy.forbiddenParameters.includes('life_support'));

console.log('ALO186 Elektrik Sürekliliği Pasaportu skor, P0, gizlilik, export ve schema testleri başarılı.');
