'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const ROOT = path.resolve(__dirname, '..', '..');
const LEAK_DIR = path.join(ROOT, 'alo186/hesaplama/su-kacagi-sensoru-otomatik-vana-uygunluk');
const COLD_DIR = path.join(ROOT, 'alo186/hesaplama/buzdolabi-dondurucu-sicaklik-alarmi-uygunluk');
const HUB_DIR = path.join(ROOT, 'alo186/sektor-rehberi/tatil-yazlik-ev-elektrik-su-guvenlik-merkezi');
const dirs = [LEAK_DIR, COLD_DIR, HUB_DIR];
const leakHtml = fs.readFileSync(path.join(LEAK_DIR, 'index.html'), 'utf8');
const leakJs = fs.readFileSync(path.join(LEAK_DIR, 'app.js'), 'utf8');
const coldHtml = fs.readFileSync(path.join(COLD_DIR, 'index.html'), 'utf8');
const coldJs = fs.readFileSync(path.join(COLD_DIR, 'app.js'), 'utf8');
const hubHtml = fs.readFileSync(path.join(HUB_DIR, 'index.html'), 'utf8');
const hubJs = fs.readFileSync(path.join(HUB_DIR, 'app.js'), 'utf8');
const cssFiles = dirs.map((dir) => fs.readFileSync(path.join(dir, 'styles.css'), 'utf8'));
const leakApi = require(path.join(LEAK_DIR, 'app.js'));
const coldApi = require(path.join(COLD_DIR, 'app.js'));
const hubApi = require(path.join(HUB_DIR, 'app.js'));
const ROUTES = [
  '/hesaplama/su-kacagi-sensoru-otomatik-vana-uygunluk/',
  '/hesaplama/buzdolabi-dondurucu-sicaklik-alarmi-uygunluk/',
  '/sektor-rehberi/tatil-yazlik-ev-elektrik-su-guvenlik-merkezi/'
];

assert(leakApi?.evaluate, 'Su kaçağı API yok');
assert(coldApi?.evaluate, 'Sıcaklık alarmı API yok');
assert(hubApi?.buildPlan && hubApi?.makeIcs, 'Tatil/yazlık merkez API yok');

const leakBase = {
  emergency: false, useCase: 'home', source: 'washer', goal: 'alert', offline: 'local',
  existing: 'none', coverage: 'none', test: 'pass', power: 'good', placement: 'verified',
  notification: 'local', valve: 'not_needed', shutoffTest: 'not_needed',
  confirmNeed: true, confirmSpecs: true, confirmAffiliate: true
};
assert.equal(leakApi.evaluate(leakBase).affiliateAllowed, true);
assert.equal(leakApi.evaluate({ ...leakBase, emergency: true }).status, 'stop');
assert.equal(leakApi.evaluate({ ...leakBase, useCase: 'commercial' }).status, 'professional');
assert.equal(leakApi.evaluate({ ...leakBase, goal: 'shutoff', source: 'whole_home', valve: 'unknown' }).status, 'professional');
assert.equal(leakApi.evaluate({ ...leakBase, confirmNeed: false }).affiliateAllowed, false);
assert.equal(leakApi.evaluate({ ...leakBase, existing: 'point', coverage: 'full' }).status, 'no-buy');

const coldBase = {
  activeOutage: false, useCase: 'home', appliance: 'fridge', goal: 'check', outageKnowledge: 'none',
  fridgeTemp: 'safe', freezerTemp: 'not_applicable', existing: 'none', validation: 'pass',
  alarmTest: 'not_needed', memory: 'not_needed', power: 'good', placement: 'verified',
  remote: 'not_needed', realTest: 'pass', confirmNeed: true, confirmSpecs: true, confirmAffiliate: true
};
assert.equal(coldApi.evaluate(coldBase).affiliateAllowed, true);
assert.equal(coldApi.evaluate({ ...coldBase, activeOutage: true }).status, 'stop');
assert.equal(coldApi.evaluate({ ...coldBase, useCase: 'medical' }).status, 'professional');
assert.equal(coldApi.evaluate({ ...coldBase, goal: 'remote', remote: 'pass', memory: 'pass' }).recommendation.code, 'remote-temperature-alarm');
assert.equal(coldApi.evaluate({ ...coldBase, confirmAffiliate: false }).affiliateAllowed, false);
assert.equal(coldApi.evaluate({ ...coldBase, existing: 'thermometer' }).status, 'no-buy');

const plan = hubApi.buildPlan({
  emergency: false, reason: 'departure', property: 'second_home', absence: 'month', interval: '30',
  cold: 'on_unknown', water: 'on_unknown', alarms: 'partial', electrical: 'unknown',
  remote: 'unknown', visit: 'none', manufacturer: true, official: true, noCommerce: true
});
assert.equal(plan.status, 'plan');
assert.equal(plan.directAffiliate, false);
assert(plan.links.includes(ROUTES[0]));
assert(plan.links.includes(ROUTES[1]));
assert(hubApi.makeIcs(plan).includes('BEGIN:VCALENDAR'));
assert.equal(hubApi.buildPlan({ emergency: true, interval: '7' }).status, 'stop');
assert.equal(hubApi.buildPlan({ property: 'commercial', interval: '90' }).status, 'professional');

const combined = leakHtml + leakJs + coldHtml + coldJs + hubHtml + hubJs;
for (const token of [
  'Su Kaçağı Sensörü', 'Buzdolabı ve Dondurucu Sıcaklık Alarmı',
  'Tatil ve Yazlık Ev', 'Satın almama sonucu', 'Şeffaf satış ortaklığı',
  '112', '187', '4°C', '-18°C', 'rel="sponsored nofollow noopener"',
  'doğrudan affiliate bağlantısı göstermez', 'href="./styles.css"'
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
  path.join(ROOT, 'alo186/deployment/routing-overlays/138-away-home-water-coldchain.json'), 'utf8'
));
assert.equal(overlay.version, 138);
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
run(process.execPath, [path.join(LEAK_DIR, 'test.js')]);
run(process.execPath, [path.join(COLD_DIR, 'test.js')]);

const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'alo186-away-home-v138-'));
const canonical = path.join(temp, 'canonical');
run('python', ['alo186/deployment/build_static_site.py', '--output', canonical, '--commit', 'away-home-v138-test']);

for (const [name, basePath] of [['custom', ''], ['project', '/chatgpt']]) {
  const target = path.join(temp, name);
  fs.cpSync(canonical, target, { recursive: true });
  run('python', [
    'alo186/deployment/prepare_github_pages.py', '--site', target, '--base-path', basePath,
    '--repository', 'ozaneryavuz/chatgpt', '--commit', 'away-home-v138-test'
  ]);
  run('python', ['alo186/deployment/inject_private_search.py', '--site', target, '--base-path', basePath]);
  run('python', ['alo186/deployment/smoke_github_pages.py', '--site', target, '--base-path', basePath]);

  const pages = fs.readdirSync(target, { recursive: true }).filter((item) => String(item).endsWith('.html'));
  assert(pages.length >= 450, `${name} HTML sayısı düşük: ${pages.length}`);
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
  version: 138,
  routes: ROUTES,
  scenarios: 25,
  waterElectricStop112: true,
  gas187: true,
  coldThresholds: { refrigeratorC: 4, freezerC: -18 },
  activeOutageCommerceClosed: true,
  noBuy: true,
  affiliateGate: 3,
  directAffiliateOnHub: false,
  repeatVisitDays: [7, 30, 90],
  routeLocalAssets: true,
  privacy: true,
  privateSearch: true,
  dualPages: true
}, null, 2));