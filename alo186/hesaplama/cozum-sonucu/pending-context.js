(() => {
  'use strict';

  const byId = (id) => document.getElementById(id);
  let pendingId = '';
  let pendingRecord = null;

  function waitForBridge(limit = 40) {
    return new Promise((resolve) => {
      let attempts = 0;
      const timer = setInterval(() => {
        attempts += 1;
        if (window.Alo186OutcomeBridge && typeof window.Alo186OutcomeBridge.get === 'function') {
          clearInterval(timer);
          resolve(window.Alo186OutcomeBridge);
        } else if (attempts >= limit) {
          clearInterval(timer);
          resolve(null);
        }
      }, 50);
    });
  }

  function safeOutcome(value) {
    return ['resolved', 'partial', 'unresolved'].includes(value) ? value : '';
  }

  function removePendingParam() {
    const url = new URL(location.href);
    url.searchParams.delete('pending');
    history.replaceState({}, '', `${url.pathname}${url.search}${url.hash}`);
  }

  function contextPanel(record, bridge) {
    const panel = document.createElement('section');
    panel.id = 'pendingSolutionContext';
    panel.className = 'panel pending-context';
    panel.setAttribute('aria-live', 'polite');
    const label = bridge.CATEGORY_LABELS[record.category] || 'Elektrik çözümü';
    panel.innerHTML = `<span class="eyebrow">Önceki adımdan otomatik bağlam</span><h2>${label}</h2><p>Bu form, daha önce izlediğiniz yolun kaynak, kategori ve eylem alanlarını otomatik doldurdu. Satın alma sonucu ile tekrar durumunu siz doğrulayın; ALO186 ürün, cihaz modeli veya kişisel veri taşımaz.</p><div class="actions"><button type="button" class="button secondary" data-use-pending>Bağlamı kullan</button><button type="button" class="button ghost" data-discard-pending>Bu bağlamı kullanma</button></div><small class="privacy">Bekleyen kayıt, sonuç kaydedildiğinde veya siz sildiğinizde cihazınızdan kaldırılır.</small>`;
    const safety = document.querySelector('.safety-note');
    if (safety && safety.parentNode) safety.insertAdjacentElement('afterend', panel);
    else document.querySelector('main')?.insertAdjacentElement('afterbegin', panel);

    panel.querySelector('[data-use-pending]').addEventListener('click', () => {
      byId('outcomeForm')?.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
    });
    panel.querySelector('[data-discard-pending]').addEventListener('click', () => {
      bridge.complete(record.id);
      pendingRecord = null;
      pendingId = '';
      panel.remove();
      removePendingParam();
      if (typeof window.Alo186Track === 'function') window.Alo186Track('solution_outcome_pending_discarded', { category: record.category, action: record.action });
    });
  }

  async function init() {
    const params = new URLSearchParams(location.search);
    pendingId = String(params.get('pending') || '').replace(/[^a-zA-Z0-9_-]/g, '').slice(0, 64);
    if (!pendingId) return;

    const bridge = await waitForBridge();
    if (!bridge) return;
    pendingRecord = bridge.get(pendingId);
    if (!pendingRecord) {
      removePendingParam();
      return;
    }

    const source = byId('source');
    const category = byId('category');
    const action = byId('action');
    const outcome = byId('outcome');
    if (source) source.value = pendingRecord.source;
    if (category) category.value = pendingRecord.category;
    if (action) action.value = pendingRecord.action;
    const requestedOutcome = safeOutcome(params.get('sonuc'));
    if (outcome && requestedOutcome) outcome.value = requestedOutcome;
    contextPanel(pendingRecord, bridge);

    byId('outcomeForm')?.addEventListener('submit', () => {
      if (!pendingRecord) return;
      const completed = { category: pendingRecord.category, action: pendingRecord.action };
      bridge.complete(pendingRecord.id);
      pendingRecord = null;
      pendingId = '';
      document.getElementById('pendingSolutionContext')?.remove();
      removePendingParam();
      if (typeof window.Alo186Track === 'function') window.Alo186Track('solution_outcome_pending_completed', completed);
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
  else init();
})();
