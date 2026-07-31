'use strict';

const assert = require('node:assert/strict');
const api = require('./app.js');

const base = {
  symptoms: false,
  gasSmell: false,
  useCase: 'home',
  source: 'fuel',
  combustionSafety: 'verified',
  coverage: 'none',
  existing: 'none',
  standard: 'verified',
  life: 'valid',
  test: 'pass',
  battery: 'good',
  placement: 'verified',
  signal: 'verified',
  interconnect: 'not_needed',
  confirmNeed: true,
  confirmSpecs: true,
  confirmAffiliate: true
};

assert.equal(api.evaluate(base).status, 'recommend');
assert.equal(api.evaluate(base).affiliateAllowed, true);
assert.equal(api.evaluate({ ...base, symptoms: true }).status, 'stop');
assert.equal(api.evaluate({ ...base, gasSmell: true }).status, 'stop');
assert.equal(api.evaluate({ ...base, combustionSafety: 'problem' }).status, 'stop');
assert.equal(api.evaluate({ ...base, useCase: 'commercial' }).status, 'professional');
assert.equal(api.evaluate({ ...base, useCase: 'mobile' }).status, 'professional');
assert.equal(api.evaluate({ ...base, source: 'none' }).status, 'evidence');
assert.equal(api.evaluate({ ...base, confirmAffiliate: false }).affiliateAllowed, false);

const noBuy = api.evaluate({
  ...base,
  coverage: 'full',
  existing: 'co',
  standard: 'verified',
  life: 'valid',
  test: 'pass',
  battery: 'sealed',
  placement: 'verified',
  signal: 'verified',
  interconnect: 'verified'
});
assert.equal(noBuy.status, 'no-buy');
assert.equal(noBuy.affiliateAllowed, false);

console.log(JSON.stringify({ ok: true, scenarios: 10, module: 'karbonmonoksit_alarmi_uygunluk' }));