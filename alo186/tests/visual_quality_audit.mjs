import { chromium } from 'playwright';
import { createRequire } from 'node:module';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';

const require = createRequire(import.meta.url);
const axeSource = await readFile(require.resolve('axe-core/axe.min.js'), 'utf8');
const base = (process.argv[2] || 'http://127.0.0.1:4173').replace(/\/$/, '');
const output = process.argv[3] || '/tmp/alo186-visual-audit';
const routes = [
  '/',
  '/elektrik-portali',
  '/amazon-elektrik-urunleri',
  '/akilli-urun-secimi',
  '/hesaplama/',
  '/il/adana',
  '/haberler/ups-online-line-interactive-offline-farki',
];
const viewports = [
  { name: 'mobile', width: 390, height: 844, isMobile: true, hasTouch: true },
  { name: 'desktop', width: 1440, height: 900, isMobile: false, hasTouch: false },
];

await mkdir(output, { recursive: true });
const browser = await chromium.launch({ headless: true });
const results = [];

function safeName(route) {
  return (route === '/' ? 'home' : route.replace(/^\//, '').replace(/[^a-z0-9]+/gi, '-').replace(/-+$/, ''));
}

for (const viewport of viewports) {
  const context = await browser.newContext({
    viewport: { width: viewport.width, height: viewport.height },
    isMobile: viewport.isMobile,
    hasTouch: viewport.hasTouch,
    deviceScaleFactor: viewport.isMobile ? 2 : 1,
    reducedMotion: 'reduce',
    locale: 'tr-TR',
  });

  for (const route of routes) {
    const page = await context.newPage();
    const consoleErrors = [];
    const failedRequests = [];
    page.on('console', message => {
      if (message.type() === 'error') consoleErrors.push(message.text());
    });
    page.on('requestfailed', request => failedRequests.push(`${request.method()} ${request.url()} — ${request.failure()?.errorText || 'failed'}`));

    const url = base + route;
    let responseStatus = null;
    let navigationError = null;
    try {
      const response = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
      responseStatus = response?.status() ?? null;
      await page.waitForTimeout(350);
    } catch (error) {
      navigationError = String(error);
    }

    const checks = navigationError ? null : await page.evaluate(() => {
      const visible = element => {
        const style = getComputedStyle(element);
        const rect = element.getBoundingClientRect();
        return style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity || 1) > 0 && rect.width > 0 && rect.height > 0;
      };
      const selector = element => {
        if (element.id) return `#${CSS.escape(element.id)}`;
        const classes = [...element.classList].slice(0, 3).map(item => `.${CSS.escape(item)}`).join('');
        return `${element.tagName.toLowerCase()}${classes}`;
      };
      const documentOverflow = Math.max(document.documentElement.scrollWidth, document.body?.scrollWidth || 0) - innerWidth;
      const overflowElements = [...document.querySelectorAll('body *')].filter(visible).flatMap(element => {
        const style = getComputedStyle(element);
        if (['auto', 'scroll', 'hidden', 'clip'].includes(style.overflowX)) return [];
        if (element.scrollWidth <= element.clientWidth + 2) return [];
        if (['TABLE', 'PRE', 'CODE'].includes(element.tagName) && element.closest('.table-wrap,[role="region"]')) return [];
        return [{ selector: selector(element), overflow: element.scrollWidth - element.clientWidth, text: (element.textContent || '').trim().slice(0, 100) }];
      }).sort((a, b) => b.overflow - a.overflow).slice(0, 20);
      const images = [...document.images].map(image => ({
        src: image.currentSrc || image.src,
        complete: image.complete,
        naturalWidth: image.naturalWidth,
        naturalHeight: image.naturalHeight,
        altPresent: image.hasAttribute('alt'),
      }));
      const badImages = images.filter(image => !image.complete || image.naturalWidth <= 0 || !image.altPresent);
      const interactives = [...document.querySelectorAll('a[href],button,input,select,textarea,summary,[role="button"]')].filter(visible).map(element => {
        const rect = element.getBoundingClientRect();
        return { element, rect, selector: selector(element) };
      }).filter(item => item.rect.bottom > 0 && item.rect.top < innerHeight && item.rect.right > 0 && item.rect.left < innerWidth);
      const overlaps = [];
      for (let first = 0; first < interactives.length; first += 1) {
        for (let second = first + 1; second < interactives.length; second += 1) {
          const a = interactives[first], b = interactives[second];
          if (a.element.contains(b.element) || b.element.contains(a.element)) continue;
          const width = Math.max(0, Math.min(a.rect.right, b.rect.right) - Math.max(a.rect.left, b.rect.left));
          const height = Math.max(0, Math.min(a.rect.bottom, b.rect.bottom) - Math.max(a.rect.top, b.rect.top));
          const intersection = width * height;
          if (!intersection) continue;
          const minimum = Math.min(a.rect.width * a.rect.height, b.rect.width * b.rect.height);
          if (minimum >= 400 && intersection / minimum >= 0.65) overlaps.push({ first: a.selector, second: b.selector, ratio: Number((intersection / minimum).toFixed(2)) });
        }
      }
      const canonical = document.querySelector('link[rel~="canonical"]')?.href || '';
      return {
        title: document.title,
        lang: document.documentElement.lang,
        h1Count: document.querySelectorAll('h1').length,
        mainCount: document.querySelectorAll('main').length,
        documentOverflow,
        overflowElements,
        imageCount: images.length,
        badImages,
        overlaps: overlaps.slice(0, 20),
        canonical,
      };
    });

    let axe = { violations: [] };
    if (!navigationError) {
      await page.addScriptTag({ content: axeSource });
      axe = await page.evaluate(async () => window.axe.run(document, {
        runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21aa'] },
        resultTypes: ['violations'],
      }));
    }
    const seriousA11y = axe.violations.filter(item => ['serious', 'critical'].includes(item.impact));
    const failures = [];
    if (navigationError) failures.push(`navigation: ${navigationError}`);
    if (responseStatus !== null && responseStatus >= 400) failures.push(`HTTP ${responseStatus}`);
    if (checks) {
      if (checks.lang !== 'tr') failures.push(`html lang=${checks.lang || 'empty'}`);
      if (checks.h1Count !== 1) failures.push(`H1 count ${checks.h1Count}`);
      if (checks.mainCount !== 1) failures.push(`main count ${checks.mainCount}`);
      if (checks.documentOverflow > 2) failures.push(`document horizontal overflow ${checks.documentOverflow}px`);
      if (checks.overflowElements.length) failures.push(`${checks.overflowElements.length} uncontained overflow element`);
      if (checks.badImages.length) failures.push(`${checks.badImages.length} broken/altless image`);
      if (checks.overlaps.length) failures.push(`${checks.overlaps.length} overlapping interactive pair`);
      if (!checks.canonical.startsWith('https://alo186.com/')) failures.push(`canonical ${checks.canonical || 'missing'}`);
    }
    if (seriousA11y.length) failures.push(`${seriousA11y.length} serious/critical axe violation`);
    if (consoleErrors.length) failures.push(`${consoleErrors.length} console error`);
    if (failedRequests.length) failures.push(`${failedRequests.length} failed request`);

    const record = {
      viewport: viewport.name,
      route,
      url,
      responseStatus,
      navigationError,
      checks,
      accessibility: {
        violationCount: axe.violations.length,
        seriousCriticalCount: seriousA11y.length,
        seriousCritical: seriousA11y.map(item => ({ id: item.id, impact: item.impact, help: item.help, nodes: item.nodes.length })),
      },
      consoleErrors: consoleErrors.slice(0, 20),
      failedRequests: failedRequests.slice(0, 20),
      failures,
      ok: failures.length === 0,
    };
    results.push(record);
    await page.screenshot({ path: path.join(output, `${viewport.name}-${safeName(route)}.png`), fullPage: true });
    await page.close();
  }
  await context.close();
}

await browser.close();
const report = {
  ok: results.every(item => item.ok),
  base,
  generatedAt: new Date().toISOString(),
  pageViewCount: results.length,
  failureCount: results.reduce((sum, item) => sum + item.failures.length, 0),
  results,
};
await writeFile(path.join(output, 'visual-quality-report.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify({ ok: report.ok, pageViewCount: report.pageViewCount, failureCount: report.failureCount }, null, 2));
if (!report.ok) process.exitCode = 1;
