(function () {
  'use strict';
  const catalog = globalThis.Alo186DisplayCableCatalogV229;
  if (!catalog) return;
  const ids = ['ports','direction','target','rootcause'];
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
      link.setAttribute('aria-disabled','true');
    });
    gate.dataset.open='false';
  }
  function refresh() {
    const fresh = catalog.verificationStatus(new Date()).fresh;
    const policyOk = catalog.category.affiliatePolicy === 'after_tool';
    const professionalOk = catalog.category.professionalOnly === false;
    const open = toolPassed && disclosure.checked && fresh && policyOk && professionalOk;
    lock();
    if (!open) {
      gateStatus.textContent = fresh ? 'Ön kontrol ve onay tamamlanmadan Amazon bağlantıları açılmaz.' : 'Teknik doğrulama süresi doldu; bağlantılar kapalı.';
      return;
    }
    document.querySelectorAll('.shop').forEach((link) => {
      link.href = catalog.amazonProductUrl(link.dataset.asin);
      link.classList.remove('locked');
      link.setAttribute('aria-disabled','false');
    });
    gate.dataset.open='true';
    gateStatus.textContent='Kapı açıldı. Amazon sayfasında ASIN, port standardı ve bağlantı yönünü yeniden doğrulayın.';
  }
  evaluate.addEventListener('click', () => {
    toolPassed = ids.every((id) => document.getElementById(id).checked);
    result.textContent = toolPassed ? 'Ön kontrol geçti. Satış ortaklığı onayını tamamlayabilirsiniz.' : 'Tüm uyumluluk kontrolleri geçmedi. Yeni kablo satın almayın; kök nedeni doğrulayın.';
    refresh();
  });
  disclosure.addEventListener('change', refresh);
  lock();
})();
