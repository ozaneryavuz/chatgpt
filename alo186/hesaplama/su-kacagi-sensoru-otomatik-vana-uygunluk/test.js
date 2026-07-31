'use strict';

const assert = require('node:assert/strict');
const api = require('./app.js');

const base = {
  emergency: false,
  useCase: 'home',
  source: 'washer',
  goal: 'alert',
  offline: 'local',
  existing: 'none',
  coverage: 'none',
  test: 'pass',
  power: 'good',
  placement: 'verified',
  notification: 'local',
  valve: 'not_needed',
  shutoffTest: 'not_needed',
  confirmNeed: true,
  confirmSpecs: true,
  confirmAffiliate: true
};

assert.equal(api.evaluate(base).affiliateAllowed, true);
assert.equal(api.evaluate(base).recommendation.code, 'point-leak-alarm');
assert.equal(api.evaluate({ ...base, goal: 'remote', notification: 'both', offline: 'both' }).recommendation.code, 'smart-leak-sensor');
assert.equal(api.evaluate({ ...base, goal: 'shutoff', source: 'whole_home', valve: 'verified', shutoffTest: 'pass' }).recommendation.code, 'flow-shutoff');
assert.equal(api.evaluate({ ...base, emergency: true }).status, 'stop');
assert.equal(api.evaluate({ ...base, useCase: 'commercial' }).status, 'professional');
assert.equal(api.evaluate({ ...base, goal: 'shutoff', source: 'whole_home', valve: 'unknown' }).status, 'professional');
assert.equal(api.evaluate({ ...base, confirmAffiliate: false }).affiliateAllowed, false);
assert.equal(api.evaluate({ ...base, existing: 'point', coverage: 'partial', test: 'unknown' }).status, 'evidence');

const noBuy = api.evaluate({
  ...base,
  existing: 'point',
  coverage: 'full',
  test: 'pass',
  power: 'good',
  placement: 'verified',
  notification: 'local',
  offline: 'local'
});
assert.equal(noBuy.status, 'no-buy');
assert.equal(noBuy.affiliateAllowed, false);

console.log(JSON.stringify({ ok: true, scenarios: 10, module: 'su_kacagi_sensoru_uygunluk' }));