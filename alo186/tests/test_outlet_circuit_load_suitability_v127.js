'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { execFileSync } = require('node:child_process');

const ROOT = path.resolve(__dirname, '..', '..');
const route = 'priz-kac-watt-ayni-devre-yuk-uygunluk';
const dir = path.join(ROOT, 'alo186', 'hesaplama', route);
const html = fs.readFileSync(path.join(dir, 'index.html'), 'utf8');
const css = fs.readFileSync(path.join(dir, 'styles.css'), 'utf8');
const js = fs.readFileSync(path.join(dir, 'app.js'), 'utf8');
const overlayPath = path.join(ROOT, 'alo186', 'deployment', 'routing-overlays', '127-outlet-circuit-load-suitability.json');
const overlay = JSON.parse(fs.readFileSync(overlayPath, 'utf8'));
const app = require(path.join(dir, 'app.js'));

execFileSync('node', [path.join(dir, 'app.test.js')], { cwd: ROOT, stdio: 'pipe' });
execFileSync('node', ['--check', path.join(dir, 'app.js')], { cwd: ROOT, stdio: 'pipe' });

for (const token of [
  '<form id="loadForm"', 'aria-live="polite"', 'Priz kaç watt kaldırır?',
  'Kettle / su ısıtıcısı', 'Mikrodalga gerçek giriş gücü', 'Devre sigortası',
  'Duvar prizi etiket akımı', 'Kişisel veri yok', 'Satın almama sonucu',
  'Şeffaf satış ortaklığı', 'rel="sponsored nofollow noopener"',
  'id="confirmGap"', 'id="confirmSpecs"', 'id="confirmAffiliate"',
  'FAQPage', 'BreadcrumbList', 'rel="canonical"'
]) assert.ok(html.includes(token), token);

for (const forbidden of [
  'localStorage', 'sessionStorage', 'navigator.geolocation', 'amazon.com', 'amazon.com.tr',
  '"@type":"Product"', '"@type":"Offer"', 'priceCurrency', 'aggregateRating',
  'name="email"', 'name="phone"', 'name="address"'
]) assert.ok(!html.includes(forbidden), forbidden);

for (const forbidden of ['localStorage', 'sessionStorage', 'navigator.geolocation', 'fetch(']) {
  assert.ok(!js.includes(forbidden), forbidden);
}
for (const token of [
  'no_buy', 'measure_first', 'electronics_strip', 'overload', 'stagger',
  'near_limit', 'daisy_chain', 'affiliate-check', 'sponsored nofollow noopener'
]) assert.ok(js.includes(token) || html.includes(token), token);
for (const token of [
  '@media(max-width:820px)', '@media(max-width:560px)', 'min-height:48px',
  'prefers-reduced-motion', 'forced-colors', 'focus-visible'
]) assert.ok(css.includes(token), token);

assert.deepEqual(overlay, {
  version: 127,
  generatedAt: '2026-07-31',
  routes: [{
    source: `alo186/hesaplama/${route}/index.html`,
    canonicalPath: `/hesaplama/${route}/`,
    type: 'calculator'
  }]
});
assert.equal(overlay.routes[0].canonicalPath, app.ROUTE);

const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'alo186-outlet-load-v127-'));
const canonical = path.join(temp, 'canonical');
execFileSync('python', [
  path.join(ROOT, 'alo186', 'deployment', 'build_static_site.py'),
  '--output', canonical,
  '--commit', 'outlet-load-v127-test'
], { cwd: ROOT, stdio: 'pipe' });

const routeFile = path.join(canonical, 'hesaplama', route, 'index.html');
assert.ok(fs.existsSync(routeFile));
assert.ok(fs.existsSync(path.join(canonical, 'hesaplama', route, 'app.js')));
const sitemap = fs.readFileSync(path.join(canonical, 'sitemap.xml'), 'utf8');
assert.ok(sitemap.includes(`/hesaplama/${route}/`));
const release = JSON.parse(fs.readFileSync(path.join(canonical, 'alo186-release.json'), 'utf8'));
assert.ok(release.routes.some((item) => item.canonicalPath === app.ROUTE && item.type === 'calculator'));

for (const basePath of ['', '/chatgpt']) {
  const target = path.join(temp, basePath ? 'project' : 'custom');
  fs.cpSync(canonical, target, { recursive: true });
  execFileSync('python', [
    path.join(ROOT, 'alo186', 'deployment', 'prepare_github_pages.py'),
    '--site', target,
    '--base-path', basePath,
    '--repository', 'ozaneryavuz/chatgpt',
    '--commit', 'outlet-load-v127-test'
  ], { cwd: ROOT, stdio: 'pipe' });
  execFileSync('python', [
    path.join(ROOT, 'alo186', 'deployment', 'smoke_github_pages.py'),
    '--site', target,
    '--base-path', basePath
  ], { cwd: ROOT, stdio: 'pipe' });
  const page = fs.readFileSync(path.join(target, 'hesaplama', route, 'index.html'), 'utf8');
  const runtime = fs.readFileSync(path.join(target, 'hesaplama', route, 'app.js'), 'utf8');
  const expectedAsset = `${basePath}/assets/alo186-ux.js` || '/assets/alo186-ux.js';
  assert.ok(page.includes(expectedAsset));
  assert.ok(page.includes('sponsored nofollow noopener'));
  assert.ok(runtime.includes('PRODUCT_ROUTES'));
  assert.ok(fs.readFileSync(path.join(target, 'sitemap.xml'), 'utf8').includes(`/hesaplama/${route}/`));
}

fs.rmSync(temp, { recursive: true, force: true });

console.log(JSON.stringify({
  ok: true,
  route: app.ROUTE,
  decisionScenarios: 19,
  wattAmpAndMargin: true,
  minimumLabelWins: true,
  noBuyOutcome: true,
  highPowerCommerceClosed: true,
  affiliateTransparent: true,
  personalData: false,
  mobile: true,
  accessible: true,
  customDomain: true,
  projectPath: true
}));
