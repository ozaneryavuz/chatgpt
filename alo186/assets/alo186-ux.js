(() => {
  'use strict';
  const doc = document;
  const body = doc.body;
  if (!body || body.dataset.alo186Ux === 'ready') return;
  body.dataset.alo186Ux = 'ready';

  const isEnglish = (doc.documentElement.lang || 'tr').toLowerCase().startsWith('en');
  const main = doc.querySelector('main');
  if (main && !main.id) main.id = 'main-content';
  if (main && !doc.querySelector(`a[href="#${CSS.escape(main.id)}"]`)) {
    const skip = doc.createElement('a');
    skip.className = 'alo-ux-skip';
    skip.href = `#${main.id}`;
    skip.textContent = isEnglish ? 'Skip to content' : 'İçeriğe geç';
    body.prepend(skip);
  }

  doc.querySelectorAll('table').forEach((table) => {
    if (table.parentElement?.classList.contains('alo-table-scroll')) return;
    const wrapper = doc.createElement('div');
    wrapper.className = 'alo-table-scroll';
    table.parentNode.insertBefore(wrapper, table);
    wrapper.appendChild(table);

    const syncOverflow = () => {
      const overflowing = table.scrollWidth > wrapper.clientWidth + 1;
      wrapper.tabIndex = overflowing ? 0 : -1;
      wrapper.dataset.overflow = String(overflowing);
      if (overflowing) {
        wrapper.setAttribute('role', 'region');
        wrapper.setAttribute('aria-label', table.querySelector('caption')?.textContent?.trim() || (isEnglish ? 'Horizontally scrollable table' : 'Yatay kaydırılabilir tablo'));
      } else {
        wrapper.removeAttribute('role');
        wrapper.removeAttribute('aria-label');
      }
    };
    requestAnimationFrame(syncOverflow);
    if ('ResizeObserver' in window) {
      const observer = new ResizeObserver(syncOverflow);
      observer.observe(wrapper);
      observer.observe(table);
    } else {
      addEventListener('resize', syncOverflow, { passive: true });
    }
  });

  doc.querySelectorAll('img').forEach((image, index) => {
    const critical = index === 0
      || image.loading === 'eager'
      || image.fetchPriority === 'high'
      || Boolean(image.closest('header,.hero,[data-critical-media]'));
    if (!critical && !image.hasAttribute('loading')) image.loading = 'lazy';
    if (!image.hasAttribute('decoding')) image.decoding = 'async';
  });

  doc.querySelectorAll('a[target="_blank"]').forEach((link) => {
    const rel = new Set((link.getAttribute('rel') || '').split(/\s+/).filter(Boolean));
    rel.add('noopener');
    rel.add('noreferrer');
    link.setAttribute('rel', [...rel].join(' '));
  });

  const normalizePath = (value) => value.replace(/\/+$/, '') || '/';
  const scriptUrl = new URL(doc.currentScript?.src || location.href, location.href);
  const assetSuffix = '/assets/alo186-ux.js';
  const basePath = scriptUrl.pathname.endsWith(assetSuffix)
    ? scriptUrl.pathname.slice(0, -assetSuffix.length)
    : '';
  const publicPath = (route) => `${basePath}${route === '/' ? '/' : route}`.replace(/\/+/g, '/');
  const current = normalizePath(location.pathname);
  const markCurrent = (root = doc) => {
    root.querySelectorAll('a[href^="/"]').forEach((link) => {
      const target = normalizePath(new URL(link.href, location.origin).pathname);
      if (target === current) link.setAttribute('aria-current', 'page');
    });
  };
  markCurrent();

  const robots = doc.querySelector('meta[name="robots"]')?.content?.toLowerCase() || '';
  const isIndexable = !robots.includes('noindex');
  const isTurkish = !isEnglish;
  if (isIndexable && isTurkish) {
    const nav = doc.createElement('nav');
    nav.className = 'alo-ux-mobilebar';
    nav.setAttribute('aria-label', 'Mobil hızlı erişim');
    nav.innerHTML = [
      [publicPath('/'), '⌂', 'Ana sayfa'],
      [publicPath('/edas-bul/'), '186', 'EDAŞ bul'],
      [publicPath('/arama/'), '⌕', 'Ara'],
      [publicPath('/acil-numaralar/'), '!', 'Acil']
    ].map(([href, icon, label]) => `<a href="${href}"><b aria-hidden="true">${icon}</b><span>${label}</span></a>`).join('');
    body.appendChild(nav);
    markCurrent(nav);
  } else {
    body.dataset.alo186UxCompact = 'true';
  }

  const top = doc.createElement('button');
  top.type = 'button';
  top.className = 'alo-ux-backtop';
  top.setAttribute('aria-label', isTurkish ? 'Sayfanın başına dön' : 'Back to top');
  top.textContent = '↑';
  top.addEventListener('click', () => window.scrollTo({ top: 0, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' }));
  body.appendChild(top);
  const updateTop = () => { top.dataset.visible = String(window.scrollY > 700); };
  updateTop();
  addEventListener('scroll', updateTop, { passive: true });
})();
