'use strict';
const assert = require('assert');
const fs = require('fs');
const path = require('path');
const Core = require('./core.js');

const root = __dirname;
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const app = fs.readFileSync(path.join(root, 'app.js'), 'utf8');
const css = fs.readFileSync(path.join(root, 'styles.css'), 'utf8');

function input(overrides = {}) {
  return Object.assign({
    equipment: 'ups-battery',
    lastCheck: '2026-07-28',
    intervalDays: 90,
    condition: 'ok',
    manualKnown: true,
    noUnsafeWork: true
  }, overrides);
}

const plan = Core.createPlan(input(), new Date('2026-07-28T08:00:00Z'));
assert.ok(!plan.error, 'valid plan should be created');
assert.equal(plan.nextCheck, '2026-10-26');
assert.equal(Core.statusForPlan(plan, '2026-10-27').key, 'overdue');
assert.equal(Core.statusForPlan(plan, '2026-10-26').key, 'today');
assert.equal(Core.statusForPlan(plan, '2026-10-10').key, 'soon');

const invalid = Core.createPlan(input({ noUnsafeWork: false }));
assert.ok(invalid.error && invalid.error.length, 'unsafe-work acknowledgement must be required');

const consumerNormal = Core.commercialDecision(plan);
assert.equal(consumerNormal.showCommercial, false, 'normal status must not show product route');

const consumerWarningNoManual = Core.commercialDecision(Object.assign({}, plan, { condition: 'attention', manualKnown: false }));
assert.equal(consumerWarningNoManual.showCommercial, false, 'missing manual check must block commercial route');
assert.equal(consumerWarningNoManual.showProfessional, true);

const consumerWarning = Core.commercialDecision(Object.assign({}, plan, { condition: 'attention', manualKnown: true }));
assert.equal(consumerWarning.showCommercial, true, 'verified consumer-replaceable category may show decision center');
assert.equal(consumerWarning.productCategory, 'ups-battery');

for (const equipment of ['generator', 'rcd', 'spd', 'inverter-storage', 'ev-charger']) {
  const fixedPlan = Object.assign({}, plan, { equipment, condition: 'service', manualKnown: true });
  const decision = Core.commercialDecision(fixedPlan);
  assert.equal(decision.showCommercial, false, `${equipment} must never show commercial product route`);
  assert.equal(decision.showProfessional, true, `${equipment} must show professional route when service is required`);
}

const summary = Core.summarize([
  Object.assign({}, plan, { id: 'a', nextCheck: '2026-07-20' }),
  Object.assign({}, plan, { id: 'b', nextCheck: '2026-08-10' }),
  Object.assign({}, plan, { id: 'c', nextCheck: '2026-12-01', condition: 'service' })
], '2026-07-28');
assert.deepEqual(summary, { total: 3, overdue: 1, soon: 1, service: 1 });

const payload = Core.exportPayload([plan]);
assert.equal(payload.schema, 'alo186-equipment-care-v1');
assert.equal(payload.plans.length, 1);
for (const forbidden of ['name', 'address', 'phone', 'email', 'subscriber', 'serial', 'brand', 'model', 'notes']) {
  assert.ok(!Object.prototype.hasOwnProperty.call(payload.plans[0], forbidden), `export must not include ${forbidden}`);
}

assert.ok(html.includes('Bağımsız elektrik bilgi ağı'));
assert.ok(html.includes('ALO186 herhangi bir markanın temsilcisi değildir'));
assert.ok(html.includes('Reklam / satış ortaklığı açıklaması'));
assert.ok(html.includes('Ürün karar merkezindeki bazı Amazon bağlantıları'));
assert.ok(!/href=["']https?:\/\/(?:www\.)?amazon\./i.test(html), 'tool page must not contain direct Amazon links');
assert.ok(!/<input[^>]+(?:name|id)=["'](?:name|email|phone|address|subscriber|serial|model|note)/i.test(html), 'PII/free-text fields must not exist');
assert.ok(html.includes('application/ld+json'));
assert.ok(html.includes('FAQPage'));
assert.ok(html.includes('WebApplication'));
assert.ok(html.includes('role="alert"'));
assert.ok(html.includes('aria-live="polite"'));
assert.ok(app.includes('localStorage'));
assert.ok(app.includes('equipment_care_product_center_opened'));
assert.ok(css.includes('@media(max-width:600px)'));
assert.ok(css.includes('min-height:44px'));

console.log('Equipment care planner tests passed.');