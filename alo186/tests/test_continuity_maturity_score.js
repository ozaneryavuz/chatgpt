const assert = require('assert');
const fs = require('fs');
const path = require('path');
const core = require('../hesaplama/elektrik-surekliligi-olgunluk-skoru/core.js');

function answers(value='yes') {
  return Object.fromEntries(core.QUESTIONS.map(question => [question.id, value]));
}

function resultWith(overrides={}) {
  return core.evaluateAssessment({...answers('yes'), ...overrides});
}

assert.strictEqual(core.DIMENSIONS.length, 8, 'Sekiz olgunluk boyutu olmalı.');
assert.strictEqual(core.QUESTIONS.length, 24, 'Yirmi dört soru olmalı.');
assert(core.QUESTIONS.every(q => q.weight > 0), 'Bütün sorular pozitif ağırlık taşımalı.');
assert.strictEqual(new Set(core.QUESTIONS.map(q => q.id)).size, 24, 'Soru kimlikleri benzersiz olmalı.');
assert(core.QUESTIONS.every(q => core.DIMENSIONS.some(d => d.id === q.dimension)), 'Her soru geçerli boyuta bağlı olmalı.');

const allYes = core.evaluateAssessment(answers('yes'));
assert(allYes.valid);
assert.strictEqual(allYes.score, 100);
assert.strictEqual(allYes.classification.id, 'advanced');
assert.strictEqual(allYes.criticalGaps.length, 0);
assert.strictEqual(allYes.professionalReviewRecommended, false);
assert.strictEqual(allYes.panelRecommended, false);
assert.strictEqual(allYes.plan.day90[0].questionId, 'continuous_review');

const allNo = core.evaluateAssessment(answers('no'));
assert(allNo.valid);
assert.strictEqual(allNo.score, 0);
assert.strictEqual(allNo.classification.id, 'fragile');
assert.strictEqual(allNo.criticalGaps.length, 5);
assert.strictEqual(allNo.professionalReviewRecommended, true);
assert.strictEqual(allNo.panelRecommended, true);
assert.strictEqual(allNo.priorityGaps.length, 6);
assert.strictEqual(allNo.plan.day30.length, 2);
assert.strictEqual(allNo.plan.day60.length, 2);
assert.strictEqual(allNo.plan.day90.length, 2);

const allPartial = core.evaluateAssessment(answers('partial'));
assert.strictEqual(allPartial.score, 50);
assert.strictEqual(allPartial.classification.id, 'controlled');
assert.strictEqual(allPartial.criticalGaps.length, 0);

assert.strictEqual(core.classifyScore(24).id, 'fragile');
assert.strictEqual(core.classifyScore(25).id, 'reactive');
assert.strictEqual(core.classifyScore(49).id, 'reactive');
assert.strictEqual(core.classifyScore(50).id, 'controlled');
assert.strictEqual(core.classifyScore(69).id, 'controlled');
assert.strictEqual(core.classifyScore(70).id, 'resilient');
assert.strictEqual(core.classifyScore(84).id, 'resilient');
assert.strictEqual(core.classifyScore(85).id, 'advanced');
assert.strictEqual(core.classifyScore(100).id, 'advanced');

const missing = answers('yes');
delete missing.critical_inventory;
const missingResult = core.evaluateAssessment(missing);
assert.strictEqual(missingResult.valid, false);
assert.deepStrictEqual(missingResult.validation.missing, ['critical_inventory']);

const invalid = answers('yes');
invalid.roles = 'unknown';
const invalidResult = core.evaluateAssessment(invalid);
assert.strictEqual(invalidResult.valid, false);
assert.deepStrictEqual(invalidResult.validation.invalid, ['roles']);

const criticalInventoryGap = resultWith({critical_inventory: 'no'});
assert(criticalInventoryGap.score < 100);
assert(criticalInventoryGap.criticalGaps.includes('critical_inventory'));
assert.strictEqual(criticalInventoryGap.professionalReviewRecommended, true);
assert.strictEqual(criticalInventoryGap.priorityGaps[0].id, 'critical_inventory');

const transferGap = resultWith({transfer_test: 'no'});
assert(transferGap.criticalGaps.includes('transfer_test'));
assert.strictEqual(transferGap.priorityGaps[0].dimension, 'testing');

const noCriticalButManyPartial = resultWith({
  documents_access: 'partial',
  backup_autonomy: 'partial',
  scenario_drill: 'partial',
  spares: 'partial',
  stakeholder_updates: 'partial'
});
assert.strictEqual(noCriticalButManyPartial.criticalGaps.length, 0);
assert.strictEqual(noCriticalButManyPartial.panelRecommended, true);
assert.strictEqual(noCriticalButManyPartial.professionalReviewRecommended, false);

const monotonicBase = resultWith({backup_coverage: 'no'});
const monotonicPartial = resultWith({backup_coverage: 'partial'});
const monotonicYes = resultWith({backup_coverage: 'yes'});
assert(monotonicBase.score < monotonicPartial.score);
assert(monotonicPartial.score < monotonicYes.score);

const dimensionScores = Object.fromEntries(allYes.dimensions.map(d => [d.id, d.score]));
assert(Object.values(dimensionScores).every(score => score === 100));

const weakDocumentation = resultWith({single_line: 'no', labels: 'no', documents_access: 'no'});
assert.strictEqual(weakDocumentation.weakestDimensions[0].id, 'documentation');
assert.strictEqual(weakDocumentation.weakestDimensions[0].score, 0);

const plan = core.buildPlan({...answers('yes'), critical_inventory: 'no', labels: 'partial'}, 6);
assert.strictEqual(plan.selected[0].id, 'critical_inventory');
assert.strictEqual(plan.plan.day30.length, 2);
assert(plan.plan.day30.every(item => typeof item.action === 'string' && item.action.length > 20));

const now = Date.UTC(2026, 6, 28, 5, 0, 0);
const stored = core.sanitizeStorage({
  facilityType: 'hotel',
  medical: true,
  immediateDanger: true,
  companyName: 'Kaydedilmemeli',
  answers: {...answers('yes'), unknown_field: 'secret'}
}, now);
assert.strictEqual(stored.facilityType, 'hotel');
assert.strictEqual(stored.savedAt, now);
assert.strictEqual(stored.medical, undefined);
assert.strictEqual(stored.immediateDanger, undefined);
assert.strictEqual(stored.companyName, undefined);
assert.strictEqual(stored.answers.unknown_field, undefined);
assert.strictEqual(Object.keys(stored.answers).length, 24);
assert.strictEqual(core.isStoredPayloadFresh(stored, now + 29 * 24 * 60 * 60 * 1000), true);
assert.strictEqual(core.isStoredPayloadFresh(stored, now + 31 * 24 * 60 * 60 * 1000), false);
assert.strictEqual(core.isStoredPayloadFresh({...stored, version: 99}, now), false);

const invalidFacility = core.sanitizeStorage({facilityType: 'hospital', answers: answers('yes')}, now);
assert.strictEqual(invalidFacility.facilityType, 'other');

const exported = core.createExport(criticalInventoryGap, 'business', '2026-07-28T05:00:00.000Z');
assert.strictEqual(exported.schemaVersion, 1);
assert.strictEqual(exported.facilityType, 'business');
assert.strictEqual(exported.score, criticalInventoryGap.score);
assert.strictEqual(exported.dimensions.length, 8);
assert.strictEqual(exported.answers, undefined);
assert.strictEqual(exported.medical, undefined);
assert(exported.disclaimer.includes('sertifikası'));
assert.throws(() => core.createExport({valid:false}, 'business'), /Geçerli sonuç/);

const toolDir = path.resolve(__dirname, '../hesaplama/elektrik-surekliligi-olgunluk-skoru');
const html = fs.readFileSync(path.join(toolDir, 'index.html'), 'utf8');
const app = fs.readFileSync(path.join(toolDir, 'app.js'), 'utf8');
const css = fs.readFileSync(path.join(toolDir, 'styles.css'), 'utf8');

assert(html.includes('rel="canonical" href="https://www.alo186.com/hesaplama/elektrik-surekliligi-olgunluk-skoru/"'));
assert(html.includes('"@type":"WebApplication"'));
assert(html.includes('"@type":"FAQPage"'));
assert(html.includes('ISO 22301:2019'));
assert(html.includes('NIST SP 800-34 Rev.1'));
assert(html.includes('Affiliate yok'));
assert(html.includes('112’yi ara'));
assert(html.includes('id="results"') && html.includes('aria-live="polite"'));
assert(html.includes('id="validation"') && html.includes('aria-live="assertive"'));
assert(!/amazon\.(com|com\.tr)|\/dp\//i.test(html), 'Doğrudan Amazon bağlantısı olmamalı.');
assert(!/<input[^>]+(?:name|id)="(?:name|email|phone|address|company|subscription)/i.test(html), 'PII input alanı olmamalı.');
assert(app.includes('continuity_maturity_assessment_completed'));
assert(app.includes('continuity_maturity_panel_opened'));
assert(app.includes('localStorage'));
assert(app.includes('medical.checked = false'));
assert(css.includes('@media(max-width:680px)'));
assert(css.includes('min-height:66px'));

console.log('ALO186 Elektrik Sürekliliği Olgunluk Skoru testleri başarılı.');
