(() => {
  'use strict';

  const checklist = [
    ['Sürekli ve kalkış gücü', 'Hesap sonucundaki asgari sürekli W ve kalkış W değerlerinin ikisini de ürün etiketinde doğrulayın.'],
    ['Gerilim, frekans ve faz', '230 V / 50 Hz ve monofaze ihtiyacınızı doğrulayın; trifaze seçim profesyonel projelendirme gerektirir.'],
    ['CO ve dış ortam güvenliği', 'Yakıtlı jeneratörü yalnız açık havada kullanın; CO algılama özelliği temel yerleşim kurallarının yerine geçmez.'],
    ['Bağlantı biçimi', 'Bina devreleri için prize ters besleme yapmayın; uygun transfer sistemi yetkili elektrikçi tarafından kurulmalıdır.'],
    ['İşletme koşulları', 'Gürültü, yakıt, çalışma süresi, rakım/sıcaklık düşümü, bakım ve yetkili servis koşullarını karşılaştırın.']
  ];

  const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, char => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[char]);

  function selectedGenerator() {
    const active = document.querySelector('[data-category="generator"][aria-pressed="true"]');
    return Boolean(active);
  }

  function checklistMarkup(marker) {
    return `<div class="guide-list generator-guide-extension" data-generator-guide="${marker}">${checklist.map(([title, text]) => `<div class="guide-item"><b>${escapeHtml(title)}</b><span>${escapeHtml(text)}</span></div>`).join('')}</div>`;
  }

  function injectRequirementChecklist() {
    if (!selectedGenerator()) return;
    const target = document.getElementById('requirementFields');
    if (!target || target.querySelector('[data-generator-guide]')) return;
    target.insertAdjacentHTML('beforeend', checklistMarkup('requirements'));
  }

  function injectResultChecklist() {
    if (!selectedGenerator()) return;
    const target = document.getElementById('guideResult');
    if (!target || target.querySelector('[data-generator-guide]')) return;
    const heading = target.querySelector('h3');
    if (heading) heading.insertAdjacentHTML('afterend', checklistMarkup('result'));
    else target.insertAdjacentHTML('afterbegin', checklistMarkup('result'));
  }

  function enablePostCalculationAffiliate() {
    const params = new URLSearchParams(location.search);
    if (!selectedGenerator() || params.get('hesaplandi') !== '1') return;
    const target = document.getElementById('guideResult');
    const catalog = window.Alo186ProductCatalog;
    if (!target || !catalog) return;

    target.querySelectorAll('.decision-gate,.actions').forEach(node => node.remove());
    const searchUrl = catalog.searchUrl('generator');
    target.insertAdjacentHTML('beforeend', `<div class="decision-gate generator-post-calc"><b>Hesaplama tamamlandı; yine de ürün etiketini doğrulayın.</b><p>ALO186 marka veya model onayı vermez. Sonuçtaki sürekli ve kalkış W değerlerini, gerilim/fazı, CO güvenliğini, gürültüyü, yakıtı ve servis koşullarını satıcının güncel sayfasında yeniden kontrol edin.</p><label class="check-item"><input type="checkbox" data-generator-confirm><span><b>Hesap sonucumu ve yukarıdaki teknik kontrol listesini ürün sayfasında yeniden doğrulayacağım.</b><br><small>Fiyat, stok, satıcı, garanti ve nihai teknik özellik yalnız Amazon’un güncel sayfasında doğrulanır.</small></span></label><div class="actions"><a class="btn btn-primary disabled-link" data-generator-amazon aria-disabled="true" tabindex="-1" href="${escapeHtml(searchUrl)}" target="_blank" rel="sponsored nofollow noopener">Amazon’da teknik ifadelerle ara</a></div></div>`);

    const confirm = target.querySelector('[data-generator-confirm]');
    const link = target.querySelector('[data-generator-amazon]');
    if (!confirm || !link) return;
    confirm.addEventListener('change', () => {
      const enabled = confirm.checked;
      link.classList.toggle('disabled-link', !enabled);
      link.setAttribute('aria-disabled', enabled ? 'false' : 'true');
      link.tabIndex = enabled ? 0 : -1;
      if (typeof window.Alo186Track === 'function') window.Alo186Track('generator_affiliate_checklist_acknowledged', { acknowledged: enabled });
    });
    link.addEventListener('click', event => {
      if (link.getAttribute('aria-disabled') === 'true') {
        event.preventDefault();
        return;
      }
      if (typeof window.Alo186Track === 'function') window.Alo186Track('affiliate_category_clicked', { category: 'generator', placement: 'after_generator_calculation' });
    });
  }

  function afterSelection() {
    queueMicrotask(() => injectRequirementChecklist());
  }

  function afterMatch() {
    queueMicrotask(() => {
      injectResultChecklist();
      enablePostCalculationAffiliate();
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('categoryGrid');
    const match = document.getElementById('matchBtn');
    if (grid) grid.addEventListener('click', event => {
      if (event.target.closest('[data-category="generator"]')) afterSelection();
    });
    if (match) match.addEventListener('click', afterMatch);
    injectRequirementChecklist();
  });
})();
