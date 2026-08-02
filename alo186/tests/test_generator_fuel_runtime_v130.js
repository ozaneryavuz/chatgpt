const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const vm = require('vm');
const { spawnSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..', '..');
const DIR = path.join(ROOT, 'alo186/hesaplama/jenerator-yakit-tuketimi-calisma-suresi');
const HTML = fs.readFileSync(path.join(DIR, 'index.html'), 'utf8');
const CSS = fs.readFileSync(path.join(DIR, 'styles.css'), 'utf8');
const JS = fs.readFileSync(path.join(DIR, 'app.js'), 'utf8');
const HUB = fs.readFileSync(path.join(ROOT, 'alo186/hesaplama/index.html'), 'utf8');
const ROUTE = '/hesaplama/jenerator-yakit-tuketimi-calisma-suresi/';

const sandbox = { console, globalThis: {}, setTimeout, clearTimeout };
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.runInContext(JS, sandbox);
const api = sandbox.Alo186GeneratorFuel;
assert(api, 'Alo186GeneratorFuel API yok');

const base = {
  emergency: '',
  coStatus: 'none',
  location: 'outdoors_clear',
  mode: 'planning',
  generatorType: 'portable',
  fuelType: 'diesel',
  connection: 'individual',
  continuousKW: 5,
  loadKW: 2.5,
  tankLiters: 20,
  usablePct: 90,
  targetHours: 6,
  fuelPrice: 50,
  fuel25: 0.8,
  fuel50: 1.2,
  fuel75: 1.7,
  fuel100: 2.3,
  curveEvidence: 'manufacturer',
  existing: 'yes',
  maintenance: 'yes',
  transferTest: 'yes',
  coAlarm: 'yes',
  fuelStorage: 'safe'
};

let metrics = api.calculate(base);
assert.strictEqual(metrics.loadPct, 50);
assert.strictEqual(metrics.fuelRate, 1.2);
assert.strictEqual(metrics.usableFuelL, 18);
assert.strictEqual(metrics.runtimeHours, 15);
assert.strictEqual(metrics.requiredFuelL, 7.2);
assert.strictEqual(metrics.estimatedCost, 360);

metrics = api.calculate({ ...base, loadKW: 3 });
assert.strictEqual(metrics.loadPct, 60);
assert.strictEqual(metrics.fuelRate, 1.4);
assert.strictEqual(metrics.fuelMethod, 'linear_interpolation');

assert.strictEqual(api.interpolateFuelRate(50, [{ pct: 50, rate: 1.2 }]).rate, 1.2);
assert.strictEqual(api.interpolateFuelRate(70, [{ pct: 50, rate: 1.2 }]).rate, null);
assert.strictEqual(api.interpolateFuelRate(10, [{ pct: 25, rate: 0.8 }, { pct: 50, rate: 1.2 }]).method, 'conservative_low');

assert.strictEqual(api.decide({ ...base, emergency: 'yes' }).code, 'emergency');
assert.strictEqual(api.decide({ ...base, coStatus: 'alarm' }).code, 'emergency');
assert.strictEqual(api.decide({ ...base, location: 'garage' }).code, 'unsafe_location');
assert.strictEqual(api.decide({ ...base, connection: 'backfeed' }).code, 'backfeed');
assert.strictEqual(api.decide({ ...base, fuelType: 'lpg_ng' }).code, 'gas_fuel_specialist');
assert.strictEqual(api.decide({ ...base, loadKW: 6 }).code, 'overload');
assert.strictEqual(api.decide({ ...base, mode: 'active', existing: 'no' }).code, 'active_no_generator');
assert.strictEqual(api.decide({ ...base, curveEvidence: 'none' }).code, 'fuel_curve_missing');
assert.strictEqual(api.decide({ ...base, fuel25: '', fuel50: '', fuel75: '', fuel100: '' }).code, 'fuel_curve_missing');
assert.strictEqual(api.decide({ ...base, loadKW: 0.5 }).code, 'very_low_load');
assert.strictEqual(api.decide({ ...base, coAlarm: 'no' }).code, 'co_alarm_missing');
assert.strictEqual(api.decide({ ...base, connection: 'unknown' }).code, 'connection_unknown');
assert.strictEqual(api.decide({ ...base, maintenance: 'no' }).code, 'maintenance_failed');
assert.strictEqual(api.decide(base).code, 'no_buy');
assert.strictEqual(api.decide({ ...base, tankLiters: 5, targetHours: 10 }).code, 'runtime_shortfall');
assert.strictEqual(api.decide({ ...base, existing: 'no', transferTest: 'unknown' }).code, 'portable_planning');
assert.strictEqual(api.decide({ ...base, generatorType: 'fixed', connection: 'unknown' }).code, 'fixed_professional');
assert.strictEqual(api.decide({ ...base, fuelStorage: 'unsafe' }).code, 'unsafe_fuel_storage');

const payload = api.summaryPayload(base, api.decide(base));
assert.strictEqual(payload.privacy, 'Kişisel veri içermez; tarayıcıda oluşturulur.');
assert.strictEqual(payload.decision.code, 'no_buy');
assert(api.icsText().includes('BEGIN:VCALENDAR'));

for (const token of [
  '<form id="generatorForm"',
  'aria-live="polite"',
  'data-affiliate-check',
  'rel="sponsored nofollow noopener"',
  'Kişisel veri yok',
  'Karbonmonoksit',
  'https://alo186.com/hesaplama/jenerator-yakit-tuketimi-calisma-suresi/'
]) assert(HTML.includes(token), token);

assert(/yeni ürün almayın/i.test(HTML + JS));
assert(/çalışan veya sıcak jeneratöre yakıt eklemeyin/i.test(HTML + JS));
assert(HUB.includes('./jenerator-yakit-tuketimi-calisma-suresi/'));
assert(HUB.includes('49 çekirdek araç'));
assert.strictEqual((HUB.match(/class="tool-card"/g) || []).length, 49);

for (const forbidden of [
  'localStorage',
  'sessionStorage',
  'navigator.geolocation',
  'fetch(',
  'amazon.com',
  'amazon.com.tr',
  '"@type":"Product"',
  '"@type":"Offer"',
  'aggregateRating',
  'availability'
]) assert(!HTML.includes(forbidden) && !JS.includes(forbidden), forbidden);

for (const token of [
  '@media(max-width:900px)',
  '@media(max-width:620px)',
  'min-height:48px',
  ':focus-visible',
  '@media(prefers-reduced-motion:reduce)',
  '@media(forced-colors:active)',
  '@media print'
]) assert(CSS.includes(token), token);

const overlayPath = path.join(ROOT, 'alo186/deployment/routing-overlays/130-generator-fuel-runtime.json');
const overlay = JSON.parse(fs.readFileSync(overlayPath, 'utf8'));
assert.strictEqual(overlay.version, 130);
assert.strictEqual(overlay.routes[0].canonicalPath, ROUTE);

function run(command, args) {
  const result = spawnSync(command, args, { cwd: ROOT, encoding: 'utf8' });
  if (result.status !== 0) {
    console.error(result.stdout);
    console.error(result.stderr);
    throw new Error(`${command} ${args.join(' ')} failed`);
  }
  return result.stdout;
}

run(process.execPath, ['--check', path.join(DIR, 'app.js')]);

const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'alo186-generator-v130-'));
const canonical = path.join(temp, 'canonical');
run('python', ['alo186/deployment/build_static_site.py', '--output', canonical, '--commit', 'generator-v130-test']);

for (const [name, basePath] of [['custom', ''], ['project', '/chatgpt']]) {
  const target = path.join(temp, name);
  fs.cpSync(canonical, target, { recursive: true });
  run('python', [
    'alo186/deployment/prepare_github_pages.py',
    '--site', target,
    '--base-path', basePath,
    '--repository', 'ozaneryavuz/chatgpt',
    '--commit', 'generator-v130-test'
  ]);
  run('python', [
    'alo186/deployment/inject_private_search.py',
    '--site', target,
    '--base-path', basePath
  ]);
  run('python', ['alo186/deployment/smoke_github_pages.py', '--site', target, '--base-path', basePath]);

  const page = path.join(target, ROUTE.replace(/^\/|\/$/g, ''), 'index.html');
  assert(fs.existsSync(page), `${name} rota yok`);
  const published = fs.readFileSync(page, 'utf8');
  assert(published.includes('Jeneratör Yakıt Tüketimi'));
  const sitemap = fs.readFileSync(path.join(target, 'sitemap.xml'), 'utf8');
  assert(sitemap.includes(`https://alo186.com${ROUTE}`) || sitemap.includes(`https://alo186.com${ROUTE}`));
  const searchIndex = fs.readFileSync(path.join(target, 'arama/search-index.json'), 'utf8');
  assert(searchIndex.includes(ROUTE));
}

console.log(JSON.stringify({
  ok: true,
  scenarios: 19,
  interpolation: true,
  noBuy: true,
  emergencyClose: true,
  coAndBackfeedClose: true,
  affiliateGate: true,
  privacy: true,
  responsive: true,
  catalogTools: 49,
  privateSearch: true,
  dualPages: true
}, null, 2));
