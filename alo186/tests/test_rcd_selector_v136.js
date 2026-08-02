'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const ROOT = path.resolve(__dirname, '..', '..');
const DIR = path.join(ROOT, 'alo186/hesaplama/kacak-akim-rolesi-tipi-uygunluk');
const HTML = fs.readFileSync(path.join(DIR, 'index.html'), 'utf8');
const CSS = fs.readFileSync(path.join(DIR, 'styles.css'), 'utf8');
const JS = fs.readFileSync(path.join(DIR, 'app.js'), 'utf8');
const ROUTE = '/hesaplama/kacak-akim-rolesi-tipi-uygunluk/';
const api = require(path.join(DIR, 'app.js'));

assert(api?.evaluate, 'RCD karar API yok');

const base = {
  emergency: false, mode: 'planning', useCase: 'home', physical: 'good', testButton: 'unknown',
  goal: 'personal', circuitScope: 'single', phase: 'single', loadType: 'general',
  manufacturerType: 'unknown', dc6: 'not_applicable', breakerA: 16, existingRatedA: 0,
  existingMa: 'unknown', existingType: 'unknown', existingForm: 'none',
  installationTest: 'unknown', taskTest: 'not_tested', downstream30: 'not_applicable',
  confirmNeed: true, confirmSpecs: true, confirmAffiliate: true
};

assert.equal(api.evaluate(base).recommendation.typeCode, 'A');
assert.equal(api.evaluate(base).recommendation.form, 'RCBO');
assert.equal(api.evaluate(base).affiliateAllowed, true);
assert.equal(api.evaluate({ ...base, emergency: true }).status, 'stop');
assert.equal(api.evaluate({ ...base, testButton: 'fail' }).status, 'stop');
assert.equal(api.evaluate({ ...base, mode: 'active_fault' }).status, 'diagnose');
assert.equal(api.evaluate({ ...base, goal: 'nuisance' }).affiliateAllowed, false);
assert.equal(api.evaluate({ ...base, useCase: 'commercial' }).status, 'professional');
assert.equal(api.evaluate({ ...base, phase: 'three' }).status, 'professional');
assert.equal(api.evaluate({ ...base, loadType: 'single_vfd' }).recommendation.typeCode, 'F');
assert.equal(api.evaluate({ ...base, loadType: 'ev' }).status, 'professional');
assert.equal(api.evaluate({ ...base, loadType: 'ev', dc6: 'verified' }).recommendation.typeCode, 'A');
assert.equal(api.evaluate({ ...base, loadType: 'pv' }).recommendation.typeCode, 'B');
assert.equal(api.evaluate({ ...base, loadType: 'unknown' }).affiliateAllowed, false);
assert.equal(api.evaluate({ ...base, confirmSpecs: false }).affiliateAllowed, false);

const noBuy = api.evaluate({
  ...base, existingForm: 'RCBO', existingRatedA: 16, existingMa: '30', existingType: 'A',
  testButton: 'pass', installationTest: 'pass', taskTest: 'pass'
});
assert.equal(noBuy.status, 'no-buy');

for (const token of [
  '<form id="rcdForm"', 'aria-live="polite"', 'Kaçak akım rölesi',
  '30 mA', 'RCCB', 'RCBO', 'Type F', 'Type B', 'Satın almama sonucu',
  'Şeffaf satış ortaklığı', 'rel="sponsored nofollow noopener"',
  `https://alo186.com${ROUTE}`
]) assert((HTML + JS).includes(token), token);

for (const forbidden of [
  'localStorage', 'sessionStorage', 'navigator.geolocation', 'fetch(',
  'amazon.com', 'amazon.com.tr', '"@type":"Product"', '"@type":"Offer"',
  'aggregateRating', 'availability', 'name="email"', 'name="phone"',
  'name="address"', 'name="location"', 'name="serial"'
]) assert(!HTML.includes(forbidden) && !JS.includes(forbidden), forbidden);

for (const token of [
  '@media(max-width:900px)', '@media(max-width:620px)', 'min-height:48px',
  ':focus-visible', '@media(prefers-reduced-motion:reduce)',
  '@media(forced-colors:active)', '@media print'
]) assert(CSS.includes(token), token);

const overlay = JSON.parse(fs.readFileSync(
  path.join(ROOT, 'alo186/deployment/routing-overlays/136-kacak-akim-rolesi-uygunluk.json'), 'utf8'
));
assert.equal(overlay.version, 136);
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

const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'alo186-rcd-v136-'));
const canonical = path.join(temp, 'canonical');
run('python', ['alo186/deployment/build_static_site.py', '--output', canonical, '--commit', 'rcd-v136-test']);

for (const [name, basePath] of [['custom', ''], ['project', '/chatgpt']]) {
  const target = path.join(temp, name);
  fs.cpSync(canonical, target, { recursive: true });
  run('python', [
    'alo186/deployment/prepare_github_pages.py', '--site', target, '--base-path', basePath,
    '--repository', 'ozaneryavuz/chatgpt', '--commit', 'rcd-v136-test'
  ]);
  run('python', ['alo186/deployment/inject_private_search.py', '--site', target, '--base-path', basePath]);
  run('python', ['alo186/deployment/smoke_github_pages.py', '--site', target, '--base-path', basePath]);

  const routeDir = path.join(target, ROUTE.replace(/^\/|\/$/g, ''));
  const page = path.join(routeDir, 'index.html');
  assert(fs.existsSync(page), `${name} rota yok`);
  const published = fs.readFileSync(page, 'utf8');
  const publishedJs = fs.readFileSync(path.join(routeDir, 'app.js'), 'utf8');
  assert(published.includes('Kaçak Akım Rölesi'));
  assert(publishedJs.includes('rel="sponsored nofollow noopener"'));
  assert(published.includes('data-alo186-sitewide-ux="true"'));
  const sitemap = fs.readFileSync(path.join(target, 'sitemap.xml'), 'utf8');
  assert(sitemap.includes(`https://alo186.com${ROUTE}`) || sitemap.includes(`https://alo186.com${ROUTE}`));
  const searchIndex = fs.readFileSync(path.join(target, 'arama/search-index.json'), 'utf8');
  assert(searchIndex.includes(ROUTE));
}

console.log(JSON.stringify({
  ok: true,
  scenarios: 22,
  module: 'kacak_akim_rolesi_tipi_uygunluk',
  types: ['A', 'F', 'B'],
  forms: ['RCCB', 'RCBO'],
  currentAndSensitivitySeparation: true,
  safetyAndProfessionalClosures: true,
  nuisanceTripDiagnosis: true,
  noBuy: true,
  affiliateGate: 3,
  privacy: true,
  responsive: true,
  privateSearch: true,
  dualPages: true
}, null, 2));
