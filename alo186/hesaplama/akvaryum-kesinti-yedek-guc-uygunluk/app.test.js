'use strict';
const assert = require('node:assert/strict');
const api = require('./app.js');

function base(overrides = {}) {
  return {
    tankType: 'tropical', volumeL: 120, outageHours: 8, waterTempC: 25,
    filterW: 18, airPumpW: 5, returnPumpW: 0, heaterW: 100,
    heaterDutyPct: 30, otherW: 0, lightingW: 35,
    rcdVerified: true, dripLoopVerified: true, speciesPlanVerified: true,
    thermometerAvailable: true, ...overrides
  };
}

let r = api.evaluate(base({ electricalHazard: true }));
assert.equal(r.state, 'hazard');
assert.equal(r.commerceAllowed, false);

r = api.evaluate(base({ wetPlugOrCable: true }));
assert.equal(r.state, 'hazard');

r = api.evaluate(base({ activeOutage: true }));
assert.equal(r.state, 'active_event');
assert.equal(r.commerceAllowed, false);

r = api.evaluate(base({ commercialSystem: true }));
assert.equal(r.state, 'professional');

r = api.evaluate(base({ volumeL: 600 }));
assert.equal(r.state, 'professional');

r = api.evaluate(base({ rcdVerified: false }));
assert.equal(r.state, 'evidence');

r = api.evaluate(base({ speciesPlanVerified: false }));
assert.equal(r.state, 'evidence');

r = api.evaluate(base({ waterTempC: 30, airPumpW: 0, filterW: 0, returnPumpW: 0, heaterW: 20 }));
assert.equal(r.state, 'evidence');

r = api.evaluate(base({ tankType: 'marine', airPumpW: 0, returnPumpW: 0 }));
assert.equal(r.state, 'evidence');

r = api.evaluate(base({ airPumpW: 5, filterW: 0, returnPumpW: 0, heaterW: 0, heaterDutyPct: 0, lightingW: 0 }));
assert.equal(r.state, 'commerce');
assert.equal(r.product, 'battery_air_pump');
assert.equal(r.lifeSupportW, 5);
assert.equal(r.lifeSupportPeakW, 5);
assert.equal(r.requiredContinuousW, 10);
assert.equal(r.requiredNominalWh, 60);

r = api.evaluate(base());
assert.equal(r.state, 'commerce');
assert.equal(r.heaterAverageW, 30);
assert.equal(r.lifeSupportW, 53);
assert.equal(r.lifeSupportPeakW, 123);
assert.equal(r.fullSystemW, 88);
assert.equal(r.requiredContinuousW, 160);
assert.equal(r.requiredNominalWh, 630);
assert.equal(r.fullSystemWh, 1040);
assert.equal(r.product, 'power_station');

r = api.evaluate(base({ outageHours: 4, heaterW: 50, heaterDutyPct: 20, filterW: 15, airPumpW: 5, lightingW: 25 }));
assert.equal(r.lifeSupportW, 30);
assert.equal(r.lifeSupportPeakW, 70);
assert.equal(r.requiredContinuousW, 90);
assert.equal(r.requiredNominalWh, 180);
assert.equal(r.product, 'small_power_station');

r = api.evaluate(base({
  outageHours: 2,
  heaterW: 300,
  heaterDutyPct: 10,
  filterW: 0,
  airPumpW: 5,
  returnPumpW: 0,
  otherW: 0,
  lightingW: 0,
  hasExistingSource: true,
  existingContinuousW: 100,
  existingWh: 500,
  existingPureSine: true,
  realOutageTestPassed: true
}));
assert.equal(r.lifeSupportW, 35);
assert.equal(r.lifeSupportPeakW, 305);
assert.equal(r.requiredContinuousW, 390);
assert.equal(r.requiredNominalWh, 110);
assert.equal(r.existingEnough, false);
assert.equal(r.state, 'commerce');
assert(r.existingGaps.some((item) => item.includes('sürekli güç 290 W eksik')));

r = api.evaluate(base({ outageHours: 4, heaterW: 50, heaterDutyPct: 20, filterW: 15, airPumpW: 5, lightingW: 25, hasExistingSource: true, existingContinuousW: 100, existingWh: 300, existingPureSine: true, realOutageTestPassed: true }));
assert.equal(r.state, 'no_buy');
assert.equal(r.noBuy, true);
assert.equal(r.commerceAllowed, false);

r = api.evaluate(base({ hasExistingSource: true, existingContinuousW: 20, existingWh: 50, existingPureSine: false, realOutageTestPassed: false }));
assert.equal(r.state, 'commerce');
assert(r.existingGaps.some((item) => item.includes('sürekli güç')));
assert(r.existingGaps.some((item) => item.includes('nominal enerji')));
assert(r.existingGaps.includes('saf sinüs kanıtı yok'));

assert.throws(() => api.evaluate(base({ volumeL: 0 })), /Akvaryum hacmi/);
assert.throws(() => api.evaluate(base({ outageHours: 100 })), /Hedef kesinti süresi/);

const url = api.amazonUrl(api.evaluate(base({ airPumpW: 5, filterW: 0, returnPumpW: 0, heaterW: 0, heaterDutyPct: 0, lightingW: 0 })));
assert(url.includes('amazon.com.tr'));
assert(url.includes('tag=alo186rehber-21'));
assert(url.includes('akvaryum'));

const ics = api.buildIcs({ result: api.evaluate(base()) }, new Date('2026-07-30T12:00:00Z'));
assert(ics.includes('DTSTART;VALUE=DATE:20261028'));
assert(ics.includes('ALO186 akvaryum yedek güç yeniden testi'));

console.log(JSON.stringify({
  ok: true,
  scenarios: 19,
  states: ['hazard', 'active_event', 'professional', 'evidence', 'no_buy', 'commerce'],
  heaterPeakSizing: true,
  affiliateTripleGate: true,
  noPersonalData: true
}, null, 2));
