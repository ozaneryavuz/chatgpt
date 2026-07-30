'use strict';

const assert = require('node:assert/strict');
const { evaluate, technicalReport, createIcs } = require('./app.js');

const base = {
  emergency: false,
  physicalCondition: 'normal',
  scenario: 'planning',
  deviceType: 'cpap',
  dependence: 'routine',
  supplementalOxygen: 'no',
  exactModelVerified: 'yes',
  manufacturerPowerGuide: 'yes',
  humidifier: 'off',
  heatedTube: 'off',
  accessoriesIncluded: 'yes',
  maxW: 65,
  energyMode: 'measured_wh',
  referenceWh: 80,
  referenceHours: 8,
  targetHours: 8,
  powerPath: 'manufacturer_dc',
  sourceStatus: 'none'
};

const emergency = evaluate({ ...base, emergency: true });
assert.equal(emergency.code, 'emergency');
assert.equal(emergency.commercial.allowed, false);

for (const input of [
  { deviceType: 'ventilator' },
  { deviceType: 'oxygen_concentrator' },
  { supplementalOxygen: 'yes' },
  { dependence: 'critical' }
]) {
  const result = evaluate({ ...base, ...input });
  assert.equal(result.code, 'clinical');
  assert.equal(result.commercial.allowed, false);
}

assert.equal(evaluate({ ...base, maxW: null }).code, 'incomplete');

const normal = evaluate(base);
assert.equal(normal.metrics.averageW, 10);
assert.equal(normal.metrics.continuousW, 85);
assert.equal(normal.metrics.requiredWh, 120);
assert.equal(normal.metrics.efficiency, 0.9);
assert.equal(normal.code, 'capacity_gap');
assert.equal(normal.commercial.allowed, true);
assert.equal(normal.commercial.url, '/amazon-elektrik-urunleri/tasinabilir-guc-istasyonu-secimi?from=cpap');

const accessoryGap = evaluate({ ...base, humidifier: 'on', accessoriesIncluded: 'unknown' });
assert.equal(accessoryGap.code, 'needs_evidence');
assert.equal(accessoryGap.commercial.allowed, false);

assert.equal(evaluate({ ...base, powerPath: 'unknown' }).code, 'needs_evidence');
for (const input of [
  { exactModelVerified: 'no' },
  { manufacturerPowerGuide: 'unknown' },
  { manufacturerPowerGuide: 'no' }
]) {
  assert.equal(evaluate({ ...base, ...input }).code, 'needs_evidence');
}

const adequate = evaluate({
  ...base,
  sourceStatus: 'existing',
  sourceContinuousW: 100,
  sourceWh: 150,
  sourceOutputVerified: 'yes',
  daytimeTest: 'success'
});
assert.equal(adequate.code, 'no_buy');
assert.equal(adequate.commercial.allowed, false);
assert.match(adequate.actions.join(' '), /Yeni ürün almayın/);
assert.equal(adequate.metrics.runtimeHours, 10.8);

const untested = evaluate({
  ...base,
  sourceStatus: 'existing',
  sourceContinuousW: 100,
  sourceWh: 150,
  sourceOutputVerified: 'yes',
  daytimeTest: 'untested'
});
assert.equal(untested.code, 'test_first');
assert.equal(untested.commercial.allowed, false);

const active = evaluate({ ...base, scenario: 'active' });
assert.equal(active.code, 'active_outage');
assert.equal(active.commercial.allowed, false);

assert.equal(evaluate({ ...base, deviceType: 'bipap' }).code, 'clinical');
assert.equal(evaluate({ ...base, targetHours: 20 }).code, 'professional');

const upperBound = evaluate({
  ...base,
  energyMode: 'upper_bound',
  averageW: null,
  referenceWh: null,
  referenceHours: null
});
assert.equal(upperBound.metrics.usedUpperBound, true);

const inconsistent = evaluate({ ...base, averageW: 80, energyMode: 'average_w' });
assert.equal(inconsistent.code, 'incomplete');

const report = technicalReport(normal);
assert.equal(report.schemaVersion, 1);
assert.equal(report.commercialAllowed, true);
for (const forbidden of ['price', 'stock', 'rating', 'warranty', 'contact', 'location']) {
  assert.ok(!(forbidden in report), `Yasak alan rapora sızdı: ${forbidden}`);
}
assert.doesNotMatch(JSON.stringify(report), /priceCurrency|aggregateRating|availability|"@type":"Offer"/);

const now = new Date('2026-07-30T08:00:00Z');
const ics = createIcs(normal, now);
assert.match(ics, /BEGIN:VCALENDAR/);
assert.match(ics, /20261028/);
assert.match(ics, /CPAP yedek güç 90 günlük kontrolü/);

console.log(JSON.stringify({
  ok: true,
  scenarios: 18,
  measuredAverageW: normal.metrics.averageW,
  requiredWh: normal.metrics.requiredWh,
  noBuyProtected: true,
  emergencyCommerceClosed: true,
  clinicalCommerceClosed: true,
  directAmazonLinks: 0
}, null, 2));
