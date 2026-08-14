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
  '/amazon-elektrik-urunleri/modem-ont-mini-ups-yedekleme-secici/',
  '/akilli-urun-secimi',
  '/hesaplama/',
  '/hesaplama/kablo-gerilim-dusumu/',
  '/karar-motoru/',
  '/edas-bul/',
  '/haberler/ups-online-line-interactive-offline-farki',
];
const viewports = [
  { name: 'phone-320', width: 320, height: 568, isMobile: true, hasTouch: true },
  { name: 'phone-360', width: 360, height: 800, isMobile: true, hasTouch: true },
  { name: 'phone-390', width: 390, height: 844, isMobile: true, hasTouch: true },
  { name: 'phone-430', width: 430, height: 932, isMobile: true, hasTouch: true },
  { name: 'desktop', width: 1440, height: 900, isMobile: false, hasTouch: false },
];

await mkdir(output, { recursive: true });
const browser = await chromium.launch({ headless: true });
const results = [];

function safeName(route) {
  return (route === '/' ? 'home' : route.replace(/^\//, '').replace(/[^a-z0-9]+/gi, '-').replace(/-+$/, ''));
}

function a11yDetails(violations) {
  return violations.map(item => ({
    id: item.id,
    impact: item.impact,
    help: item.help,
    helpUrl: item.helpUrl,
    nodes: item.nodes.slice(0, 12).map(entry => ({
      target: entry.target,
      html: entry.html,
      failureSummary: entry.failureSummary,
    })),
  }));
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
        const style = getComputedStyle(element);
        return { element, rect, style, selector: selector(element) };
      }).filter(item => item.rect.bottom > 0 && item.rect.top < innerHeight && item.rect.right > 0 && item.rect.left < innerWidth);
      const smallTargets = interactives.filter(item => {
        if (item.element.matches('input[type="checkbox"],input[type="radio"],input[type="hidden"]')) return false;
        if (item.element.matches('a[href]') && item.style.display === 'inline') return false;
        return item.rect.width < 44 || item.rect.height < 44;
      }).map(item => ({
        selector: item.selector,
        width: Number(item.rect.width.toFixed(1)),
        height: Number(item.rect.height.toFixed(1)),
        text: (item.element.textContent || item.element.getAttribute('aria-label') || '').trim().slice(0, 100),
      })).slice(0, 30);
      const readabilitySelector = [
        '.amazon-intent-card small',
        '[class*="heroProof"] span',
        '[class*="taskTop"] > span',
        '[class*="taskCard"] small',
        '[class*="task-card"] small',
        '[class*="answerList"] > article > span',
        '#analytics-preferences-open',
        'button[data-analytics-choice]',
      ].join(',');
      const smallText = [...document.querySelectorAll(readabilitySelector)].filter(visible).map(element => {
        const style = getComputedStyle(element);
        return { selector: selector(element), fontSize: Number.parseFloat(style.fontSize), text: (element.textContent || '').trim().slice(0, 100) };
      }).filter(item => item.fontSize < 14).slice(0, 30);
      const undersizedMobileControls = innerWidth <= 760
        ? [...document.querySelectorAll('input:not([type="hidden"]),select,textarea,button')].filter(visible).map(element => ({
            selector: selector(element),
            fontSize: Number.parseFloat(getComputedStyle(element).fontSize),
            text: (element.textContent || element.getAttribute('aria-label') || '').trim().slice(0, 100),
          })).filter(item => item.fontSize < 16).slice(0, 30)
        : [];
      const menuIssues = [...document.querySelectorAll('header nav,.site-header nav,[aria-label*="menü" i],[aria-label*="menu" i]')].filter(visible).flatMap(element => {
        const style = getComputedStyle(element);
        const containedScroll = ['auto', 'scroll'].includes(style.overflowX);
        if (element.scrollWidth <= element.clientWidth + 2 || containedScroll) return [];
        return [{ selector: selector(element), clientWidth: element.clientWidth, scrollWidth: element.scrollWidth }];
      }).slice(0, 20);
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
        smallTargets,
        smallText,
        undersizedMobileControls,
        menuIssues,
        imageCount: images.length,
        badImages,
        overlaps: overlaps.slice(0, 20),
        canonical,
      };
    });

    let axe = { violations: [] };
    if (!navigationError && responseStatus !== null && responseStatus < 400) {
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
      if (viewport.width <= 430 && checks.smallTargets.length) failures.push(`${checks.smallTargets.length} touch target below 44×44px`);
      if (checks.smallText.length) failures.push(`${checks.smallText.length} key label below 14px`);
      if (checks.undersizedMobileControls.length) failures.push(`${checks.undersizedMobileControls.length} mobile form/control text below 16px`);
      if (checks.menuIssues.length) failures.push(`${checks.menuIssues.length} uncontained mobile menu overflow`);
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
        seriousCritical: a11yDetails(seriousA11y),
      },
      consoleErrors: consoleErrors.slice(0, 20),
      failedRequests: failedRequests.slice(0, 20),
      failures,
      ok: failures.length === 0,
    };
    results.push(record);
    const basename = `${viewport.name}-${safeName(route)}`;
    await page.screenshot({ path: path.join(output, `${basename}.png`), fullPage: true });
    if (failures.length) await writeFile(path.join(output, `${basename}.html`), await page.content());
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
