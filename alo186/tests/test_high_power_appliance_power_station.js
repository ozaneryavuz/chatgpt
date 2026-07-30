'use strict';

const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..', '..');
const moduleDir = path.join(ROOT, 'alo186', 'hesaplama', 'yuksek-guclu-ev-aleti-power-station-uygunluk');
const app = require(path.join(moduleDir, 'app.js'));
const html = fs.readFileSync(path.join(moduleDir, 'index.html'), 'utf8');
const css = fs.readFileSync(path.join(moduleDir, 'styles.css'), 'utf8');
const js = fs.readFileSync(path.join(moduleDir, 'app.js'), 'utf8');
const overlay = JSON.parse(fs.readFileSync(path.join(ROOT, 'alo186', 'deployment', 'routing-overlays', '122-high-power-appliance-power-station.json'), 'utf8'));

function base(overrides = {}) {
  return {
    emergency: false,
    scenario: 'planning',
    applianceType: 'kettle',
    connection: 'direct',
    supervised: 'yes',
    powerEvidence: 'input',
    labelW: '2000',
    explicitSurgeW: '',
    cycleMinutes: '5',
    cycleCount: '2',
    otherW: '0',
    sourceStatus: 'none',
    sourceType: 'auto',
    sourceContinuousW: '',
    sourceSurgeW: '',
    sourceWh: '',
    waveform: 'unknown',
    outputSpec: 'unknown',
    directOutput: 'unknown',
    loadTest: 'untested',
    ...overrides,
  };
}

const kettle = app.calculations(base());
assert.strictEqual(kettle.totalRunningW, 2000);
assert.strictEqual(kettle.requiredContinuousW, 2300);
assert.strictEqual(kettle.totalMinutes, 10);
assert(kettle.requiredWh >= 489 && kettle.requiredWh <= 491, kettle);
assert(kettle.requiredSurgeW > 2400);

let result = app.evaluate(base({ emergency: true }));
assert.strictEqual(result.status, 'emergency');
assert.strictEqual(result.commerceClosed, true);

result = app.evaluate(base({ applianceType: 'microwave', powerEvidence: 'microwave_output', labelW: '800' }));
assert.strictEqual(result.status, 'evidence_required');
assert.match(result.title, /giriş watt/i);

result = app.evaluate(base({ applianceType: 'fixed_high_power', connection: 'fixed', labelW: '3000' }));
assert.strictEqual(result.status, 'professional');
assert.strictEqual(result.commerceClosed, true);

result = app.evaluate(base({ connection: 'extension' }));
assert.strictEqual(result.status, 'stop');
assert(result.toolKeys.includes('extension'));

result = app.evaluate(base({ supervised: 'no' }));
assert.strictEqual(result.status, 'stop');

result = app.evaluate(base({ scenario: 'active' }));
assert.strictEqual(result.status, 'active_event');
assert.strictEqual(result.commerceClosed, true);

result = app.evaluate(base({
  scenario: 'existing',
  sourceStatus: 'existing',
  sourceType: 'power_station',
  sourceContinuousW: '2600',
  sourceSurgeW: '5000',
  sourceWh: '1200',
  waveform: 'pure',
  outputSpec: 'confirmed',
  directOutput: 'yes',
  loadTest: 'success',
}));
assert.strictEqual(result.status, 'no_buy');
assert.match(result.title, /yeni ürün almayın/i);
assert.strictEqual(result.commerceClosed, true);

result = app.evaluate(base({
  scenario: 'existing',
  sourceStatus: 'existing',
  sourceType: 'power_station',
  sourceContinuousW: '2600',
  sourceSurgeW: '5000',
  sourceWh: '1200',
  waveform: 'unknown',
  outputSpec: 'confirmed',
  directOutput: 'yes',
  loadTest: 'success',
}));
assert.strictEqual(result.status, 'evidence_required');
assert(result.issues.some(item => /Saf sinüs/.test(item)));

result = app.evaluate(base({
  applianceType: 'airfryer',
  labelW: '1500',
  cycleMinutes: '20',
  cycleCount: '1',
}));
assert.strictEqual(result.status, 'conditional_purchase');
assert.deepStrictEqual(result.commerceCategories, ['power_station']);
assert.strictEqual(result.commerceClosed, false);

result = app.evaluate(base({
  applianceType: 'vacuum',
  labelW: '2200',
  cycleMinutes: '30',
  sourceType: 'generator',
}));
assert.strictEqual(result.status, 'conditional_purchase');
assert.deepStrictEqual(result.commerceCategories, ['generator']);

result = app.evaluate(base({ labelW: '2600', otherW: '500' }));
assert.strictEqual(result.status, 'professional');

assert.strictEqual(app.gateReady(true, true, true), true);
assert.strictEqual(app.gateReady(true, true, false), false);

for (const token of [
  '<form id="applianceForm"',
  'aria-live="polite"',
  'Kişisel veri yok',
  'Satın almama sonucu',
  'Mikrodalganın pişirme veya output wattını',
  'rel="canonical"',
  'FAQPage',
  'BreadcrumbList',
]) assert(html.includes(token), token);

for (const forbidden of [
  'localStorage',
  'sessionStorage',
  'navigator.geolocation',
  'amazon.com',
  'amazon.com.tr',
  'Product"',
  'Offer"',
  'priceCurrency',
  'aggregateRating',
]) assert(!html.includes(forbidden), forbidden);

for (const forbidden of ['localStorage', 'sessionStorage', 'geolocation', 'fetch(']) assert(!js.includes(forbidden), forbidden);
for (const token of ['sponsored nofollow noopener', 'affiliate_category_gate_open']) assert(js.includes(token), token);
for (const token of ['@media(max-width:820px)', '@media(max-width:560px)', 'min-height:48px', 'prefers-reduced-motion', 'forced-colors']) assert(css.includes(token), token);

assert.strictEqual(overlay.version, 122);
assert.strictEqual(overlay.routes.length, 1);
assert.strictEqual(overlay.routes[0].canonicalPath, app.ROUTE);
assert.strictEqual(overlay.routes[0].type, 'calculator');

const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'alo186-high-power-'));
const canonical = path.join(temp, 'canonical');
execFileSync('python', [
  path.join(ROOT, 'alo186', 'deployment', 'build_static_site.py'),
  '--output', canonical,
  '--commit', 'high-power-test',
], { cwd: ROOT, stdio: 'pipe' });

const routeFile = path.join(canonical, 'hesaplama', 'yuksek-guclu-ev-aleti-power-station-uygunluk', 'index.html');
assert(fs.existsSync(routeFile));
assert(fs.readFileSync(routeFile, 'utf8').includes('https://alo186.com/hesaplama/yuksek-guclu-ev-aleti-power-station-uygunluk/'));
assert(fs.readFileSync(path.join(canonical, 'sitemap.xml'), 'utf8').includes('/hesaplama/yuksek-guclu-ev-aleti-power-station-uygunluk/'));

for (const basePath of ['', '/chatgpt']) {
  const target = path.join(temp, basePath ? 'project' : 'custom');
  fs.cpSync(canonical, target, { recursive: true });
  execFileSync('python', [
    path.join(ROOT, 'alo186', 'deployment', 'prepare_github_pages.py'),
    '--site', target,
    '--base-path', basePath,
    '--repository', 'ozaneryavuz/chatgpt',
    '--commit', 'high-power-test',
  ], { cwd: ROOT, stdio: 'pipe' });
  execFileSync('python', [
    path.join(ROOT, 'alo186', 'deployment', 'smoke_github_pages.py'),
    '--site', target,
    '--base-path', basePath,
  ], { cwd: ROOT, stdio: 'pipe' });
  const page = fs.readFileSync(path.join(target, 'hesaplama', 'yuksek-guclu-ev-aleti-power-station-uygunluk', 'index.html'), 'utf8');
  const expectedAsset = `${basePath}/assets/alo186-ux.js` || '/assets/alo186-ux.js';
  assert(page.includes(expectedAsset), { basePath, expectedAsset });
}

fs.rmSync(temp, { recursive: true, force: true });
console.log(JSON.stringify({
  ok: true,
  scenarios: 12,
  route: app.ROUTE,
  mobile: true,
  accessible: true,
  personalData: false,
  affiliateGate: true,
  noBuyOutcome: true,
  customDomain: true,
  projectPath: true,
}));
