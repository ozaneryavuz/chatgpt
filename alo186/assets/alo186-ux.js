(() => {
  'use strict';

  const doc = document;
  const body = doc.body;
  if (!body || body.dataset.alo186Ux === 'ready') return;
  body.dataset.alo186Ux = 'ready';

  const main = doc.querySelector('main');
  const language = (doc.documentElement.lang || 'tr').toLowerCase();
  const isEnglish = language.startsWith('en');
  const isTurkish = !isEnglish;
  const labels = isEnglish ? {
    skip: 'Skip to content',
    table: 'Scrollable table',
    mobile: 'Mobile quick access',
    top: 'Back to top',
    affiliate: 'Affiliate',
    nextTitle: 'Continue with the right next step',
    nextIntro: 'Choose a verified route instead of starting the same search again.',
    trust: 'ALO186 is an independent information platform. It does not create official outage or application records.'
  } : {
    skip: 'İçeriğe geç',
    table: 'Kaydırılabilir tablo',
    mobile: 'Mobil hızlı erişim',
    top: 'Sayfanın başına dön',
    affiliate: 'Satış ortaklığı',
    nextTitle: 'Sonraki doğru adım',
    nextIntro: 'Aynı aramayı baştan yapmak yerine doğrulanmış bir devam rotası seçin.',
    trust: 'ALO186 bağımsız bilgi platformudur; resmî başvuru, arıza veya ihbar kaydı oluşturmaz.'
  };

  if (main && !main.id) main.id = 'main-content';
  if (main && !doc.querySelector(`a[href="#${CSS.escape(main.id)}"]`)) {
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
    if (!image.hasAttribute('alt')) {
      const caption = image.closest('figure')?.querySelector('figcaption')?.textContent?.trim();
      const label = image.getAttribute('aria-label') || image.getAttribute('title') || caption || '';
      image.alt = label;
      image.dataset.alo186AltFallback = label ? 'derived' : 'decorative';
    }
  });

  const normalizePath = (value) => String(value || '/').replace(/\/{2,}/g, '/').replace(/\/+$/, '') || '/';
  const runtimeScript = doc.currentScript || doc.querySelector('script[data-alo186-sitewide-ux="true"]');
  const scriptUrl = new URL(runtimeScript?.src || location.href, location.href);
  const assetSuffix = '/assets/alo186-ux.js';
  const explicitBase = runtimeScript?.dataset.basePath;
  const basePath = explicitBase !== undefined
    ? normalizePath(explicitBase) === '/' ? '' : normalizePath(explicitBase)
    : scriptUrl.pathname.endsWith(assetSuffix) ? scriptUrl.pathname.slice(0, -assetSuffix.length) : '';
  const publicPath = (route) => {
    const path = route.startsWith('/') ? route : `/${route}`;
    if (!basePath) return normalizePath(path) === '/' ? '/' : path;
    return path === '/' ? `${basePath}/` : `${basePath}${path}`.replace(/\/{2,}/g, '/');
  };
  const current = normalizePath(location.pathname);
  const routePath = basePath && current.startsWith(basePath)
    ? normalizePath(current.slice(basePath.length) || '/')
    : current;

  const relSet = (link) => new Set((link.getAttribute('rel') || '').split(/\s+/).filter(Boolean));
  const hardenAnchor = (link) => {
    if (!(link instanceof HTMLAnchorElement) || !link.getAttribute('href')) return;
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
    const value = [...rel].join(' ');
    if (value && value !== link.getAttribute('rel')) link.setAttribute('rel', value);
  };
  const hardenLinks = (root) => {
    if (root instanceof HTMLAnchorElement) hardenAnchor(root);
    root.querySelectorAll?.('a[href]').forEach(hardenAnchor);
  };
  hardenLinks(doc);
  const linkObserver = new MutationObserver((records) => {
    for (const record of records) {
      if (record.type === 'attributes') hardenAnchor(record.target);
      for (const added of record.addedNodes || []) {
        if (added.nodeType === Node.ELEMENT_NODE) hardenLinks(added);
      }
    }
  });
  linkObserver.observe(body, { subtree: true, childList: true, attributes: true, attributeFilter: ['href', 'target', 'rel'] });

  const markCurrent = (root = doc) => {
    root.querySelectorAll('a[href]').forEach((link) => {
      let url;
      try { url = new URL(link.href, location.href); } catch (_) { return; }
      if (url.origin !== location.origin) return;
      if (normalizePath(url.pathname) === current) link.setAttribute('aria-current', 'page');
    });
  };
  markCurrent();

  const robots = doc.querySelector('meta[name="robots"]')?.content?.toLowerCase() || '';
  const isIndexable = !robots.includes('noindex');

  const headings = main ? [...main.querySelectorAll('h2')].filter((heading) => heading.textContent.trim()) : [];
  if (main && isIndexable && headings.length >= 4 && main.textContent.trim().length > 2600 && !main.querySelector('.alo-ux-toc')) {
    const slugCounts = new Map();
    headings.forEach((heading, index) => {
      if (heading.id) return;
      const base = heading.textContent.trim().toLocaleLowerCase(isTurkish ? 'tr-TR' : 'en-US')
        .normalize('NFKD').replace(/[\u0300-\u036f]/g, '')
        .replace(/[^a-z0-9çğıöşü]+/gi, '-').replace(/^-|-$/g, '') || `section-${index + 1}`;
      const count = (slugCounts.get(base) || 0) + 1;
      slugCounts.set(base, count);
      heading.id = count === 1 ? base : `${base}-${count}`;
    });
    const toc = doc.createElement('details');
    toc.className = 'alo-ux-toc';
    toc.dataset.alo186Toc = 'true';
    toc.innerHTML = `<summary>${isTurkish ? 'Bu sayfada neler var?' : 'On this page'}</summary><nav aria-label="${isTurkish ? 'Sayfa içeriği' : 'Page contents'}"></nav>`;
    const tocNav = toc.querySelector('nav');
    headings.slice(0, 18).forEach((heading) => {
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

  if (isIndexable) {
    const mobileItems = isEnglish ? [
      ['/en/', '⌂', 'Home'],
      ['/en/electricity-distribution-company-finder/', '186', 'Distributor'],
      ['/en/electricity-outage-turkey/', '↯', 'Outage'],
      ['/en/emergency-numbers-turkey/', '!', 'Emergency']
    ] : [
      ['/', '⌂', 'Ana sayfa'],
      ['/edas-bul/', '186', 'EDAŞ bul'],
      ['/arama/', '⌕', 'Ara'],
      ['/acil-numaralar/', '!', 'Acil']
    ];
    const nav = doc.createElement('nav');
    nav.className = 'alo-ux-mobilebar';
    nav.setAttribute('aria-label', labels.mobile);
    for (const [href, icon, label] of mobileItems) {
      const link = doc.createElement('a');
      link.href = publicPath(href);
      const symbol = doc.createElement('b');
      symbol.setAttribute('aria-hidden', 'true');
      symbol.textContent = icon;
      const text = doc.createElement('span');
      text.textContent = label;
      link.append(symbol, text);
      nav.appendChild(link);
    }
    body.appendChild(nav);
    markCurrent(nav);
  } else {
    body.dataset.alo186UxCompact = 'true';
  }

  const journeyData = () => {
    if (isEnglish) {
      if (routePath.includes('affiliate')) return [
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
    if (routePath.startsWith('/hesaplama/')) return [
      ['/hesaplama/', 'Tüm hesaplayıcılar', 'Başka bir teknik hesabı aynı merkezden açın.'],
      ['/hesaplama/cozum-sonucu/', 'Sonucu takip edin', 'Uygulamanın işe yarayıp yaramadığını kişisel veri vermeden kaydedin.'],
      ['/akilli-urun-secimi', 'Ürün gerekliyse önce uygunluğu doğrulayın', 'Fiyat yerine gerçek teknik eksik üzerinden ilerleyin.']
    ];
    if (routePath.startsWith('/amazon-elektrik-urunleri') || routePath.startsWith('/urun-') || routePath.startsWith('/affiliate-') || routePath === '/akilli-urun-secimi') return [
      ['/akilli-urun-secimi', 'Akıllı ürün seçimi', 'Mevcut ürünün yeterli olup olmadığını önce kontrol edin.'],
      ['/katalog-guven-durumu', 'Katalog güven durumu', 'Doğrulama tarihi ve ticari sınırları görün.'],
      ['/yasal/amazon-satis-ortakligi', 'Satış ortaklığı açıklaması', 'Affiliate ilişkinin nasıl işlediğini inceleyin.']
    ];
    if (routePath.startsWith('/haberler/') || routePath.startsWith('/sektor-rehberi/') || routePath === '/mevzuat') return [
      ['/arama/', 'Benzer konuyu teknik aramada bulun', 'Aynı sorunun araç, rehber ve resmî kaynaklarını birlikte görün.'],
      ['/mevzuat/', 'Mevzuatı resmî kaynaktan doğrulayın', 'Güncel ve mülga düzenlemeleri ayırarak ilerleyin.'],
      ['/elektrik-durum-merkezi/', 'Belirtiyi sınıflandırın', '112, 186, elektrikçi veya teknik araç rotasını ayırın.']
    ];
    if (routePath.includes('kesinti') || routePath === '/edas-bul' || routePath.startsWith('/acil-')) return [
      ['/elektrik-durum-merkezi/', 'Durumu sınıflandırın', 'Tehlike, şebeke ve iç tesisat ayrımını yapın.'],
      ['/edas-bul/', 'Yetkili dağıtım şirketini bulun', '81 il için doğrulanmış resmî kanala ilerleyin.'],
      ['/acil-numaralar/', 'Acil numaraları açın', '112, 186 ve diğer ulusal hatları doğru durumda kullanın.']
    ];
    if (routePath.startsWith('/yasal/') || ['/hakkimizda', '/yayin-ilkeleri', '/gizlilik', '/iletisim', '/kaynaklar'].includes(routePath)) return [
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
    if (!main || !isIndexable || main.querySelector('[data-alo186-next-steps="true"]')) return;
    if (['/', '/en', '/elektrik-portali', '/hesaplama', '/amazon-elektrik-urunleri'].includes(routePath)) return;
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
      link.href = publicPath(href);
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
    markCurrent(section);
  };
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
