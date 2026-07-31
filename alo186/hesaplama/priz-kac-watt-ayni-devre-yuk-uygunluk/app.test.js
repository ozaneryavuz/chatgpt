'use strict';
const assert = require('node:assert/strict');
const { calculate, decide, ROUTE, PRODUCT_ROUTES } = require('./app.js');

assert.equal(ROUTE, '/hesaplama/priz-kac-watt-ayni-devre-yuk-uygunluk/');
assert.equal(PRODUCT_ROUTES.meter, '/akilli-urun-secimi?intent=priz-tipi-enerji-olcer');
assert.equal(PRODUCT_ROUTES.strip, '/amazon-elektrik-urunleri/akim-korumali-grup-priz-secimi');

const base = {
  emergency: false,
  evaluationMode: 'existing',
  usageContext: 'kitchen',
  connection: 'direct',
  duration: 'short',
  evidence: 'nameplate',
  voltage: 230,
  breakerA: 16,
  socketA: 16,
  stripA: 0,
  physicalCondition: 'good',
  earthStatus: 'verified',
  rcdStatus: 'tested',
  needMoreOutlets: 'no',
  kettleW: 1800,
  airfryerW: 0,
  microwaveW: 0,
  coffeeW: 900,
  heaterW: 0,
  laundryW: 0,
  electronicsW: 0,
  otherW: 0
};

assert.deepEqual(calculate(base), {
  totalW: 2700,
  currentA: 11.74,
  limitA: 16,
  planningA: 14.4,
  planningW: 3312,
  remainingW: 612,
  highPowerCount: 1,
  largestLoadW: 1800,
  voltage: 230,
  planningFactor: 0.9
});

assert.equal(decide({ ...base, emergency: true }).code, 'emergency');
assert.equal(decide({ ...base, physicalCondition: 'hot' }).code, 'physical_hazard');
assert.equal(decide({ ...base, usageContext: 'medical' }).code, 'specialist');
assert.equal(decide({ ...base, usageContext: 'ev' }).code, 'specialist');
assert.equal(decide({ ...base, connection: 'daisy', stripA: 16 }).code, 'daisy_chain');
assert.equal(decide({ ...base, connection: 'adapter', stripA: 16 }).code, 'adapter_chain');
assert.equal(decide({ ...base, connection: 'wound_reel', stripA: 16 }).code, 'wound_reel');
assert.equal(decide({ ...base, kettleW: 0, coffeeW: 0 }).code, 'missing_load');
assert.equal(decide({ ...base, usageContext: 'electronics', evidence: 'estimated', kettleW: 0, coffeeW: 0, electronicsW: 500 }).code, 'measure_first');
assert.equal(decide({ ...base, breakerA: 0 }).code, 'label_needed');
assert.equal(decide({ ...base, earthStatus: 'failed' }).code, 'earth_failed');
assert.equal(decide({ ...base, rcdStatus: 'failed' }).code, 'rcd_failed');
assert.equal(decide({ ...base, earthStatus: 'unknown' }).code, 'earth_unknown');
assert.equal(decide({ ...base, kettleW: 4000, coffeeW: 0 }).code, 'overload');
assert.equal(decide({ ...base, kettleW: 1400, airfryerW: 1400, coffeeW: 0 }).code, 'stagger');
assert.equal(decide({ ...base, duration: 'long', kettleW: 3000, coffeeW: 0 }).code, 'near_limit');
assert.equal(decide(base).code, 'no_buy');
assert.equal(decide({ ...base, evaluationMode: 'planned', usageContext: 'electronics', kettleW: 0, coffeeW: 0, electronicsW: 600, needMoreOutlets: 'yes' }).code, 'electronics_strip');
assert.equal(decide({ ...base, evaluationMode: 'planned' }).code, 'direct_only');

const stripLimit = calculate({ ...base, connection: 'single_strip', stripA: 10, kettleW: 1500, coffeeW: 0 });
assert.equal(stripLimit.limitA, 10);
assert.equal(stripLimit.planningW, 2070);

console.log(JSON.stringify({
  ok: true,
  scenarios: 19,
  wattAmpCalculation: true,
  minimumLabelWins: true,
  noBuy: true,
  highPowerCommerceClosed: true,
  affiliateOnlyForMeasuredNeed: true
}));
