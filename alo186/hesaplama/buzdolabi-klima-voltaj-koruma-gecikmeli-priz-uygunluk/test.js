const assert = require('assert');
const fs = require('fs');
const vm = require('vm');
const path = require('path');

const DIR = __dirname;
const JS = fs.readFileSync(path.join(DIR, 'app.js'), 'utf8');
const HTML = fs.readFileSync(path.join(DIR, 'index.html'), 'utf8');
const CSS = fs.readFileSync(path.join(DIR, 'styles.css'), 'utf8');
const sandbox = { console, globalThis: {}, setTimeout, clearTimeout };
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.runInContext(JS, sandbox);
const api = sandbox.Alo186VoltageProtection;
assert(api, 'Alo186VoltageProtection API yok');

const base = {
  emergency: '', mode: 'planning', symptom: 'repeated_restart', scope: 'single',
  physicalCondition: 'good', earthStatus: 'verified', rcdStatus: 'tested',
  applianceType: 'fridge', connection: 'direct', voltage: 230, deviceW: 180, deviceA: 1.2,
  manualDelayMinutes: 5, manualEvidence: 'verified', measurementEvidence: 'verified_logger',
  measuredMinV: 180, measuredMaxV: 248, existingType: 'none', existingFunctions: 'unknown',
  existingRatedA: 0, existingDelayMinutes: 0, lowThresholdV: 190, highThresholdV: 250,
  existingEvidence: 'none', existingTest: 'not_tested'
};

let m = api.calculate(base);
assert.strictEqual(m.calculatedA, 0.78);
assert.strictEqual(m.workingA, 1.2);
assert.strictEqual(m.requiredA, 1.5);
assert.strictEqual(m.standardA, 6);
assert.strictEqual(m.lowEventDetected, true);
assert.strictEqual(m.highEventDetected, false);

assert.strictEqual(api.decide({ ...base, emergency: 'yes' }).code, 'emergency');
assert.strictEqual(api.decide({ ...base, physicalCondition: 'hot' }).code, 'emergency');
assert.strictEqual(api.decide({ ...base, symptom: 'bright_dim' }).code, 'neutral_grid_risk');
assert.strictEqual(api.decide({ ...base, scope: 'building_area' }).code, 'neutral_grid_risk');
assert.strictEqual(api.decide({ ...base, applianceType: 'medical' }).code, 'medical_professional');
assert.strictEqual(api.decide({ ...base, applianceType: 'split_ac', connection: 'fixed' }).code, 'fixed_professional');
assert.strictEqual(api.decide({ ...base, connection: 'extension' }).code, 'unsafe_connection');
assert.strictEqual(api.decide({ ...base, earthStatus: 'failed' }).code, 'earth_rcd_failed');
assert.strictEqual(api.decide({ ...base, mode: 'active_outage' }).code, 'active_outage');
assert.strictEqual(api.decide({ ...base, measurementEvidence: 'unsafe_handheld' }).code, 'unsafe_measurement');
assert.strictEqual(api.decide({ ...base, deviceW: 0, deviceA: 0 }).code, 'load_evidence_missing');
assert.strictEqual(api.decide({ ...base, manualEvidence: 'unknown', manualDelayMinutes: 0 }).code, 'manual_delay_missing');
assert.strictEqual(api.decide({ ...base, deviceA: 12 }).code, 'high_current_professional');
assert.strictEqual(api.decide({ ...base, existingType: 'surge_only' }).code, 'surge_not_voltage');
assert.strictEqual(api.decide({ ...base, symptom: 'single_appliance_only', measurementEvidence: 'verified_normal' }).code, 'appliance_service');
assert.strictEqual(api.decide(base).code, 'eligible_compare');

const adequate = {
  ...base, existingType: 'plug_voltage', existingFunctions: 'under_over_delay', existingRatedA: 10,
  existingDelayMinutes: 5, existingEvidence: 'verified', existingTest: 'passed'
};
assert.strictEqual(api.decide(adequate).code, 'no_buy');
assert.strictEqual(api.decide({ ...adequate, existingRatedA: 1 }).code, 'current_shortfall');
assert.strictEqual(api.decide({ ...adequate, existingDelayMinutes: 2 }).code, 'delay_shortfall');
assert.strictEqual(api.decide({ ...adequate, existingEvidence: 'unknown' }).code, 'protector_evidence_missing');
assert.strictEqual(api.decide({ ...adequate, existingFunctions: 'under_over' }).code, 'functions_missing');
assert.strictEqual(api.decide({ ...adequate, existingTest: 'failed' }).code, 'test_missing');

const payload = api.summaryPayload(base, api.decide(base));
assert.strictEqual(payload.privacy, 'Kişisel veri içermez; tarayıcıda oluşturulur.');
assert.strictEqual(payload.decision.code, 'eligible_compare');

for (const token of [
  '<form id="voltageForm"', 'aria-live="polite"', 'data-affiliate-check',
  'rel="sponsored nofollow noopener"', 'Kişisel veri yok', 'yeni ürün almayın',
  'https://alo186.com/hesaplama/buzdolabi-klima-voltaj-koruma-gecikmeli-priz-uygunluk/'
]) assert((HTML + JS).includes(token), token);

for (const forbidden of [
  'localStorage', 'sessionStorage', 'navigator.geolocation', 'fetch(',
  'amazon.com', 'amazon.com.tr', '"@type":"Product"', '"@type":"Offer"',
  'aggregateRating', 'availability', 'name="email"', 'name="phone"', 'name="address"'
]) assert(!HTML.includes(forbidden) && !JS.includes(forbidden), forbidden);

for (const token of [
  '@media(max-width:900px)', '@media(max-width:620px)', 'min-height:48px',
  ':focus-visible', '@media(prefers-reduced-motion:reduce)', '@media(forced-colors:active)', '@media print'
]) assert(CSS.includes(token), token);

console.log(JSON.stringify({ ok: true, scenarios: 22, noBuy: true, neutralAndEmergencyClose: true, affiliateGate: true, privacy: true, responsive: true }, null, 2));
