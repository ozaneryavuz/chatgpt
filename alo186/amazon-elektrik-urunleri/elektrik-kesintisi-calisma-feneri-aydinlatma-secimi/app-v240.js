(() => {
  'use strict';

  const start = () => {
    const catalog = window.Alo186PortableWorkLightCatalogV240;
    const toolChecks = [
      'toolNeed',
      'toolNoEmergency',
      'toolNoLiveWork',
      'toolEnvironment',
      'toolBattery',
      'toolIdentity'
    ];
    const commerceChecks = ['gateNeed', 'gateAffiliate'];
    const toolButton = document.getElementById('runCompatibilityTool');
    const toolResult = document.getElementById('toolResult');
    const gatePanel = document.getElementById('gatePanel');
    const gateStatus = document.getElementById('gateStatus');
    const links = [...document.querySelectorAll('[data-affiliate-asin]')];
    let toolPassed = false;

    if (!catalog || !toolButton || !toolResult || !gatePanel || !gateStatus) return;

    const checked = (ids) => ids.every((id) => document.getElementById(id)?.checked === true);

    const sync = () => {
      const freshness = catalog.verificationStatus(new Date());
      const categoryAllowed = catalog.category.affiliatePolicy === 'after_tool'
        && catalog.category.requiredTool === 'embedded-portable-work-light-outage-inspection-v240'
        && catalog.category.professionalOnly === false
        && catalog.category.risk === 'consumer-low';
      const gateOpen = categoryAllowed && toolPassed && checked(commerceChecks) && freshness.fresh;
      const knownAsins = new Set(catalog.products.map((item) => item.asin));

      gatePanel.dataset.open = String(gateOpen);
      links.forEach((link) => {
        const permitted = gateOpen && knownAsins.has(link.dataset.affiliateAsin);
        if (permitted) {
          link.href = catalog.amazonProductUrl(link.dataset.affiliateAsin);
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
        gateStatus.textContent = 'Ürün kimliği doğrulaması 45 günü aştı; Amazon bağlantıları kapalı.';
      } else if (!toolPassed) {
        gateStatus.textContent = 'Önce kullanım görevi, ortam, batarya durumu ve ürün kimliğini doğrulayın.';
      } else if (!checked(commerceChecks)) {
        gateStatus.textContent = 'Teknik ön kontrol geçti; gerçek ihtiyaç ve satış ortaklığı açıklamasını doğrulayın.';
      } else if (!categoryAllowed) {
        gateStatus.textContent = 'Kategori güven sözleşmesi doğrulanamadı; bağlantılar kapalı.';
      } else {
        gateStatus.textContent = 'Koşullar tamamlandı. Amazon kaydında ASIN, MPN, ışık gücü ve IP sınıfını yeniden doğrulayın.';
      }
    };

    toolButton.addEventListener('click', () => {
      toolPassed = checked(toolChecks);
      toolResult.dataset.passed = String(toolPassed);
      toolResult.textContent = toolPassed
        ? 'Ön kontrol geçti: yalnız elektrik kesintisi hazırlığı ve gerilimsiz, düşük riskli yakın alan aydınlatması için ürünler karşılaştırılabilir.'
        : 'Ön kontrol geçmedi: acil durum, gerilim altında çalışma, ortam koşulları, batarya ve ürün kimliği birlikte doğrulanmalıdır.';
      sync();
    });

    [...toolChecks, ...commerceChecks].forEach((id) => {
      document.getElementById(id)?.addEventListener('change', () => {
        if (toolChecks.includes(id)) {
          toolPassed = false;
          toolResult.dataset.passed = 'false';
          toolResult.textContent = 'Teknik girdiler değişti; ön kontrolü yeniden çalıştırın.';
        }
        sync();
      });
    });

    document.getElementById('resetGate')?.addEventListener('click', () => {
      [...toolChecks, ...commerceChecks].forEach((id) => {
        const input = document.getElementById(id);
        if (input) input.checked = false;
      });
      toolPassed = false;
      toolResult.dataset.passed = 'false';
      toolResult.textContent = 'Henüz değerlendirilmedi.';
      sync();
    });

    links.forEach((link) => link.addEventListener('click', (event) => {
      if (!toolPassed || !checked(commerceChecks) || !catalog.verificationStatus(new Date()).fresh || !link.href) {
        event.preventDefault();
        sync();
      }
    }));

    sync();
  };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, { once: true });
  else start();
})();
