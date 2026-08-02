const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const vm = require('vm');
const { spawnSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..', '..');
const DIR = path.join(ROOT, 'alo186/hesaplama/klima-btu-elektrik-altyapi-uygunluk');
const HTML = fs.readFileSync(path.join(DIR, 'index.html'), 'utf8');
const CSS = fs.readFileSync(path.join(DIR, 'styles.css'), 'utf8');
const JS = fs.readFileSync(path.join(DIR, 'app.js'), 'utf8');
const ROUTE = '/hesaplama/klima-btu-elektrik-altyapi-uygunluk/';

const sandbox = { console, globalThis: {}, setTimeout, clearTimeout };
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.runInContext(JS, sandbox);
const api = sandbox.Alo186AirConditionerSizing;
assert(api, 'Alo186AirConditionerSizing API yok');

const base = {
  emergency: '', mode: 'planning', symptom: 'none', scope: 'single_room', useCase: 'home_room',
  physicalCondition: 'good', areaM2: 25, ceilingM: 2.7, sun: 'normal', climate: 'hot',
  insulation: 'average', people: 2, kitchen: 'no', electronicsW: 0,
  unitType: 'split', existingUnit: 'no', candidateBtu: 9000, candidateInputW: 950,
  candidateRatedA: 4.5, voltage: 230, manualEvidence: 'verified', requiredBreakerA: 16,
  circuitBreakerA: 16, dedicatedCircuit: 'yes', earthStatus: 'verified', rcdStatus: 'tested',
  connection: 'fixed', realPerformanceTest: 'not_tested', comfortResult: 'unknown',
  confirmNeed: 'yes', confirmEvidence: 'yes', confirmAffiliate: 'yes'
};

const metrics = api.calculate(base);
assert.strictEqual(metrics.valid, true);
assert.strictEqual(metrics.recommendedBtu, 9000);
assert.strictEqual(metrics.workingA, 4.5);
assert.strictEqual(api.decide(base).code, 'eligible_compare');
assert.strictEqual(api.decide(base).commerce, true);

const scenarios = [
  [{ ...base, emergency: 'yes' }, 'danger'],
  [{ ...base, physicalCondition: 'burned' }, 'danger'],
  [{ ...base, symptom: 'bright_dim' }, 'grid_risk'],
  [{ ...base, mode: 'active_outage' }, 'active_outage'],
  [{ ...base, useCase: 'commercial' }, 'professional'],
  [{ ...base, connection: 'power_strip' }, 'unsafe_connection'],
  [{ ...base, earthStatus: 'unknown' }, 'electrical_evidence_missing'],
  [{ ...base, dedicatedCircuit: 'no' }, 'dedicated_circuit_missing'],
  [{ ...base, manualEvidence: 'unknown' }, 'manual_missing'],
  [{ ...base, requiredBreakerA: 20, circuitBreakerA: 16 }, 'circuit_mismatch'],
  [{ ...base, candidateBtu: 5000 }, 'undersized'],
  [{ ...base, candidateBtu: 18000 }, 'oversized']
];
for (const [input, code] of scenarios) assert.strictEqual(api.decide(input).code, code, code);

const adequate = {
  ...base, existingUnit: 'yes', realPerformanceTest: 'passed', comfortResult: 'good'
};
assert.strictEqual(api.decide(adequate).code, 'no_buy');
assert.strictEqual(api.decide({ ...adequate, realPerformanceTest: 'failed' }).code, 'service_first');
assert.strictEqual(api.decide({ ...base, confirmAffiliate: '' }).commerce, false);

for (const token of [
  '<form id="airForm"', 'aria-live="polite"', 'data-affiliate-check',
  'rel="sponsored nofollow noopener"', 'Kişisel veri yok', 'yeni ürün almayın',
  'BTU ile elektrik gücünü karıştırmayın', 'ENERGY STAR',
  `https://alo186.com${ROUTE}`
]) assert((HTML + JS).includes(token), token);

for (const forbidden of [
  'localStorage', 'sessionStorage', 'navigator.geolocation', 'fetch(',
  'amazon.com', 'amazon.com.tr', '"@type":"Product"', '"@type":"Offer"',
  'aggregateRating', 'availability', 'name="email"', 'name="phone"', 'name="address"',
  'name="location"', 'name="serial"'
]) assert(!HTML.includes(forbidden) && !JS.includes(forbidden), forbidden);

for (const token of [
  '@media(max-width:900px)', '@media(max-width:620px)', 'min-height:48px',
  ':focus-visible', '@media(prefers-reduced-motion:reduce)',
  '@media(forced-colors:active)', '@media print'
]) assert(CSS.includes(token), token);

const overlay = JSON.parse(fs.readFileSync(
  path.join(ROOT, 'alo186/deployment/routing-overlays/134-klima-btu-elektrik-altyapi.json'), 'utf8'
));
assert.strictEqual(overlay.version, 134);
assert.strictEqual(overlay.routes[0].canonicalPath, ROUTE);
assert.strictEqual(overlay.routes[0].type, 'calculator');

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
run(process.execPath, [path.join(DIR, 'test.js')]);

const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'alo186-air-v134-'));
const canonical = path.join(temp, 'canonical');
run('python', ['alo186/deployment/build_static_site.py', '--output', canonical, '--commit', 'air-v134-test']);

for (const [name, basePath] of [['custom', ''], ['project', '/chatgpt']]) {
  const target = path.join(temp, name);
  fs.cpSync(canonical, target, { recursive: true });
  run('python', [
    'alo186/deployment/prepare_github_pages.py', '--site', target, '--base-path', basePath,
    '--repository', 'ozaneryavuz/chatgpt', '--commit', 'air-v134-test'
  ]);
  run('python', ['alo186/deployment/inject_private_search.py', '--site', target, '--base-path', basePath]);
  run('python', ['alo186/deployment/smoke_github_pages.py', '--site', target, '--base-path', basePath]);

  const page = path.join(target, ROUTE.replace(/^\/|\/$/g, ''), 'index.html');
  assert(fs.existsSync(page), `${name} rota yok`);
  const published = fs.readFileSync(page, 'utf8');
  assert(published.includes('Klima BTU ve Elektrik Altyapısı'));
  assert(published.includes('rel="sponsored nofollow noopener"'));
  assert(published.includes('data-alo186-sitewide-ux="true"'));
  const sitemap = fs.readFileSync(path.join(target, 'sitemap.xml'), 'utf8');
  assert(sitemap.includes(`https://alo186.com${ROUTE}`) || sitemap.includes(`https://alo186.com${ROUTE}`));
  const searchIndex = fs.readFileSync(path.join(target, 'arama/search-index.json'), 'utf8');
  assert(searchIndex.includes(ROUTE));
}

console.log(JSON.stringify({
  ok: true,
  scenarios: scenarios.length + 5,
  capacityAndElectricalDecision: true,
  noBuy: true,
  emergencyAndGridClose: true,
  affiliateGate: true,
  privacy: true,
  responsive: true,
  privateSearch: true,
  dualPages: true
}, null, 2));
