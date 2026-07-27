import fs from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright-core';
import axe from 'axe-core';

const origin = 'https://alo186.com';
const out = 'artifacts/live-quality';
fs.mkdirSync(out, { recursive: true });
const urls = [
  `${origin}/`,
  `${origin}/elektrik-kesintisi`,
  `${origin}/elektrik-portali`,
  `${origin}/il/mugla`,
  `${origin}/sektor-rehberi/planli-elektrik-kesintisi-sorgulama`,
  `${origin}/haberler`,
  `${origin}/iletisim`,
  `${origin}/acil-numaralar`,
];
const executablePath = ['/usr/bin/google-chrome','/usr/bin/google-chrome-stable','/usr/bin/chromium'].find(fs.existsSync);
if (!executablePath) throw new Error('Chrome bulunamadı');
const browser = await chromium.launch({ executablePath, headless: true, args: ['--no-sandbox','--disable-dev-shm-usage'] });
const profiles = [
  { name: 'mobile', viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 },
  { name: 'desktop', viewport: { width: 1440, height: 1000 }, isMobile: false, hasTouch: false, deviceScaleFactor: 1 },
];
const results = [];
for (const url of urls) {
  for (const profile of profiles) {
    const context = await browser.newContext({ ...profile, locale: 'tr-TR' });
    const page = await context.newPage();
    const consoleErrors = [], pageErrors = [], failedRequests = [];
    page.on('console', msg => { if (msg.type() === 'error') consoleErrors.push(msg.text()); });
    page.on('pageerror', error => pageErrors.push(String(error)));
    page.on('requestfailed', req => failedRequests.push({ url: req.url(), resourceType: req.resourceType(), error: req.failure()?.errorText || null }));
    let response = null, navigationError = null;
    try { response = await page.goto(url, { waitUntil: 'networkidle', timeout: 45000 }); }
    catch (error) { navigationError = String(error); }
    await page.evaluate(async () => {
      const step = 700;
      for (let y = 0; y < document.documentElement.scrollHeight; y += step) {
        window.scrollTo(0, y);
        await new Promise(resolve => setTimeout(resolve, 60));
      }
      window.scrollTo(0, 0);
    });
    await page.waitForTimeout(500);
    const layout = await page.evaluate(() => {
      const root = document.documentElement;
      const overflow = [...document.querySelectorAll('body *')].map(el => {
        const r = el.getBoundingClientRect();
        return { tag: el.tagName.toLowerCase(), id: el.id || null, className: typeof el.className === 'string' ? el.className.slice(0,160) : null, text: (el.textContent || '').trim().replace(/\s+/g,' ').slice(0,100), left: r.left, right: r.right, width: r.width };
      }).filter(item => item.width > 0 && (item.left < -1 || item.right > root.clientWidth + 1)).slice(0,25);
      const brokenImages = [...document.images].map(img => ({ src: img.currentSrc || img.src, alt: img.alt, complete: img.complete, naturalWidth: img.naturalWidth, naturalHeight: img.naturalHeight })).filter(img => img.complete && img.naturalWidth === 0);
      const smallTargets = [...document.querySelectorAll('a,button,input,select,textarea,[role="button"]')].map(el => { const r=el.getBoundingClientRect(); return { tag: el.tagName.toLowerCase(), text: (el.textContent || el.getAttribute('aria-label') || el.getAttribute('placeholder') || '').trim().slice(0,90), width:r.width, height:r.height }; }).filter(item => item.width > 0 && item.height > 0 && (item.width < 24 || item.height < 24)).slice(0,30);
      return { viewportWidth: root.clientWidth, scrollWidth: root.scrollWidth, horizontalOverflowPx: Math.max(0, root.scrollWidth-root.clientWidth), overflow, brokenImages, smallTargets };
    });
    await page.addScriptTag({ content: axe.source });
    const accessibility = await page.evaluate(async () => await window.axe.run(document, { resultTypes: ['violations'] }));
    const name = new URL(url).pathname.replace(/^\/+|\/+$/g,'').replace(/[^a-z0-9]+/gi,'-') || 'home';
    const screenshot = path.join(out, `${name}-${profile.name}.png`);
    await page.screenshot({ path: screenshot, fullPage: true });
    results.push({ url, profile: profile.name, status: response?.status() || 0, finalUrl: page.url(), navigationError, consoleErrors: [...new Set(consoleErrors)].slice(0,30), pageErrors: [...new Set(pageErrors)].slice(0,20), failedRequests: failedRequests.slice(0,30), layout, violations: accessibility.violations.map(v => ({ id:v.id, impact:v.impact, help:v.help, nodes:v.nodes.slice(0,8).map(n => ({ target:n.target, failureSummary:n.failureSummary, html:n.html.slice(0,400) })) })), screenshot });
    await context.close();
  }
}
await browser.close();
const issues = [];
for (const item of results) {
  if (item.status < 200 || item.status >= 400) issues.push({ level:'P0', category:'http', url:item.url, profile:item.profile, message:`HTTP ${item.status || 'error'}` });
  if (item.layout.horizontalOverflowPx > 1) issues.push({ level:'P1', category:'layout', url:item.url, profile:item.profile, message:`Yatay taşma ${item.layout.horizontalOverflowPx}px`, evidence:item.layout.overflow });
  if (item.layout.brokenImages.length) issues.push({ level:'P0', category:'image', url:item.url, profile:item.profile, message:'Yüklenmesi tamamlandığı halde doğal boyutu sıfır olan görsel', evidence:item.layout.brokenImages });
  const failedImageRequests = item.failedRequests.filter(request => request.resourceType === 'image' && !/ERR_ABORTED/i.test(request.error || ''));
  if (failedImageRequests.length) issues.push({ level:'P1', category:'image-request', url:item.url, profile:item.profile, message:'Başarısız görsel ağ isteği', evidence:failedImageRequests });
  if (item.pageErrors.length) issues.push({ level:'P0', category:'javascript', url:item.url, profile:item.profile, message:'JavaScript page error', evidence:item.pageErrors });
  if (item.consoleErrors.length) issues.push({ level:'P1', category:'console', url:item.url, profile:item.profile, message:'Konsol hatası', evidence:item.consoleErrors });
  const serious = item.violations.filter(v => ['critical','serious'].includes(v.impact));
  if (serious.length) issues.push({ level:'P1', category:'accessibility', url:item.url, profile:item.profile, message:'Ciddi erişilebilirlik ihlali', evidence:serious });
  if (item.layout.smallTargets.length) issues.push({ level:'P2', category:'usability', url:item.url, profile:item.profile, message:'24px altı etkileşim hedefi', evidence:item.layout.smallTargets });
}
fs.writeFileSync(path.join(out,'browser-report.json'), JSON.stringify({ generatedAt:new Date().toISOString(), results, issues }, null, 2));
const lines = ['# ALO186 tarayıcı kalite denetimi','',`- Senaryo: ${results.length}`,`- Sorun: ${issues.length}`,'','## Sorunlar','',...issues.map(i => `- **${i.level} · ${i.category} · ${i.profile}** — ${i.message} — ${i.url}`)];
fs.writeFileSync(path.join(out,'browser-report.md'), lines.join('\n')+'\n');
console.log(lines.join('\n'));
