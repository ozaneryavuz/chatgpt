'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const ROOT = path.resolve(__dirname, '..', '..');
const DIR = path.join(ROOT, 'alo186/hesaplama/vantilator-hava-sogutucu-portatif-klima-karsilastirma');
const HTML = fs.readFileSync(path.join(DIR, 'index.html'), 'utf8');
const CSS = fs.readFileSync(path.join(DIR, 'styles.css'), 'utf8');
const JS = fs.readFileSync(path.join(DIR, 'app.js'), 'utf8');
const ROUTE = '/hesaplama/vantilator-hava-sogutucu-portatif-klima-karsilastirma/';
const api = require(path.join(DIR, 'app.js'));

assert(api?.evaluate, 'Serinletme karar API yok');

const base = {
  emergency: false, mode: 'planning', useCase: 'home_room', physical: 'good', gridSymptom: 'none',
  goal: 'personal_breeze', areaM2: 20, ceilingM: 2.7, humidity: 'medium', ventilation: 'yes',
  sun: 'normal', people: 2, electronicsW: 0, deviceType: 'none', existing: 'no', inputW: 0,
  ratedA: 0, candidateBtu: 0, manual: 'unknown', connection: 'direct', protection: 'verified',
  hose: 'unknown', drainage: 'unknown', taskTest: 'not_tested', confirmNeed: true,
  confirmSpecs: true, confirmAffiliate: true
};

assert.equal(api.evaluate(base).recommendation, 'fan');
assert.equal(api.evaluate(base).affiliateAllowed, true);
assert.equal(api.evaluate({ ...base, goal: 'humidity_relief', humidity: 'high' }).recommendation, 'dehumidifier');
assert.equal(api.evaluate({ ...base, emergency: true }).status, 'stop');
assert.equal(api.evaluate({ ...base, gridSymptom: 'bright_dim' }).status, 'professional');
assert.equal(api.evaluate({ ...base, mode: 'active_outage' }).affiliateAllowed, false);
assert.equal(api.evaluate({ ...base, useCase: 'commercial' }).status, 'professional');
assert.equal(api.evaluate({ ...base, goal: 'room_cooling', deviceType: 'fan', manual: 'verified', inputW: 55 }).status, 'evidence');
assert.equal(api.evaluate({ ...base, goal: 'room_cooling', humidity: 'high', deviceType: 'evaporative', manual: 'verified', inputW: 100 }).affiliateAllowed, false);
assert.equal(api.evaluate({ ...base, goal: 'room_cooling', deviceType: 'portable_ac', manual: 'verified', inputW: 1200, candidateBtu: 8000, hose: 'verified', drainage: 'verified', connection: 'extension' }).status, 'stop');
assert.equal(api.evaluate({ ...base, goal: 'room_cooling', deviceType: 'portable_ac', existing: 'yes', manual: 'verified', inputW: 1200, candidateBtu: 8000, hose: 'verified', drainage: 'verified', taskTest: 'pass' }).status, 'no-buy');
assert.equal(api.evaluate({ ...base, confirmAffiliate: false }).affiliateAllowed, false);

for (const token of [
  '<form id="coolingForm"', 'aria-live="polite"', 'Vantilatör mü, hava soğutucu mu',
  'Satın almama sonucu', 'Şeffaf satış ortaklığı', 'rel="sponsored nofollow noopener"',
  'Bağıl nem bandı', 'Sürekli dış hava çıkışı', 'Sıcak hava hortumu',
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
  ':focus-visible', '@media(prefers-reduced-motion:reduce)', '@media(forced-colors:active)', '@media print'
]) assert(CSS.includes(token), token);

const overlay = JSON.parse(fs.readFileSync(
  path.join(ROOT, 'alo186/deployment/routing-overlays/135-serinletme-cozumu-karsilastirma.json'), 'utf8'
));
assert.equal(overlay.version, 135);
assert.equal(overlay.routes[0].canonicalPath, ROUTE);
assert.equal(overlay.routes[0].type, 'calculator');

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

const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'alo186-cooling-v135-'));
const canonical = path.join(temp, 'canonical');
run('python', ['alo186/deployment/build_static_site.py', '--output', canonical, '--commit', 'cooling-v135-test']);

for (const [name, basePath] of [['custom', ''], ['project', '/chatgpt']]) {
  const target = path.join(temp, name);
  fs.cpSync(canonical, target, { recursive: true });
  run('python', [
    'alo186/deployment/prepare_github_pages.py', '--site', target, '--base-path', basePath,
    '--repository', 'ozaneryavuz/chatgpt', '--commit', 'cooling-v135-test'
  ]);
  run('python', ['alo186/deployment/inject_private_search.py', '--site', target, '--base-path', basePath]);
  run('python', ['alo186/deployment/smoke_github_pages.py', '--site', target, '--base-path', basePath]);

  const routeDir = path.join(target, ROUTE.replace(/^\/|\/$/g, ''));
  const page = path.join(routeDir, 'index.html');
  assert(fs.existsSync(page), `${name} rota yok`);
  const published = fs.readFileSync(page, 'utf8');
  const publishedJs = fs.readFileSync(path.join(routeDir, 'app.js'), 'utf8');
  assert(published.includes('Vantilatör, Hava Soğutucu'));
  assert(publishedJs.includes('rel="sponsored nofollow noopener"'));
  assert(published.includes('data-alo186-sitewide-ux="true"'));
  const sitemap = fs.readFileSync(path.join(target, 'sitemap.xml'), 'utf8');
  assert(sitemap.includes(`https://alo186.com${ROUTE}`) || sitemap.includes(`https://alo186.com${ROUTE}`));
  const searchIndex = fs.readFileSync(path.join(target, 'arama/search-index.json'), 'utf8');
  assert(searchIndex.includes(ROUTE));
}

console.log(JSON.stringify({
  ok: true,
  scenarios: 18,
  comparison: ['vantilator', 'evaporatif', 'portatif_klima', 'nem_alma'],
  calculations: ['oda_hacmi', 'btu_on_secim', 'watt_amper', 'saatlik_kwh'],
  safetyAndProfessionalClosures: true,
  noBuy: true,
  affiliateGate: 3,
  privacy: true,
  responsive: true,
  privateSearch: true,
  dualPages: true
}, null, 2));
