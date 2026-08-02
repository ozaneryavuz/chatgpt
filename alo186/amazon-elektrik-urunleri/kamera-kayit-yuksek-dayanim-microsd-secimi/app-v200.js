(() => {
  'use strict';

  const affiliateTag = 'alo186rehber-21';
  const verifiedAt = '2026-08-02';
  const maxAgeDays = 45;
  const gateIds = ['gateNeed', 'gateCompatibility', 'gateAffiliate'];
  const status = document.getElementById('gateStatus');
  const panel = document.getElementById('gatePanel');
  const links = [...document.querySelectorAll('[data-affiliate-asin]')];

  const dateOnly = value => {
    const date = new Date(`${value}T00:00:00Z`);
    return Number.isNaN(date.getTime()) ? null : date;
  };

  const verification = () => {
    const checked = dateOnly(verifiedAt);
    const now = dateOnly(new Date().toISOString().slice(0, 10));
    if (!checked || !now) return { fresh: false, ageDays: null };
    const ageDays = Math.max(0, Math.floor((now - checked) / 86400000));
    return { fresh: ageDays <= maxAgeDays, ageDays };
  };

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
    const freshness = verification();
    const open = gateOpen() && freshness.fresh;
    panel.dataset.open = String(open);

    links.forEach(link => {
      const asin = link.dataset.affiliateAsin;
      if (open) {
        link.href = `https://www.amazon.com.tr/dp/${encodeURIComponent(asin)}?tag=${encodeURIComponent(affiliateTag)}`;
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
    if (!gateOpen() || !verification().fresh) {
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
    verified_at: verifiedAt,
  });
})();
