(() => {
  'use strict';

  const catalog = window.Alo186ProductCatalog;
  const byId = (id) => document.getElementById(id);

  function track(name, data = {}) {
    const allowed = {};
    for (const key of ['category', 'policy', 'status']) {
      if (typeof data[key] === 'string' && data[key].length < 80) allowed[key] = data[key];
    }
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ event: name, ...allowed });
  }

  function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>'"]/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[char]));
  }

  function formatDate(value) {
    const date = new Date(`${value}T00:00:00Z`);
    if (Number.isNaN(date.getTime())) return 'Bilinmiyor';
    return new Intl.DateTimeFormat('tr-TR', { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' }).format(date);
  }

  function addDays(value, days) {
    const date = new Date(`${value}T00:00:00Z`);
    if (Number.isNaN(date.getTime())) return null;
    date.setUTCDate(date.getUTCDate() + days);
    return date.toISOString().slice(0, 10);
  }

  function categoryState(category, now) {
    const all = catalog.products.filter((product) => product.category === category.id && product.status === 'verified_listing');
    const fresh = all.filter((product) => catalog.verificationStatus(product, now).fresh);
    const stale = all.length - fresh.length;
    if (category.affiliatePolicy === 'professional_only') {
      return { key: 'professional', label: 'Affiliate kapalı', detail: 'Ürün yerine güvenli yönlendirme ve profesyonel ölçüm gerekir.', all, fresh, stale };
    }
    if (category.affiliatePolicy === 'after_tool') {
      return { key: 'tool', label: 'Önce ücretsiz araç', detail: 'Yük, süre, gerilim, güç veya uyumluluk hesabı tamamlanmadan ürün rotası açılmaz.', all, fresh, stale };
    }
    if (category.affiliatePolicy === 'after_checklist') {
      return { key: 'checklist', label: 'Önce kontrol listesi', detail: 'Standart, ürün ömrü ve kullanım koşulu doğrulandıktan sonra kategori karşılaştırması yapılır.', all, fresh, stale };
    }
    if (fresh.length) {
      return { key: 'fresh', label: 'Güncel doğrulanmış kart', detail: `${fresh.length} kart 45 günlük teknik doğrulama sınırı içinde.`, all, fresh, stale };
    }
    if (stale) {
      return { key: 'stale', label: 'Doğrulama yenileme bekliyor', detail: `${stale} kartın doğrulama süresi geçtiği için doğrudan ürün bağlantısı kapalı.`, all, fresh, stale };
    }
    return { key: 'empty', label: 'Doğrulanmış kart yok', detail: 'ALO186 sırf sonuç üretmek için eksik veya kaynaksız ürün önermez.', all, fresh, stale };
  }

  function categoryAction(category, state) {
    if (category.nextStepUrl) return { href: category.nextStepUrl, label: category.nextStepLabel || 'Ücretsiz aracı aç' };
    if (state.key === 'professional') return { href: '/karar-motoru', label: 'Güvenli yönlendirmeyi aç' };
    return { href: `/akilli-urun-secimi?kategori=${encodeURIComponent(category.id)}`, label: 'Teknik eşleştirmeyi aç' };
  }

  document.addEventListener('DOMContentLoaded', () => {
    if (!catalog || !Array.isArray(catalog.categories) || !Array.isArray(catalog.products)) {
      byId('categoryGrid').innerHTML = '<p class="error">Katalog verisi yüklenemedi. Ürün bağlantısı gösterilmedi.</p>';
      return;
    }

    const now = new Date();
    const verified = catalog.products.filter((product) => product.status === 'verified_listing');
    const fresh = verified.filter((product) => catalog.verificationStatus(product, now).fresh);
    const dates = verified.map((product) => product.verifiedAt).filter(Boolean).sort();
    const latest = dates.length ? dates[dates.length - 1] : catalog.verifiedAt;
    const nextReview = addDays(latest, catalog.verificationMaxAgeDays);

    byId('categoryCount').textContent = String(catalog.categories.length);
    byId('verifiedCount').textContent = String(verified.length);
    byId('freshCount').textContent = String(fresh.length);
    byId('lastVerified').textContent = formatDate(latest);
    byId('nextReview').textContent = nextReview ? `En geç ${formatDate(nextReview)} yeniden doğrulama` : 'Yenileme tarihi bilinmiyor';

    byId('categoryGrid').innerHTML = catalog.categories.map((category) => {
      const state = categoryState(category, now);
      const action = categoryAction(category, state);
      return `<article class="category-card state-${state.key}"><div class="card-head"><span class="status">${escapeHtml(state.label)}</span><h3>${escapeHtml(category.name)}</h3></div><p>${escapeHtml(category.description)}</p><dl><div><dt>Affiliate politikası</dt><dd>${escapeHtml(category.affiliatePolicy)}</dd></div><div><dt>Doğrulanmış kart</dt><dd>${state.all.length}</dd></div><div><dt>Güncel / eski</dt><dd>${state.fresh.length} / ${state.stale}</dd></div></dl><p class="state-detail">${escapeHtml(state.detail)}</p><a class="button secondary category-action" data-category="${escapeHtml(category.id)}" data-policy="${escapeHtml(category.affiliatePolicy)}" data-status="${escapeHtml(state.key)}" href="${escapeHtml(action.href)}">${escapeHtml(action.label)}</a></article>`;
    }).join('');

    document.querySelectorAll('.category-action').forEach((link) => link.addEventListener('click', () => track('catalog_trust_category_opened', {
      category: link.dataset.category,
      policy: link.dataset.policy,
      status: link.dataset.status
    })));

    track('catalog_trust_status_viewed', { status: fresh.length === verified.length ? 'all_fresh' : 'mixed' });
  });
})();
