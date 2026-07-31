'use strict';
const assert = require('node:assert/strict');
const { evaluate } = require('./app.js');

const base = {
  electricalWaterRisk: false,
  scope: 'room',
  source: 'resolved',
  rhKnown: 'yes',
  rh: 66,
  days: 7,
  condensation: 'yes',
  mold: 'none',
  existingGauge: 'yes',
  existingDehumidifier: 'no',
  existingPass: 'no',
  outletSafe: 'yes',
  confirmNeed: true,
  confirmSpecs: true,
  confirmAffiliate: true
};

let result = evaluate(base);
assert.equal(result.status, 'recommend');
assert.deepEqual(result.categories, ['portable_dehumidifier']);
assert.equal(result.affiliateAllowed, true);

result = evaluate({ ...base, existingDehumidifier: 'yes', existingPass: 'yes' });
assert.equal(result.status, 'no-buy');
assert.equal(result.affiliateAllowed, false);

result = evaluate({ ...base, electricalWaterRisk: true });
assert.equal(result.status, 'stop');
assert.equal(result.affiliateAllowed, false);

result = evaluate({ ...base, rhKnown: 'no', existingGauge: 'no', rh: 0, days: 0, condensation: 'no' });
assert.equal(result.status, 'recommend');
assert.deepEqual(result.categories, ['hygrometer']);

result = evaluate({ ...base, source: 'active-leak' });
assert.notEqual(result.status, 'recommend');
assert.equal(result.affiliateAllowed, false);

console.log(JSON.stringify({ ok: true, scenarios: 5 }));
