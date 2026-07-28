'use strict';

const assert = require('assert');
const fs = require('fs');
const path = require('path');
const core = require('./core.js');

function base(overrides) {
  return Object.assign({
    loads: [{ name: 'Laptop', runningW: 90, surgeW: 120, quantity: 1, loadType: 'sensitive' }],
    dcVoltage: 24,
    batteryAh: 100,
    desiredHours: 4,
    efficiencyPct: 90,
    reservePct: 20,
    chemistry: 'lead',
    depthOfDischargePct: 50,
    startPolicy: 'largest',
    usage: 'portable',
    bms: 'not-applicable',
    dcProtection: 'verified',
    medical: false
  }, overrides || {});
}

(function testLowRiskPortableRoute() {
  const result = core.calculate(base());
  assert.equal(result.route, 'product-guide');
  assert.equal(result.waveform, 'pure-sine-required');
  assert.equal(result.recommendedContinuousW, 150);
  assert(result.estimatedRuntimeHours > 10);
})();

(function testMotorSurge() {
  const result = core.calculate(base({
    loads: [{ name: 'Buzdolabı', runningW: 150, surgeW: 800, quantity: 1, loadType: 'motor' }],
    batteryAh: 200
  }));
  assert.equal(result.totals.runningW, 150);
  assert.equal(result.totals.peakW, 800);
  assert.equal(result.recommendedSurgeW, 1000);
  assert.equal(result.waveform, 'pure-sine-required');
})();

(function testSimultaneousMotorStarts() {
  const loads = [
    { name: 'Pompa 1', runningW: 500, surgeW: 1500, quantity: 1, loadType: 'motor' },
    { name: 'Pompa 2', runningW: 300, surgeW: 900, quantity: 1, loadType: 'motor' }
  ];
  const largest = core.calculate(base({ loads, startPolicy: 'largest', dcVoltage: 48, batteryAh: 200 }));
  const simultaneous = core.calculate(base({ loads, startPolicy: 'simultaneous', dcVoltage: 48, batteryAh: 200 }));
  assert.equal(largest.totals.peakW, 1800);
  assert.equal(simultaneous.totals.peakW, 2400);
})();

(function testHighDcCurrentBlocksAffiliate() {
  const result = core.calculate(base({
    loads: [{ name: 'Isıtıcı', runningW: 1500, surgeW: 1500, quantity: 1, loadType: 'resistive' }],
    dcVoltage: 12,
    batteryAh: 300
  }));
  assert.equal(result.route, 'professional');
  assert(result.dcCurrentAtRecommendedA > 120);
  assert(result.professionalReasons.some((item) => item.includes('DC akımı')));
})();

(function testFixedAndHybridRoutesBlocked() {
  assert.equal(core.calculate(base({ usage: 'fixed' })).route, 'professional');
  assert.equal(core.calculate(base({ usage: 'hybrid' })).route, 'professional');
  assert.equal(core.calculate(base({ usage: 'vehicle' })).route, 'professional');
})();

(function testMedicalRouteBlocked() {
  const result = core.calculate(base({ medical: true }));
  assert.equal(result.route, 'professional');
  assert(result.professionalReasons.some((item) => item.includes('Tıbbi')));
})();

(function testLithiumBmsRequired() {
  const blocked = core.calculate(base({ chemistry: 'lithium', depthOfDischargePct: 80, bms: 'unknown' }));
  const allowed = core.calculate(base({ chemistry: 'lithium', depthOfDischargePct: 80, bms: 'verified' }));
  assert.equal(blocked.route, 'professional');
  assert.equal(allowed.route, 'product-guide');
})();

(function testDcProtectionRequired() {
  assert.equal(core.calculate(base({ dcProtection: 'unknown' })).route, 'professional');
})();

(function testRuntimeAndRequiredAh() {
  const result = core.calculate(base({
    loads: [{ name: 'Yük', runningW: 240, surgeW: 240, quantity: 1, loadType: 'standard' }],
    dcVoltage: 24,
    batteryAh: 100,
    desiredHours: 5,
    efficiencyPct: 90,
    depthOfDischargePct: 50
  }));
  assert.equal(result.usableAcWh, 1080);
  assert.equal(result.estimatedRuntimeHours, 4.5);
  assert.equal(result.requiredBatteryAh, 111);
  assert.equal(result.runtimeMeetsTarget, false);
})();

(function testInvalidLoads() {
  assert.throws(() => core.calculate(base({ loads: [] })), /En az bir cihaz/);
  assert.throws(() => core.calculate(base({ loads: [{ name: 'Hatalı', runningW: 0, surgeW: 0, quantity: 1 }] })), /sürekli gücü/);
  assert.throws(() => core.calculate(base({ loads: [{ name: 'Hatalı', runningW: 500, surgeW: 100, quantity: 1 }] })), /tepe gücü/);
})();

(function testPublishingContract() {
  const html = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');
  const app = fs.readFileSync(path.join(__dirname, 'app.js'), 'utf8');
  assert(html.includes('https://www.alo186.com/hesaplama/inverter-uygunluk/'));
  assert(html.includes('"@type":"WebApplication"'));
  assert(html.includes('Kişisel veri yok'));
  assert(html.includes('Reklam / satış ortaklığı açıklaması'));
  assert(html.includes('aria-disabled="true"'));
  assert(html.includes('rel="nofollow noopener"'));
  assert(!/amazon\.(com|com\.tr)/i.test(html));
  assert(!/type="(email|tel)"/i.test(html));
  assert(!/name="(address|adres|email|telefon|phone|tc|abonelik)/i.test(html));
  assert(app.includes('inverter_suitability_calculated'));
  assert(app.includes('inverter_affiliate_checklist_acknowledged'));
  assert(app.includes('setAffiliateEnabled(false)'));
})();

console.log('Inverter uygunluk testleri başarılı.');