(() => {
  'use strict';
  const start = () => {
    const catalog = window.Alo186NvmeSsdCatalogV236;
    const toolChecks = ['toolSlot','toolProtocol','toolSize','toolBackup','toolPower','toolScope','toolNeed'];
    const commerceChecks = ['gateNeed','gateAffiliate'];
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
        && catalog.category.requiredTool === 'embedded-nvme-slot-backup-compatibility-v236'
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
          link.setAttribute('aria-disabled','true');
          link.tabIndex = -1;
        }
      });
      if (!freshness.fresh) gateStatus.textContent = 'Ürün kimliği doğrulaması 45 günü aştı; Amazon bağlantıları kapalı.';
      else if (!toolPassed) gateStatus.textContent = 'Önce yuva, NVMe protokolü, boyut, yedekleme, enerjisiz çalışma ve kullanım kapsamını doğrulayın.';
      else if (!checked(commerceChecks)) gateStatus.textContent = 'Teknik ön kontrol geçti; gerçek ihtiyaç ve satış ortaklığı açıklamasını doğrulayın.';
      else if (!categoryAllowed) gateStatus.textContent = 'Kategori güven sözleşmesi doğrulanamadı; bağlantılar kapalı.';
      else gateStatus.textContent = 'Koşullar tamamlandı. Amazon kaydında ASIN ve MPN ile cihaz kılavuzundaki uyumu yeniden doğrulayın.';
    };
    toolButton.addEventListener('click', () => {
      toolPassed = checked(toolChecks);
      toolResult.dataset.passed = String(toolPassed);
      toolResult.textContent = toolPassed
        ? 'Ön kontrol geçti: yalnız kritik olmayan kişisel bilgisayarda, tamamen enerjisiz ve kılavuzla doğrulanmış M.2 NVMe yükseltmesi karşılaştırılabilir.'
        : 'Ön kontrol geçmedi: cihazı açmayın ve ürün bağlantısını kullanmayın. Üretici kılavuzu veya yetkin teknik destekle uyumu doğrulayın.';
      sync();
    });
    [...toolChecks,...commerceChecks].forEach((id) => document.getElementById(id)?.addEventListener('change', () => {
      if (toolChecks.includes(id)) {
        toolPassed = false;
        toolResult.dataset.passed = 'false';
        toolResult.textContent = 'Teknik girdiler değişti; ön kontrolü yeniden çalıştırın.';
      }
      sync();
    }));
    document.getElementById('resetGate')?.addEventListener('click', () => {
      [...toolChecks,...commerceChecks].forEach((id) => { const input=document.getElementById(id); if(input) input.checked=false; });
      toolPassed = false;
      toolResult.dataset.passed = 'false';
      toolResult.textContent = 'Henüz değerlendirilmedi.';
      sync();
    });
    links.forEach((link) => link.addEventListener('click', (event) => {
      if (!toolPassed || !checked(commerceChecks) || !catalog.verificationStatus(new Date()).fresh || !link.href) {
        event.preventDefault(); sync();
      }
    }));
    sync();
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, {once:true}); else start();
})();
