'use strict';

const assert = require('node:assert/strict');
const api = require('./app.js');

const base = {
  activeOutage: false,
  useCase: 'home',
  appliance: 'fridge',
  goal: 'check',
  outageKnowledge: 'none',
  fridgeTemp: 'safe',
  freezerTemp: 'not_applicable',
  existing: 'none',
  validation: 'pass',
  alarmTest: 'not_needed',
  memory: 'not_needed',
  power: 'good',
  placement: 'verified',
  remote: 'not_needed',
  realTest: 'pass',
  confirmNeed: true,
  confirmSpecs: true,
  confirmAffiliate: true
};

assert.equal(api.evaluate(base).affiliateAllowed, true);
assert.equal(api.evaluate(base).recommendation.code, 'appliance-thermometer');
assert.equal(api.evaluate({ ...base, goal: 'alarm', alarmTest: 'pass', memory: 'pass' }).recommendation.code, 'fridge-freezer-temperature-alarm');
assert.equal(api.evaluate({ ...base, goal: 'remote', remote: 'pass', memory: 'pass' }).recommendation.code, 'remote-temperature-alarm');
assert.equal(api.evaluate({ ...base, activeOutage: true }).status, 'stop');
assert.equal(api.evaluate({ ...base, useCase: 'commercial' }).status, 'professional');
assert.equal(api.evaluate({ ...base, useCase: 'medical' }).affiliateAllowed, false);
assert.equal(api.evaluate({ ...base, confirmAffiliate: false }).affiliateAllowed, false);
assert.equal(api.evaluate({ ...base, existing: 'thermometer', validation: 'unknown' }).status, 'evidence');

const noBuy = api.evaluate({
  ...base,
  existing: 'thermometer',
  validation: 'pass',
  power: 'good',
  placement: 'verified',
  realTest: 'pass',
  fridgeTemp: 'safe'
});
assert.equal(noBuy.status, 'no-buy');
assert.equal(noBuy.affiliateAllowed, false);

console.log(JSON.stringify({ ok: true, scenarios: 10, module: 'buzdolabi_dondurucu_sicaklik_alarmi' }));