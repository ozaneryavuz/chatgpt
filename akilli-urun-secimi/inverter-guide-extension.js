(() => {
  'use strict';

  const checklist = [
    ['Saf sinüs çıkış', 'Hassas elektronik, aktif PFC, motor ve kontrol kartı içeren yüklerde üreticinin saf sinüs uyumluluğunu doğrulayın.'],
    ['Sürekli ve tepe W', 'Hesap sonucundaki rezervli sürekli W ile kısa süreli tepe W değerlerinin ikisini de ürün teknik sayfasında kontrol edin.'],
    ['DC sistem gerilimi', 'İnverterin 12, 24 veya 48 V girişi batarya dizilimi, şarj cihazı ve BMS ile aynı olmalıdır.'],
    ['Batarya akımı', 'Batarya ve BMS sürekli/tepe deşarj akımı, hesaplanan DC akımını karşılamalıdır.'],
    ['DC koruma', 'Batarya yakını sigorta/ayırma, kablo kesiti, bağlantı ve havalandırma üretici kılavuzuna göre tasarlanmalıdır.']
  ];

  const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, char => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[char]);

  function selectedInverter() {
    return Boolean(document.querySelector('[data-category="inverter"][aria-pressed="true"]'));
  }

  function checklistMarkup(marker) {
    return `<div class="guide-list inverter-guide-extension" data-inverter-guide="${marker}">${checklist.map(([title, text]) => `<div class="guide-item"><b>${escapeHtml(title)}</b><span>${escapeHtml(text)}</span></div>`).join('')}</div>`;
  }

  function injectRequirementChecklist() {
    if (!selectedInverter()) return;
    const target = document.getElementById('requirementFields');
    if (!target || target.querySelector('[data-inverter-guide]')) return;
    target.insertAdjacentHTML('beforeend', checklistMarkup('requirements'));
  }

  function injectResultChecklist() {
    if (!selectedInverter()) return;
    const target = document.getElementById('guideResult');
    if (!target || target.querySelector('[data-inverter-guide]')) return;
    const heading = target.querySelector('h3');
    if (heading) heading.insertAdjacentHTML('afterend', checklistMarkup('result'));
    else target.insertAdjacentHTML('afterbegin', checklistMarkup('result'));
  }

  function enablePostCalculationAffiliate() {
    const params = new URLSearchParams(location.search);
    const verifiedHandoff = params.get('hesaplandi') === '1' || params.get('kaynak') === 'inverter-uygunluk';
    if (!selectedInverter() || !verifiedHandoff) return;
    const target = document.getElementById('guideResult');
    const catalog = window.Alo186ProductCatalog;
    if (!target || !catalog) return;

    target.querySelectorAll('.decision-gate,.actions').forEach(node => node.remove());
    const searchUrl = catalog.searchUrl('inverter');
    target.insertAdjacentHTML('beforeend', `<div class="decision-gate inverter-post-calc"><b>Hesaplama tamamlandı; ürün verilerini yine de doğrulayın.</b><p>ALO186 marka veya model onayı vermez. Saf sinüs, sürekli/tepe W, DC giriş gerilimi, boşta tüketim, düşük gerilim kesmesi, BMS ve üretici kablo/sigorta koşullarını güncel ürün sayfasında yeniden kontrol edin.</p><label class="check-item"><input type="checkbox" data-inverter-confirm><span><b>Hesap sonucumu ve teknik kontrol listesini ürün sayfasında yeniden doğrulayacağım.</b><br><small>Fiyat, stok, satıcı, garanti ve nihai uygunluk yalnız satıcının ve üreticinin güncel sayfasında doğrulanır.</small></span></label><div class="actions"><a class="btn btn-primary disabled-link" data-inverter-amazon aria-disabled="true" tabindex="-1" href="${escapeHtml(searchUrl)}" target="_blank" rel="sponsored nofollow noopener">Amazon’da teknik ifadelerle ara</a></div></div>`);

    const confirm = target.querySelector('[data-inverter-confirm]');
    const link = target.querySelector('[data-inverter-amazon]');
    if (!confirm || !link) return;
    confirm.addEventListener('change', () => {
      const enabled = confirm.checked;
      link.classList.toggle('disabled-link', !enabled);
      link.setAttribute('aria-disabled', enabled ? 'false' : 'true');
      link.tabIndex = enabled ? 0 : -1;
      if (typeof window.Alo186Track === 'function') window.Alo186Track('inverter_affiliate_checklist_acknowledged', { acknowledged: enabled });
    });
    link.addEventListener('click', event => {
      if (link.getAttribute('aria-disabled') === 'true') {
        event.preventDefault();
        return;
      }
      if (typeof window.Alo186Track === 'function') window.Alo186Track('affiliate_category_clicked', { category: 'inverter', placement: 'after_inverter_calculation' });
    });
  }

  function afterSelection() {
    queueMicrotask(injectRequirementChecklist);
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
      if (event.target.closest('[data-category="inverter"]')) afterSelection();
    });
    if (match) match.addEventListener('click', afterMatch);
    injectRequirementChecklist();
  });
})();