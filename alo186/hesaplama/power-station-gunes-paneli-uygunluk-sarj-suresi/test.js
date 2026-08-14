'use strict';
const assert = require('assert');
const core = require('./core.js');

function base(overrides={}) {
  return Object.assign({
    stationMinV: 11, stationMaxV: 55, stationMaxCurrentA: 13, stationMaxIscA: 15, stationMaxPowerW: 220,
    batteryWh: 768, currentSoc: 20, targetSoc: 80, solarPlanningPct: 75,
    panelPmaxW: 200, panelVocV: 24.3, panelVmpV: 20.5, panelIscA: 10.2, panelImpA: 9.8,
    tempCoeffVocPct: -0.28, minTempC: 0, seriesCount: 1, parallelCount: 1,
    installationType: 'portable', ownership: 'candidate',
    noDamageDry: true, noLiveWork: true, activeStorm: false,
    stationDocsVerified: true, panelDocsVerified: true, connectorPolarityVerified: true,
    cableVerified: true, tempDataVerified: true, currentClippingVerified: false, overpanelVerified: false,
    realSolarTestPassed: false
  }, overrides);
}

let r = core.evaluate(base());
assert.equal(r.status, 'compatible_candidate');
assert.equal(r.affiliateEligible, true);
assert(r.calc.arrayColdVocV > r.calc.arrayVocStcV);
assert(r.calc.estimatedSolarHours > 0);

r = core.evaluate(base({seriesCount: 3}));
assert.equal(r.status, 'incompatible');
assert(r.reasons.includes('cold_voc_at_or_above_max'));

r = core.evaluate(base({panelVmpV: 10, panelVocV: 12}));
assert.equal(r.status, 'incompatible');
assert(r.reasons.includes('vmp_below_mppt_min'));

r = core.evaluate(base({stationMaxIscA: '', panelImpA: 14, panelIscA: 14.5}));
assert.equal(r.status, 'conditional');
assert(r.reasons.includes('no_documented_isc_limit_for_overcurrent'));

r = core.evaluate(base({panelPmaxW: 300}));
assert.equal(r.status, 'conditional');
assert(r.reasons.includes('overpanel_power_not_verified'));

r = core.evaluate(base({panelPmaxW: 300, overpanelVerified: true}));
assert.equal(r.status, 'compatible_candidate');

r = core.evaluate(base({ownership:'owned', realSolarTestPassed:true}));
assert.equal(r.status, 'no_buy');
assert.equal(r.affiliateEligible, false);

r = core.evaluate(base({ownership:'owned', realSolarTestPassed:false}));
assert.equal(r.status, 'conditional');

r = core.evaluate(base({activeStorm:true}));
assert.equal(r.status, 'stop');

r = core.evaluate(base({installationType:'rooftop'}));
assert.equal(r.status, 'professional');

r = core.evaluate(base({stationDocsVerified:false}));
assert.equal(r.status, 'evidence');

r = core.evaluate(base({tempCoeffVocPct: 0}));
assert.equal(r.status, 'invalid');

console.log('ALO186 power-station solar input v356 core: PASS');
