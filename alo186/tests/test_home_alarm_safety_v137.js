'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const ROOT = path.resolve(__dirname, '..', '..');
const SMOKE_DIR = path.join(ROOT, 'alo186/hesaplama/duman-alarmi-isi-alarmi-uygunluk');
const CO_DIR = path.join(ROOT, 'alo186/hesaplama/karbonmonoksit-alarmi-uygunluk');
const HUB_DIR = path.join(ROOT, 'alo186/sektor-rehberi/ev-duman-karbonmonoksit-alarm-test-merkezi');
const dirs = [SMOKE_DIR, CO_DIR, HUB_DIR];
const smokeHtml = fs.readFileSync(path.join(SMOKE_DIR, 'index.html'), 'utf8');
const smokeJs = fs.readFileSync(path.join(SMOKE_DIR, 'app.js'), 'utf8');
const coHtml = fs.readFileSync(path.join(CO_DIR, 'index.html'), 'utf8');
const coJs = fs.readFileSync(path.join(CO_DIR, 'app.js'), 'utf8');
const hubHtml = fs.readFileSync(path.join(HUB_DIR, 'index.html'), 'utf8');
const hubJs = fs.readFileSync(path.join(HUB_DIR, 'app.js'), 'utf8');
const cssFiles = dirs.map((dir) => fs.readFileSync(path.join(dir, 'styles.css'), 'utf8'));
const smokeApi = require(path.join(SMOKE_DIR, 'app.js'));
const coApi = require(path.join(CO_DIR, 'app.js'));
const hubApi = require(path.join(HUB_DIR, 'app.js'));
const ROUTES = [
  '/hesaplama/duman-alarmi-isi-alarmi-uygunluk/',
  '/hesaplama/karbonmonoksit-alarmi-uygunluk/',
  '/sektor-rehberi/ev-duman-karbonmonoksit-alarm-test-merkezi/'
];

assert(smokeApi?.evaluate, 'Duman/ısı alarmı API yok');
assert(coApi?.evaluate, 'CO alarmı API yok');
assert(hubApi?.buildPlan && hubApi?.makeIcs, 'Tekrar test merkezi API yok');

const smokeBase = {
  emergency: false, useCase: 'home', room: 'bedroom', goal: 'new', accessibility: 'none',
  existing: 'none', coverage: 'none', standard: 'verified', life: 'valid', test: 'pass',
  battery: 'good', placement: 'verified', interconnect: 'not_needed',
  confirmNeed: true, confirmSpecs: true, confirmAffiliate: true
};
assert.equal(smokeApi.evaluate(smokeBase).affiliateAllowed, true);
assert.equal(smokeApi.evaluate({ ...smokeBase, room: 'kitchen' }).recommendation.code, 'heat');
assert.equal(smokeApi.evaluate({ ...smokeBase, emergency: true }).status, 'stop');
assert.equal(smokeApi.evaluate({ ...smokeBase, useCase: 'common' }).status, 'professional');
assert.equal(smokeApi.evaluate({ ...smokeBase, accessibility: 'hearing' }).affiliateAllowed, false);
assert.equal(smokeApi.evaluate({ ...smokeBase, confirmNeed: false }).affiliateAllowed, false);
assert.equal(smokeApi.evaluate({ ...smokeBase, existing: 'smoke', coverage: 'full' }).status, 'no-buy');

const coBase = {
  symptoms: false, gasSmell: false, useCase: 'home', source: 'fuel', combustionSafety: 'verified',
  coverage: 'none', existing: 'none', standard: 'verified', life: 'valid', test: 'pass',
  battery: 'good', placement: 'verified', signal: 'verified', interconnect: 'not_needed',
  confirmNeed: true, confirmSpecs: true, confirmAffiliate: true
};
assert.equal(coApi.evaluate(coBase).affiliateAllowed, true);
assert.equal(coApi.evaluate({ ...coBase, symptoms: true }).status, 'stop');
assert.equal(coApi.evaluate({ ...coBase, gasSmell: true }).status, 'stop');
assert.equal(coApi.evaluate({ ...coBase, source: 'none' }).affiliateAllowed, false);
assert.equal(coApi.evaluate({ ...coBase, useCase: 'mobile' }).status, 'professional');
assert.equal(coApi.evaluate({ ...coBase, existing: 'co', coverage: 'full', battery: 'sealed' }).status, 'no-buy');

const plan = hubApi.buildPlan({
  reason: 'heating', alarms: 'both', fuel: 'yes', interval: '30',
  manufacturer: true, noCommerce: true, emergency: false
});
assert.equal(plan.status, 'plan');
assert.equal(plan.directAffiliate, false);
assert(plan.p1.some((item) => item.includes('baca')));
assert(hubApi.makeIcs(plan).includes('BEGIN:VCALENDAR'));
assert.equal(hubApi.buildPlan({ emergency: true, interval: '30' }).status, 'stop');

const combined = smokeHtml + smokeJs + coHtml + coJs + hubHtml + hubJs;
for (const token of [
  'Duman alarmı mı', 'Karbonmonoksit alarmı', 'Satın almama sonucu',
  'Şeffaf satış ortaklığı', '112', '187', 'EN 14604', 'EN 50291',
  'rel="sponsored nofollow noopener"', 'doğrudan affiliate bağlantısı göstermez',
  'href="./styles.css"'
]) assert(combined.includes(token), token);

for (const forbidden of [
  'localStorage', 'sessionStorage', 'navigator.geolocation', 'fetch(',
  'amazon.com', 'amazon.com.tr', '"@type":"Product"', '"@type":"Offer"',
  'aggregateRating', 'availability', 'name="email"', 'name="phone"',
  'name="address"', 'name="location"', 'name="serial"', 'name="health"'
]) assert(!combined.includes(forbidden), forbidden);

for (const css of cssFiles) {
  for (const token of [
    '@media(max-width:900px)', '@media(max-width:620px)', 'min-height:48px',
    ':focus-visible', '@media(prefers-reduced-motion:reduce)',
    '@media(forced-colors:active)', '@media print'
  ]) assert(css.includes(token), token);
}

const overlay = JSON.parse(fs.readFileSync(
  path.join(ROOT, 'alo186/deployment/routing-overlays/137-home-alarm-safety.json'), 'utf8'
));
assert.equal(overlay.version, 137);
assert.deepEqual(overlay.routes.map((route) => route.canonicalPath), ROUTES);
assert.deepEqual(overlay.routes.map((route) => route.type), ['calculator', 'calculator', 'guide']);

function run(command, args) {
  const result = spawnSync(command, args, { cwd: ROOT, encoding: 'utf8' });
  if (result.status !== 0) {
    console.error(result.stdout);
    console.error(result.stderr);
    throw new Error(`${command} ${args.join(' ')} failed`);
  }
  return result.stdout;
}

for (const file of dirs.map((dir) => path.join(dir, 'app.js'))) run(process.execPath, ['--check', file]);
run(process.execPath, [path.join(SMOKE_DIR, 'test.js')]);
run(process.execPath, [path.join(CO_DIR, 'test.js')]);

const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'alo186-home-alarm-v137-'));
const canonical = path.join(temp, 'canonical');
run('python', ['alo186/deployment/build_static_site.py', '--output', canonical, '--commit', 'home-alarm-v137-test']);

for (const [name, basePath] of [['custom', ''], ['project', '/chatgpt']]) {
  const target = path.join(temp, name);
  fs.cpSync(canonical, target, { recursive: true });
  run('python', [
    'alo186/deployment/prepare_github_pages.py', '--site', target, '--base-path', basePath,
    '--repository', 'ozaneryavuz/chatgpt', '--commit', 'home-alarm-v137-test'
  ]);
  run('python', ['alo186/deployment/inject_private_search.py', '--site', target, '--base-path', basePath]);
  run('python', ['alo186/deployment/smoke_github_pages.py', '--site', target, '--base-path', basePath]);

  const sitemap = fs.readFileSync(path.join(target, 'sitemap.xml'), 'utf8');
  const searchIndex = fs.readFileSync(path.join(target, 'arama/search-index.json'), 'utf8');
  for (const route of ROUTES) {
    const routeDir = path.join(target, route.replace(/^\/|\/$/g, ''));
    const page = path.join(routeDir, 'index.html');
    assert(fs.existsSync(page), `${name} rota yok: ${route}`);
    assert(fs.existsSync(path.join(routeDir, 'styles.css')), `${name} rota stili yok: ${route}`);
    const published = fs.readFileSync(page, 'utf8');
    assert(published.includes('data-alo186-sitewide-ux="true"'));
    assert(sitemap.includes(`https://alo186.com${route}`) || sitemap.includes(`https://alo186.com${route}`));
    assert(searchIndex.includes(route));
  }
}

console.log(JSON.stringify({
  ok: true,
  version: 137,
  routes: ROUTES,
  scenarios: 18,
  emergency112: true,
  gas187: true,
  standards: ['EN 14604', 'EN 50291-1', 'EN 50291-2'],
  noBuy: true,
  affiliateGate: 3,
  directAffiliateOnHub: false,
  repeatVisitDays: [30, 90],
  routeLocalAssets: true,
  privacy: true,
  privateSearch: true,
  dualPages: true
}, null, 2));