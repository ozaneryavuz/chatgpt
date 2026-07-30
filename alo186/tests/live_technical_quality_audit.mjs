import fs from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import { chromium, devices } from 'playwright';
import axeCore from 'axe-core';

const ORIGIN = process.env.ALO186_LIVE_ORIGIN || 'https://alo186.com';
const OUTPUT = path.resolve(process.env.ALO186_AUDIT_OUTPUT || '/tmp/alo186-live-audit');
const PAGE_PATHS = (process.env.ALO186_AUDIT_PATHS || [
  '/',
  '/elektrik-portali',
  '/amazon-elektrik-urunleri',
  '/akilli-urun-secimi',
  '/urun-bilgi-grafigi/',
  '/il/adana',
].join(',')).split(',').map((item) => item.trim()).filter(Boolean);
const MAX_SITEMAP_URLS = Number(process.env.ALO186_MAX_SITEMAP_URLS || 220);
const MAX_LINKS_PER_PAGE = Number(process.env.ALO186_MAX_LINKS_PER_PAGE || 120);
const INTERNAL_HOSTS = new Set(['alo186.com', 'www.alo186.com']);

const profiles = {
  mobile: {
    viewport: { width: 390, height: 844 },
    userAgent: devices['iPhone 13'].userAgent,
    deviceScaleFactor: 3,
    isMobile: true,
    hasTouch: true,
  },
  desktop: {
    viewport: { width: 1440, height: 1000 },
    userAgent: devices['Desktop Chrome'].userAgent,
    deviceScaleFactor: 1,
    isMobile: false,
    hasTouch: false,
  },
};

function unique(values) {
  return [...new Set(values)];
}

function normalizeInternalUrl(value, base = ORIGIN) {
  try {
    const url = new URL(value, base);
    if (!INTERNAL_HOSTS.has(url.hostname)) return null;
    url.hash = '';
    return url.toString();
  } catch {
    return null;
  }
}

async function fetchText(url, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), options.timeout || 30000);
  try {
    const response = await fetch(url, {
      redirect: options.redirect || 'follow',
      signal: controller.signal,
      headers: {
        'user-agent': options.userAgent || 'ALO186-Technical-Quality-Audit/1.0',
        accept: options.accept || '*/*',
      },
    });
    return {
      ok: response.ok,
      status: response.status,
      url: response.url,
      headers: Object.fromEntries(response.headers.entries()),
      text: await response.text(),
    };
  } catch (error) {
    return { ok: false, status: 0, url, headers: {}, text: '', error: String(error) };
  } finally {
    clearTimeout(timeout);
  }
}

async function traceRedirects(url) {
  const chain = [];
  let current = url;
  for (let index = 0; index < 8; index += 1) {
    const result = await fetchText(current, { redirect: 'manual' });
    chain.push({ url: current, status: result.status, location: result.headers.location || null });
    if (![301, 302, 303, 307, 308].includes(result.status) || !result.headers.location) break;
    current = new URL(result.headers.location, current).toString();
  }
  return chain;
}

function parseSitemapXml(xml) {
  return unique([...xml.matchAll(/<loc>\s*([^<]+?)\s*<\/loc>/gi)].map((match) => match[1].trim()));
}

function parseRobots(text) {
  const directives = [];
  let currentAgents = [];
  for (const rawLine of text.split(/\r?\n/)) {
    const line = rawLine.replace(/#.*/, '').trim();
    if (!line || !line.includes(':')) continue;
    const [rawKey, ...rest] = line.split(':');
    const key = rawKey.trim().toLowerCase();
    const value = rest.join(':').trim();
    if (key === 'user-agent') currentAgents = [value.toLowerCase()];
    if (['allow', 'disallow'].includes(key)) directives.push({ agents: [...currentAgents], key, value });
  }
  return directives;
}

function overlapArea(a, b) {
  const width = Math.max(0, Math.min(a.right, b.right) - Math.max(a.left, b.left));
  const height = Math.max(0, Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top));
  return width * height;
}

async function auditPage(browser, profileName, pagePath) {
  const profile = profiles[profileName];
  const context = await browser.newContext({
    viewport: profile.viewport,
    userAgent: profile.userAgent,
    deviceScaleFactor: profile.deviceScaleFactor,
    isMobile: profile.isMobile,
    hasTouch: profile.hasTouch,
    locale: 'tr-TR',
    colorScheme: 'light',
    reducedMotion: 'reduce',
    serviceWorkers: 'block',
  });
  const page = await context.newPage();
  const consoleErrors = [];
  const pageErrors = [];
  const failedRequests = [];
  const badResponses = [];
  page.on('console', (message) => {
    if (message.type() === 'error') consoleErrors.push(message.text().slice(0, 500));
  });
  page.on('pageerror', (error) => pageErrors.push(String(error).slice(0, 500)));
  page.on('requestfailed', (request) => failedRequests.push({ url: request.url(), reason: request.failure()?.errorText || 'unknown' }));
  page.on('response', (response) => {
    if (response.status() >= 400 && response.request().resourceType() !== 'image') {
      badResponses.push({ url: response.url(), status: response.status(), type: response.request().resourceType() });
    }
  });

  const requestedUrl = new URL(pagePath, ORIGIN).toString();
  const started = Date.now();
  let navigationStatus = 0;
  let navigationError = null;
  try {
    const response = await page.goto(requestedUrl, { waitUntil: 'networkidle', timeout: 60000 });
    navigationStatus = response?.status() || 0;
  } catch (error) {
    navigationError = String(error);
  }
  await page.waitForTimeout(800);

  const screenshotPath = path.join(OUTPUT, 'screenshots', profileName, `${pagePath === '/' ? 'home' : pagePath.replace(/^\/+|\/+$/g, '').replaceAll('/', '__')}.png`);
  await fs.mkdir(path.dirname(screenshotPath), { recursive: true });
  await page.screenshot({ path: screenshotPath, fullPage: true });

  await page.addScriptTag({ content: axeCore.source });
  const axe = await page.evaluate(async () => {
    const result = await window.axe.run(document, {
      runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'] },
      resultTypes: ['violations', 'incomplete'],
    });
    return {
      violations: result.violations.map((item) => ({
        id: item.id,
        impact: item.impact,
        description: item.description,
        help: item.help,
        nodes: item.nodes.slice(0, 12).map((node) => ({ target: node.target, failureSummary: node.failureSummary })),
      })),
      incomplete: result.incomplete.map((item) => ({ id: item.id, impact: item.impact, help: item.help, nodeCount: item.nodes.length })),
    };
  });

  const dom = await page.evaluate(({ maxLinks }) => {
    const absolute = (value) => {
      try { return new URL(value, location.href).toString(); } catch { return null; }
    };
    const visible = (element) => {
      const style = getComputedStyle(element);
      const rect = element.getBoundingClientRect();
      return style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity) > 0 && rect.width > 0 && rect.height > 0;
    };
    const selector = (element) => {
      if (element.id) return `#${CSS.escape(element.id)}`;
      const classes = [...element.classList].slice(0, 3).map((item) => `.${CSS.escape(item)}`).join('');
      return `${element.tagName.toLowerCase()}${classes}`;
    };
    const viewportWidth = document.documentElement.clientWidth;
    const documentWidth = Math.max(document.documentElement.scrollWidth, document.body?.scrollWidth || 0);
    const overflowElements = [...document.querySelectorAll('body *')]
      .filter(visible)
      .map((element) => ({ element, rect: element.getBoundingClientRect() }))
      .filter(({ rect }) => rect.left < -2 || rect.right > viewportWidth + 2)
      .slice(0, 80)
      .map(({ element, rect }) => ({ selector: selector(element), left: Math.round(rect.left), right: Math.round(rect.right), width: Math.round(rect.width), text: (element.textContent || '').trim().slice(0, 120) }));

    const interactives = [...document.querySelectorAll('a[href],button,input,select,textarea,[role="button"],[tabindex]:not([tabindex="-1"])')]
      .filter(visible)
      .map((element) => ({ element, selector: selector(element), rect: element.getBoundingClientRect(), parent: element.parentElement }));
    const overlaps = [];
    for (let i = 0; i < interactives.length; i += 1) {
      for (let j = i + 1; j < interactives.length; j += 1) {
        const a = interactives[i];
        const b = interactives[j];
        if (a.element.contains(b.element) || b.element.contains(a.element)) continue;
        const area = Math.max(0, Math.min(a.rect.right, b.rect.right) - Math.max(a.rect.left, b.rect.left)) * Math.max(0, Math.min(a.rect.bottom, b.rect.bottom) - Math.max(a.rect.top, b.rect.top));
        const smaller = Math.min(a.rect.width * a.rect.height, b.rect.width * b.rect.height);
        if (area > 64 && smaller > 0 && area / smaller > 0.18) overlaps.push({ a: a.selector, b: b.selector, overlapArea: Math.round(area) });
        if (overlaps.length >= 40) break;
      }
      if (overlaps.length >= 40) break;
    }

    const images = [...document.images].map((image) => ({
      src: image.currentSrc || image.src,
      alt: image.getAttribute('alt'),
      loading: image.getAttribute('loading'),
      widthAttr: image.getAttribute('width'),
      heightAttr: image.getAttribute('height'),
      naturalWidth: image.naturalWidth,
      naturalHeight: image.naturalHeight,
      complete: image.complete,
      visible: visible(image),
    }));
    const schemas = [...document.querySelectorAll('script[type="application/ld+json"]')].map((script, index) => {
      try {
        const parsed = JSON.parse(script.textContent || '{}');
        const nodes = Array.isArray(parsed['@graph']) ? parsed['@graph'] : [parsed];
        return { index, valid: true, types: nodes.map((node) => node && node['@type']).filter(Boolean).flat() };
      } catch (error) {
        return { index, valid: false, error: String(error) };
      }
    });
    const canonical = document.querySelector('link[rel="canonical"]')?.href || null;
    const robots = document.querySelector('meta[name="robots"]')?.content || null;
    const viewport = document.querySelector('meta[name="viewport"]')?.content || null;
    const lang = document.documentElement.getAttribute('lang');
    const headings = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].map((heading) => ({ level: Number(heading.tagName.slice(1)), text: (heading.textContent || '').trim().slice(0, 160) }));
    const links = [...document.querySelectorAll('a[href]')].map((link) => absolute(link.getAttribute('href'))).filter(Boolean).slice(0, maxLinks);
    const forms = [...document.forms].map((form) => ({
      action: absolute(form.getAttribute('action') || location.href),
      method: (form.getAttribute('method') || 'get').toLowerCase(),
      personalInputs: [...form.querySelectorAll('input,textarea,select')].filter((input) => {
        const haystack = `${input.name || ''} ${input.id || ''} ${input.placeholder || ''} ${input.autocomplete || ''}`.toLowerCase();
        return /(^|\s)(name|email|e-mail|phone|tel|address|adres|tc|tckn|abone|subscriber|meter|sayaç)(\s|$)/i.test(haystack) || ['email', 'tel'].includes(input.type);
      }).map((input) => ({ type: input.type, name: input.name, id: input.id, placeholder: input.placeholder })),
    }));
    return {
      title: document.title,
      canonical,
      robots,
      viewport,
      lang,
      h1Count: document.querySelectorAll('h1').length,
      headings,
      documentWidth,
      viewportWidth,
      horizontalOverflow: documentWidth > viewportWidth + 2,
      overflowElements,
      overlaps,
      images,
      schemas,
      links,
      forms,
      bodyTextLength: (document.body?.innerText || '').length,
    };
  }, { maxLinks: MAX_LINKS_PER_PAGE });

  const internalLinks = unique(dom.links.map((url) => normalizeInternalUrl(url, page.url())).filter(Boolean));
  await context.close();
  return {
    profile: profileName,
    path: pagePath,
    requestedUrl,
    finalUrl: page.url(),
    status: navigationStatus,
    navigationError,
    durationMs: Date.now() - started,
    consoleErrors: unique(consoleErrors),
    pageErrors: unique(pageErrors),
    failedRequests,
    badResponses,
    screenshot: screenshotPath,
    axe,
    dom: { ...dom, links: undefined },
    internalLinks,
  };
}

async function checkUrls(urls) {
  const results = [];
  let index = 0;
  const workers = Array.from({ length: 10 }, async () => {
    while (index < urls.length) {
      const currentIndex = index;
      index += 1;
      const url = urls[currentIndex];
      const result = await fetchText(url, { timeout: 25000, accept: 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' });
      results[currentIndex] = {
        requestedUrl: url,
        finalUrl: result.url,
        status: result.status,
        ok: result.ok,
        contentType: result.headers['content-type'] || null,
        error: result.error || null,
      };
    }
  });
  await Promise.all(workers);
  return results;
}

function deriveFindings(report) {
  const findings = [];
  const add = (severity, code, message, evidence = {}) => findings.push({ severity, code, message, evidence });

  if (!report.robots.fetch.ok) add('P0', 'robots-unreachable', 'robots.txt canlı ortamda alınamadı.', report.robots.fetch);
  if (!report.sitemap.fetch.ok) add('P0', 'sitemap-unreachable', 'sitemap.xml canlı ortamda alınamadı.', report.sitemap.fetch);
  if (report.hostRedirects.wwwToApex.some((item) => item.location?.includes('alo186.com')) && report.canonicalHosts.includes('www.alo186.com')) {
    add('P1', 'canonical-host-mismatch', 'Canlı yönlendirme apex alan adına giderken sayfa canonical değerleri www alan adını kullanıyor.', { redirects: report.hostRedirects.wwwToApex, canonicalHosts: report.canonicalHosts });
  }
  for (const page of report.pages) {
    if (page.status >= 400 || page.status === 0) add('P0', 'page-unreachable', `${page.profile} ${page.path} yüklenemedi.`, { status: page.status, error: page.navigationError });
    if (page.dom.horizontalOverflow) add('P1', 'horizontal-overflow', `${page.profile} ${page.path} yatay taşma oluşturuyor.`, { viewport: page.dom.viewportWidth, document: page.dom.documentWidth, elements: page.dom.overflowElements.slice(0, 10) });
    if (page.dom.overlaps.length) add('P1', 'interactive-overlap', `${page.profile} ${page.path} etkileşimli öğelerde olası çakışma bulundu.`, { overlaps: page.dom.overlaps.slice(0, 10) });
    const brokenImages = page.dom.images.filter((image) => image.visible && (!image.complete || image.naturalWidth === 0));
    if (brokenImages.length) add('P1', 'broken-images', `${page.profile} ${page.path} görünür kırık görsel içeriyor.`, { images: brokenImages.slice(0, 10) });
    const missingAlt = page.dom.images.filter((image) => image.visible && image.alt === null);
    if (missingAlt.length) add('P2', 'missing-image-alt', `${page.profile} ${page.path} görünür görsellerde alt niteliği eksik.`, { images: missingAlt.slice(0, 10) });
    const unsized = page.dom.images.filter((image) => image.visible && (!image.widthAttr || !image.heightAttr));
    if (unsized.length) add('P2', 'unsized-images', `${page.profile} ${page.path} görünür görsellerde width/height eksik; CLS riski var.`, { images: unsized.slice(0, 10) });
    if (page.dom.h1Count !== 1) add('P1', 'h1-count', `${page.profile} ${page.path} H1 sayısı ${page.dom.h1Count}.`, {});
    if (!page.dom.canonical) add('P1', 'canonical-missing', `${page.profile} ${page.path} canonical etiketi eksik.`, {});
    if (page.dom.schemas.some((item) => !item.valid)) add('P1', 'invalid-jsonld', `${page.profile} ${page.path} geçersiz JSON-LD içeriyor.`, { schemas: page.dom.schemas });
    if (page.consoleErrors.length || page.pageErrors.length) add('P1', 'runtime-errors', `${page.profile} ${page.path} tarayıcı çalışma zamanı hatası üretiyor.`, { consoleErrors: page.consoleErrors, pageErrors: page.pageErrors });
    if (page.failedRequests.length || page.badResponses.length) add('P1', 'resource-failures', `${page.profile} ${page.path} kaynak isteği başarısız.`, { failedRequests: page.failedRequests.slice(0, 10), badResponses: page.badResponses.slice(0, 10) });
    const seriousAxe = page.axe.violations.filter((item) => ['critical', 'serious'].includes(item.impact));
    if (seriousAxe.length) add('P1', 'accessibility-serious', `${page.profile} ${page.path} ciddi erişilebilirlik ihlalleri içeriyor.`, { violations: seriousAxe });
    if (page.dom.forms.some((form) => form.personalInputs.length)) add('P0', 'personal-data-form', `${page.profile} ${page.path} kişisel veri niteliğinde alan içeriyor.`, { forms: page.dom.forms });
  }
  const broken = report.linkChecks.filter((item) => item.status >= 400 || item.status === 0);
  if (broken.length) add('P1', 'broken-internal-links', `${broken.length} iç bağlantı canlı ortamda başarısız.`, { links: broken.slice(0, 30) });
  const redirected = report.linkChecks.filter((item) => item.requestedUrl !== item.finalUrl);
  if (redirected.length > Math.max(8, report.linkChecks.length * 0.12)) add('P2', 'redirect-heavy-links', 'İç bağlantıların önemli bölümü doğrudan hedef yerine yönlendirmeye gidiyor.', { count: redirected.length, sample: redirected.slice(0, 20) });
  return findings.sort((a, b) => ({ P0: 0, P1: 1, P2: 2, P3: 3 }[a.severity] - ({ P0: 0, P1: 1, P2: 2, P3: 3 }[b.severity]));
}

function markdownReport(report) {
  const lines = [
    '# ALO186 canlı teknik kalite denetimi',
    '',
    `- Origin: ${ORIGIN}`,
    `- Denetlenen sayfa/profil: ${report.pages.length}`,
    `- Sitemap URL: ${report.sitemap.urls.length}`,
    `- Kontrol edilen iç URL: ${report.linkChecks.length}`,
    '',
    '## Bulgular',
    '',
  ];
  if (!report.findings.length) lines.push('P0–P2 düzeyinde otomatik bulgu yok.');
  for (const finding of report.findings) lines.push(`- **${finding.severity} · ${finding.code}:** ${finding.message}`);
  lines.push('', '## Sayfa özeti', '', '| Profil | Sayfa | HTTP | Final URL | Taşma | Axe ciddi | Kırık görsel |', '|---|---|---:|---|---:|---:|---:|');
  for (const page of report.pages) {
    const serious = page.axe.violations.filter((item) => ['critical', 'serious'].includes(item.impact)).length;
    const brokenImages = page.dom.images.filter((image) => image.visible && (!image.complete || image.naturalWidth === 0)).length;
    lines.push(`| ${page.profile} | ${page.path} | ${page.status} | ${page.finalUrl} | ${page.dom.horizontalOverflow ? 'Evet' : 'Hayır'} | ${serious} | ${brokenImages} |`);
  }
  return `${lines.join('\n')}\n`;
}

async function main() {
  await fs.mkdir(OUTPUT, { recursive: true });
  const robotsFetch = await fetchText(`${ORIGIN}/robots.txt`, { accept: 'text/plain,*/*' });
  const sitemapFetch = await fetchText(`${ORIGIN}/sitemap.xml`, { accept: 'application/xml,text/xml,*/*' });
  const sitemapUrls = sitemapFetch.ok ? parseSitemapXml(sitemapFetch.text).filter((url) => normalizeInternalUrl(url)) : [];
  const browser = await chromium.launch({ headless: true });
  const pages = [];
  try {
    for (const profile of Object.keys(profiles)) {
      for (const pagePath of PAGE_PATHS) pages.push(await auditPage(browser, profile, pagePath));
    }
  } finally {
    await browser.close();
  }

  const pageLinks = pages.flatMap((page) => page.internalLinks);
  const linkTargets = unique([...sitemapUrls.slice(0, MAX_SITEMAP_URLS), ...pageLinks]).slice(0, MAX_SITEMAP_URLS + 300);
  const linkChecks = await checkUrls(linkTargets);
  const canonicalHosts = unique(pages.map((page) => {
    try { return new URL(page.dom.canonical).hostname; } catch { return null; }
  }).filter(Boolean));
  const report = {
    generatedAt: new Date().toISOString(),
    origin: ORIGIN,
    hostRedirects: {
      wwwToApex: await traceRedirects('https://www.alo186.com/'),
      apex: await traceRedirects('https://alo186.com/'),
    },
    canonicalHosts,
    robots: { fetch: { ok: robotsFetch.ok, status: robotsFetch.status, finalUrl: robotsFetch.url, error: robotsFetch.error || null }, directives: parseRobots(robotsFetch.text), text: robotsFetch.text },
    sitemap: { fetch: { ok: sitemapFetch.ok, status: sitemapFetch.status, finalUrl: sitemapFetch.url, error: sitemapFetch.error || null }, urls: sitemapUrls },
    pages,
    linkChecks,
  };
  report.findings = deriveFindings(report);
  await fs.writeFile(path.join(OUTPUT, 'report.json'), JSON.stringify(report, null, 2));
  await fs.writeFile(path.join(OUTPUT, 'report.md'), markdownReport(report));
  console.log(markdownReport(report));
  const p0 = report.findings.filter((item) => item.severity === 'P0');
  if (p0.length && process.env.ALO186_AUDIT_FAIL_P0 === '1') process.exitCode = 1;
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
