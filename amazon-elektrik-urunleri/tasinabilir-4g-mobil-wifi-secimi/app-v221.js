(() => {
  'use strict';

  const start = () => {
    const catalog = window.Alo186MobileWifiCatalogV221;
    const toolChecks = ['toolCoverage', 'toolSim', 'toolCapacity', 'toolPower'];
    const commerceChecks = ['gateNeed', 'gateAffiliate'];
    const toolButton = document.getElementById('runCompatibilityTool');
    const toolResult = document.getElementById('toolResult');
    const gatePanel = document.getElementById('gatePanel');
    const gateStatus = document.getElementById('gateStatus');
    const resetButton = document.getElementById('resetGate');
    const links = [...document.querySelectorAll('[data-affiliate-asin]')];
    let toolPassed = false;

    if (!catalog || !toolButton || !toolResult || !gatePanel || !gateStatus) return;

    const allChecked = (ids) => ids.every((id) => document.getElementById(id)?.checked === true);

    const track = (eventName, parameters = {}) => {
      const safe = { collection: 'portable_4g_mobile_wifi_v221', ...parameters };
      try {
        if (typeof window.Alo186Track === 'function') window.Alo186Track(eventName, safe);
      } catch (_error) {}
      try {
        const analytics = window.alo186Analytics;
        if (analytics && typeof analytics.track === 'function') {
          if (typeof analytics.getConsent !== 'function' || analytics.getConsent() === 'granted') {
            analytics.track(eventName, safe);
          }
        }
      } catch (_error) {}
    };

    const sync = () => {
      const freshness = catalog.verificationStatus(new Date());
      const categoryAllowed = catalog.category.affiliatePolicy === 'after_tool'
        && catalog.category.requiredTool === 'embedded-mobile-wifi-compatibility-v221'
        && catalog.category.professionalOnly === false
        && catalog.category.risk === 'consumer-medium';
      const gateOpen = categoryAllowed && toolPassed && allChecked(commerceChecks) && freshness.fresh;
      const knownAsins = new Set(catalog.products.map((item) => item.asin));

      gatePanel.dataset.open = String(gateOpen);
      links.forEach((link) => {
        const asin = link.dataset.affiliateAsin;
        const permitted = gateOpen && knownAsins.has(asin);
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

      if (!freshness.fresh) {
        gateStatus.textContent = 'Ürün doğrulaması 45 günü aştı. Amazon bağlantıları kayıtlar yenilenene kadar kapalı.';
      } else if (!toolPassed) {
        gateStatus.textContent = 'Mağaza bağlantıları kapalı. Önce 4G/SIM/kapasite/güç uygunluk kontrolünü başarıyla tamamlayın.';
      } else if (!allChecked(commerceChecks)) {
        gateStatus.textContent = 'Teknik ön kontrol tamamlandı. Mevcut çözüm ihtiyacı ve satış ortaklığı açıklamasını doğrulayın.';
      } else if (!categoryAllowed) {
        gateStatus.textContent = 'Kategori güven sözleşmesi doğrulanamadı. Mağaza bağlantıları kapalı.';
      } else {
        gateStatus.textContent = 'Koşullar tamamlandı. Tam model, donanım sürümü, SIM ve bölgesel uyumu Amazon ile üretici sayfasında yeniden doğrulayın.';
      }
    };

    toolButton.addEventListener('click', () => {
      toolPassed = allChecked(toolChecks);
      toolResult.dataset.passed = String(toolPassed);
      toolResult.textContent = toolPassed
        ? 'Ön kontrol geçti: tüketici tipi taşınabilir 4G mobil Wi-Fi modelleri karşılaştırılabilir. Bu sonuç kapsama veya çalışma süresi garantisi değildir.'
        : 'Ön kontrol geçmedi: eksik koşulları tamamlamadan ürün seçmeyin. Mobil kapsama, SIM/operatör uyumu, cihaz sayısı ve şarj yolu birlikte doğrulanmalıdır.';
      track('affiliate_mobile_wifi_tool_result', { result: toolPassed ? 'pass' : 'blocked' });
      sync();
    });

    [...toolChecks, ...commerceChecks].forEach((id) => {
      document.getElementById(id)?.addEventListener('change', () => {
        if (toolChecks.includes(id)) {
          toolPassed = false;
          toolResult.dataset.passed = 'false';
          toolResult.textContent = 'Teknik girdiler değişti. Ön kontrolü yeniden çalıştırın.';
        }
        sync();
      });
    });

    resetButton?.addEventListener('click', () => {
      [...toolChecks, ...commerceChecks].forEach((id) => {
        const input = document.getElementById(id);
        if (input) input.checked = false;
      });
      toolPassed = false;
      toolResult.dataset.passed = 'false';
      toolResult.textContent = 'Henüz değerlendirilmedi.';
      track('affiliate_mobile_wifi_gate_reset');
      sync();
    });

    links.forEach((link) => link.addEventListener('click', (event) => {
      const freshness = catalog.verificationStatus(new Date());
      if (!toolPassed || !allChecked(commerceChecks) || !freshness.fresh || !link.href) {
        event.preventDefault();
        sync();
        return;
      }
      track('affiliate_mobile_wifi_select', { model: link.dataset.productModel || 'unknown' });
    }));

    sync();
  };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, { once: true });
  else start();
})();
