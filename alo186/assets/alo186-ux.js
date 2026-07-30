(() => {
  'use strict';

  const doc = document;
  const body = doc.body;
  if (!body || body.dataset.alo186Ux === 'ready') return;
  body.dataset.alo186Ux = 'ready';

  const slash = String.fromCharCode(47);
  const language = (doc.documentElement.lang || 'tr').toLowerCase();
  const isEnglish = language.startsWith('en');
  const isTurkish = !isEnglish;
  const copy = {
    skip: isEnglish ? 'Skip to content' : 'İçeriğe geç',
    table: isEnglish ? 'Horizontally scrollable table' : 'Yatay kaydırılabilir tablo',
    tableSuffix: isEnglish ? ' table' : ' tablosu',
    toc: isEnglish ? 'On this page' : 'Bu sayfada neler var?',
    tocLabel: isEnglish ? 'Page contents' : 'Sayfa içeriği',
    mobileNav: isEnglish ? 'Mobile quick access' : 'Mobil hızlı erişim',
    home: isEnglish ? 'Home' : 'Ana sayfa',
    search: isEnglish ? 'Search' : 'Ara',
    emergency: isEnglish ? 'Emergency' : 'Acil',
    edas: isEnglish ? 'Find distributor' : 'EDAŞ bul',
    backTop: isEnglish ? 'Back to top' : 'Sayfanın başına dön',
    primaryAction: isEnglish ? 'Open the primary recommended action' : 'Birincil önerilen işlemi aç',
    secondaryAction: isEnglish ? 'Open the secondary recommended action' : 'İkinci önerilen işlemi aç',
    productLink: isEnglish ? 'Open the product selection guide' : 'Ürün seçim rehberini aç',
    actionLink: isEnglish ? 'Open the recommended action' : 'Önerilen işlemi aç',
  };

  const main = doc.querySelector('main');
  if (main && !main.id) main.id = 'main-content';
  if (main && !doc.querySelector(`a[href="#${CSS.escape(main.id)}"]`)) {
    const skip = doc.createElement('a');
    skip.className = 'alo-ux-skip';
    skip.href = `#${main.id}`;
    skip.textContent = copy.skip;
    body.prepend(skip);
  }

  const tableLabel = (table) => {
    const caption = table.querySelector('caption')?.textContent?.trim();
    if (caption) return caption;
    const labelledBy = table.getAttribute('aria-labelledby');
    if (labelledBy) {
      const label = labelledBy.split(/\s+/).map((id) => doc.getElementById(id)?.textContent?.trim()).filter(Boolean).join(' · ');
      if (label) return label;
    }
    const container = table.closest('section,article,main');
    const heading = container?.querySelector('h2,h3,h4');
    return heading?.textContent?.trim() ? `${heading.textContent.trim()}${copy.tableSuffix}` : copy.table;
  };

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
        wrapper.setAttribute('aria-label', tableLabel(table));
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
    if (!image.hasAttribute('alt')) {
      const caption = image.closest('figure')?.querySelector('figcaption')?.textContent?.trim();
      const label = image.getAttribute('aria-label') || image.getAttribute('title') || caption || '';
      image.alt = label;
      image.dataset.alo186AltFallback = label ? 'derived' : 'decorative';
    }
  });

  const hasLabel = (control) => {
    if ((control.getAttribute('aria-label') || '').trim()) return true;
    if ((control.getAttribute('aria-labelledby') || '').trim()) return true;
    if (control.closest('label')) return true;
    const id = control.id;
    return Boolean(id && doc.querySelector(`label[for="${CSS.escape(id)}"]`));
  };

  const cleanLabel = (value) => String(value || '').replace(/\s+/g, ' ').trim().slice(0, 140);
  const deriveControlLabel = (control) => {
    const fieldsetLegend = control.closest('fieldset')?.querySelector('legend')?.textContent;
    if (cleanLabel(fieldsetLegend)) return cleanLabel(fieldsetLegend);
    const item = control.closest('.item,.field,.form-row,.control,.input-group');
    const itemLabel = item?.querySelector('strong,.label,[data-label],h2,h3,h4')?.textContent;
    if (cleanLabel(itemLabel)) return cleanLabel(itemLabel);
    const previous = control.previousElementSibling?.textContent;
    if (cleanLabel(previous)) return cleanLabel(previous);
    const raw = control.getAttribute('name') || control.id || control.getAttribute('data-id');
    return cleanLabel(raw?.replace(/[-_]+/g, ' '));
  };

  doc.querySelectorAll('select,textarea,input:not([type="hidden"]):not([type="button"]):not([type="submit"]):not([type="reset"])').forEach((control) => {
    if (hasLabel(control)) return;
    const label = deriveControlLabel(control);
    if (!label) return;
    control.setAttribute('aria-label', label);
    control.dataset.alo186LabelFallback = 'derived';
  });

  const fallbackLinkLabels = {
    primaryAction: copy.primaryAction,
    secondaryAction: copy.secondaryAction,
    productLink: copy.productLink,
  };
  const syncLinkName = (link) => {
    const visibleName = cleanLabel(link.textContent);
    const href = link.getAttribute('href') || '';
    if (visibleName) {
      if (link.dataset.alo186LinkFallback === 'true') {
        link.removeAttribute('aria-label');
        link.removeAttribute('aria-disabled');
        link.removeAttribute('tabindex');
        delete link.dataset.alo186LinkFallback;
      }
      return;
    }
    if ((link.getAttribute('aria-label') || '').trim() || (link.getAttribute('title') || '').trim()) return;
    if (href !== '#') return;
    link.setAttribute('aria-label', fallbackLinkLabels[link.id] || copy.actionLink);
    link.setAttribute('aria-disabled', 'true');
    link.tabIndex = -1;
    link.dataset.alo186LinkFallback = 'true';
  };

  doc.querySelectorAll('a[href]').forEach((link) => {
    syncLinkName(link);
    if (link.dataset.alo186LinkFallback === 'true' && 'MutationObserver' in window) {
      const observer = new MutationObserver(() => syncLinkName(link));
      observer.observe(link, { childList: true, subtree: true, attributes: true, attributeFilter: ['href', 'aria-label'] });
    }
  });

  doc.querySelectorAll('a[target="_blank"]').forEach((link) => {
    const rel = new Set((link.getAttribute('rel') || '').split(/\s+/).filter(Boolean));
    rel.add('noopener');
    rel.add('noreferrer');
    link.setAttribute('rel', [...rel].join(' '));
  });

  const normalizePath = (value) => value.replace(/\/+$/, '') || slash;
  const filePath = (...parts) => `${slash}${parts.filter(Boolean).join(slash)}`;
  const routePath = (...parts) => `${filePath(...parts)}${slash}`;
  const scriptUrl = new URL(doc.currentScript?.src || location.href, location.href);
  const assetSuffix = filePath('assets', 'alo186-ux.js');
  const basePath = scriptUrl.pathname.endsWith(assetSuffix) ? scriptUrl.pathname.slice(0, -assetSuffix.length) : '';
  const publicPath = (route) => `${basePath}${route === slash ? slash : route}`.replace(/\/+/g, slash);
  const current = normalizePath(location.pathname);
  const markCurrent = (root = doc) => {
    root.querySelectorAll('a[href]').forEach((link) => {
      const raw = link.getAttribute('href') || '';
      if (!raw.startsWith(slash)) return;
      const target = normalizePath(new URL(link.href, location.origin).pathname);
      if (target === current) link.setAttribute('aria-current', 'page');
    });
  };
  markCurrent();

  const robots = doc.querySelector('meta[name="robots"]')?.content?.toLowerCase() || '';
  const isIndexable = !robots.includes('noindex');
  const headings = main ? [...main.querySelectorAll('h2')].filter((heading) => heading.textContent.trim()) : [];
  if (main && isIndexable && headings.length >= 4 && main.textContent.trim().length > 2600 && !main.querySelector('.alo-ux-toc')) {
    const usedIds = new Set([...doc.querySelectorAll('[id]')].map((node) => node.id).filter(Boolean));
    headings.forEach((heading, index) => {
      if (heading.id) return;
      const raw = heading.textContent.trim().toLocaleLowerCase(isTurkish ? 'tr-TR' : 'en-US')
        .normalize('NFKD').replace(/[\u0300-\u036f]/g, '')
        .replace(/[^a-z0-9çğıöşü]+/gi, '-').replace(/^-|-$/g, '') || `section-${index + 1}`;
      let candidate = raw;
      let suffix = 2;
      while (usedIds.has(candidate)) candidate = `${raw}-${suffix++}`;
      heading.id = candidate;
      usedIds.add(candidate);
    });

    const toc = doc.createElement('details');
    toc.className = 'alo-ux-toc';
    toc.innerHTML = `<summary>${copy.toc}</summary><nav aria-label="${copy.tocLabel}"></nav>`;
    const tocNav = toc.querySelector('nav');
    headings.slice(0, 12).forEach((heading) => {
      const link = doc.createElement('a');
      link.href = `#${heading.id}`;
      link.textContent = heading.textContent.trim();
      tocNav.appendChild(link);
    });
    const h1 = main.querySelector('h1');
    const anchor = h1?.closest('section,article,header') || h1;
    if (anchor?.parentNode) anchor.parentNode.insertBefore(toc, anchor.nextSibling);
    else main.prepend(toc);
  }

  const existingDock = doc.querySelector('.mobile-dock,.bottom-dock,[data-mobile-dock="true"]');
  if (existingDock) {
    body.dataset.alo186UxNativeDock = 'true';
  } else if (isIndexable && isTurkish) {
    const nav = doc.createElement('nav');
    nav.className = 'alo-ux-mobilebar';
    nav.setAttribute('aria-label', copy.mobileNav);
    const links = [
      [slash, '⌂', copy.home],
      [routePath('edas-bul'), '186', copy.edas],
      [routePath('arama'), '⌕', copy.search],
      [routePath('acil-numaralar'), '112', copy.emergency],
    ];
    nav.innerHTML = links.map(([route, icon, label]) => `<a href="${publicPath(route)}"><b aria-hidden="true">${icon}</b><span>${label}</span></a>`).join('');
    body.appendChild(nav);
    markCurrent(nav);
  } else {
    body.dataset.alo186UxCompact = 'true';
  }

  const consentSettings = doc.getElementById('alo186-consent-settings');
  if (consentSettings && 'MutationObserver' in window) {
    const syncConsent = () => {
      body.dataset.alo186ConsentSettingsVisible = String(consentSettings.dataset.visible === 'true');
    };
    syncConsent();
    new MutationObserver(syncConsent).observe(consentSettings, { attributes: true, attributeFilter: ['data-visible'] });
  }

  const top = doc.createElement('button');
  top.type = 'button';
  top.className = 'alo-ux-backtop';
  top.setAttribute('aria-label', copy.backTop);
  top.textContent = '↑';
  top.tabIndex = -1;
  top.addEventListener('click', () => window.scrollTo({ top: 0, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' }));
  body.appendChild(top);

  let scrollFrame = 0;
  const updateTop = () => {
    scrollFrame = 0;
    const visible = window.scrollY > 700;
    top.dataset.visible = String(visible);
    top.tabIndex = visible ? 0 : -1;
    top.setAttribute('aria-hidden', String(!visible));
  };
  const queueTopUpdate = () => {
    if (!scrollFrame) scrollFrame = requestAnimationFrame(updateTop);
  };
  updateTop();
  addEventListener('scroll', queueTopUpdate, { passive: true });
})();
