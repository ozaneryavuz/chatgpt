const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const vm = require('vm');
const { spawnSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..', '..');
const DIR = path.join(ROOT, 'alo186/hesaplama/buzdolabi-klima-voltaj-koruma-gecikmeli-priz-uygunluk');
const HTML = fs.readFileSync(path.join(DIR, 'index.html'), 'utf8');
const CSS = fs.readFileSync(path.join(DIR, 'styles.css'), 'utf8');
const JS = fs.readFileSync(path.join(DIR, 'app.js'), 'utf8');
const ROUTE = '/hesaplama/buzdolabi-klima-voltaj-koruma-gecikmeli-priz-uygunluk/';

const sandbox = { console, globalThis: {}, setTimeout, clearTimeout };
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.runInContext(JS, sandbox);
const api = sandbox.Alo186VoltageProtection;
assert(api, 'Alo186VoltageProtection API yok');

const base = {
  emergency: '', mode: 'planning', symptom: 'repeated_restart', scope: 'single',
  physicalCondition: 'good', earthStatus: 'verified', rcdStatus: 'tested',
  applianceType: 'fridge', connection: 'direct', voltage: 230, deviceW: 180, deviceA: 1.2,
  manualDelayMinutes: 5, manualEvidence: 'verified', measurementEvidence: 'verified_logger',
  measuredMinV: 180, measuredMaxV: 248, existingType: 'none', existingFunctions: 'unknown',
  existingRatedA: 0, existingDelayMinutes: 0, lowThresholdV: 190, highThresholdV: 250,
  existingEvidence: 'none', existingTest: 'not_tested'
};

const metrics = api.calculate(base);
assert.strictEqual(metrics.workingA, 1.2);
assert.strictEqual(metrics.requiredA, 1.5);
assert.strictEqual(metrics.standardA, 6);
assert.strictEqual(metrics.lowEventDetected, true);

const scenarios = [
  [{ ...base, emergency: 'yes' }, 'emergency'],
  [{ ...base, physicalCondition: 'hot' }, 'emergency'],
  [{ ...base, symptom: 'bright_dim' }, 'neutral_grid_risk'],
  [{ ...base, scope: 'building_area' }, 'neutral_grid_risk'],
  [{ ...base, applianceType: 'medical' }, 'medical_professional'],
  [{ ...base, applianceType: 'split_ac', connection: 'fixed' }, 'fixed_professional'],
  [{ ...base, connection: 'extension' }, 'unsafe_connection'],
  [{ ...base, earthStatus: 'failed' }, 'earth_rcd_failed'],
  [{ ...base, mode: 'active_outage' }, 'active_outage'],
  [{ ...base, measurementEvidence: 'unsafe_handheld' }, 'unsafe_measurement'],
  [{ ...base, deviceW: 0, deviceA: 0 }, 'load_evidence_missing'],
  [{ ...base, manualEvidence: 'unknown', manualDelayMinutes: 0 }, 'manual_delay_missing'],
  [{ ...base, deviceA: 12 }, 'high_current_professional'],
  [{ ...base, existingType: 'surge_only' }, 'surge_not_voltage'],
  [{ ...base, symptom: 'single_appliance_only', measurementEvidence: 'verified_normal' }, 'appliance_service'],
  [base, 'eligible_compare']
];
for (const [input, code] of scenarios) assert.strictEqual(api.decide(input).code, code);

const adequate = {
  ...base, existingType: 'plug_voltage', existingFunctions: 'under_over_delay', existingRatedA: 10,
  existingDelayMinutes: 5, existingEvidence: 'verified', existingTest: 'passed'
};
assert.strictEqual(api.decide(adequate).code, 'no_buy');
assert.strictEqual(api.decide({ ...adequate, existingRatedA: 1 }).code, 'current_shortfall');
assert.strictEqual(api.decide({ ...adequate, existingDelayMinutes: 2 }).code, 'delay_shortfall');
assert.strictEqual(api.decide({ ...adequate, existingEvidence: 'unknown' }).code, 'protector_evidence_missing');
assert.strictEqual(api.decide({ ...adequate, existingFunctions: 'under_over' }).code, 'functions_missing');
assert.strictEqual(api.decide({ ...adequate, existingTest: 'failed' }).code, 'test_missing');

for (const token of [
  '<form id="voltageForm"', 'aria-live="polite"', 'data-affiliate-check',
  'rel="sponsored nofollow noopener"', 'Kişisel veri yok', 'yeni ürün almayın',
  'Düşük + yüksek gerilim + yeniden bağlama gecikmesi',
  `https://alo186.com${ROUTE}`
]) assert((HTML + JS).includes(token), token);

for (const forbidden of [
  'localStorage', 'sessionStorage', 'navigator.geolocation', 'fetch(',
  'amazon.com', 'amazon.com.tr', '"@type":"Product"', '"@type":"Offer"',
  'aggregateRating', 'availability', 'name="email"', 'name="phone"', 'name="address"'
]) assert(!HTML.includes(forbidden) && !JS.includes(forbidden), forbidden);

for (const token of [
  '@media(max-width:900px)', '@media(max-width:620px)', 'min-height:48px',
  ':focus-visible', '@media(prefers-reduced-motion:reduce)', '@media(forced-colors:active)', '@media print'
]) assert(CSS.includes(token), token);

const overlay = JSON.parse(fs.readFileSync(path.join(ROOT, 'alo186/deployment/routing-overlays/132-compressor-voltage-protection.json'), 'utf8'));
assert.strictEqual(overlay.version, 132);
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
run(process.execPath, [path.join(DIR, 'test.js')]);

const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'alo186-voltage-v132-'));
const canonical = path.join(temp, 'canonical');
run('python', ['alo186/deployment/build_static_site.py', '--output', canonical, '--commit', 'voltage-v132-test']);

for (const [name, basePath] of [['custom', ''], ['project', '/chatgpt']]) {
  const target = path.join(temp, name);
  fs.cpSync(canonical, target, { recursive: true });
  run('python', [
    'alo186/deployment/prepare_github_pages.py', '--site', target, '--base-path', basePath,
    '--repository', 'ozaneryavuz/chatgpt', '--commit', 'voltage-v132-test'
  ]);
  run('python', ['alo186/deployment/inject_private_search.py', '--site', target, '--base-path', basePath]);
  run('python', ['alo186/deployment/smoke_github_pages.py', '--site', target, '--base-path', basePath]);

  const page = path.join(target, ROUTE.replace(/^\/|\/$/g, ''), 'index.html');
  assert(fs.existsSync(page), `${name} rota yok`);
  const published = fs.readFileSync(page, 'utf8');
  assert(published.includes('Voltaj Koruma'));
  assert(published.includes('rel="sponsored nofollow noopener"'));
  const sitemap = fs.readFileSync(path.join(target, 'sitemap.xml'), 'utf8');
  assert(sitemap.includes(`https://alo186.com${ROUTE}`) || sitemap.includes(`https://alo186.com${ROUTE}`));
  const searchIndex = fs.readFileSync(path.join(target, 'arama/search-index.json'), 'utf8');
  assert(searchIndex.includes(ROUTE));
}

console.log(JSON.stringify({
  ok: true,
  scenarios: 22,
  noBuy: true,
  emergencyAndNeutralClose: true,
  compressorDelayEvidence: true,
  affiliateGate: true,
  privacy: true,
  responsive: true,
  privateSearch: true,
  dualPages: true
}, null, 2));
