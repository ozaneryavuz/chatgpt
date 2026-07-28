(() => {
  'use strict';

  const core = window.Alo186SolutionOutcome;
  const STORE_KEY = 'alo186:solution-outcomes:v1';
  const byId = (id) => document.getElementById(id);
  let memoryRecords = [];
  let lastRecord = null;
  let storageAvailable = true;

  function track(name, params = {}) {
    const allowedEvents = new Set([
      'solution_outcome_recorded',
      'solution_outcome_followup_opened',
      'solution_outcome_calendar_downloaded',
      'solution_outcome_exported',
      'solution_outcome_deleted',
      'solution_outcome_cleared'
    ]);
    if (!allowedEvents.has(name)) return;
    const clean = {};
    const allowedKeys = new Set(['source', 'category', 'action', 'outcome', 'recurrence', 'purchase', 'decision_key', 'route']);
    Object.entries(params).forEach(([key, value]) => {
      if (allowedKeys.has(key) && typeof value === 'string' && value.length <= 80) clean[key] = value;
    });
    if (typeof window.Alo186Track === 'function') window.Alo186Track(name, clean);
    else {
      window.dataLayer = window.dataLayer || [];
      window.dataLayer.push({ event: name, ...clean });
    }
  }

  function readStore() {
    if (!storageAvailable) return core.pruneRecords(memoryRecords);
    try {
      const parsed = JSON.parse(localStorage.getItem(STORE_KEY) || '[]');
      memoryRecords = core.pruneRecords(parsed);
      return memoryRecords;
    } catch (_) {
      storageAvailable = false;
      byId('storageNotice').textContent = 'Tarayıcı depolaması kullanılamıyor. Araç bu oturumda çalışır; kayıtlar sayfa kapanınca silinir.';
      return core.pruneRecords(memoryRecords);
    }
  }

  function writeStore(records) {
    memoryRecords = core.pruneRecords(records);
    if (!storageAvailable) return;
    try {
      localStorage.setItem(STORE_KEY, JSON.stringify(memoryRecords));
    } catch (_) {
      storageAvailable = false;
      byId('storageNotice').textContent = 'Tarayıcı depolaması kullanılamıyor. Yeni kayıt yalnız bu oturumda tutuluyor.';
    }
  }

  function safeSelect(id, allowed) {
    const value = String(byId(id).value || '');
    return Object.prototype.hasOwnProperty.call(allowed, value) ? value : Object.keys(allowed)[0];
  }

  function readForm() {
    return {
      source: safeSelect('source', core.SOURCES),
      category: safeSelect('category', core.CATEGORIES),
      action: safeSelect('action', core.ACTIONS),
      outcome: safeSelect('outcome', core.OUTCOMES),
      recurrence: safeSelect('recurrence', core.RECURRENCES),
      purchase: safeSelect('purchase', core.PURCHASES)
    };
  }

  function label(map, key) {
    return map[key] || key;
  }

  function formatDate(value) {
    if (!value) return 'Takip gerekmiyor';
    const date = new Date(value);
    return new Intl.DateTimeFormat('tr-TR', { dateStyle: 'medium' }).format(date);
  }

  function daysUntil(value) {
    if (!value) return null;
    return Math.ceil((Date.parse(value) - Date.now()) / (24 * 60 * 60 * 1000));
  }

  function outcomeBadge(record) {
    if (record.outcome === 'resolved') return '<span class="status resolved">Çözüldü</span>';
    if (record.outcome === 'partial') return '<span class="status partial">Kısmi</span>';
    if (record.outcome === 'safety') return '<span class="status danger">Güvenlik</span>';
    return '<span class="status unresolved">Çözülmedi</span>';
  }

  function actionMarkup(action) {
    const external = /^https?:\/\//.test(action.href);
    const rel = external ? ' rel="external noopener"' : '';
    return `<a class="button ${action.kind === 'secondary' ? 'secondary' : action.kind === 'danger' ? 'danger' : 'primary'}" href="${action.href}"${rel} data-route="${action.href}">${action.label}</a>`;
  }

  function renderDecision(decision, record) {
    byId('result').classList.remove('hidden');
    byId('result').dataset.decision = decision.key;
    byId('resultEyebrow').textContent = decision.categoryLabel;
    byId('resultTitle').textContent = decision.title;
    byId('resultText').textContent = decision.summary;
    byId('resultSteps').innerHTML = decision.steps.map((step, index) => `<li><span>${index + 1}</span><p>${step}</p></li>`).join('');
    byId('resultActions').innerHTML = decision.actions.map(actionMarkup).join('');
    byId('followupDate').textContent = record.dueAt ? formatDate(record.dueAt) : 'Acil güvenlik sonucunda normal takip takvimi oluşturulmaz.';
    byId('calendarBtn').disabled = !record.dueAt;
    byId('resultPrivacy').textContent = decision.revenueAllowed
      ? 'Bu sonuç ticari rota açabilir.'
      : 'Bu sonuç yeni ürün satın alma yönlendirmesi açmaz.';
    byId('result').scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
  }

  function renderDashboard() {
    const records = readStore();
    const summary = core.summarizeRecords(records);
    byId('metricTotal').textContent = String(summary.total);
    byId('metricResolution').textContent = `${summary.resolutionRate}%`;
    byId('metricNoPurchase').textContent = `${summary.noPurchaseRate}%`;
    byId('metricRecurrence').textContent = `${summary.recurrenceRate}%`;
    byId('metricDue').textContent = String(summary.due);
    byId('topCategory').textContent = summary.topCategoryLabel;
    byId('dashboardEmpty').classList.toggle('hidden', summary.total > 0);
    byId('historySection').classList.toggle('hidden', summary.total === 0);

    byId('historyList').innerHTML = records.map((record) => {
      const due = daysUntil(record.dueAt);
      const dueText = due === null ? 'Takip yok' : due < 0 ? `${Math.abs(due)} gün gecikti` : due === 0 ? 'Bugün kontrol edin' : `${due} gün sonra`;
      return `<article class="history-card" data-id="${record.id}">
        <div class="history-head"><div>${outcomeBadge(record)}<strong>${label(core.CATEGORIES, record.category).label || label(core.CATEGORIES, record.category)}</strong></div><time datetime="${record.createdAt}">${formatDate(record.createdAt)}</time></div>
        <dl><div><dt>Kullanılan yol</dt><dd>${label(core.ACTIONS, record.action)}</dd></div><div><dt>Satın alma</dt><dd>${label(core.PURCHASES, record.purchase)}</dd></div><div><dt>Tekrar</dt><dd>${label(core.RECURRENCES, record.recurrence)}</dd></div><div><dt>Takip</dt><dd>${dueText}</dd></div></dl>
        <div class="history-actions"><a class="button secondary" href="${record.followupRoute}" data-followup-route="${record.followupRoute}">Takip rotasını aç</a><button type="button" class="button ghost" data-delete-id="${record.id}">Kaydı sil</button></div>
      </article>`;
    }).join('');
  }

  function makeId() {
    if (window.crypto && typeof window.crypto.randomUUID === 'function') return window.crypto.randomUUID();
    return `outcome_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`;
  }

  function downloadBlob(name, content, type) {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = name;
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  function applyPrefill() {
    const params = new URLSearchParams(location.search);
    const raw = {
      source: params.get('kaynak') || '',
      category: params.get('kategori') || '',
      action: params.get('eylem') || '',
      outcome: params.get('sonuc') || '',
      recurrence: params.get('tekrar') || '',
      purchase: params.get('satin_alma') || ''
    };
    if (params.get('guvenlik') === 'true') raw.outcome = 'safety';
    if (params.get('rota') === 'buy_nothing') raw.purchase = 'no_purchase';
    if (params.get('rota') === 'paid_b2b') raw.action = 'professional_service';
    if (params.get('rota') === 'affiliate_product_center') raw.action = 'free_tool';
    const safe = core.sanitizeInput(raw);
    Object.entries(safe).forEach(([key, value]) => {
      const element = byId(key);
      if (element) element.value = value;
    });
  }

  function recordOutcome(event) {
    event.preventDefault();
    const input = readForm();
    input.id = makeId();
    const decision = core.deriveDecision(input);
    const record = core.normalizeRecord(input);
    lastRecord = record;
    writeStore(core.upsertRecord(readStore(), record));
    renderDecision(decision, record);
    renderDashboard();
    track('solution_outcome_recorded', { ...input, decision_key: decision.key });
  }

  function downloadCalendar() {
    if (!lastRecord || !lastRecord.dueAt) return;
    const content = core.buildCalendar(lastRecord, location.origin);
    if (!content) return;
    downloadBlob(`alo186-yeniden-kontrol-${lastRecord.id}.ics`, content, 'text/calendar;charset=utf-8');
    track('solution_outcome_calendar_downloaded', { category: lastRecord.category, outcome: lastRecord.outcome });
  }

  function exportJson() {
    const payload = core.exportPayload(readStore());
    downloadBlob(`alo186-cozum-sonuclari-${new Date().toISOString().slice(0, 10)}.json`, JSON.stringify(payload, null, 2), 'application/json;charset=utf-8');
    track('solution_outcome_exported', { route: 'json' });
  }

  function clearAll() {
    if (!confirm('Bu tarayıcıdaki bütün çözüm sonuçları silinsin mi?')) return;
    memoryRecords = [];
    if (storageAvailable) localStorage.removeItem(STORE_KEY);
    lastRecord = null;
    byId('result').classList.add('hidden');
    renderDashboard();
    track('solution_outcome_cleared', { route: 'all' });
  }

  function deleteRecord(id) {
    const records = readStore().filter((record) => record.id !== id);
    writeStore(records);
    if (lastRecord && lastRecord.id === id) lastRecord = null;
    renderDashboard();
    track('solution_outcome_deleted', { route: 'single' });
  }

  document.addEventListener('DOMContentLoaded', () => {
    if (!core) {
      byId('formStatus').textContent = 'Çözüm sonuç motoru yüklenemedi. Can güvenliği riskinde 112; şebeke arızasında 186 veya resmî EDAŞ kanalını kullanın.';
      return;
    }
    applyPrefill();
    renderDashboard();
    byId('outcomeForm').addEventListener('submit', recordOutcome);
    byId('calendarBtn').addEventListener('click', downloadCalendar);
    byId('exportBtn').addEventListener('click', exportJson);
    byId('printBtn').addEventListener('click', () => window.print());
    byId('clearBtn').addEventListener('click', clearAll);
    byId('resultActions').addEventListener('click', (event) => {
      const link = event.target.closest('a[data-route]');
      if (!link) return;
      track('solution_outcome_followup_opened', { route: link.dataset.route, category: lastRecord ? lastRecord.category : 'unknown' });
    });
    byId('historyList').addEventListener('click', (event) => {
      const deleteButton = event.target.closest('[data-delete-id]');
      if (deleteButton) {
        deleteRecord(deleteButton.dataset.deleteId);
        return;
      }
      const followup = event.target.closest('[data-followup-route]');
      if (followup) track('solution_outcome_followup_opened', { route: followup.dataset.followupRoute });
    });
  });
})();
