(() => {
  'use strict';
  document.querySelectorAll('[data-commerce-gate]').forEach((gate) => {
    const checks = [...gate.querySelectorAll('[data-commerce-check]')];
    const link = gate.querySelector('[data-affiliate-link]');
    const status = gate.querySelector('[data-commerce-status]');
    if (!checks.length || !link || !status) return;
    const update = () => {
      const ready = checks.every((item) => item.checked);
      link.setAttribute('aria-disabled', ready ? 'false' : 'true');
      link.tabIndex = ready ? 0 : -1;
      status.classList.toggle('ready', ready);
      status.textContent = ready
        ? 'Teknik kontrol beyanı tamamlandı. Amazon araması ürün uygunluk onayı değildir.'
        : `${checks.filter((item) => !item.checked).length} teknik kontrol daha gerekli.`;
      if (ready && typeof window.Alo186Track === 'function') {
        window.Alo186Track('commerce_gate_completed', {
          category: gate.dataset.category || 'unknown',
          placement: 'commerce_guide'
        });
      }
    };
    checks.forEach((item) => item.addEventListener('change', update));
    link.addEventListener('click', (event) => {
      if (link.getAttribute('aria-disabled') !== 'false') {
        event.preventDefault();
        status.textContent = 'Amazon aramasından önce bütün teknik kontrolleri onaylayın.';
        return;
      }
      if (typeof window.Alo186Track === 'function') {
        window.Alo186Track('affiliate_search_clicked', {
          category: gate.dataset.category || 'unknown',
          placement: 'commerce_guide'
        });
      }
    });
    update();
  });
})();
