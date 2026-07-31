'use strict';

const assert = require('node:assert/strict');
const api = require('./app.js');

const base = {
  emergency: false,
  useCase: 'home',
  room: 'bedroom',
  goal: 'new',
  accessibility: 'none',
  existing: 'none',
  coverage: 'none',
  standard: 'verified',
  life: 'valid',
  test: 'pass',
  battery: 'good',
  placement: 'verified',
  interconnect: 'not_needed',
  confirmNeed: true,
  confirmSpecs: true,
  confirmAffiliate: true
};

assert.equal(api.evaluate(base).recommendation.code, 'smoke');
assert.equal(api.evaluate(base).affiliateAllowed, true);
assert.equal(api.evaluate({ ...base, room: 'kitchen' }).recommendation.code, 'heat');
assert.equal(api.evaluate({ ...base, emergency: true }).status, 'stop');
assert.equal(api.evaluate({ ...base, useCase: 'commercial' }).status, 'professional');
assert.equal(api.evaluate({ ...base, accessibility: 'hearing' }).status, 'professional');
assert.equal(api.evaluate({ ...base, room: 'bathroom' }).status, 'professional');
assert.equal(api.evaluate({ ...base, confirmAffiliate: false }).affiliateAllowed, false);
assert.equal(api.evaluate({ ...base, standard: 'unknown', existing: 'smoke' }).status, 'evidence');

const noBuy = api.evaluate({
  ...base,
  existing: 'smoke',
  coverage: 'full',
  standard: 'verified',
  life: 'valid',
  test: 'pass',
  battery: 'sealed',
  placement: 'verified',
  interconnect: 'not_needed'
});
assert.equal(noBuy.status, 'no-buy');
assert.equal(noBuy.affiliateAllowed, false);

console.log(JSON.stringify({ ok: true, scenarios: 10, module: 'duman_isi_alarmi_uygunluk' }));