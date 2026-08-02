(() => {
  'use strict';

  const catalog = window.Alo186ProductCatalog;
  const body = document.body;
  const categoryId = body ? body.dataset.category : '';
  const professionalOnly = Boolean(body && body.dataset.commercialScope === 'professional-only');
  const revenueHubRoute = '/amazon-elektrik-urunleri/dogrulanmis-tak-calistir-urunler/';
  const escapeHtml = (value) => String(value ?? '').replace(/[&<>"]/g, (char) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[char]));
  const escapeAttr = (value) => escapeHtml(value).replace(/'/g, '&#39;');
  const disclosureSuffix = ' Nitelikli satın alımlardan komisyon kazanılabilir; kullanıcıya ek maliyet yansımaz. Fiyat, stok, satıcı, teslimat, puan ve garanti yalnız Amazon’un güncel sayfasında doğrulanır.';

  function track(name, params = {}) {
    if (typeof window.Alo186Track === 'function') window.Alo186Track(name, params);
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
    const currentPath = window.location.pathname.replace(/\/+$/, '') || '/';
    if (categoryId || !currentPath.endsWith('/amazon-elektrik-urunleri')) return;
    if (document.querySelector('[data-affiliate-revenue-entry-v177]')) return;
    const anchor = document.querySelector('.affiliate-disclosure') || document.querySelector('.hero');
    if (!anchor) return;
    const section = document.createElement('section');
    section.className = 'section';
    section.dataset.affiliateRevenueEntryV177 = 'true';
    section.setAttribute('aria-labelledby', 'affiliateRevenueV177Title');
    section.innerHTML = `<div class="section-head"><div><span class="eyebrow">Güncel doğrulanmış tak-çalıştır katalog</span><h2 id="affiliateRevenueV177Title">Powerbank, USB-C, ağ, görüntü, araç ve şarjlı pil ürünlerini tek görev merkezinde açın.</h2><p class="lead">Güncel doğrulanmış model havuzunu, 25+ uzun kuyruk ürün sınıfını ve yedi kullanım paketini aynı teknik filtrede görün. Mevcut güvenli ürün yeterliyse satın alma bağlantısı açılmaz.</p><div class="chips"><span class="chip">45 günlük doğrulama sınırı</span><span class="chip">ASIN tekilleştirme</span><span class="chip">Üçlü teknik ve ticari kapı</span><span class="chip">Yüksek riskli ürünlerde doğrudan satış yok</span></div><div class="button-row"><a class="button primary" data-commercial-route="verified-hub-v177" href="${revenueHubRoute}">Doğrulanmış ürün merkezini aç</a><a class="button secondary" href="/hesaplama/usb-c-hub-goruntu-pd-uygunluk/">Önce bağlantı uygunluğunu kontrol et</a></div></div></div>`;
    anchor.insertAdjacentElement('afterend', section);
    track('affiliate_revenue_v177_entry_view', { placement: 'amazon_product_center' });
  }

  function renderAffiliateGate(category, products, staleCount) {
    const gateId = `affiliateGate-${category.id}`;
    const cards = products.map((product) => {
      const freshness = catalog.verificationStatus(product, new Date());
      return `<article class="product-card"><span class="eyebrow">Doğrulanmış teknik liste</span><h3>${escapeHtml(product.name)}</h3><div class="product-meta">${escapeHtml(product.brand)} · ASIN ${escapeHtml(product.asin)}</div><h4>Güçlü yanlar</h4><ul>${product.strengths.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul><h4>Sınırlar</h4><ul>${product.limits.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul><div class="verification">Teknik liste kontrolü: ${escapeHtml(product.verifiedAt)} · ${Number.isFinite(freshness.ageDays) ? `${freshness.ageDays} gün önce` : 'tarih yeniden doğrulanmalı'}<br>${escapeHtml(product.sourceNote)}</div><a class="button primary" data-affiliate-product="${escapeAttr(product.id)}" data-asin="${escapeAttr(product.asin)}" data-affiliate-url="${escapeAttr(product.url)}" aria-disabled="true" tabindex="-1">Amazon ürün sayfasını aç</a></article>`;
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
    renderCategoryState();
    document.querySelectorAll('[data-commercial-route]').forEach((link) => link.addEventListener('click', () => {
      track('commercial_route_opened', {
        route: link.getAttribute('href') || '',
        placement: link.dataset.commercialRoute || 'commercial_page'
      });
    }));
  });
})();
