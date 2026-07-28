'use strict';
const assert = require('node:assert/strict');
const core = require('./core.js');

const settings = {
  usage: 'home',
  voltage: 'ag',
  area: 'inside',
  priorities: { internet: true, lighting: true, cold: false, pump: false, medical: false }
};

const longSummary = core.summarize([
  { date: '2026-07-20', durationMinutes: 721, kind: 'unplanned', scope: 'street', officialRecord: true }
], { year: 2026, settings });
assert.equal(longSummary.longDurationEntries.length, 1);
assert.equal(longSummary.hasCompensationReviewSignal, true);

const plannedEntries = Array.from({ length: 7 }, (_, index) => ({
  date: `2026-0${(index % 7) + 1}-01`,
  durationMinutes: 30,
  kind: 'planned',
  scope: 'street'
}));
const thresholdSummary = core.summarize(plannedEntries, { year: 2026, settings });
assert.equal(thresholdSummary.annualSignals.planned.countExceeded, true);
assert.equal(thresholdSummary.annualSignals.planned.status, 'review');

const routeSummary = core.summarize([
  { date: '2026-07-01', durationMinutes: 90, kind: 'unplanned', scope: 'street' },
  { date: '2026-07-10', durationMinutes: 60, kind: 'unplanned', scope: 'street' }
], { year: 2026, settings });
const routes = core.buildResilienceRoutes(routeSummary);
assert.equal(routes.showProductCenter, true);
assert.ok(routes.routes.some((item) => item.id === 'modem-backup'));
assert.ok(routes.routes.some((item) => item.id === 'ups-duration'));

const medicalSummary = core.summarize([
  { date: '2026-07-01', durationMinutes: 300, kind: 'unplanned', scope: 'building' }
], { year: 2026, settings: { ...settings, priorities: { ...settings.priorities, medical: true } } });
const medicalRoutes = core.buildResilienceRoutes(medicalSummary);
assert.equal(medicalRoutes.commercialSuppressed, true);
assert.equal(medicalRoutes.showProductCenter, false);
assert.equal(medicalRoutes.routes.length, 1);

const exported = core.createExport([
  { date: '2026-07-01', durationMinutes: 60, kind: 'unknown', scope: 'unit', secretNote: 'silinmeli' }
], settings);
assert.equal(exported.entries[0].secretNote, undefined);
assert.equal(exported.entries[0].date, '2026-07-01');

console.log('Kesinti günlüğü çekirdek testleri başarılı.');
