(() => {
  'use strict';

  const doc = document;
  const body = doc.body;
  const script = doc.currentScript;
  if (!body || body.dataset.alo186Ux === 'ready') return;
  body.dataset.alo186Ux = 'ready';

  const configuredBase = script?.dataset.basePath || '';
  const basePath = configuredBase === '/' ? '' : configuredBase.replace(/\/+$/, '');
  const route = (path) => {
    const normalized = path.startsWith('/') ? path : `/${path}`;
    return `${basePath}${normalized}` || '/';
  };
  const localPath = (path) => {
    let normalized = path || '/';
    if (basePath && normalized.startsWith(basePath)) normalized = normalized.slice(basePath.length) || '/';
    return normalized.replace(/\/$/, '') || '/';
  };

  const main = doc.querySelector('main');
  if (main && !main.id) main.id = 'main-content';
  if (main) {
    const targetHash = `#${main.id}`;
    const hasMatchingSkip = [...doc.querySelectorAll('a[href^="#"]')]
      .some((link) => link.hash === targetHash);
    if (!hasMatchingSkip) {
      const skip = doc.createElement('a');
      skip.className = 'alo-ux-skip';
      skip.href = targetHash;
      skip.textContent = 'İçeriğe geç';
      body.prepend(skip);
    }
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
        wrapper.setAttribute('aria-label', table.querySelector('caption')?.textContent?.trim() || 'Yatay kaydırılabilir tablo');
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

  const current = localPath(location.pathname);
  doc.querySelectorAll('a[href^="/"]').forEach((link) => {
    const target = localPath(new URL(link.href, location.origin).pathname);
    if (target === current) link.setAttribute('aria-current', 'page');
  });

  if (!doc.querySelector('[data-alo186-mobilebar="true"]')) {
    const nav = doc.createElement('nav');
    nav.className = 'alo-ux-mobilebar';
    nav.dataset.alo186Mobilebar = 'true';
    nav.setAttribute('aria-label', 'Mobil hızlı erişim');
    nav.innerHTML = [
      ['/', '⌂', 'Ana sayfa'],
      ['/edas-bul', '186', 'EDAŞ bul'],
      ['/arama/', '⌕', 'Ara'],
      ['/acil-numaralar/', '!', 'Acil'],
    ].map(([href, icon, label]) => `<a href="${route(href)}"><b aria-hidden="true">${icon}</b><span>${label}</span></a>`).join('');
    body.appendChild(nav);
  }

  if (!doc.querySelector('[data-alo186-backtop="true"]')) {
    const top = doc.createElement('button');
    top.type = 'button';
    top.className = 'alo-ux-backtop';
    top.dataset.alo186Backtop = 'true';
    top.setAttribute('aria-label', 'Sayfanın başına dön');
    top.textContent = '↑';
    top.addEventListener('click', () => window.scrollTo({
      top: 0,
      behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
    }));
    body.appendChild(top);
    const updateTop = () => { top.dataset.visible = String(window.scrollY > 700); };
    updateTop();
    addEventListener('scroll', updateTop, { passive: true });
  }
})();
