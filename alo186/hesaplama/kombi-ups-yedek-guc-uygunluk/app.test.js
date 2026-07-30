'use strict';

const assert = require('node:assert/strict');
const { evaluate, technicalReport, createIcs } = require('./app.js');

const base = {
  emergency: false,
  physicalCondition: 'normal',
  scenario: 'planning',
  applianceType: 'gas_combi',
  exactModelVerified: 'yes',
  manufacturerPowerGuide: 'yes',
  connectionType: 'grounded_plug',
  maxW: 110,
  energyMode: 'average_w',
  averageW: 45,
  targetHours: 8,
  startupKnown: 'yes',
  startupW: 180,
  outputPf: 0.7,
  pureSineRequirement: 'yes',
  groundingRequirement: 'verified',
  continuityNeed: 'no_restart',
  freezeRisk: 'no',
  sourceStatus: 'none'
};

const emergency = evaluate({ ...base, emergency: true });
assert.equal(emergency.code, 'emergency');
assert.equal(emergency.commercial.allowed, false);
assert.match(emergency.actions.join(' '), /187/);
assert.match(emergency.actions.join(' '), /112/);

for (const physicalCondition of ['hot', 'wet', 'damaged', 'smell', 'burned']) {
  assert.equal(evaluate({ ...base, physicalCondition }).code, 'emergency');
}

for (const applianceType of ['electric_boiler', 'central_boiler', 'heat_pump']) {
  const result = evaluate({ ...base, applianceType });
  assert.equal(result.code, 'professional');
  assert.equal(result.commercial.allowed, false);
}
assert.equal(evaluate({ ...base, connectionType: 'fixed' }).code, 'professional');
assert.equal(evaluate({ ...base, maxW: null }).code, 'incomplete');
assert.equal(evaluate({ ...base, targetHours: 0 }).code, 'incomplete');

const normal = evaluate(base);
assert.equal(normal.metrics.averageW, 45);
assert.equal(normal.metrics.continuousW, 140);
assert.equal(normal.metrics.surgeW, 180);
assert.equal(normal.metrics.requiredWh, 550);
assert.equal(normal.metrics.referenceVa, 200);
assert.equal(normal.code, 'capacity_gap');
assert.equal(normal.commercial.allowed, true);
assert.equal(normal.commercial.category, 'pure_sine_ups');
assert.equal(normal.commercial.url, '/amazon-elektrik-urunleri/kesintisiz-guc-kaynagi-secimi?from=kombi');

const measured = evaluate({ ...base, energyMode: 'measured_wh', referenceWh: 360, referenceHours: 8, averageW: null });
assert.equal(measured.metrics.averageW, 45);
assert.equal(measured.code, 'capacity_gap');

const upper = evaluate({ ...base, energyMode: 'upper_bound', averageW: null });
assert.equal(upper.metrics.usedUpperBound, true);
assert.equal(upper.metrics.averageW, 110);
assert.match(upper.warnings.join(' '), /konservatif/);

assert.equal(evaluate({ ...base, averageW: 120 }).code, 'incomplete');
for (const patch of [
  { exactModelVerified: 'no' },
  { manufacturerPowerGuide: 'unknown' },
  { startupKnown: 'no', startupW: null },
  { pureSineRequirement: 'unknown' },
  { groundingRequirement: 'unknown' },
  { connectionType: 'unknown' },
  { continuityNeed: 'unknown' }
]) {
  const result = evaluate({ ...base, ...patch });
  assert.equal(result.code, 'needs_evidence');
  assert.equal(result.commercial.allowed, false);
}

const adequate = evaluate({
  ...base,
  sourceStatus: 'existing',
  sourceContinuousW: 200,
  sourceSurgeW: 250,
  sourceWh: 600,
  sourceVa: 500,
  sourcePureSine: 'yes',
  sourceGroundingVerified: 'yes',
  daytimeTest: 'success'
});
assert.equal(adequate.code, 'no_buy');
assert.equal(adequate.commercial.allowed, false);
assert.match(adequate.actions.join(' '), /Yeni ürün almayın/);
assert.equal(adequate.metrics.runtimeHours, 8.75);

const testFirst = evaluate({
  ...base,
  sourceStatus: 'existing',
  sourceContinuousW: 200,
  sourceSurgeW: 250,
  sourceWh: 600,
  sourceVa: 500,
  sourcePureSine: 'yes',
  sourceGroundingVerified: 'yes',
  daytimeTest: 'untested'
});
assert.equal(testFirst.code, 'test_first');
assert.equal(testFirst.commercial.allowed, false);

const active = evaluate({ ...base, scenario: 'active', freezeRisk: 'yes' });
assert.equal(active.code, 'active_outage');
assert.equal(active.commercial.allowed, false);
assert.match(active.actions.join(' '), /Donma riski/);

const station = evaluate({ ...base, continuityNeed: 'restart_ok' });
assert.equal(station.commercial.allowed, true);
assert.equal(station.commercial.category, 'portable_power');
assert.equal(station.commercial.url, '/amazon-elektrik-urunleri/tasinabilir-guc-istasyonu-secimi?from=kombi');

const high = evaluate({ ...base, targetHours: 30 });
assert.equal(high.code, 'professional');
assert.equal(high.commercial.allowed, false);

const inadequate = evaluate({
  ...base,
  sourceStatus: 'existing',
  sourceContinuousW: 100,
  sourceSurgeW: 120,
  sourceWh: 200,
  sourcePureSine: 'no',
  sourceGroundingVerified: 'unknown',
  daytimeTest: 'failed'
});
assert.equal(inadequate.code, 'capacity_gap');
assert.equal(inadequate.commercial.allowed, true);
assert.ok(inadequate.warnings.length >= 4);

const report = technicalReport(normal);
assert.equal(report.schemaVersion, 1);
assert.equal(report.commercialAllowed, true);
for (const forbidden of ['price', 'stock', 'rating', 'warranty', 'contact', 'location', 'address', 'serialNumber']) {
  assert.ok(!(forbidden in report), `Yasak alan rapora sızdı: ${forbidden}`);
}
assert.doesNotMatch(JSON.stringify(report), /priceCurrency|aggregateRating|availability|"@type":"Offer"/);

const now = new Date('2026-07-30T08:00:00Z');
const ics = createIcs(normal, now);
assert.match(ics, /BEGIN:VCALENDAR/);
assert.match(ics, /20261028/);
assert.match(ics, /Kombi yedek güç 90 günlük kontrolü/);
assert.match(ics, /187/);

console.log(JSON.stringify({
  ok: true,
  scenarios: 27,
  requiredWh: normal.metrics.requiredWh,
  continuousW: normal.metrics.continuousW,
  surgeW: normal.metrics.surgeW,
  referenceVa: normal.metrics.referenceVa,
  noBuyProtected: true,
  gasEmergencyCommerceClosed: true,
  fixedSystemsCommerceClosed: true,
  directAmazonLinks: 0
}, null, 2));
