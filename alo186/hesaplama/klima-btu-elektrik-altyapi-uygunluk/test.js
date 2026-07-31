const assert = require('assert');
const api = require('./app.js');

const base = {
  emergency: '', mode: 'planning', symptom: 'none', scope: 'single_room', useCase: 'home_room',
  physicalCondition: 'good', areaM2: 25, ceilingM: 2.7, sun: 'normal', climate: 'hot',
  insulation: 'average', people: 2, kitchen: 'no', electronicsW: 0,
  unitType: 'split', existingUnit: 'no', candidateBtu: 9000, candidateInputW: 950,
  candidateRatedA: 4.5, voltage: 230, manualEvidence: 'verified', requiredBreakerA: 16,
  circuitBreakerA: 16, dedicatedCircuit: 'yes', earthStatus: 'verified', rcdStatus: 'tested',
  connection: 'fixed', realPerformanceTest: 'not_tested', comfortResult: 'unknown',
  confirmNeed: 'yes', confirmEvidence: 'yes', confirmAffiliate: 'yes'
};

assert.strictEqual(api.baseCapacity(20), 6000);
assert.strictEqual(api.standardClass(11900), 12000);
const metrics = api.calculate(base);
assert.strictEqual(metrics.valid, true);
assert(metrics.adjustedBtu > 6000);
assert.strictEqual(metrics.recommendedBtu, 9000);
assert.strictEqual(metrics.workingA, 4.5);
assert.strictEqual(api.decide(base).code, 'eligible_compare');
assert.strictEqual(api.decide(base).commerce, true);

const scenarios = [
  [{ ...base, emergency: 'yes' }, 'danger'],
  [{ ...base, physicalCondition: 'hot' }, 'danger'],
  [{ ...base, symptom: 'bright_dim' }, 'grid_risk'],
  [{ ...base, scope: 'building_area' }, 'grid_risk'],
  [{ ...base, mode: 'active_outage' }, 'active_outage'],
  [{ ...base, areaM2: 0 }, 'sizing_input_missing'],
  [{ ...base, useCase: 'commercial' }, 'professional'],
  [{ ...base, connection: 'extension' }, 'unsafe_connection'],
  [{ ...base, earthStatus: 'unknown' }, 'electrical_evidence_missing'],
  [{ ...base, rcdStatus: 'failed' }, 'electrical_evidence_missing'],
  [{ ...base, dedicatedCircuit: 'no' }, 'dedicated_circuit_missing'],
  [{ ...base, manualEvidence: 'unknown' }, 'manual_missing'],
  [{ ...base, requiredBreakerA: 0 }, 'electrical_spec_missing'],
  [{ ...base, requiredBreakerA: 20, circuitBreakerA: 16 }, 'circuit_mismatch'],
  [{ ...base, candidateBtu: 5000 }, 'undersized'],
  [{ ...base, candidateBtu: 18000 }, 'oversized'],
  [{ ...base, candidateBtu: 0, manualEvidence: 'unknown', requiredBreakerA: 0, circuitBreakerA: 16 }, 'eligible_compare'],
  [{ ...base, confirmAffiliate: '' }, 'eligible_compare']
];
for (const [input, code] of scenarios) {
  assert.strictEqual(api.decide(input).code, code, code);
}
assert.strictEqual(api.decide({ ...base, confirmAffiliate: '' }).commerce, false);

const existingGood = {
  ...base, existingUnit: 'yes', candidateBtu: 9000, realPerformanceTest: 'passed', comfortResult: 'good'
};
assert.strictEqual(api.decide(existingGood).code, 'no_buy');
assert.strictEqual(api.decide({ ...existingGood, realPerformanceTest: 'failed' }).code, 'service_first');

const sunnyKitchen = api.calculate({
  ...base, areaM2: 30, ceilingM: 3, sun: 'sunny', climate: 'very_hot', insulation: 'poor', people: 4,
  kitchen: 'yes', electronicsW: 500
});
assert(sunnyKitchen.adjustedBtu > 18000);
assert(sunnyKitchen.recommendedBtu >= 21000);

console.log(JSON.stringify({
  ok: true,
  route: api.ROUTE,
  scenarios: scenarios.length + 4,
  noBuy: true,
  underAndOversize: true,
  electricalSafety: true,
  affiliateGate: true
}, null, 2));
