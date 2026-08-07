(function () {
  'use strict';
  const Core = window.ALO186EquipmentCare;
  if (!Core) return;

  const STORAGE_KEY = 'alo186_equipment_care_v1';
  const $ = (id) => document.getElementById(id);
  const form = $('planForm');
  const dashboard = $('dashboard');
  const list = $('planList');
  const emptyState = $('emptyState');
  let plans = loadPlans();
  let selectedId = null;

  function track(eventName, params) {
    const safeParams = Object.assign({ tool: 'equipment-care' }, params || {});
    if (typeof window.gtag === 'function') window.gtag('event', eventName, safeParams);
    window.dispatchEvent(new CustomEvent('alo186:analytics', { detail: { event: eventName, params: safeParams } }));
  }

  function loadPlans() {
    try {
      return Core.sanitizePlans(JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'));
    } catch (_) {
      return [];
    }
  }

  function savePlans() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(Core.sanitizePlans(plans)));
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>'"]/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[char]));
  }

  function todayIso() {
    const date = new Date();
    const local = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
    return local.toISOString().slice(0, 10);
  }

  function formatDate(value) {
    const parsed = new Date(`${value}T12:00:00`);
    return Number.isNaN(parsed.getTime()) ? '—' : new Intl.DateTimeFormat('tr-TR', { day: '2-digit', month: 'long', year: 'numeric' }).format(parsed);
  }

  function render() {
    const summary = Core.summarize(plans, todayIso());
    $('metricTotal').textContent = String(summary.total);
    $('metricOverdue').textContent = String(summary.overdue);
    $('metricSoon').textContent = String(summary.soon);
    $('metricService').textContent = String(summary.service);
    dashboard.classList.toggle('hidden', plans.length === 0);
    emptyState.hidden = plans.length > 0;

    const sorted = [...plans].sort((a, b) => a.nextCheck.localeCompare(b.nextCheck));
    list.innerHTML = sorted.map((plan) => {
      const equipment = Core.EQUIPMENT[plan.equipment];
      const status = Core.statusForPlan(plan, todayIso());
      const selected = plan.id === selectedId;
      return `<article class="plan-card status-${status.key}${selected ? ' selected' : ''}" data-plan-id="${escapeHtml(plan.id)}">
        <button type="button" class="plan-select" data-action="select" data-id="${escapeHtml(plan.id)}" aria-pressed="${selected}">
          <span class="plan-title"><b>${escapeHtml(equipment.label)}</b><small>${escapeHtml(Core.CONDITIONS[plan.condition])}</small></span>
          <span class="status-pill">${escapeHtml(status.label)}</span>
          <span class="plan-dates">Son kontrol: ${formatDate(plan.lastCheck)} · Sonraki: ${formatDate(plan.nextCheck)}</span>
        </button>
        <div class="plan-actions"><button class="mini-button" type="button" data-action="complete" data-id="${escapeHtml(plan.id)}">Bugün kontrol edildi</button><button class="mini-button danger-button" type="button" data-action="delete" data-id="${escapeHtml(plan.id)}">Sil</button></div>
      </article>`;
    }).join('');

    if (!selectedId || !plans.some((plan) => plan.id === selectedId)) selectedId = sorted[0] ? sorted[0].id : null;
    renderGuidance();
  }

  function renderGuidance() {
    const guidance = $('guidance');
    const commercial = $('commercialRoute');
    const professional = $('professionalRoute');
    const plan = plans.find((item) => item.id === selectedId);
    commercial.classList.add('hidden');
    professional.classList.add('hidden');
    if (!plan) {
      guidance.innerHTML = '<p>Bir plan seçtiğinizde güvenli kontrol sınırı burada gösterilir.</p>';
      return;
    }

    const equipment = Core.EQUIPMENT[plan.equipment];
    const decision = Core.commercialDecision(plan);
    const status = Core.statusForPlan(plan, todayIso());
    guidance.innerHTML = `<h3>${escapeHtml(equipment.label)}</h3><p>${escapeHtml(decision.reason)}</p><div class="decision-summary"><span>Takvim durumu</span><strong>${escapeHtml(status.label)}</strong></div><div class="decision-summary"><span>Kılavuz doğrulaması</span><strong>${plan.manualKnown ? 'Yapıldı' : 'Eksik'}</strong></div>`;

    if (decision.showCommercial) {
      const link = $('productLink');
      link.href = `https://alo186.com/akilli-urun-secimi?source=equipment-care&category=${encodeURIComponent(decision.productCategory)}`;
      commercial.classList.remove('hidden');
      track('equipment_care_commercial_route_shown', { equipment: plan.equipment, condition: plan.condition });
    }
    if (decision.showProfessional) {
      professional.classList.remove('hidden');
      track('equipment_care_professional_route_shown', { equipment: plan.equipment, condition: plan.condition });
    }
  }

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const input = {
      equipment: $('equipment').value,
      lastCheck: $('lastCheck').value,
      intervalDays: Number($('interval').value),
      condition: $('condition').value,
      manualKnown: $('manualKnown').checked,
      noUnsafeWork: $('noUnsafeWork').checked
    };
    const result = Core.createPlan(input);
    if (result.error) {
      $('formError').textContent = result.error.join(' ');
      return;
    }
    $('formError').textContent = '';
    plans.push(result);
    selectedId = result.id;
    savePlans();
    render();
    track('equipment_care_plan_added', { equipment: result.equipment, interval_days: result.intervalDays, condition: result.condition });
    form.reset();
    $('interval').value = '90';
    $('condition').value = 'ok';
    $('lastCheck').value = todayIso();
  });

  list.addEventListener('click', (event) => {
    const target = event.target.closest('[data-action]');
    if (!target) return;
    const id = target.dataset.id;
    const index = plans.findIndex((plan) => plan.id === id);
    if (index < 0) return;
    const action = target.dataset.action;
    if (action === 'select') {
      selectedId = id;
      render();
      track('equipment_care_plan_selected', { equipment: plans[index].equipment });
      return;
    }
    if (action === 'delete') {
      const equipment = plans[index].equipment;
      plans.splice(index, 1);
      if (selectedId === id) selectedId = null;
      savePlans();
      render();
      track('equipment_care_plan_deleted', { equipment });
      return;
    }
    if (action === 'complete') {
      const plan = plans[index];
      plan.lastCheck = todayIso();
      plan.nextCheck = Core.addDays(plan.lastCheck, plan.intervalDays);
      plan.condition = 'ok';
      plans[index] = plan;
      selectedId = id;
      savePlans();
      render();
      track('equipment_care_check_completed', { equipment: plan.equipment, interval_days: plan.intervalDays });
    }
  });

  $('clearBtn').addEventListener('click', () => {
    if (!plans.length) return;
    if (!window.confirm('Bu tarayıcıdaki tüm ekipman kontrol planları silinsin mi?')) return;
    plans = [];
    selectedId = null;
    localStorage.removeItem(STORAGE_KEY);
    render();
    track('equipment_care_all_cleared');
  });

  $('exportBtn').addEventListener('click', () => {
    const payload = Core.exportPayload(plans);
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `alo186-ekipman-kontrol-plani-${todayIso()}.json`;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
    track('equipment_care_exported', { plan_count: plans.length });
  });

  $('printBtn').addEventListener('click', () => {
    track('equipment_care_printed', { plan_count: plans.length });
    window.print();
  });

  $('productLink').addEventListener('click', () => {
    const plan = plans.find((item) => item.id === selectedId);
    if (plan) track('equipment_care_product_center_opened', { equipment: plan.equipment, condition: plan.condition });
  });

  $('lastCheck').value = todayIso();
  render();
})();