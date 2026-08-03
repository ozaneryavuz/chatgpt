(() => {
  'use strict';
  const start = () => {
    const catalog = window.Alo186VehicleUsbChargerCatalogV235;
    const toolChecks = ['toolSocket','toolDevicePower','toolPorts','toolCable','toolNoDamage','toolScope','toolExisting'];
    const commerceChecks = ['gateNeed','gateAffiliate'];
    const toolButton = document.getElementById('runCompatibilityTool');
    const toolResult = document.getElementById('toolResult');
    const gatePanel = document.getElementById('gatePanel');
    const gateStatus = document.getElementById('gateStatus');
    const links = [...document.querySelectorAll('[data-affiliate-asin]')];
    let toolPassed = false;
    let toolEvaluated = false;
    if (!catalog || !toolButton || !toolResult || !gatePanel || !gateStatus) return;
    const checked = (ids) => ids.every((id) => document.getElementById(id)?.checked === true);
    const sync = () => {
      const freshness = catalog.verificationStatus(new Date());
      const categoryAllowed = catalog.category.affiliatePolicy === 'after_tool'
        && catalog.category.requiredTool === 'embedded-vehicle-accessory-socket-usb-power-measurement-v235'
        && catalog.category.professionalOnly === false
        && catalog.category.risk === 'consumer-medium';
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
      if (!freshness.fresh) gateStatus.textContent = 'Ürün kimliği doğrulaması 45 günü aştı; Amazon bağlantıları kapalı.';
      else if (!toolPassed) gateStatus.textContent = 'Önce araç prizi, cihaz gücü, port, kablo, hasar ve kullanım kapsamını doğrulayın.';
      else if (!checked(commerceChecks)) gateStatus.textContent = 'Teknik ön kontrol geçti; gerçek ihtiyaç ve satış ortaklığı açıklamasını doğrulayın.';
      else if (!categoryAllowed) gateStatus.textContent = 'Kategori güven sözleşmesi doğrulanamadı; bağlantılar kapalı.';
      else gateStatus.textContent = 'Koşullar tamamlandı. Amazon Türkiye kaydında ASIN ve MPN değerlerini yeniden doğrulayın.';
    };
    toolButton.addEventListener('click', () => {
      toolEvaluated = true;
      toolPassed = checked(toolChecks);
      toolResult.dataset.passed = String(toolPassed);
      toolResult.textContent = toolPassed
        ? 'Ön kontrol geçti: yalnız sağlam araç aksesuar prizinde, kritik olmayan tüketici cihazları için ürünler karşılaştırılabilir.'
        : 'Ön kontrol geçmedi: araç prizi, güç/protokol, kablo, fiziksel durum, mevcut çözüm ve kritik olmayan kullanım birlikte doğrulanmalıdır.';
      sync();
    });
    [...toolChecks, ...commerceChecks].forEach((id) => document.getElementById(id)?.addEventListener('change', () => {
      if (toolChecks.includes(id)) {
        toolPassed = false;
        toolEvaluated = false;
        toolResult.dataset.passed = 'false';
        toolResult.textContent = 'Teknik girdiler değişti; ön kontrolü yeniden çalıştırın.';
      }
      sync();
    }));
    document.getElementById('resetGate')?.addEventListener('click', () => {
      [...toolChecks, ...commerceChecks].forEach((id) => {
        const input = document.getElementById(id);
        if (input) input.checked = false;
      });
      toolPassed = false;
      toolEvaluated = false;
      toolResult.dataset.passed = 'false';
      toolResult.textContent = 'Henüz değerlendirilmedi.';
      sync();
    });
    links.forEach((link) => link.addEventListener('click', (event) => {
      if (!toolEvaluated || !toolPassed || !checked(commerceChecks) || !catalog.verificationStatus(new Date()).fresh || !link.href) {
        event.preventDefault();
        sync();
      }
    }));
    sync();
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, {once: true});
  else start();
})();
