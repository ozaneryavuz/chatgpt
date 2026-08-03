(() => {
  'use strict';
  const start = () => {
    const catalog = window.Alo186WebcamCatalogV232;
    const toolChecks = ['toolNeed', 'toolUsb', 'toolResolution', 'toolPrivacy', 'toolScope'];
    const gateChecks = ['gateNeed', 'gateAffiliate'];
    const run = document.getElementById('runTool');
    const result = document.getElementById('toolResult');
    const panel = document.getElementById('gatePanel');
    const status = document.getElementById('gateStatus');
    const links = [...document.querySelectorAll('[data-affiliate-asin]')];
    let toolPassed = false;
    if (!catalog || !run || !result || !panel || !status) return;

    const checked = (ids) => ids.every((id) => document.getElementById(id)?.checked === true);
    const sync = () => {
      const freshness = catalog.verificationStatus(new Date());
      const policyOk = catalog.category.affiliatePolicy === 'after_tool'
        && catalog.category.requiredTool === 'embedded-webcam-need-compatibility-v232'
        && catalog.category.professionalOnly === false
        && catalog.category.risk === 'consumer-low';
      const open = policyOk && toolPassed && checked(gateChecks) && freshness.fresh;
      const known = new Set(catalog.products.map((item) => item.asin));
      panel.dataset.open = String(open);
      links.forEach((link) => {
        const allowed = open && known.has(link.dataset.affiliateAsin);
        if (allowed) {
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
      if (!freshness.fresh) status.textContent = 'Teknik doğrulama 45 günü aştı; Amazon bağlantıları kapalı.';
      else if (!toolPassed) status.textContent = 'Önce gerçek ihtiyaç, USB bağlantısı, çözünürlük, gizlilik ve kullanım kapsamını doğrulayın.';
      else if (!checked(gateChecks)) status.textContent = 'Ön kontrol geçti; gerçek ihtiyaç ve satış ortaklığı açıklamasını ayrıca doğrulayın.';
      else if (!policyOk) status.textContent = 'Kategori güven sözleşmesi doğrulanamadı; bağlantılar kapalı.';
      else status.textContent = 'Koşullar tamamlandı; Amazon’da ASIN, MPN ve paket içeriğini yeniden doğrulayın.';
    };

    run.addEventListener('click', () => {
      toolPassed = checked(toolChecks);
      result.dataset.passed = String(toolPassed);
      result.textContent = toolPassed ? 'Ön kontrol geçti: tüketici tipi USB web kameraları karşılaştırılabilir.' : 'Ön kontrol geçmedi: bütün teknik ve ihtiyaç koşullarını doğrulayın.';
      sync();
    });
    [...toolChecks, ...gateChecks].forEach((id) => document.getElementById(id)?.addEventListener('change', () => {
      if (toolChecks.includes(id)) {
        toolPassed = false;
        result.dataset.passed = 'false';
        result.textContent = 'Girdiler değişti; ön kontrolü yeniden çalıştırın.';
      }
      sync();
    }));
    document.getElementById('resetGate')?.addEventListener('click', () => {
      [...toolChecks, ...gateChecks].forEach((id) => { const input = document.getElementById(id); if (input) input.checked = false; });
      toolPassed = false;
      result.dataset.passed = 'false';
      result.textContent = 'Henüz değerlendirilmedi.';
      sync();
    });
    links.forEach((link) => link.addEventListener('click', (event) => {
      if (!toolPassed || !checked(gateChecks) || !catalog.verificationStatus(new Date()).fresh || !link.href) {
        event.preventDefault();
        sync();
      }
    }));
    sync();
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, { once: true });
  else start();
})();