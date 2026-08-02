'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { calculate, normalizeLoad, classifyBand } = require('./core.js');

const basic = calculate([
  { name: 'Modem', runningW: 25, startingW: 25, quantity: 1 },
  { name: 'LED', runningW: 100, startingW: 100, quantity: 1 }
], { reservePct: 20, powerFactor: 0.8, connection: 'appliances', phase: 'single' });
assert.equal(basic.runningW, 125);
assert.equal(basic.peakW, 125);
assert.equal(basic.recommendedRunningW, 200);
assert.equal(basic.recommendedStartingW, 200);
assert.equal(basic.approximateKva, 0.3);
assert.equal(basic.productRouteAllowed, true);
assert.equal(basic.band.key, 'compact');

const refrigerator = calculate([
  { name: 'Buzdolabı', runningW: 200, startingW: 1200, quantity: 1, motor: true },
  { name: 'Aydınlatma', runningW: 100, startingW: 100, quantity: 1 }
], { reservePct: 20, powerFactor: 0.8, startPolicy: 'largest', connection: 'appliances', phase: 'single' });
assert.equal(refrigerator.runningW, 300);
assert.equal(refrigerator.peakW, 1300);
assert.equal(refrigerator.recommendedRunningW, 400);
assert.equal(refrigerator.recommendedStartingW, 1600);
assert.equal(refrigerator.productRouteAllowed, true);

const simultaneous = calculate([
  { name: 'İki pompa', runningW: 750, startingW: 2250, quantity: 2, motor: true }
], { reservePct: 0, startPolicy: 'simultaneous', connection: 'appliances', phase: 'single' });
assert.equal(simultaneous.runningW, 1500);
assert.equal(simultaneous.surgeExtraW, 3000);
assert.equal(simultaneous.peakW, 4500);

const threePhase = calculate([
  { name: 'Yük', runningW: 1000, startingW: 1000, quantity: 1 }
], { connection: 'selected-circuits', phase: 'three' });
assert.equal(threePhase.productRouteAllowed, false);
assert.ok(threePhase.professionalReasons.some((item) => item.includes('transfer')));
assert.ok(threePhase.professionalReasons.some((item) => item.includes('faz')));

const medical = calculate([
  { name: 'Kritik cihaz', runningW: 300, startingW: 300, quantity: 1 }
], { connection: 'appliances', phase: 'single', medical: true });
assert.equal(medical.productRouteAllowed, false);
assert.ok(medical.warnings[0].includes('Tıbbi'));

assert.equal(classifyBand(2500).key, 'compact');
assert.equal(classifyBand(2501).key, 'medium');
assert.equal(classifyBand(7501).key, 'professional');
assert.throws(() => normalizeLoad({ name: 'Hatalı', runningW: 500, startingW: 200, quantity: 1 }, 0), /küçük olamaz/);
assert.throws(() => calculate([], {}), /En az bir/);

const repoRoot = path.resolve(__dirname, '../../..');
const html = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');
const hub = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const portal = fs.readFileSync(path.join(repoRoot, 'alo186', 'index.html'), 'utf8');
const manifest = fs.readFileSync(path.join(repoRoot, 'alo186', 'deployment', 'routing-manifest.json'), 'utf8');
const sitemap = fs.readFileSync(path.join(repoRoot, 'alo186', 'sitemap.xml'), 'utf8');
const catalog = require(path.join(repoRoot, 'alo186', 'urun-eslestirme', 'catalog.js'));

assert.match(html, /https:\/\/www\.alo186\.com\/hesaplama\/jenerator-gucu-secimi\//);
assert.match(html, /Satış ortaklığı açıklaması/);
assert.match(html, /sunucuya gönderilmez/);
assert.match(html, /Bu senaryoda ürün bağlantısı gösterilmiyor/);
assert.doesNotMatch(html, /amazon\.com\.tr/i);
assert.doesNotMatch(html, /type="(?:email|tel)"/i);
assert.doesNotMatch(html, /abone numarası|T\.C\.|açık adres/i);
assert.match(hub, /\.\/jenerator-gucu-secimi\//);
assert.match(portal, /href="\/hesaplama\/jenerator-gucu-secimi\//);
assert.doesNotMatch(portal, /href="\.\/hesaplama\/jenerator-gucu-secimi\//);
assert.match(manifest, /alo186\/hesaplama\/jenerator-gucu-secimi\/index\.html/);
assert.match(sitemap, /https:\/\/alo186\.com\/hesaplama\/jenerator-gucu-secimi\//);
assert.ok(catalog.getCategory('generator'));
assert.equal(catalog.getCategory('generator').mode, 'guide');
assert.equal(catalog.getCategory('generator').risk, 'safety');

console.log('Jeneratör güç seçimi: hesap, güvenlik, gizlilik, affiliate ve canonical yayın rotası testleri başarılı.');
