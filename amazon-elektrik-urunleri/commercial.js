(() => {
  'use strict';

  const catalog = window.Alo186ProductCatalog;
  const body = document.body;
  const categoryId = body ? body.dataset.category : '';
  const professionalOnly = Boolean(body && body.dataset.commercialScope === 'professional-only');
  const revenueHubRoute = '/amazon-elektrik-urunleri/dogrulanmis-tak-calistir-urunler/';
  const hubPath = '/amazon-elektrik-urunleri';
  const returnVisitRoute = '/hesaplama/kesinti-kiti-donemsel-kontrolu/';
  const escapeHtml = (value) => String(value ?? '').replace(/[&<>"]/g, (char) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[char]));
  const escapeAttr = (value) => escapeHtml(value).replace(/'/g, '&#39;');
  const disclosureSuffix = ' Nitelikli satın alımlardan komisyon kazanılabilir; kullanıcıya ek maliyet yansımaz. Fiyat, stok, satıcı, teslimat, puan ve garanti yalnız Amazon’un güncel sayfasında doğrulanır.';

  function track(name, params = {}) {
    if (typeof window.Alo186Track === 'function') window.Alo186Track(name, params);
  }

  function currentPath() {
    return window.location.pathname.replace(/\/+$/, '') || '/';
  }

  function isHubPage() {
    return !categoryId && currentPath().endsWith(hubPath);
  }

  function normalizeDisclosures() {
    if (professionalOnly) return;
    document.querySelectorAll('.affiliate-disclosure').forEach((element) => {
      const current = element.textContent.toLocaleLowerCase('tr-TR');
      const missingCost = !current.includes('kullanıcıya ek maliyet yansımaz');
      const missingFreshness = !current.includes('fiyat') || !current.includes('stok');
      if (missingCost || missingFreshness) element.append(document.createTextNode(disclosureSuffix));
    });
  }

  function injectRevenueHubEntry() {
    if (categoryId || !isHubPage()) return;
    if (document.querySelector('[data-affiliate-revenue-entry-v177]')) return;
    const anchor = document.querySelector('.affiliate-disclosure') || document.querySelector('.hero');
    if (!anchor) return;
    const section = document.createElement('section');
    section.className = 'section';
    section.dataset.affiliateRevenueEntryV177 = 'true';
    section.setAttribute('aria-labelledby', 'affiliateRevenueV177Title');
    section.innerHTML = `<div class="section-head"><div><span class="eyebrow">Güncel doğrulanmış tak-çalıştır katalog</span><h2 id="affiliateRevenueV177Title">Kesinti, iletişim ve ölçüm görevlerini tek teknik filtrede açın.</h2><p class="lead">Güncel doğrulanmış model havuzunu kullanım görevine göre inceleyin. Mevcut güvenli ürün yeterliyse satın alma bağlantısı açılmaz; sabit tesisat ve kritik sistemlerde profesyonel yol gösterilir.</p><div class="chips"><span class="chip">45 günlük doğrulama sınırı</span><span class="chip">ASIN tekilleştirme</span><span class="chip">Teknik ve ticari güven kapısı</span><span class="chip">Yüksek riskte doğrudan satış yok</span></div><div class="button-row"><a class="button primary" data-commercial-route="verified-hub-v177" href="${revenueHubRoute}">Doğrulanmış ürün merkezini aç</a><a class="button secondary" href="/kesinti-cihaz-surekliligi-karar-merkezi/">Önce ihtiyacı sınıflandır</a></div></div></div>`;
    anchor.insertAdjacentElement('afterend', section);
    track('affiliate_revenue_v177_entry_view', { placement: 'amazon_product_center' });
  }

  function deEmphasizeCatalogCounts() {
    if (!isHubPage()) return;
    const replacements = [
      [/\b96\s+ürün seçim yolu\b/gi, 'güncel teknik seçim yolları'],
      [/\b96\s+ürün karşılaştırma seçeneği\b/gi, 'güncel teknik karşılaştırma yolları'],
      [/\b154\s+doğrulanmış ASIN\b/gi, 'güncel doğrulanmış ürün kimlikleri'],
      [/\b154\s+benzersiz ASIN(?:’i|i)?\b/gi, 'güncel doğrulanmış ürünleri'],
      [/\b154\s+model(?:i|in)?\b/gi, 'güncel doğrulanmış modelleri'],
      [/\b25\+\s+uzun kuyruk ürün sınıfı\b/gi, 'seçilmiş uzun kuyruk ürün sınıflarını']
    ];
    const candidates = document.querySelectorAll('.hero p, .hero-card, .section-head p, .section-head h2, .button, .chip');
    let changes = 0;
    candidates.forEach((element) => {
      let html = element.innerHTML;
      replacements.forEach(([pattern, replacement]) => {
        const next = html.replace(pattern, replacement);
        if (next !== html) changes += 1;
        html = next;
      });
      if (html !== element.innerHTML) element.innerHTML = html;
    });
    if (changes) track('catalog_vanity_counts_deemphasized', { changes });
  }

  function hubTechnicalRouteFor(link) {
    const scope = link.closest('article, .card, section, li');
    if (scope) {
      const technical = [...scope.querySelectorAll('a[href]')].find((candidate) => {
        if (candidate === link) return false;
        const href = candidate.getAttribute('href') || '';
        return href.startsWith('/') && !href.startsWith('/yasal/');
      });
      if (technical) return technical.getAttribute('href');
    }
    return '/kesinti-cihaz-surekliligi-karar-merkezi/';
  }

  function gateHubDirectStoreLinks() {
    if (!isHubPage()) return;
    const links = [...document.querySelectorAll('a[href*="amazon.com.tr"]')];
    if (!links.length) return;
    links.forEach((link) => {
      const storeUrl = link.getAttribute('href') || '';
      const technicalRoute = hubTechnicalRouteFor(link);
      link.dataset.originalAffiliateUrl = storeUrl;
      link.dataset.hubStoreLinkGated = 'true';
      link.href = technicalRoute;
      link.removeAttribute('target');
      link.rel = 'nofollow noopener';
      link.textContent = 'Önce teknik ihtiyacı doğrula';
      link.addEventListener('click', () => {
        track('hub_store_link_intercepted', {
          original_host: 'www.amazon.com.tr',
          technical_route: technicalRoute,
          placement: link.closest('article, section') ? 'hub_content' : 'hub_other'
        });
      });
    });

    const disclosure = document.querySelector('.affiliate-disclosure');
    if (disclosure && !document.querySelector('[data-hub-store-gate-note]')) {
      const note = document.createElement('p');
      note.className = 'verification';
      note.dataset.hubStoreGateNote = 'true';
      note.textContent = 'Ürün merkezi genel bakışında doğrudan mağaza geçişi kapalıdır. Önce teknik rehber veya hesaplayıcı açılır; mağaza bağlantısı yalnız gerçek ihtiyaç doğrulanırsa gösterilir.';
      disclosure.insertAdjacentElement('afterend', note);
    }
    track('hub_direct_store_links_gated', { link_count: links.length });
  }

  function formatIcsDate(date) {
    return date.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}Z$/, 'Z');
  }

  function downloadReturnVisitReminder(days) {
    const start = new Date();
    start.setDate(start.getDate() + days);
    start.setHours(10, 0, 0, 0);
    const end = new Date(start.getTime() + 30 * 60 * 1000);
    const stamp = new Date();
    const url = new URL(returnVisitRoute, window.location.origin).href;
    const description = [
      'Elektrik kesintisi hazırlık ekipmanlarını yeniden kontrol edin.',
      'Mevcut sistem yeterliyse yeni ürün almayın.',
      'Batarya süresi, fiziksel hasar, yeni yükler ve gerçek kesinti deneyimini yeniden değerlendirin.',
      url
    ].join('\\n');
    const ics = [
      'BEGIN:VCALENDAR',
      'VERSION:2.0',
      'PRODID:-//ALO186//Kesinti Hazirlik Kontrolu//TR',
      'CALSCALE:GREGORIAN',
      'BEGIN:VEVENT',
      `UID:alo186-kesinti-kontrol-${days}-${Date.now()}@alo186.com`,
      `DTSTAMP:${formatIcsDate(stamp)}`,
      `DTSTART:${formatIcsDate(start)}`,
      `DTEND:${formatIcsDate(end)}`,
      'SUMMARY:ALO186 elektrik kesintisi hazırlık kontrolü',
      `DESCRIPTION:${description}`,
      `URL:${url}`,
      'END:VEVENT',
      'END:VCALENDAR'
    ].join('\r\n');
    const blob = new Blob([ics], { type: 'text/calendar;charset=utf-8' });
    const objectUrl = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = objectUrl;
    anchor.download = `alo186-kesinti-hazirlik-kontrolu-${days}-gun.ics`;
    document.body.append(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(objectUrl);
    track('return_visit_reminder_downloaded', { days, placement: 'product_hub' });
  }

  function injectReturnVisitPlanner() {
    if (!isHubPage() || document.querySelector('[data-return-visit-planner-v244]')) return;
    const anchor = document.querySelector('[data-affiliate-revenue-entry-v177]') || document.querySelector('.affiliate-disclosure');
    if (!anchor) return;
    const section = document.createElement('section');
    section.className = 'section status-box';
    section.dataset.returnVisitPlannerV244 = 'true';
    section.setAttribute('aria-labelledby', 'returnVisitPlannerTitle');
    section.innerHTML = `<span class="eyebrow">Tekrar ziyaret nedeni · fiyat veya kampanya değil</span><h2 id="returnVisitPlannerTitle">Ekipman koşulları değiştiğinde yeniden kontrol edin.</h2><p>Batarya çalışma süresi, modem/ONT yükü, acil aydınlatma, fiziksel hasar veya kesinti sıklığı değiştiğinde ücretsiz kontrolü yenileyin. Takvim dosyası yalnız cihazınızda oluşturulur; ad, e-posta, adres veya abonelik bilgisi istenmez.</p><div class="button-row"><button class="button primary" type="button" data-return-reminder-days="30">30 günlük kontrolü takvime ekle</button><button class="button secondary" type="button" data-return-reminder-days="90">90 günlük kontrolü takvime ekle</button><a class="button secondary" href="${returnVisitRoute}">Kontrol listesini şimdi aç</a></div><p class="verification">Mevcut sistem güvenli ve yeterliyse satın alma yapmayın; yalnız ihtiyaç veya uyumluluk değişirse yeniden değerlendirin.</p>`;
    anchor.insertAdjacentElement('afterend', section);
    section.querySelectorAll('[data-return-reminder-days]').forEach((button) => {
      button.addEventListener('click', () => downloadReturnVisitReminder(Number(button.dataset.returnReminderDays)));
    });
    track('return_visit_planner_viewed', { placement: 'product_hub' });
  }

  function renderAffiliateGate(category, products, staleCount) {
    const gateId = `affiliateGate-${category.id}`;
    const cards = products.map((product) => {
      const freshness = catalog.verificationStatus(product, new Date());
      return `<article class="product-card"><span class="eyebrow">Doğrulanmış teknik liste</span><h3>${escapeHtml(product.name)}</h3><div class="product-meta">${escapeHtml(product.brand)} · ASIN ${escapeHtml(product.asin)}</div><h4>Güçlü yanlar</h4><ul>${product.strengths.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul><h4>Sınırlar</h4><ul>${product.limits.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul><div class="verification">Teknik liste kontrolü: ${escapeHtml(product.verifiedAt)} · ${Number.isFinite(freshness.ageDays) ? `${freshness.ageDays} gün önce` : 'tarih yeniden doğrulanmalı'}<br>${escapeHtml(product.sourceNote)}</div><a class="button primary" data-affiliate-product="${escapeAttr(product.id)}" data-asin="${escapeAttr(product.asin)}" data-affiliate-url="${escapeAttr(product.url)}" rel="sponsored nofollow noopener" aria-disabled="true" tabindex="-1">Amazon ürün sayfasını aç</a></article>`;
    }).join('');

    return `<section class="affiliate-gate status-box" data-affiliate-gate aria-labelledby="${gateId}-title"><span class="eyebrow">Satın alma öncesi güven kapısı</span><h3 id="${gateId}-title">Ürün bağlantıları yalnız gerçek ihtiyaç ve teknik uygunluk doğrulandıktan sonra açılır.</h3><p>Bu adım kişisel veri toplamaz ve seçiminizi tarayıcıda saklamaz. Mevcut güvenli ürün görevi karşılıyorsa yeni ürün almayın.</p><fieldset><legend>Üç koşulu ayrı ayrı doğrulayın</legend><label><input type="checkbox" data-affiliate-confirm="need"> Mevcut güvenli ürün ihtiyacı karşılamıyor.</label><label><input type="checkbox" data-affiliate-confirm="fit"> Model, gerilim, güç, port, kablo ve kullanım sınırlarını yeniden kontrol edeceğim.</label><label><input type="checkbox" data-affiliate-confirm="disclosure"> Bağlantıların Amazon satış ortaklığı bağlantısı olduğunu ve fiyat, stok, puan ile garantinin yalnız mağazada doğrulanacağını anladım.</label></fieldset><div class="button-row"><button class="button primary" type="button" data-affiliate-unlock disabled>Ürün bağlantılarını aç</button><button class="button secondary" type="button" data-affiliate-no-buy>Mevcut ürünüm yeterli — satın alma yapmayacağım</button></div><p data-affiliate-gate-status role="status">Bağlantılar kapalı. Ücretsiz teknik kontrolü tamamlamadan mağazaya geçmeyin.</p></section><div class="product-grid" data-affiliate-product-grid>${cards}</div>${staleCount ? `<p class="verification">${staleCount} doğrulama süresi geçmiş kart ticari bağlantıdan çıkarıldı.</p>` : ''}`;
  }

  function activateAffiliateGate(container, category) {
    const gate = container.querySelector('[data-affiliate-gate]');
    if (!gate) return;
    const checks = [...gate.querySelectorAll('[data-affiliate-confirm]')];
    const unlock = gate.querySelector('[data-affiliate-unlock]');
    const noBuy = gate.querySelector('[data-affiliate-no-buy]');
    const status = gate.querySelector('[data-affiliate-gate-status]');
    const links = [...container.querySelectorAll('[data-affiliate-product]')];

    const updateGate = () => {
      unlock.disabled = !checks.every((checkbox) => checkbox.checked);
    };
    checks.forEach((checkbox) => checkbox.addEventListener('change', updateGate));

    unlock.addEventListener('click', () => {
      if (!checks.every((checkbox) => checkbox.checked)) return;
      links.forEach((link) => {
        link.href = link.dataset.affiliateUrl;
        link.target = '_blank';
        link.rel = 'sponsored nofollow noopener';
        link.removeAttribute('aria-disabled');
        link.removeAttribute('tabindex');
      });
      status.textContent = 'Teknik ve ticari onay tamamlandı. Yalnız ihtiyacınıza uyan kartın mağaza sayfasını açın.';
      unlock.disabled = true;
      checks.forEach((checkbox) => { checkbox.disabled = true; });
      track('affiliate_gate_passed', { category: category.id, product_count: links.length });
    });

    noBuy.addEventListener('click', () => {
      links.forEach((link) => {
        link.removeAttribute('href');
        link.setAttribute('aria-disabled', 'true');
        link.setAttribute('tabindex', '-1');
      });
      checks.forEach((checkbox) => {
        checkbox.checked = false;
        checkbox.disabled = true;
      });
      unlock.disabled = true;
      noBuy.disabled = true;
      status.textContent = 'Satın almama kararı kaydedilmedi; bağlantılar bu ziyaret için kapalı kaldı. Mevcut ürününüzü kullanın ve yalnız ihtiyaç değişirse yeniden değerlendirin.';
      track('affiliate_no_buy_selected', { category: category.id, reason: 'existing_product_sufficient' });
    });

    links.forEach((link) => link.addEventListener('click', (event) => {
      if (!link.getAttribute('href')) {
        event.preventDefault();
        status.textContent = 'Önce üç güven koşulunu doğrulayın veya mevcut ürününüz yeterliyse satın almama seçeneğini kullanın.';
        return;
      }
      track('affiliate_product_clicked', {
        category: category.id,
        product_id: link.dataset.affiliateProduct,
        asin: link.dataset.asin,
        placement: 'commercial_category_page_after_gate'
      });
    }));

    track('affiliate_gate_viewed', { category: category.id, product_count: links.length });
  }

  function renderFreshProducts(container, category) {
    const products = catalog.productsFor(category.id, { freshOnly: true });
    const staleCount = catalog.productsFor(category.id).length - products.length;
    if (!products.length) {
      container.innerHTML = `<div class="status-box" data-state="blocked"><strong>Güncel doğrulanmış doğrudan ürün kartı yok.</strong><p>Teknik doğrulama süresi geçmiş veya eksik alanlı kartlar ticari bağlantıdan çıkarılır. Ürün merkezindeki gereksinimlerinizi saklayıp katalog yenilendiğinde yeniden kontrol edin.</p><a class="button secondary" href="/akilli-urun-secimi?kategori=${encodeURIComponent(category.id)}">Teknik ürün merkezini aç</a></div>`;
      track('commercial_products_blocked', { category: category.id, reason: staleCount ? 'stale_catalog' : 'no_verified_product' });
      return;
    }
    container.innerHTML = renderAffiliateGate(category, products, staleCount);
    activateAffiliateGate(container, category);
  }

  function renderCategoryState() {
    const status = document.querySelector('[data-category-status]');
    if (!status) return;
    if (!catalog || !categoryId) {
      status.dataset.state = 'blocked';
      status.innerHTML = '<strong>Katalog durumu okunamadı.</strong><p>Doğrudan ürün bağlantısı gösterilmiyor. Teknik uygunluk aracını kullanın.</p>';
      return;
    }
    const category = catalog.getCategory(categoryId);
    if (!category) {
      status.dataset.state = 'blocked';
      status.innerHTML = '<strong>Kategori bulunamadı.</strong><p>Ürün merkezindeki güncel kategori listesini kullanın.</p>';
      return;
    }
    const productCount = catalog.productsFor(category.id, { freshOnly: true }).length;
    if (category.mode === 'direct' && productCount > 0) {
      status.dataset.state = 'ready';
      status.innerHTML = `<strong>${productCount} güncel teknik ürün kartı bulundu.</strong><p>Mağaza bağlantıları üçlü güven kapısı tamamlanana kadar kapalıdır. Fiyat, stok, satıcı, teslimat ve garanti yalnız Amazon sayfasında doğrulanır.</p>`;
    } else {
      status.dataset.state = 'blocked';
      status.innerHTML = `<strong>Önce ücretsiz uygunluk kontrolü gerekli.</strong><p>${escapeHtml(category.description)} Doğrudan Amazon bağlantısı bu sayfada açılmaz.</p>`;
    }

    const products = document.querySelector('[data-fresh-products]');
    if (products && category.mode === 'direct') renderFreshProducts(products, category);
    document.querySelectorAll('[data-product-center]').forEach((link) => {
      link.href = `/akilli-urun-secimi?kategori=${encodeURIComponent(category.id)}`;
      link.addEventListener('click', () => track('commercial_product_center_opened', { category: category.id }));
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    normalizeDisclosures();
    injectRevenueHubEntry();
    deEmphasizeCatalogCounts();
    gateHubDirectStoreLinks();
    injectReturnVisitPlanner();
    renderCategoryState();
    document.querySelectorAll('[data-commercial-route]').forEach((link) => link.addEventListener('click', () => {
      track('commercial_route_opened', {
        route: link.getAttribute('href') || '',
        placement: link.dataset.commercialRoute || 'commercial_page'
      });
    }));
  });
})();
