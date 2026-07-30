'use strict';

const assert = require('assert');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
const route = '/hesaplama/yuksek-guclu-ev-aleti-power-station-uygunluk/';
const center = fs.readFileSync(path.join(ROOT, 'alo186', 'hesaplama', 'index.html'), 'utf8');
const moduleHtml = fs.readFileSync(path.join(ROOT, 'alo186', 'hesaplama', 'yuksek-guclu-ev-aleti-power-station-uygunluk', 'index.html'), 'utf8');
const overlay = JSON.parse(fs.readFileSync(path.join(ROOT, 'alo186', 'deployment', 'routing-overlays', '122-high-power-appliance-power-station.json'), 'utf8'));

assert(center.includes('./yuksek-guclu-ev-aleti-power-station-uygunluk/'));
assert(center.includes('Yüksek Güçlü Ev Aleti Power Station Uygunluğu'));
assert(center.includes('47 çekirdek araç'));
assert.strictEqual((center.match(/yuksek-guclu-ev-aleti-power-station-uygunluk/g) || []).length, 1);
assert(moduleHtml.includes(`https://alo186.com${route}`));
assert.strictEqual(overlay.routes[0].canonicalPath, route);
assert.strictEqual(overlay.routes[0].source, 'alo186/hesaplama/yuksek-guclu-ev-aleti-power-station-uygunluk/index.html');

console.log(JSON.stringify({
  ok: true,
  calculationCenter: true,
  visibleToolCount: 47,
  canonicalRoute: route,
}));
