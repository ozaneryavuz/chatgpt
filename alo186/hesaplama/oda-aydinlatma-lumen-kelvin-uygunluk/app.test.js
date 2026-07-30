'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { evaluate, amazonUrl, buildIcs } = require('./app.js');

const base = {
  room: 'living',
  use: 'general',
  surface: 'medium',
  areaM2: 20,
  currentLumens: 0,
  socketType: 'e27',
  hasExisting: false,
  existingSafe: false,
  electricalHazard: false,
  fixedInstallation: false,
  dimmerPresent: false,
  dimmerCompatible: false,
  enclosedFixture: false,
  enclosedRated: false,
  wetZone: false,
  ipRated: false,
  motionSensor: false,
  solarPossible: false
};

const living = evaluate(base);
assert.equal(living.state, 'commerce');
assert.equal(living.product, 'e27_led');
assert.equal(living.targetLux, 150);
assert.equal(living.targetKelvin, 3000);
assert.equal(living.targetCri, 80);
assert.equal(living.requiredLumens, 5050);
assert.equal(living.deficitLumens, 5050);
assert.equal(living.bulbLumens, 1521);
assert.equal(living.approximateCount, 4);
assert.equal(living.commerceAllowed, true);

const noBuy = evaluate({ ...base, hasExisting: true, existingSafe: true, currentLumens: 5000 });
assert.equal(noBuy.state, 'no_buy');
assert.equal(noBuy.noBuy, true);
assert.equal(noBuy.commerceAllowed, false);
assert.match(noBuy.title, /yeni ürün almayın/i);

const hazard = evaluate({ ...base, electricalHazard: true });
assert.equal(hazard.state, 'hazard');
assert.equal(hazard.commerceAllowed, false);
assert.match(hazard.summary, /112/);

const wetBathroom = evaluate({ ...base, room: 'bathroom', wetZone: true, ipRated: false });
assert.equal(wetBathroom.state, 'professional');
assert.equal(wetBathroom.commerceAllowed, false);

const fixed = evaluate({ ...base, fixedInstallation: true });
assert.equal(fixed.state, 'professional');

const dimmerUnknown = evaluate({ ...base, dimmerPresent: true, dimmerCompatible: false });
assert.equal(dimmerUnknown.state, 'evidence');
assert.match(dimmerUnknown.title, /Dimmer/);

const enclosedUnknown = evaluate({ ...base, enclosedFixture: true, enclosedRated: false });
assert.equal(enclosedUnknown.state, 'evidence');
assert.match(enclosedUnknown.title, /Kapalı armatür/);

const integrated = evaluate({ ...base, socketType: 'integrated' });
assert.equal(integrated.state, 'evidence');
assert.equal(integrated.commerceAllowed, false);

const study = evaluate({ ...base, room: 'study', use: 'task', areaM2: 10, surface: 'light', currentLumens: 900 });
assert.equal(study.state, 'commerce');
assert.equal(study.product, 'task_lamp');
assert.equal(study.targetLux, 500);
assert.equal(study.targetCri, 90);
assert.equal(study.targetKelvin, 4000);

const corridor = evaluate({ ...base, room: 'corridor', areaM2: 7, motionSensor: true });
assert.equal(corridor.product, 'sensor_bulb');

const outdoor = evaluate({ ...base, room: 'outdoor', use: 'night', areaM2: 12, surface: 'dark', socketType: 'none', solarPossible: true });
assert.equal(outdoor.state, 'commerce');
assert.equal(outdoor.product, 'solar_outdoor');
assert.equal(outdoor.targetLux, 50);

const safeWetBathroom = evaluate({ ...base, room: 'bathroom', wetZone: true, ipRated: true, socketType: 'e27' });
assert.equal(safeWetBathroom.state, 'commerce');

assert.throws(() => evaluate({ ...base, areaM2: 0 }), /Alan/);
assert.throws(() => evaluate({ ...base, currentLumens: -1 }), /Mevcut toplam lümen/);

const affiliate = amazonUrl(living);
assert.match(affiliate, /^https:\/\/www\.amazon\.com\.tr\/s\?k=/);
assert.match(affiliate, /tag=alo186rehber-21/);
assert.doesNotMatch(affiliate, /price|stock|rating|warranty/i);

const payload = { result: living };
const ics = buildIcs(payload, new Date('2026-07-30T10:00:00Z'));
assert.match(ics, /BEGIN:VCALENDAR/);
assert.match(ics, /DTSTART;VALUE=DATE:20270126/);
assert.doesNotMatch(ics, /mailto:|tel:/i);

const html = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');
const js = fs.readFileSync(path.join(__dirname, 'app.js'), 'utf8');
const css = fs.readFileSync(path.join(__dirname, 'styles.css'), 'utf8');

assert.match(html, /https:\/\/alo186\.com\/hesaplama\/oda-aydinlatma-lumen-kelvin-uygunluk\//);
assert.match(html, /Amazon satış ortaklığı bağlantısı/);
assert.match(html, /Bir Amazon Gelir Ortağı/);
assert.match(html, /ALO186 EDAŞ, kamu kurumu/);
assert.match(html, /id="actualNeed"/);
assert.match(html, /id="technicalCheck"/);
assert.match(html, /id="affiliateCheck"/);
assert.match(html, /rel="sponsored nofollow noopener"/);
assert.match(html, /JSON teknik fişi indir/);
assert.match(html, /180 günlük yeniden kontrol/);
assert.match(html, /ISO\/CIE 8995-1:2025/);
assert.match(html, /IEC 62560/);
assert.match(html, /IEC 62612/);
assert.doesNotMatch(html, /"@type"\s*:\s*"Product"/);
assert.doesNotMatch(html, /"@type"\s*:\s*"Offer"/);
assert.doesNotMatch(html, /"price"\s*:|"availability"\s*:|"aggregateRating"\s*:|"review"\s*:/);
assert.doesNotMatch(js, /localStorage|sessionStorage|fetch\s*\(/);
assert.doesNotMatch(js, /\bprice\b|\bstock\b|\brating\b|\bwarranty\b/i);
assert.match(css, /@media\(max-width:620px\)/);
assert.match(css, /prefers-reduced-motion/);

console.log(JSON.stringify({
  ok: true,
  scenarios: 13,
  route: '/hesaplama/oda-aydinlatma-lumen-kelvin-uygunluk/',
  requiredLumens: living.requiredLumens,
  noBuy: noBuy.noBuy,
  hazardCommerceClosed: !hazard.commerceAllowed,
  affiliateTripleGate: true,
  personalData: false,
  revisitDays: 180
}, null, 2));
