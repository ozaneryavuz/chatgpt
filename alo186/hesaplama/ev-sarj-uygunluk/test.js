'use strict';
const assert = require('assert');
const fs = require('fs');
const path = require('path');
const core = require('./core.js');

function base(overrides) {
  return Object.assign({
    phase: 'single',
    mainCurrentA: 50,
    otherLoadKw: 1.5,
    reservePct: 15,
    vehicleMaxKw: 11,
    dailyKm: 50,
    consumptionKwh100: 18,
    availableHours: 10,
    efficiencyPct: 90,
    dedicatedCircuit: 'yes',
    protection: 'verified',
    parking: 'private',
    loadManagement: false
  }, overrides || {});
}

assert(Math.abs(core.connectionPowerKw('single', 32) - 7.36) < 0.001);
assert(Math.abs(core.connectionPowerKw('three', 16) - 11.085) < 0.01);

const single = core.calculate(base());
assert.strictEqual(single.staticMax.key, 'ac-7-4');
assert.strictEqual(single.recommendedStatic.key, 'portable-10a');
assert.strictEqual(single.route, 'portable-guide');
assert(single.dailyNeedMet);

const three = core.calculate(base({ phase: 'three', mainCurrentA: 32, otherLoadKw: 5, vehicleMaxKw: 22, dailyKm: 180, availableHours: 8 }));
assert.strictEqual(three.staticMax.key, 'ac-11');
assert.strictEqual(three.route, 'wallbox-guide');
assert(three.dailyGridKwh > 30);

const noSpare = core.calculate(base({ mainCurrentA: 25, otherLoadKw: 5, reservePct: 20, loadManagement: true }));
assert.strictEqual(noSpare.staticMax, null);
assert(noSpare.managedMax);
assert.strictEqual(noSpare.route, 'portable-guide');

const unknown = core.calculate(base({ phase: 'unknown' }));
assert.strictEqual(unknown.route, 'professional');
assert(unknown.professionalReasons.some(x => x.includes('Faz yapısı')));

const unverified = core.calculate(base({ dedicatedCircuit: 'unknown', protection: 'unknown' }));
assert.strictEqual(unverified.route, 'professional');
assert(unverified.professionalReasons.length >= 2);

const commonParking = core.calculate(base({ parking: 'common' }));
assert.strictEqual(commonParking.route, 'professional');
assert(commonParking.warnings[0].includes('Apartman'));

assert.throws(() => core.calculate(base({ dailyKm: 0 })), /Günlük sürüş/);
assert.throws(() => core.calculate(base({ mainCurrentA: 500 })), /Ana besleme/);

const html = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');
const app = fs.readFileSync(path.join(__dirname, 'app.js'), 'utf8');
const css = fs.readFileSync(path.join(__dirname, 'styles.css'), 'utf8');
assert(html.includes('rel="canonical" href="https://www.alo186.com/hesaplama/ev-sarj-uygunluk/"'));
assert(html.includes('"@type":"WebApplication"'));
assert(html.includes('aria-live="assertive"'));
assert(html.includes('role="alert"'));
assert(html.toLocaleLowerCase('tr-TR').includes('satış ortaklığı açıklaması'));
assert(html.includes('rel="sponsored nofollow noopener"'));
assert(html.includes('Bu form ad, adres, araç plakası, abonelik veya iletişim bilgisi istemez'));
assert(!/<input[^>]+(?:name|id)="(?:name|email|phone|address|plate|subscriber)/i.test(html));
assert(app.includes('ev_suitability_completed'));
assert(app.includes('ev_affiliate_search_opened'));
assert(app.includes('aria-disabled'));
assert(css.includes('@media(max-width:520px)'));

console.log('EV şarj uygunluk motoru ve yayın sözleşmesi: tüm kontroller geçti.');