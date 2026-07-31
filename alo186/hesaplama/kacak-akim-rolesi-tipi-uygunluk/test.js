'use strict';

const assert = require('node:assert/strict');
const api = require('./app.js');

const base = {
  emergency: false,
  mode: 'planning',
  useCase: 'home',
  physical: 'good',
  testButton: 'unknown',
  goal: 'personal',
  circuitScope: 'single',
  phase: 'single',
  loadType: 'general',
  manufacturerType: 'unknown',
  dc6: 'not_applicable',
  breakerA: 16,
  existingRatedA: 0,
  existingMa: 'unknown',
  existingType: 'unknown',
  existingForm: 'none',
  installationTest: 'unknown',
  taskTest: 'not_tested',
  downstream30: 'not_applicable',
  confirmNeed: true,
  confirmSpecs: true,
  confirmAffiliate: true
};

const general = api.evaluate(base);
assert.equal(general.ok, true);
assert.equal(general.recommendation.typeCode, 'A');
assert.equal(general.recommendation.form, 'RCBO');
assert.equal(general.recommendation.sensitivity, '30 mA');
assert.equal(general.affiliateAllowed, true);

assert.equal(api.evaluate({ ...base, emergency: true }).status, 'stop');
assert.equal(api.evaluate({ ...base, physical: 'hot' }).status, 'stop');
assert.equal(api.evaluate({ ...base, testButton: 'fail' }).status, 'stop');
assert.equal(api.evaluate({ ...base, installationTest: 'fail' }).status, 'stop');
assert.equal(api.evaluate({ ...base, mode: 'active_fault' }).status, 'diagnose');
assert.equal(api.evaluate({ ...base, goal: 'nuisance' }).status, 'diagnose');
assert.equal(api.evaluate({ ...base, useCase: 'commercial' }).status, 'professional');
assert.equal(api.evaluate({ ...base, phase: 'three' }).status, 'professional');
assert.equal(api.evaluate({ ...base, loadType: 'single_vfd' }).recommendation.typeCode, 'F');
assert.equal(api.evaluate({ ...base, loadType: 'ev', dc6: 'unknown' }).status, 'professional');
assert.equal(api.evaluate({ ...base, loadType: 'ev', dc6: 'verified' }).recommendation.typeCode, 'A');
assert.equal(api.evaluate({ ...base, loadType: 'pv' }).recommendation.typeCode, 'B');
assert.equal(api.evaluate({ ...base, loadType: 'ups_vfd' }).affiliateAllowed, false);
assert.equal(api.evaluate({ ...base, manufacturerType: 'B' }).recommendation.typeCode, 'B');
assert.equal(api.evaluate({ ...base, loadType: 'unknown' }).affiliateAllowed, false);
assert.equal(api.evaluate({ ...base, loadType: 'single_vfd', manufacturerType: 'unknown' }).status, 'evidence');

const insufficient = api.evaluate({
  ...base,
  existingForm: 'RCCB',
  existingRatedA: 25,
  breakerA: 40,
  existingMa: '30',
  existingType: 'A',
  testButton: 'pass',
  installationTest: 'pass',
  taskTest: 'pass'
});
assert.equal(insufficient.status, 'evidence');
assert(insufficient.evidence.some((item) => item.includes('25 A')));

const noBuy = api.evaluate({
  ...base,
  existingForm: 'RCBO',
  existingRatedA: 16,
  existingMa: '30',
  existingType: 'A',
  testButton: 'pass',
  installationTest: 'pass',
  taskTest: 'pass'
});
assert.equal(noBuy.status, 'no-buy');
assert.equal(noBuy.affiliateAllowed, false);

const upstream = api.evaluate({
  ...base,
  useCase: 'whole_dwelling',
  goal: 'upstream_fire',
  circuitScope: 'multiple',
  breakerA: 63,
  downstream30: 'verified'
});
assert.equal(upstream.recommendation.form, 'RCCB veya devre başına RCBO');
assert.equal(upstream.recommendation.sensitivity, '100/300 mA seçici üst kademe + alt devrelerde 30 mA');

assert.equal(api.evaluate({ ...base, confirmAffiliate: false }).affiliateAllowed, false);
assert.equal(api.evaluate({ ...base, breakerA: 0 }).ok, false);
assert.equal(api.typeMeets('B', 'F'), true);
assert.equal(api.typeMeets('AC', 'A'), false);

console.log(JSON.stringify({
  ok: true,
  scenarios: 22,
  types: ['A', 'F', 'B'],
  forms: ['RCCB', 'RCBO'],
  safetyClosures: true,
  nuisanceDiagnosis: true,
  noBuy: true,
  affiliateGate: 3,
  privacy: true
}, null, 2));
