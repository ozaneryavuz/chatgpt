(() => {
  'use strict';

  const catalog = window.Alo186EnduranceMicroSDCatalogV200;
  const gateIds = ['gateNeed', 'gateCompatibility', 'gateAffiliate'];
  const status = document.getElementById('gateStatus');
  const panel = document.getElementById('gatePanel');
  const links = [...document.querySelectorAll('[data-affiliate-asin]')];

  const gateOpen = () => gateIds.every(id => document.getElementById(id)?.checked);

  const track = (name, params = {}) => {
    const payload = { collection: 'endurance_microsd_v200', ...params };
    try {
      if (typeof window.Alo186Track === 'function') window.Alo186Track(name, payload);
    } catch (_error) {}
    try {
      const analytics = window.alo186Analytics;
      if (analytics && typeof analytics.track === 'function') {
        if (typeof analytics.getConsent !== 'function' || analytics.getConsent() === 'granted') {
          analytics.track(name, payload);
        }
      }
    } catch (_error) {}
  };

  const sync = () => {
    const freshness = catalog?.verificationStatus(new Date()) || { fresh: false, ageDays: null };
    const knownAsins = new Set(catalog?.products?.map(item => item.asin) || []);
    const open = Boolean(catalog) && gateOpen() && freshness.fresh;
    panel.dataset.open = String(open);

    links.forEach(link => {
      const asin = link.dataset.affiliateAsin;
      const permitted = open && knownAsins.has(asin);
      if (permitted) {
        link.href = catalog.amazonProductUrl(asin);
        link.classList.remove('locked');
        link.removeAttribute('aria-disabled');
        link.tabIndex = 0;
      } else {
        link.removeAttribute('href');
        link.classList.add('locked');
        link.setAttribute('aria-disabled', 'true');
        link.tabIndex = -1;
      }
    });

    if (!catalog) {
      status.textContent = 'Doğrulanmış model kataloğu yüklenemedi. Amazon bağlantıları güvenlik gereği kapalı.';
      return;
    }
    if (!freshness.fresh) {
      status.textContent = 'Model doğrulama tarihi 45 günü aştı. Amazon bağlantıları teknik kayıtlar yenilenene kadar kapalı.';
      return;
    }
    status.textContent = open
      ? 'Üç koşul doğrulandı. Model, kapasite ve cihaz desteğini Amazon’da ve kamera kılavuzunda yeniden kontrol edin.'
      : 'Mağaza bağlantıları kapalı. Gerçek ihtiyaç, cihaz uyumu ve satış ortaklığı açıklamasını doğrulayın.';
  };

  gateIds.forEach(id => document.getElementById(id)?.addEventListener('change', () => {
    sync();
    track('affiliate_endurance_microsd_gate_changed', { field: id, open: gateOpen() });
  }));

  document.getElementById('resetGate')?.addEventListener('click', () => {
    gateIds.forEach(id => {
      const input = document.getElementById(id);
      if (input) input.checked = false;
    });
    sync();
    track('affiliate_endurance_microsd_gate_reset');
  });

  links.forEach(link => link.addEventListener('click', event => {
    const fresh = catalog?.verificationStatus(new Date()).fresh;
    if (!catalog || !gateOpen() || !fresh) {
      event.preventDefault();
      return;
    }
    track('affiliate_endurance_microsd_clicked', {
      asin: link.dataset.affiliateAsin,
      model: link.dataset.model,
    });
  }));

  sync();
  track('affiliate_endurance_microsd_viewed', {
    product_count: links.length,
    verified_at: catalog?.verifiedAt || null,
    catalog_version: catalog?.version || null,
  });
})();
