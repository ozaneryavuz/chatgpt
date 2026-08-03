(() => {
  'use strict';

  const start = () => {
    const catalog = window.Alo186UsbFlashCatalogV226;
    const toolChecks = ['toolTask', 'toolPorts', 'toolCapacity', 'toolCopies', 'toolSecurity'];
    const commerceChecks = ['gateNeed', 'gateAffiliate'];
    const toolButton = document.getElementById('runFitTool');
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
        && catalog.category.requiredTool === 'embedded-usb-flash-transfer-fit-v226'
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
        gateStatus.textContent = 'Teknik doğrulama 45 günü aştı. Amazon bağlantıları kayıtlar yenilenene kadar kapalı.';
      } else if (!toolPassed) {
        gateStatus.textContent = 'Mağaza bağlantıları kapalı. Önce görev, bağlantı tipi, kapasite, ikinci kopya ve veri hassasiyeti koşullarını doğrulayın.';
      } else if (!checked(commerceChecks)) {
        gateStatus.textContent = 'Teknik ön kontrol geçti. Gerçek ihtiyaç ve satış ortaklığı açıklamasını ayrıca doğrulayın.';
      } else if (!categoryAllowed) {
        gateStatus.textContent = 'Kategori güven sözleşmesi doğrulanamadı. Mağaza bağlantıları kapalı.';
      } else {
        gateStatus.textContent = 'Koşullar tamamlandı. Amazon’da ASIN, tam model kodu, kapasite ve bağlantı tipini yeniden doğrulayın.';
      }
    };

    toolButton.addEventListener('click', () => {
      toolPassed = checked(toolChecks);
      toolResult.dataset.passed = String(toolPassed);
      toolResult.textContent = toolPassed
        ? 'Ön kontrol geçti: USB bellek yalnız geçici çevrimdışı aktarım veya ikinci kopya görevi için karşılaştırılabilir.'
        : 'Ön kontrol geçmedi: USB bellek tek kopyalı yedek, hassas veri kasası veya doğrulanmamış port uyumu için seçilmemelidir.';
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
      const fresh = catalog.verificationStatus(new Date()).fresh;
      if (!toolPassed || !checked(commerceChecks) || !fresh || !link.href) {
        event.preventDefault();
        sync();
      }
    }));

    sync();
  };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, { once: true });
  else start();
})();
