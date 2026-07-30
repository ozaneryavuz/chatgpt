(() => {
  'use strict';
  const doc = document;
  const body = doc.body;
  if (!body || body.dataset.alo186Ux === 'ready') return;
  body.dataset.alo186Ux = 'ready';

  const main = doc.querySelector('main');
  if (main && !main.id) main.id = 'main-content';
  if (main && !doc.querySelector('a[href="#main-content"],a[href="#content"],a[href="#main"]')) {
    const skip = doc.createElement('a');
    skip.className = 'alo-ux-skip';
    skip.href = `#${main.id}`;
    skip.textContent = 'İçeriğe geç';
    body.prepend(skip);
  }

  doc.querySelectorAll('table').forEach((table) => {
    if (table.parentElement?.classList.contains('alo-table-scroll')) return;
    const wrapper = doc.createElement('div');
    wrapper.className = 'alo-table-scroll';
    wrapper.tabIndex = 0;
    wrapper.setAttribute('role', 'region');
    wrapper.setAttribute('aria-label', table.querySelector('caption')?.textContent?.trim() || 'Kaydırılabilir tablo');
    table.parentNode.insertBefore(wrapper, table);
    wrapper.appendChild(table);
  });

  doc.querySelectorAll('img').forEach((image, index) => {
    if (index > 0 && !image.hasAttribute('loading')) image.loading = 'lazy';
    if (!image.hasAttribute('decoding')) image.decoding = 'async';
    if (!image.hasAttribute('alt')) {
      const caption = image.closest('figure')?.querySelector('figcaption')?.textContent?.trim();
      const label = image.getAttribute('aria-label') || image.getAttribute('title') || caption || '';
      image.alt = label;
      image.dataset.alo186AltFallback = label ? 'derived' : 'decorative';
    }
  });

  doc.querySelectorAll('a[target="_blank"]').forEach((link) => {
    const rel = new Set((link.getAttribute('rel') || '').split(/\s+/).filter(Boolean));
    rel.add('noopener');
    rel.add('noreferrer');
    link.setAttribute('rel', [...rel].join(' '));
  });

  const current = location.pathname.replace(/\/$/, '') || '/';
  doc.querySelectorAll('a[href^="/"]').forEach((link) => {
    const target = new URL(link.href, location.origin).pathname.replace(/\/$/, '') || '/';
    if (target === current) link.setAttribute('aria-current', 'page');
  });

  const headings = main ? [...main.querySelectorAll('h2')].filter((heading) => heading.textContent.trim()) : [];
  if (main && headings.length >= 4 && main.textContent.trim().length > 2600 && !main.querySelector('.alo-ux-toc')) {
    const slugCounts = new Map();
    headings.forEach((heading, index) => {
      if (heading.id) return;
      const base = heading.textContent.trim().toLocaleLowerCase('tr-TR')
        .normalize('NFKD').replace(/[\u0300-\u036f]/g, '')
        .replace(/[^a-z0-9çğıöşü]+/gi, '-').replace(/^-|-$/g, '') || `bolum-${index + 1}`;
      const count = (slugCounts.get(base) || 0) + 1;
      slugCounts.set(base, count);
      heading.id = count === 1 ? base : `${base}-${count}`;
    });
    const toc = doc.createElement('details');
    toc.className = 'alo-ux-toc';
    toc.innerHTML = '<summary>Bu sayfada neler var?</summary><nav aria-label="Sayfa içeriği"></nav>';
    const nav = toc.querySelector('nav');
    headings.slice(0, 12).forEach((heading) => {
      const link = doc.createElement('a');
      link.href = `#${heading.id}`;
      link.textContent = heading.textContent.trim();
      nav.appendChild(link);
    });
    const h1 = main.querySelector('h1');
    const anchor = h1?.closest('section,article,header') || h1;
    if (anchor?.parentNode) anchor.parentNode.insertBefore(toc, anchor.nextSibling);
    else main.prepend(toc);
  }

  const nav = doc.createElement('nav');
  nav.className = 'alo-ux-mobilebar';
  nav.setAttribute('aria-label', 'Mobil hızlı erişim');
  nav.innerHTML = [
    ['/', '⌂', 'Ana sayfa'],
    ['/edas-bul', '186', 'EDAŞ bul'],
    ['/arama/', '⌕', 'Ara'],
    ['/acil-numaralar/', '!', 'Acil']
  ].map(([href, icon, label]) => `<a href="${href}"><b aria-hidden="true">${icon}</b><span>${label}</span></a>`).join('');
  body.appendChild(nav);

  const top = doc.createElement('button');
  top.type = 'button';
  top.className = 'alo-ux-backtop';
  top.setAttribute('aria-label', 'Sayfanın başına dön');
  top.textContent = '↑';
  top.addEventListener('click', () => window.scrollTo({ top: 0, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' }));
  body.appendChild(top);
  const updateTop = () => { top.dataset.visible = String(window.scrollY > 700); };
  updateTop();
  addEventListener('scroll', updateTop, { passive: true });
})();