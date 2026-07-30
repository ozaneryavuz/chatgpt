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
    affiliate: isEnglish ? 'Affiliate' : 'Satış ortaklığı',
    nextTitle: isEnglish ? 'Continue with the right next step' : 'Sonraki doğru adım',
    nextIntro: isEnglish
      ? 'Choose a verified route instead of starting the same search again.'
      : 'Aynı aramayı baştan yapmak yerine doğrulanmış bir devam rotası seçin.',
    trust: isEnglish
      ? 'ALO186 is an independent information platform. It does not create official outage or application records.'
      : 'ALO186 bağımsız bilgi platformudur; resmî başvuru, arıza veya ihbar kaydı oluşturmaz.',
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

  const hardenLink = (link) => {
    if (!(link instanceof HTMLAnchorElement)) return;
    syncLinkName(link);
    const rawHref = link.getAttribute('href');
    if (!rawHref) return;
    let url;
    try { url = new URL(link.href, location.href); } catch (_) { return; }
    const rel = new Set((link.getAttribute('rel') || '').split(/\s+/).filter(Boolean));
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
      if (!/satış ortaklığı|affiliate/i.test(cleanLabel(link.textContent))) {
        link.dataset.aloAffiliateBadge = 'true';
        link.dataset.aloAffiliateLabel = copy.affiliate;
        if (!link.getAttribute('aria-label')) {
          link.setAttribute('aria-label', `${cleanLabel(link.textContent) || 'Amazon'} — ${copy.affiliate}`);
        }
      }
    }
    const nextRel = [...rel].join(' ');
    if (nextRel && nextRel !== link.getAttribute('rel')) link.setAttribute('rel', nextRel);
  };

  doc.querySelectorAll('a').forEach((link) => {
    hardenLink(link);
    if (link.dataset.alo186LinkFallback === 'true' && 'MutationObserver' in window) {
      const observer = new MutationObserver(() => hardenLink(link));
      observer.observe(link, { childList: true, subtree: true, attributes: true, attributeFilter: ['href', 'aria-label'] });
    }
  });
  if ('MutationObserver' in window) {
    const linkObserver = new MutationObserver((records) => {
      for (const record of records) {
        if (record.type === 'attributes') hardenLink(record.target);
        for (const added of record.addedNodes || []) {
          if (added.nodeType !== Node.ELEMENT_NODE) continue;
          hardenLink(added);
          added.querySelectorAll?.('a').forEach(hardenLink);
        }
      }
    });
    linkObserver.observe(body, {
      subtree: true,
      childList: true,
      attributes: true,
      attributeFilter: ['href', 'target', 'rel'],
    });
  }

  const normalizePath = (value) => value.replace(/\/+$/, '') || slash;
  const filePath = (...parts) => `${slash}${parts.filter(Boolean).join(slash)}`;
  const routePath = (...parts) => `${filePath(...parts)}${slash}`;
  const scriptUrl = new URL(doc.currentScript?.src || location.href, location.href);
  const assetSuffix = filePath('assets', 'alo186-ux.js');
  const basePath = scriptUrl.pathname.endsWith(assetSuffix) ? scriptUrl.pathname.slice(0, -assetSuffix.length) : '';
  const publicPath = (route) => `${basePath}${route === slash ? slash : route}`.replace(/\/+/g, slash);
  const current = normalizePath(location.pathname);
  const localCurrent = basePath && current.startsWith(basePath)
    ? normalizePath(current.slice(basePath.length) || slash)
    : current;
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
  const headings = main ? [...main.querySelectorAll('h2')].filter((heading) => (
    heading.textContent.trim()
    && !heading.closest('[hidden],template,nav,footer,.alo-ux-next')
  )) : [];
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
  } else if (isIndexable) {
    const nav = doc.createElement('nav');
    nav.className = 'alo-ux-mobilebar';
    nav.setAttribute('aria-label', copy.mobileNav);
    const links = isEnglish ? [
      [routePath('en'), '⌂', copy.home],
      [routePath('en', 'electricity-distribution-company-finder'), '186', copy.edas],
      [routePath('en', 'electricity-outage-turkey'), '↯', 'Outage'],
      [routePath('en', 'emergency-numbers-turkey'), '112', copy.emergency],
    ] : [
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

  const journeyData = () => {
    if (isEnglish) {
      if (localCurrent.includes('affiliate')) return [
        [routePath('en', 'affiliate-disclosure'), 'Affiliate disclosure', 'See how commercial links are labelled.'],
        [routePath('en', 'editorial-methodology'), 'Editorial methodology', 'Review how sources and boundaries are handled.'],
        [routePath('en', 'contact'), 'Report an issue', 'Tell us about an incorrect or outdated route.'],
      ];
      return [
        [routePath('en', 'electricity-outage-turkey'), 'Check an outage', 'Use the official distribution route for your location.'],
        [routePath('en', 'electricity-distribution-company-finder'), 'Find the distributor', 'Identify the authorised electricity distribution company.'],
        [routePath('en', 'emergency-numbers-turkey'), 'Emergency numbers', 'Separate 112 emergencies from the 186 outage line.'],
      ];
    }
    const sensitiveTool = /cpap|bipap|ventilat|karbonmonoksit|duman-alarmi|dogal-gaz|gaz-kokusu/i.test(localCurrent);
    if (localCurrent.startsWith(filePath('hesaplama')) && sensitiveTool) return [
      [routePath('acil-numaralar'), 'Acil numaraları açın', '112, 186 ve 187 rotalarını doğru durumda kullanın.'],
      [routePath('hesaplama', 'kesinti-hazirlik-plani'), 'Kesinti planı oluşturun', 'Kritik ihtiyacı ürün satın almadan önce görev ve kanıt planına bağlayın.'],
      [routePath('hesaplama'), 'Tüm hesaplayıcılar', 'Başka bir teknik hesabı aynı merkezden açın.'],
    ];
    if (localCurrent.startsWith(filePath('hesaplama'))) return [
      [routePath('hesaplama'), 'Tüm hesaplayıcılar', 'Başka bir teknik hesabı aynı merkezden açın.'],
      [routePath('hesaplama', 'cozum-sonucu'), 'Sonucu takip edin', 'Uygulamanın işe yarayıp yaramadığını kişisel veri vermeden kaydedin.'],
      [filePath('akilli-urun-secimi'), 'Ürün gerekliyse önce uygunluğu doğrulayın', 'Fiyat yerine gerçek teknik eksik üzerinden ilerleyin.'],
    ];
    if (
      localCurrent.startsWith(filePath('amazon-elektrik-urunleri'))
      || localCurrent.startsWith(filePath('urun-'))
      || localCurrent.startsWith(filePath('affiliate-'))
      || localCurrent === filePath('akilli-urun-secimi')
    ) return [
      [filePath('akilli-urun-secimi'), 'Akıllı ürün seçimi', 'Mevcut ürünün yeterli olup olmadığını önce kontrol edin.'],
      [filePath('katalog-guven-durumu'), 'Katalog güven durumu', 'Doğrulama tarihi ve ticari sınırları görün.'],
      [filePath('yasal', 'amazon-satis-ortakligi'), 'Satış ortaklığı açıklaması', 'Affiliate ilişkinin nasıl işlediğini inceleyin.'],
    ];
    if (
      localCurrent.startsWith(filePath('haberler'))
      || localCurrent.startsWith(filePath('sektor-rehberi'))
      || localCurrent === filePath('mevzuat')
    ) return [
      [routePath('arama'), 'Benzer konuyu teknik aramada bulun', 'Aynı sorunun araç, rehber ve resmî kaynaklarını birlikte görün.'],
      [routePath('mevzuat'), 'Mevzuatı resmî kaynaktan doğrulayın', 'Güncel ve mülga düzenlemeleri ayırarak ilerleyin.'],
      [routePath('elektrik-durum-merkezi'), 'Belirtiyi sınıflandırın', '112, 186, elektrikçi veya teknik araç rotasını ayırın.'],
    ];
    if (localCurrent.includes('kesinti') || localCurrent === filePath('edas-bul') || localCurrent.startsWith(filePath('acil-'))) return [
      [routePath('elektrik-durum-merkezi'), 'Durumu sınıflandırın', 'Tehlike, şebeke ve iç tesisat ayrımını yapın.'],
      [routePath('edas-bul'), 'Yetkili dağıtım şirketini bulun', '81 il için doğrulanmış resmî kanala ilerleyin.'],
      [routePath('acil-numaralar'), 'Acil numaraları açın', '112, 186 ve diğer ulusal hatları doğru durumda kullanın.'],
    ];
    if (
      localCurrent.startsWith(filePath('yasal'))
      || [filePath('hakkimizda'), filePath('yayin-ilkeleri'), filePath('gizlilik'), filePath('iletisim'), filePath('kaynaklar')].includes(localCurrent)
    ) return [
      [filePath('elektrik-portali'), 'Elektrik Portalı', 'Araç, rehber ve resmî yönlendirmelere dönün.'],
      [filePath('yayin-ilkeleri'), 'Yayın ilkeleri', 'Kaynak, güncellik ve ticari sınırları inceleyin.'],
      [filePath('iletisim'), 'Hatalı bilgi bildirin', 'Güncel olmayan bağlantı veya içerik için geri bildirim verin.'],
    ];
    return [
      [routePath('elektrik-durum-merkezi'), 'Elektrik Durum Merkezi', 'Belirtiyi güvenli bir sonraki adıma dönüştürün.'],
      [routePath('arama'), 'Teknik arama', 'Araç, rehber ve kaynakları tek aramada bulun.'],
      [routePath('hesaplama'), 'Hesaplama Merkezi', 'Kişisel veri vermeden teknik ön değerlendirme yapın.'],
    ];
  };

  if (main && isIndexable && !main.querySelector('[data-alo186-next-steps="true"]')) {
    const excluded = new Set([slash, filePath('en'), filePath('elektrik-portali'), filePath('hesaplama'), filePath('amazon-elektrik-urunleri')]);
    if (!excluded.has(localCurrent)) {
      const section = doc.createElement('section');
      section.className = 'alo-ux-next';
      section.dataset.alo186NextSteps = 'true';
      const header = doc.createElement('div');
      header.className = 'alo-ux-next-head';
      const title = doc.createElement('h2');
      title.textContent = copy.nextTitle;
      const intro = doc.createElement('p');
      intro.textContent = copy.nextIntro;
      header.append(title, intro);
      const grid = doc.createElement('div');
      grid.className = 'alo-ux-next-grid';
      for (const [route, label, description] of journeyData()) {
        const href = publicPath(route);
        if (normalizePath(new URL(href, location.origin).pathname) === current) continue;
        const link = doc.createElement('a');
        link.href = href;
        const strong = doc.createElement('strong');
        strong.textContent = label;
        const text = doc.createElement('span');
        text.textContent = description;
        link.append(strong, text);
        grid.appendChild(link);
      }
      const trust = doc.createElement('small');
      trust.textContent = copy.trust;
      section.append(header, grid, trust);
      main.appendChild(section);
      grid.querySelectorAll('a').forEach(hardenLink);
      markCurrent(section);
    }
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
