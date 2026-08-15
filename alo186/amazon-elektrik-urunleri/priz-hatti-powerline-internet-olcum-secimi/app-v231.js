(function () {
  'use strict';
  const catalog = globalThis.Alo186PowerlineInternetCatalogV231;
  if (!catalog) return;
  const checks = ['measured', 'wallOutlet', 'boundary', 'safe', 'nonCritical'];
  const evaluate = document.getElementById('evaluate');
  const disclosure = document.getElementById('disclosure');
  const result = document.getElementById('result');
  const gate = document.getElementById('gate');
  const gateStatus = document.getElementById('gateStatus');
  let toolPassed = false;

  function lock() {
    document.querySelectorAll('.shop').forEach((link) => {
      link.removeAttribute('href');
      link.classList.add('locked');
      link.setAttribute('aria-disabled', 'true');
    });
    gate.dataset.open = 'false';
  }

  function refresh() {
    const fresh = catalog.verificationStatus(new Date()).fresh;
    const policyOk = catalog.category.affiliatePolicy === 'after_tool';
    const professionalOk = catalog.category.professionalOnly === false;
    const open = toolPassed && disclosure.checked && fresh && policyOk && professionalOk;
    lock();
    if (!open) {
      gateStatus.textContent = fresh
        ? 'Ölçüm, priz güvenliği, tesisat sınırı ve satış ortaklığı onayı tamamlanmadan Amazon bağlantıları açılmaz.'
        : 'Ürün doğrulama süresi doldu. Amazon bağlantıları yeniden doğrulama yapılana kadar kapalıdır.';
      return;
    }
    document.querySelectorAll('.shop').forEach((link) => {
      link.href = catalog.amazonProductUrl(link.dataset.asin);
      link.classList.remove('locked');
      link.setAttribute('aria-disabled', 'false');
    });
    gate.dataset.open = 'true';
    gateStatus.textContent = 'Kapı açıldı. Amazon Türkiye sayfasında ASIN, model, donanım sürümü ve paket içeriğini yeniden doğrulayın.';
  }

  evaluate.addEventListener('click', () => {
    toolPassed = checks.every((id) => document.getElementById(id).checked);
    result.dataset.passed = String(toolPassed);
    result.textContent = toolPassed
      ? 'Ön kontrol geçti. Ürünleri tesisat ve hız sınırlarıyla karşılaştırabilirsiniz.'
      : 'Kontrollerin tamamı geçmedi. Yeni ürün satın almak yerine Wi-Fi yerleşimi, Ethernet, mesh, priz güvenliği veya tesisat sınırını çözün.';
    refresh();
  });
  disclosure.addEventListener('change', refresh);
  lock();
})();
