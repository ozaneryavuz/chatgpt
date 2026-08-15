(function () {
  'use strict';
  const core = window.ALO186OutageJournalCore;
  if (!core) return;

  const STORAGE_KEY = 'alo186.outageJournal.v1';
  const DEFAULT_STATE = { entries: [], settings: core.normalizeSettings({ priorities: { internet: true, lighting: true } }) };
  const byId = (id) => document.getElementById(id);
  const qsa = (selector) => Array.from(document.querySelectorAll(selector));
  let state = loadState();

  const labels = {
    planned: 'Planlı', unplanned: 'Plansız', unknown: 'Bilinmiyor',
    street: 'Sokak / mahalle', building: 'Bina', unit: 'Daire / iş yeri'
  };

  function loadState() {
    try {
      const parsed = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null');
      if (!parsed || !Array.isArray(parsed.entries)) return structuredClone(DEFAULT_STATE);
      return { entries: parsed.entries.map(core.normalizeEntry), settings: core.normalizeSettings(parsed.settings || {}) };
    } catch (_) {
      return structuredClone(DEFAULT_STATE);
    }
  }

  function saveState() { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); }

  function emit(name, detail) {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ event: name, ...(detail || {}) });
  }

  function formatDuration(minutes) {
    const safe = Math.max(0, Math.round(Number(minutes) || 0));
    const hours = Math.floor(safe / 60);
    const remainder = safe % 60;
    if (!hours) return `${remainder} dk`;
    return remainder ? `${hours} sa ${remainder} dk` : `${hours} sa`;
  }

  function currentSettingsFromForm() {
    const priorities = {};
    qsa('[data-priority]').forEach((input) => { priorities[input.dataset.priority] = input.checked; });
    return core.normalizeSettings({ usage: byId('usage').value, voltage: byId('voltage').value, area: byId('area').value, priorities });
  }

  function populateSettings() {
    byId('usage').value = state.settings.usage;
    byId('voltage').value = state.settings.voltage;
    byId('area').value = state.settings.area;
    qsa('[data-priority]').forEach((input) => { input.checked = Boolean(state.settings.priorities[input.dataset.priority]); });
  }

  function populateYears() {
    const current = new Date().getFullYear();
    const years = new Set([current, ...state.entries.map((entry) => Number(entry.date.slice(0, 4)))]);
    const currentSelection = Number(byId('yearFilter').value) || current;
    byId('yearFilter').innerHTML = [...years].sort((a, b) => b - a).map((year) => `<option value="${year}">${year}</option>`).join('');
    byId('yearFilter').value = years.has(currentSelection) ? String(currentSelection) : String(current);
  }

  function renderSignals(summary) {
    const items = [];
    if (summary.longDurationEntries.length) {
      items.push(`<div class="signal review"><strong>12 saati aşan ${summary.longDurationEntries.length} kayıt var.</strong><span>EPDK tüketici bilgisindeki uzun süreli kesinti tazminatı sürecini yetkili dağıtım şirketinin resmî kanalından kontrol edin. Bu işaret otomatik hak kazanımı değildir.</span></div>`);
    }
    for (const kind of ['unplanned', 'planned']) {
      const signal = summary.annualSignals[kind];
      const title = kind === 'unplanned' ? 'Bildirimsiz / plansız yıllık kayıtlar' : 'Bildirimli / planlı yıllık kayıtlar';
      if (signal.status === 'unknown') {
        items.push(`<div class="signal unknown"><strong>${title}: sınıf seçimi bekleniyor.</strong><span>AG/OG ve imar alanı seçilmeden yıllık eşik karşılaştırması yapılmaz.</span></div>`);
      } else if (signal.status === 'review') {
        const reasons = [];
        if (signal.durationExceeded) reasons.push(`süre ${signal.actual.hours.toFixed(1)} sa > ${signal.threshold.hours} sa`);
        if (signal.countExceeded) reasons.push(`sayı ${signal.actual.count} > ${signal.threshold.count}`);
        items.push(`<div class="signal review"><strong>${title}: resmî kontrol önerilir.</strong><span>Girdiğiniz kayıtlar eşik sinyali üretiyor (${reasons.join(', ')}). Dağıtım şirketinin resmî kayıtları ve mevzuat istisnaları belirleyicidir.</span></div>`);
      } else {
        items.push(`<div class="signal good"><strong>${title}: girilen kayıtlar seçili eşiği aşmıyor.</strong><span>${signal.actual.hours.toFixed(1)} saat / ${signal.actual.count} kayıt. Kayıtlarınız eksikse sonuç değişebilir.</span></div>`);
      }
    }
    if (summary.damageEntries.length) {
      items.push(`<div class="signal review"><strong>${summary.damageEntries.length} cihaz hasarı şüphesi işaretlendi.</strong><span>EPDK tüketici bilgisinde dağıtım şebekesi kaynaklı hasar talebi için zararın ortaya çıktığı tarihten itibaren 30 günlük süre düzenlenir. Yetkili servis raporu ve resmî başvuru kaydını gecikmeden hazırlayın.</span></div>`);
    }
    byId('rightsSignals').innerHTML = items.join('');
  }

  function renderRoutes(summary) {
    const decision = core.buildResilienceRoutes(summary);
    byId('routeList').innerHTML = decision.routes.map((route) => `<a class="route-card" href="${route.href}" data-route="${route.id}"><strong>${route.label} →</strong><span>${route.reason}</span></a>`).join('') || '<p class="info">En az bir kesinti kaydı ve kritik ihtiyaç seçtiğinizde ücretsiz hesaplama rotaları burada görünür.</p>';
    byId('affiliateRoute').classList.toggle('hidden', !decision.showProductCenter);
    byId('medicalBlock').classList.toggle('hidden', !decision.commercialSuppressed);
    qsa('[data-route]').forEach((link) => link.addEventListener('click', () => emit('outage_resilience_route_opened', { route: link.dataset.route })));
  }

  function render() {
    populateYears();
    const year = Number(byId('yearFilter').value) || new Date().getFullYear();
    const summary = core.summarize(state.entries, { year, settings: state.settings });
    byId('dashboard').classList.toggle('hidden', state.entries.length === 0);
    byId('metricCount').textContent = String(summary.count);
    byId('metricYear').textContent = `${year} takvim yılı`;
    byId('metricTotal').textContent = formatDuration(summary.totalMinutes);
    byId('metricLongest').textContent = formatDuration(summary.longestMinutes);
    byId('metricLongSignal').textContent = summary.longDurationEntries.length ? `${summary.longDurationEntries.length} kayıt 12 saati aşıyor` : '12 saat sinyali yok';
    byId('metricReview').textContent = summary.hasCompensationReviewSignal ? 'Resmî kontrol önerilir' : (summary.count ? 'Kayıtları sürdürün' : 'Kayıt bekleniyor');
    byId('entryRows').innerHTML = summary.entries.map((entry) => `<tr><td>${entry.date}</td><td>${formatDuration(entry.durationMinutes)}</td><td>${labels[entry.kind] || labels.unknown}</td><td>${labels[entry.scope] || 'Bilinmiyor'}</td><td><small>${entry.officialRecord ? 'Resmî kayıt var' : 'Resmî kayıt işaretlenmedi'}${entry.deviceDamage ? '<br>Cihaz hasarı şüphesi' : ''}</small></td><td><button type="button" class="delete-entry" data-delete="${entry.id}" aria-label="${entry.date} tarihli kaydı sil">Sil</button></td></tr>`).join('');
    byId('emptyState').classList.toggle('hidden', summary.count > 0);
    qsa('[data-delete]').forEach((button) => button.addEventListener('click', () => {
      state.entries = state.entries.filter((entry) => entry.id !== button.dataset.delete);
      saveState(); emit('outage_journal_entry_deleted'); render();
    }));
    renderSignals(summary);
    byId('evidenceList').innerHTML = core.buildEvidenceChecklist(summary).map((item) => `<li>${item}</li>`).join('');
    renderRoutes(summary);
    if (summary.hasCompensationReviewSignal) emit('outage_compensation_signal_shown', { year, count: summary.count });
  }

  byId('entryDate').value = new Date().toISOString().slice(0, 10);
  populateSettings();
  populateYears();

  byId('entryForm').addEventListener('submit', (event) => {
    event.preventDefault();
    byId('entryError').textContent = '';
    try {
      const hours = Math.max(0, Number(byId('durationHours').value) || 0);
      const minutes = Math.max(0, Number(byId('durationMinutes').value) || 0);
      const duration = Math.round(hours * 60 + minutes);
      if (duration < 1) throw new Error('Kesinti süresi en az 1 dakika olmalıdır.');
      const entry = core.normalizeEntry({ date: byId('entryDate').value, durationMinutes: duration, kind: byId('kind').value, scope: byId('scope').value, officialRecord: byId('officialRecord').checked, deviceDamage: byId('deviceDamage').checked });
      state.entries.push(entry);
      state.settings = currentSettingsFromForm();
      saveState();
      emit('outage_journal_entry_added', { kind: entry.kind, scope: entry.scope, duration_bucket: duration >= 720 ? '12h_plus' : duration >= 240 ? '4h_plus' : duration >= 60 ? '1h_plus' : 'under_1h' });
      byId('durationHours').value = '1'; byId('durationMinutes').value = '0'; byId('officialRecord').checked = false; byId('deviceDamage').checked = false;
      render();
    } catch (error) {
      byId('entryError').textContent = error.message || 'Kayıt eklenemedi.';
    }
  });

  byId('saveSettingsBtn').addEventListener('click', () => {
    state.settings = currentSettingsFromForm(); saveState();
    emit('outage_journal_settings_saved', { usage: state.settings.usage, voltage: state.settings.voltage, area: state.settings.area, medical: state.settings.priorities.medical });
    render();
  });
  byId('yearFilter').addEventListener('change', render);
  byId('clearAllBtn').addEventListener('click', () => {
    if (!window.confirm('Bu tarayıcıdaki bütün kesinti kayıtları silinsin mi?')) return;
    state = structuredClone(DEFAULT_STATE); localStorage.removeItem(STORAGE_KEY); populateSettings(); emit('outage_journal_cleared'); render();
  });
  byId('printBtn').addEventListener('click', () => { emit('outage_evidence_checklist_printed'); window.print(); });
  byId('exportBtn').addEventListener('click', () => {
    const payload = core.createExport(state.entries, state.settings);
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob); link.download = `alo186-kesinti-gunlugu-${new Date().toISOString().slice(0, 10)}.json`; link.click(); URL.revokeObjectURL(link.href);
    emit('outage_journal_exported', { count: state.entries.length });
  });
  byId('productCenterLink').addEventListener('click', () => emit('outage_product_center_opened'));
  render();
})();
