(() => {
  'use strict';

  const doc = document;
  const body = doc.body;
  if (!body || body.dataset.alo186Ux === 'ready') return;
  body.dataset.alo186Ux = 'ready';

  const runtimeScript = doc.currentScript || doc.querySelector('script[data-alo186-sitewide-ux="true"]');
  const normalizeBase = (value) => {
    const clean = String(value || '').trim();
    if (!clean || clean === '/') return '';
    return `/${clean.replace(/^\/+|\/+$/g, '')}`;
  };
  const basePath = normalizeBase(runtimeScript?.dataset.basePath || '');
  const isEnglish = (doc.documentElement.lang || '').toLowerCase().startsWith('en');
  const labels = isEnglish ? {
    skip: 'Skip to content',
    table: 'Scrollable table',
    top: 'Back to top',
    mobile: 'Mobile quick access',
    affiliate: 'Affiliate',
    toc: 'On this page',
    nextTitle: 'Continue with the right next step',
    nextIntro: 'Choose a verified route instead of starting the same search again.',
    trust: 'ALO186 is an independent information platform. It does not create official outage or application records.'
  } : {
    skip: 'İçeriğe geç',
    table: 'Kaydırılabilir tablo',
    top: 'Sayfanın başına dön',
    mobile: 'Mobil hızlı erişim',
    affiliate: 'Satış ortaklığı',
    toc: 'Bu sayfada',
    nextTitle: 'Sonraki doğru adım',
    nextIntro: 'Aynı aramayı baştan yapmak yerine doğrulanmış bir devam rotası seçin.',
    trust: 'ALO186 bağımsız bilgi platformudur; resmî başvuru, arıza veya ihbar kaydı oluşturmaz.'
  };
  const noindex = /noindex/i.test(doc.querySelector('meta[name="robots"]')?.content || '');

  const withBase = (route) => {
    if (!route || /^(?:https?:|mailto:|tel:|#)/i.test(route)) return route;
    let path = route.startsWith('/') ? route : `/${route}`;
    if (basePath && (path === basePath || path.startsWith(`${basePath}/`))) return path;
    if (!basePath) return path;
    return path === '/' ? `${basePath}/` : `${basePath}${path}`;
  };
  const stripBase = (pathname) => {
    if (!basePath) return pathname || '/';
    if (pathname === basePath) return '/';
    if (pathname.startsWith(`${basePath}/`)) return pathname.slice(basePath.length) || '/';
    return pathname || '/';
  };
  const normalizePath = (pathname) => {
    const clean = (pathname || '/').replace(/\/{2,}/g, '/');
    return clean === '/' ? '/' : clean.replace(/\/$/, '');
  };
  const currentPath = normalizePath(stripBase(location.pathname));

  const main = doc.querySelector('main');
  if (main && !main.id) main.id = 'main-content';
  if (main && !doc.querySelector('a[href="#main-content"],a[href="#content"],a[href="#main"]')) {
    const skip = doc.createElement('a');
    skip.className = 'alo-ux-skip';
    skip.href = `#${main.id}`;
    skip.textContent = labels.skip;
    body.prepend(skip);
  }

  doc.querySelectorAll('table').forEach((table) => {
    if (table.parentElement?.classList.contains('alo-table-scroll')) return;
    const wrapper = doc.createElement('div');
    wrapper.className = 'alo-table-scroll';
    wrapper.tabIndex = 0;
    wrapper.setAttribute('role', 'region');
    wrapper.setAttribute('aria-label', table.querySelector('caption')?.textContent?.trim() || labels.table);
    table.parentNode?.insertBefore(wrapper, table);
    wrapper.appendChild(table);
  });

  doc.querySelectorAll('img').forEach((image, index) => {
    if (index > 0 && !image.hasAttribute('loading') && image.getAttribute('fetchpriority') !== 'high') image.loading = 'lazy';
    if (!image.hasAttribute('decoding')) image.decoding = 'async';
  });

  const relSet = (link) => new Set((link.getAttribute('rel') || '').split(/\s+/).filter(Boolean));
  const hardenAnchor = (link) => {
    if (!(link instanceof HTMLAnchorElement) || !link.href) return;
    let url;
    try { url = new URL(link.href, location.href); } catch (_) { return; }
    const rel = relSet(link);
    if (link.target === '_blank') {
      rel.add('noopener');
      rel.add('noreferrer');
    }
    const host = url.hostname.toLowerCase().replace(/^www\./, '');
    const amazon = host === 'amazon.com.tr' || host.endsWith('.amazon.com.tr') || host === 'amzn.to';
    if (amazon) {
      rel.add('sponsored');
      rel.add('nofollow');
      rel.add('noopener');
      link.dataset.aloAffiliate = 'true';
      const text = (link.textContent || '').trim();
      if (!/amazon|satış ortaklığı|affiliate/i.test(text)) {
        link.dataset.aloAffiliateBadge = 'true';
        link.dataset.aloAffiliateLabel = labels.affiliate;
        if (!link.getAttribute('aria-label')) link.setAttribute('aria-label', `${text || 'Amazon'} — ${labels.affiliate}`);
      }
    }
    const nextRel = [...rel].join(' ');
    if (nextRel && nextRel !== link.getAttribute('rel')) link.setAttribute('rel', nextRel);
  };
  const hardenLinks = (root) => {
    if (root instanceof HTMLAnchorElement) hardenAnchor(root);
    root.querySelectorAll?.('a').forEach(hardenAnchor);
  };
  hardenLinks(doc);
  const observer = new MutationObserver((records) => {
    for (const record of records) {
      if (record.type === 'attributes') hardenAnchor(record.target);
      for (const node of record.addedNodes || []) if (node.nodeType === Node.ELEMENT_NODE) hardenLinks(node);
    }
  });
  observer.observe(body, { subtree: true, childList: true, attributes: true, attributeFilter: ['href', 'target', 'rel'] });

  const markCurrentLinks = (root = doc) => {
    root.querySelectorAll('a[href]').forEach((link) => {
      let url;
      try { url = new URL(link.href, location.href); } catch (_) { return; }
      if (url.origin !== location.origin) return;
      const target = normalizePath(stripBase(url.pathname));
      if (target === currentPath) link.setAttribute('aria-current', 'page');
    });
  };
  markCurrentLinks();

  const mobileItems = isEnglish ? [
    ['/en/', '⌂', 'Home'],
    ['/en/electricity-distribution-company-finder/', '186', 'Distributor'],
    ['/en/electricity-outage-turkey/', '↯', 'Outage'],
    ['/en/emergency-numbers-turkey/', '!', 'Emergency']
  ] : [
    ['/', '⌂', 'Ana sayfa'],
    ['/edas-bul', '186', 'EDAŞ bul'],
    ['/arama/', '⌕', 'Ara'],
    ['/acil-numaralar/', '!', 'Acil']
  ];
  if (!noindex) {
    const nav = doc.createElement('nav');
    nav.className = 'alo-ux-mobilebar';
    nav.setAttribute('aria-label', labels.mobile);
    for (const [href, icon, label] of mobileItems) {
      const link = doc.createElement('a');
      link.href = withBase(href);
      const symbol = doc.createElement('b');
      symbol.setAttribute('aria-hidden', 'true');
      symbol.textContent = icon;
      const text = doc.createElement('span');
      text.textContent = label;
      link.append(symbol, text);
      nav.appendChild(link);
    }
    body.appendChild(nav);
    markCurrentLinks(nav);
  }

  const slugify = (value) => String(value || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9ğüşöçıİ]+/gi, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 72) || 'bolum';

  const addLongPageToc = () => {
    if (!main || noindex || main.querySelector('[data-alo186-toc="true"],.toc,nav[aria-label*="Bu sayfada"],nav[aria-label*="On this page"]')) return;
    const longContent = currentPath.startsWith('/haberler/') || currentPath.startsWith('/sektor-rehberi/') || currentPath === '/mevzuat' || currentPath.startsWith('/en/');
    if (!longContent) return;
    const headings = [...main.querySelectorAll('h2')].filter((heading) => !heading.closest('.alo-ux-next,nav,footer'));
    if (headings.length < 4 || headings.length > 30) return;
    const used = new Set([...doc.querySelectorAll('[id]')].map((node) => node.id));
    headings.forEach((heading, index) => {
      if (heading.id) return;
      const base = slugify(heading.textContent);
      let id = base;
      let suffix = 2;
      while (used.has(id)) id = `${base}-${suffix++}`;
      heading.id = id || `bolum-${index + 1}`;
      used.add(heading.id);
    });
    const details = doc.createElement('details');
    details.className = 'alo-ux-toc';
    details.dataset.alo186Toc = 'true';
    const summary = doc.createElement('summary');
    summary.textContent = labels.toc;
    const list = doc.createElement('ol');
    headings.slice(0, 18).forEach((heading) => {
      const item = doc.createElement('li');
      const link = doc.createElement('a');
      link.href = `#${heading.id}`;
      link.textContent = heading.textContent?.trim() || heading.id;
      item.appendChild(link);
      list.appendChild(item);
    });
    const nav = doc.createElement('nav');
    nav.setAttribute('aria-label', labels.toc);
    nav.appendChild(list);
    details.append(summary, nav);
    const h1 = main.querySelector('h1');
    const hero = h1?.closest('.hero');
    if (hero && hero.parentElement) hero.insertAdjacentElement('afterend', details);
    else if (h1) h1.insertAdjacentElement('afterend', details);
    else main.prepend(details);
  };

  const journeyData = () => {
    if (isEnglish) {
      if (currentPath.includes('affiliate')) return [
        ['/en/affiliate-disclosure/', 'Affiliate disclosure', 'See how commercial links are labelled.'],
        ['/en/editorial-methodology/', 'Editorial methodology', 'Review how sources and boundaries are handled.'],
        ['/en/contact/', 'Report an issue', 'Tell us about an incorrect or outdated route.']
      ];
      return [
        ['/en/electricity-outage-turkey/', 'Check an outage', 'Use the official distribution route for your location.'],
        ['/en/electricity-distribution-company-finder/', 'Find the distributor', 'Identify the authorised electricity distribution company.'],
        ['/en/emergency-numbers-turkey/', 'Emergency numbers', 'Separate 112 emergencies from the 186 outage line.']
      ];
    }
    if (currentPath.startsWith('/hesaplama/')) return [
      ['/hesaplama/', 'Tüm hesaplayıcılar', 'Başka bir teknik hesabı aynı merkezden açın.'],
      ['/hesaplama/cozum-sonucu/', 'Sonucu takip edin', 'Uygulamanın işe yarayıp yaramadığını kişisel veri vermeden kaydedin.'],
      ['/akilli-urun-secimi', 'Ürün gerekliyse önce uygunluğu doğrulayın', 'Fiyat yerine gerçek teknik eksik üzerinden ilerleyin.']
    ];
    if (currentPath.startsWith('/amazon-elektrik-urunleri') || currentPath.startsWith('/urun-') || currentPath.startsWith('/affiliate-') || currentPath === '/akilli-urun-secimi') return [
      ['/akilli-urun-secimi', 'Akıllı ürün seçimi', 'Mevcut ürünün yeterli olup olmadığını önce kontrol edin.'],
      ['/katalog-guven-durumu', 'Katalog güven durumu', 'Doğrulama tarihi ve ticari sınırları görün.'],
      ['/yasal/amazon-satis-ortakligi', 'Satış ortaklığı açıklaması', 'Affiliate ilişkinin nasıl işlediğini inceleyin.']
    ];
    if (currentPath.startsWith('/haberler/') || currentPath.startsWith('/sektor-rehberi/') || currentPath === '/mevzuat') return [
      ['/arama/', 'Benzer konuyu teknik aramada bulun', 'Aynı sorunun araç, rehber ve resmî kaynaklarını birlikte görün.'],
      ['/mevzuat/', 'Mevzuatı resmî kaynaktan doğrulayın', 'Güncel ve mülga düzenlemeleri ayırarak ilerleyin.'],
      ['/elektrik-durum-merkezi/', 'Belirtiyi sınıflandırın', '112, 186, elektrikçi veya teknik araç rotasını ayırın.']
    ];
    if (currentPath.includes('kesinti') || currentPath === '/edas-bul' || currentPath.startsWith('/acil-')) return [
      ['/elektrik-durum-merkezi/', 'Durumu sınıflandırın', 'Tehlike, şebeke ve iç tesisat ayrımını yapın.'],
      ['/edas-bul', 'Yetkili dağıtım şirketini bulun', '81 il için doğrulanmış resmî kanala ilerleyin.'],
      ['/acil-numaralar/', 'Acil numaraları açın', '112, 186 ve diğer ulusal hatları doğru durumda kullanın.']
    ];
    if (currentPath.startsWith('/yasal/') || ['/hakkimizda', '/yayin-ilkeleri', '/gizlilik', '/iletisim', '/kaynaklar'].includes(currentPath)) return [
      ['/elektrik-portali', 'Elektrik Portalı', 'Araç, rehber ve resmî yönlendirmelere dönün.'],
      ['/yayin-ilkeleri', 'Yayın ilkeleri', 'Kaynak, güncellik ve ticari sınırları inceleyin.'],
      ['/iletisim', 'Hatalı bilgi bildirin', 'Güncel olmayan bağlantı veya içerik için geri bildirim verin.']
    ];
    return [
      ['/elektrik-durum-merkezi/', 'Elektrik Durum Merkezi', 'Belirtiyi güvenli bir sonraki adıma dönüştürün.'],
      ['/arama/', 'Teknik arama', 'Araç, rehber ve kaynakları tek aramada bulun.'],
      ['/hesaplama/', 'Hesaplama Merkezi', 'Kişisel veri vermeden teknik ön değerlendirme yapın.']
    ];
  };

  const addNextSteps = () => {
    if (!main || noindex || main.querySelector('[data-alo186-next-steps="true"]')) return;
    if (['/', '/en', '/elektrik-portali', '/hesaplama', '/amazon-elektrik-urunleri'].includes(currentPath)) return;
    const section = doc.createElement('section');
    section.className = 'alo-ux-next';
    section.dataset.alo186NextSteps = 'true';
    const header = doc.createElement('div');
    header.className = 'alo-ux-next-head';
    const heading = doc.createElement('h2');
    heading.textContent = labels.nextTitle;
    const intro = doc.createElement('p');
    intro.textContent = labels.nextIntro;
    header.append(heading, intro);
    const grid = doc.createElement('div');
    grid.className = 'alo-ux-next-grid';
    for (const [href, title, description] of journeyData()) {
      const link = doc.createElement('a');
      link.href = withBase(href);
      const strong = doc.createElement('strong');
      strong.textContent = title;
      const text = doc.createElement('span');
      text.textContent = description;
      link.append(strong, text);
      grid.appendChild(link);
    }
    const trust = doc.createElement('small');
    trust.textContent = labels.trust;
    section.append(header, grid, trust);
    main.appendChild(section);
    markCurrentLinks(section);
  };

  addLongPageToc();
  addNextSteps();

  const top = doc.createElement('button');
  top.type = 'button';
  top.className = 'alo-ux-backtop';
  top.setAttribute('aria-label', labels.top);
  top.textContent = '↑';
  top.addEventListener('click', () => window.scrollTo({ top: 0, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' }));
  body.appendChild(top);
  const updateTop = () => { top.dataset.visible = String(window.scrollY > 700); };
  updateTop();
  addEventListener('scroll', updateTop, { passive: true });
})();
