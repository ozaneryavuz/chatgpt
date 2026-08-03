(function () {
  'use strict';

  const catalog = globalThis.Alo186LaptopCoolingCatalogV229;
  if (!catalog) return;

  const checks = ['measured', 'maintained', 'airflow', 'safe'];
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
        ? 'Ön kontrol ve satış ortaklığı onayı tamamlanmadan Amazon bağlantıları açılmaz.'
        : 'Ürün doğrulama süresi doldu. Amazon bağlantıları yenileme yapılana kadar kapalıdır.';
      return;
    }

    document.querySelectorAll('.shop').forEach((link) => {
      link.href = catalog.amazonProductUrl(link.dataset.asin);
      link.classList.remove('locked');
      link.setAttribute('aria-disabled', 'false');
    });
    gate.dataset.open = 'true';
    gateStatus.textContent = 'Kapı açıldı. Amazon sayfasında ASIN, model, ölçü ve fan yerleşimini yeniden doğrulayın.';
  }

  evaluate.addEventListener('click', () => {
    toolPassed = checks.every((id) => document.getElementById(id).checked);
    result.dataset.passed = String(toolPassed);
    result.textContent = toolPassed
      ? 'Ön kontrol geçti. İhtiyaca uygun ürünleri sınırlarıyla karşılaştırabilirsiniz.'
      : 'Kontrollerin tamamı geçmedi. Yeni soğutucu satın almak yerine bakım, güvenlik veya hava girişi sorununu çözün.';
    refresh();
  });

  disclosure.addEventListener('change', refresh);
  lock();
})();
