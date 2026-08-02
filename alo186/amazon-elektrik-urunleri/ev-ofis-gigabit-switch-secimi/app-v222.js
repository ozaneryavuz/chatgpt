(() => {
  'use strict';

  const start = () => {
    const catalog = window.Alo186GigabitSwitchCatalogV222;
    const toolChecks = ['toolPorts', 'toolSpeed', 'toolNoPoe', 'toolScope'];
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
        && catalog.category.requiredTool === 'embedded-gigabit-switch-compatibility-v222'
        && catalog.category.professionalOnly === false
        && catalog.category.risk === 'consumer-medium';
      const open = categoryAllowed && toolPassed && checked(commerceChecks) && freshness.fresh;
      const knownAsins = new Set(catalog.products.map((item) => item.asin));

      gatePanel.dataset.open = String(open);
      links.forEach((link) => {
        const permitted = open && knownAsins.has(link.dataset.affiliateAsin);
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

      if (!freshness.fresh) gateStatus.textContent = 'Teknik doğrulama 45 günü aştı. Amazon bağlantıları kayıtlar yenilenene kadar kapalı.';
      else if (!toolPassed) gateStatus.textContent = 'Mağaza bağlantıları kapalı. Önce port, hız, PoE ve kullanım kapsamını doğrulayın.';
      else if (!checked(commerceChecks)) gateStatus.textContent = 'Teknik kontrol geçti. Mevcut çözümün yetersizliğini ve satış ortaklığı açıklamasını doğrulayın.';
      else if (!categoryAllowed) gateStatus.textContent = 'Kategori güven sözleşmesi doğrulanamadı. Mağaza bağlantıları kapalı.';
      else gateStatus.textContent = 'Koşullar tamamlandı. Tam model, donanım sürümü, port sayısı ve PoE ihtiyacını Amazon ile üretici sayfasında yeniden doğrulayın.';
    };

    toolButton.addEventListener('click', () => {
      toolPassed = checked(toolChecks);
      toolResult.dataset.passed = String(toolPassed);
      toolResult.textContent = toolPassed
        ? 'Ön kontrol geçti: yalnız tüketici tipi, PoE’siz masaüstü Gigabit switch modelleri karşılaştırılabilir.'
        : 'Ön kontrol geçmedi: port sayısı, Gigabit uçtan uca destek, PoE gereksinimi ve profesyonel kapsam birlikte doğrulanmalıdır.';
      sync();
    });

    [...toolChecks, ...commerceChecks].forEach((id) => document.getElementById(id)?.addEventListener('change', () => {
      if (toolChecks.includes(id)) {
        toolPassed = false;
        toolResult.dataset.passed = 'false';
        toolResult.textContent = 'Teknik girdiler değişti. Ön kontrolü yeniden çalıştırın.';
      }
      sync();
    }));

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
