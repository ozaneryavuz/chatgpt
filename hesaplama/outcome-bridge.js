(function(root, factory) {
  const api = factory(root);
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root && typeof root === 'object') root.Alo186OutcomeBridge = api;
  if (root && root.document) api.init();
})(typeof globalThis !== 'undefined' ? globalThis : this, function(root) {
  'use strict';

  const STORAGE_KEY = 'alo186:pending-solutions:v1';
  const MAX_PENDING = 6;
  const TTL_DAYS = 45;
  const DISMISS_DAYS = 7;
  const HOUR_MS = 60 * 60 * 1000;
  const DAY_MS = 24 * HOUR_MS;
  const OUTCOME_PATH = '/hesaplama/cozum-sonucu/';

  const SOURCES = new Set(['decision_engine', 'outage_workshop', 'calculator', 'product_center', 'guide', 'professional']);
  const CATEGORIES = new Set(['outage_official', 'indoor_fault', 'backup_power', 'protection', 'solar_storage', 'ev_charging', 'product_selection', 'business_continuity']);
  const ACTIONS = new Set(['official_channel', 'free_tool', 'maintenance', 'existing_equipment', 'product', 'electrician', 'professional_service']);
  const OUTCOMES = new Set(['resolved', 'partial', 'unresolved']);

  const CATEGORY_LABELS = {
    outage_official: 'Kesinti ve resmî işlem',
    indoor_fault: 'İç tesisat, pano veya priz',
    backup_power: 'UPS, jeneratör ve yedek güç',
    protection: 'RCD, parafudr ve gerilim koruması',
    solar_storage: 'GES, inverter ve enerji depolama',
    ev_charging: 'EV şarj ve wallbox',
    product_selection: 'Tak-çalıştır ürün seçimi',
    business_continuity: 'Otel, site ve işletme sürekliliği'
  };

  const CATEGORY_ALIASES = {
    outage: 'outage_official', external: 'outage_official', meter: 'outage_official',
    panel: 'indoor_fault', indoor: 'indoor_fault',
    internet: 'backup_power', cold_chain: 'backup_power', long_outage: 'backup_power', mini_ups: 'backup_power', generator: 'backup_power', power_station: 'backup_power', ups_battery: 'backup_power',
    electronics: 'protection', surge_strip: 'protection', outlet_tester: 'protection',
    inverter: 'solar_storage', solar: 'solar_storage', ges: 'solar_storage',
    ev_cable: 'ev_charging', ev: 'ev_charging', wallbox: 'ev_charging',
    mobile: 'product_selection', lighting: 'product_selection', powerbank: 'product_selection', emergency_light: 'product_selection', smoke_alarm: 'product_selection', smart_plug: 'product_selection',
    hotel_site: 'business_continuity', business: 'business_continuity'
  };

  const SOURCE_ALIASES = {
    'karar-motoru': 'decision_engine',
    'kesinti-atolyesi': 'outage_workshop',
    'hesaplayici': 'calculator',
    'urun-secimi': 'product_center',
    'rehber': 'guide',
    'profesyonel': 'professional'
  };

  const ACTION_DELAYS_HOURS = {
    free_tool: 12,
    official_channel: 72,
    maintenance: 72,
    existing_equipment: 72,
    product: 72,
    electrician: 7 * 24,
    professional_service: 7 * 24
  };

  let activeContext = null;
  let initialized = false;
  let memoryRecords = [];
  let storageAvailable = true;

  function hasOwn(object, key) {
    return Object.prototype.hasOwnProperty.call(object, key);
  }

  function normalizeEnum(value, allowed, aliases, fallback) {
    const raw = String(value || '').trim();
    const aliased = aliases && hasOwn(aliases, raw) ? aliases[raw] : raw;
    return allowed.has(aliased) ? aliased : fallback;
  }

  function sanitizePath(value) {
    if (!value) return '';
    try {
      const raw = String(value).trim();
      const parsed = new URL(raw, 'https://alo186.com');
      if (!['https:', 'http:'].includes(parsed.protocol)) return '';
      if (/^https?:\/\//i.test(raw) && !['www.alo186.com', 'alo186.com'].includes(parsed.hostname.toLowerCase())) return '';
      const path = parsed.pathname.replace(/\/{2,}/g, '/').slice(0, 180);
      return /^\/[a-zA-Z0-9_\-/.]*$/.test(path) ? path : '';
    } catch (_) {
      return '';
    }
  }

  function inferSourceFromPath(value) {
    const path = sanitizePath(value).toLowerCase();
    if (path.includes('/karar-motoru')) return 'decision_engine';
    if (path.includes('/kesintiye-hazirlik-atolyesi')) return 'outage_workshop';
    if (path.includes('/akilli-urun-secimi')) return 'product_center';
    if (path.includes('/haberler/')) return 'guide';
    if (path.includes('/kurumsal-elektrik-surekliligi-on-degerlendirme')) return 'professional';
    return 'calculator';
  }

  function inferCategoryFromPath(value) {
    const path = sanitizePath(value).toLowerCase();
    if (/\/(edas-bul|karar-motoru|fatura-analizi|kesinti-gunlugu|elektrik-kesintisi)/.test(path)) return 'outage_official';
    if (/\/(jenerator|ups|yedek-guc|modem-internet|power-station)/.test(path)) return 'backup_power';
    if (/\/(parafudr|gerilim-koruma|akim-korumali|uzatma-kablosu|topraklama|kacak-akim)/.test(path)) return 'protection';
    if (/\/(inverter|gunes-paneli|ges-|enerji-depolama|lifepo4|batarya)/.test(path)) return 'solar_storage';
    if (/\/(ev-sarj|wallbox|type-2|v2l|v2h|v2g)/.test(path)) return 'ev_charging';
    if (/\/(sureklilik|tatbikati|olgunluk|pasaportu|isletme-surekliligi)/.test(path)) return 'business_continuity';
    if (/\/(pano|priz|notr|faz-dengesizligi|kompanzasyon)/.test(path)) return 'indoor_fault';
    return 'product_selection';
  }

  function inferActionFromTarget(href, rel = '') {
    const raw = String(href || '').trim();
    const relValue = String(rel || '').toLowerCase();
    if (/^tel:112$/i.test(raw)) return null;
    if (/^tel:186$/i.test(raw) || /\/edas-bul\/?(?:[?#]|$)/.test(raw)) return 'official_channel';
    if (/kurumsal-elektrik-surekliligi-on-degerlendirme/.test(raw)) return 'professional_service';
    if (/akilli-urun-secimi/.test(raw)) return 'free_tool';
    if (/ekipman-bakim-plani|kesinti-hazirlik-plani/.test(raw)) return 'maintenance';
    if (/amazon\.(?:com|com\.tr)/i.test(raw) || relValue.includes('sponsored')) return 'product';
    if (/^https?:/i.test(raw) && !/alo186\.com/i.test(raw)) return null;
    return 'free_tool';
  }

  function delayHours(action) {
    return ACTION_DELAYS_HOURS[action] || 24;
  }

  function randomId(now) {
    if (root.crypto && typeof root.crypto.randomUUID === 'function') return root.crypto.randomUUID();
    return `pending_${now.getTime().toString(36)}_${Math.random().toString(36).slice(2, 9)}`;
  }

  function sanitizeContext(raw = {}, nowValue = new Date()) {
    const now = nowValue instanceof Date ? nowValue : new Date(nowValue);
    const originPath = sanitizePath(raw.originPath || (root.location && root.location.pathname) || '/');
    const source = normalizeEnum(raw.source, SOURCES, SOURCE_ALIASES, inferSourceFromPath(originPath));
    const category = normalizeEnum(raw.category, CATEGORIES, CATEGORY_ALIASES, inferCategoryFromPath(originPath));
    const action = normalizeEnum(raw.action, ACTIONS, null, 'free_tool');
    const createdAt = Number.isFinite(Date.parse(raw.createdAt)) ? new Date(raw.createdAt) : now;
    const askAfter = Number.isFinite(Date.parse(raw.askAfter)) ? new Date(raw.askAfter) : new Date(createdAt.getTime() + delayHours(action) * HOUR_MS);
    const expiresAt = Number.isFinite(Date.parse(raw.expiresAt)) ? new Date(raw.expiresAt) : new Date(createdAt.getTime() + TTL_DAYS * DAY_MS);
    const dismissedUntil = Number.isFinite(Date.parse(raw.dismissedUntil)) ? new Date(raw.dismissedUntil).toISOString() : null;
    return {
      version: 1,
      id: String(raw.id || randomId(now)).replace(/[^a-zA-Z0-9_-]/g, '').slice(0, 64),
      source,
      category,
      action,
      originPath: originPath || '/',
      recommendedPath: sanitizePath(raw.recommendedPath),
      createdAt: createdAt.toISOString(),
      askAfter: askAfter.toISOString(),
      expiresAt: expiresAt.toISOString(),
      dismissedUntil
    };
  }

  function isValid(record) {
    return record && typeof record === 'object'
      && record.version === 1
      && SOURCES.has(record.source)
      && CATEGORIES.has(record.category)
      && ACTIONS.has(record.action)
      && Boolean(sanitizePath(record.originPath))
      && Number.isFinite(Date.parse(record.createdAt))
      && Number.isFinite(Date.parse(record.askAfter))
      && Number.isFinite(Date.parse(record.expiresAt));
  }

  function prune(records, nowValue = new Date()) {
    const now = nowValue instanceof Date ? nowValue : new Date(nowValue);
    const byId = new Map();
    (Array.isArray(records) ? records : []).forEach((record) => {
      if (!isValid(record)) return;
      if (Date.parse(record.expiresAt) <= now.getTime()) return;
      const previous = byId.get(record.id);
      if (!previous || Date.parse(previous.createdAt) < Date.parse(record.createdAt)) byId.set(record.id, { ...record });
    });
    return [...byId.values()]
      .sort((a, b) => Date.parse(b.createdAt) - Date.parse(a.createdAt))
      .slice(0, MAX_PENDING);
  }

  function readStore() {
    if (!storageAvailable || !root.localStorage) return prune(memoryRecords);
    try {
      memoryRecords = prune(JSON.parse(root.localStorage.getItem(STORAGE_KEY) || '[]'));
      return memoryRecords;
    } catch (_) {
      storageAvailable = false;
      return prune(memoryRecords);
    }
  }

  function writeStore(records) {
    memoryRecords = prune(records);
    if (!storageAvailable || !root.localStorage) return memoryRecords;
    try {
      root.localStorage.setItem(STORAGE_KEY, JSON.stringify(memoryRecords));
    } catch (_) {
      storageAvailable = false;
    }
    return memoryRecords;
  }

  function fingerprint(record) {
    return [record.source, record.category, record.action, record.originPath, record.recommendedPath].join('|');
  }

  function start(raw = {}, nowValue = new Date()) {
    if (raw.safety === true) return null;
    const context = sanitizeContext({ ...(activeContext || {}), ...raw }, nowValue);
    let records = readStore();
    if (['product', 'official_channel', 'electrician', 'professional_service'].includes(context.action)) {
      records = records.filter((record) => !(record.category === context.category && record.action === 'free_tool'));
    }
    const existing = records.find((record) => fingerprint(record) === fingerprint(context));
    if (existing) return existing;
    writeStore([context, ...records]);
    dispatch('alo186:outcome-pending-created', context);
    return context;
  }

  function get(id) {
    return readStore().find((record) => record.id === id) || null;
  }

  function complete(id) {
    if (!id) return false;
    const before = readStore();
    const after = before.filter((record) => record.id !== id);
    writeStore(after);
    if (after.length !== before.length) dispatch('alo186:outcome-pending-completed', { id });
    return after.length !== before.length;
  }

  function clear() {
    writeStore([]);
    return true;
  }

  function dismiss(id, nowValue = new Date()) {
    const now = nowValue instanceof Date ? nowValue : new Date(nowValue);
    let changed = false;
    const records = readStore().map((record) => {
      if (record.id !== id) return record;
      changed = true;
      return { ...record, dismissedUntil: new Date(now.getTime() + DISMISS_DAYS * DAY_MS).toISOString() };
    });
    writeStore(records);
    return changed;
  }

  function eligible(nowValue = new Date()) {
    const now = nowValue instanceof Date ? nowValue : new Date(nowValue);
    return readStore()
      .filter((record) => Date.parse(record.askAfter) <= now.getTime())
      .filter((record) => !record.dismissedUntil || Date.parse(record.dismissedUntil) <= now.getTime())
      .sort((a, b) => Date.parse(a.askAfter) - Date.parse(b.askAfter));
  }

  function buildOutcomeUrl(record, outcome) {
    if (!isValid(record)) return OUTCOME_PATH;
    const params = new URLSearchParams({
      pending: record.id,
      kaynak: record.source,
      kategori: record.category,
      eylem: record.action
    });
    if (OUTCOMES.has(outcome)) params.set('sonuc', outcome);
    return `${OUTCOME_PATH}?${params.toString()}`;
  }

  function dispatch(name, detail) {
    if (root.dispatchEvent && typeof root.CustomEvent === 'function') root.dispatchEvent(new root.CustomEvent(name, { detail }));
  }

  function track(name, params = {}) {
    const clean = {};
    ['source', 'category', 'action', 'outcome', 'route'].forEach((key) => {
      const value = params[key];
      if (typeof value === 'string' && value.length <= 80) clean[key] = value;
    });
    if (typeof root.Alo186Track === 'function') root.Alo186Track(name, clean);
  }

  function updateActiveContext(event) {
    const detail = event && event.detail ? event.detail : {};
    const path = (root.location && root.location.pathname) || '/';
    const current = activeContext || {
      source: inferSourceFromPath(path),
      category: inferCategoryFromPath(path),
      action: 'free_tool',
      originPath: path
    };
    if (detail.event === 'product_category_selected' && detail.category) current.category = normalizeEnum(detail.category, CATEGORIES, CATEGORY_ALIASES, current.category);
    if (detail.event === 'product_match_completed' && detail.category) current.category = normalizeEnum(detail.category, CATEGORIES, CATEGORY_ALIASES, current.category);
    if (detail.event === 'fast_revenue_plan_rendered') {
      current.source = 'outage_workshop';
      current.category = normalizeEnum(detail.priority, CATEGORIES, CATEGORY_ALIASES, current.category);
      if (detail.route === 'paid_b2b') current.action = 'professional_service';
      else if (detail.route === 'buy_nothing') current.action = 'existing_equipment';
      else current.action = 'free_tool';
    }
    if (detail.event === 'electrical_decision_completed') {
      current.source = 'decision_engine';
      current.category = ['electrician', 'building', 'mixed'].includes(detail.route) ? 'indoor_fault' : 'outage_official';
      current.action = ['official', 'admin', 'danger'].includes(detail.route) ? 'official_channel' : ['electrician', 'building', 'mixed'].includes(detail.route) ? 'electrician' : 'free_tool';
    }
    activeContext = current;
  }

  function isTrackableAnchor(anchor) {
    if (!anchor) return false;
    const href = anchor.getAttribute('href') || '';
    if (!href || href.startsWith('#') || href.startsWith('mailto:') || href.includes(OUTCOME_PATH)) return false;
    if (anchor.hasAttribute('data-outcome-start')) return true;
    if ((anchor.getAttribute('rel') || '').toLowerCase().includes('sponsored')) return true;
    if (anchor.matches('[data-product], [data-route]')) return true;
    return Boolean(anchor.closest('#actionGrid, #resultActions, #result, .result, .result-actions, .actions, .product-card, .journey-stage, .history-actions'));
  }

  function clickHandler(event) {
    const anchor = event.target && event.target.closest ? event.target.closest('a[href]') : null;
    if (!isTrackableAnchor(anchor)) return;
    const href = anchor.getAttribute('href') || '';
    const action = normalizeEnum(anchor.dataset.outcomeAction || inferActionFromTarget(href, anchor.getAttribute('rel')), ACTIONS, null, 'free_tool');
    if (!action || /^tel:112$/i.test(href)) return;
    const path = (root.location && root.location.pathname) || '/';
    const external = /^https?:\/\//i.test(href) && !/alo186\.com/i.test(href);
    const context = {
      ...(activeContext || {}),
      source: anchor.dataset.outcomeSource || (activeContext && activeContext.source) || inferSourceFromPath(path),
      category: anchor.dataset.outcomeCategory || (activeContext && activeContext.category) || inferCategoryFromPath(path),
      action,
      originPath: path,
      recommendedPath: external ? '/akilli-urun-secimi' : href,
      safety: anchor.dataset.outcomeSafety === 'true'
    };
    const pending = start(context);
    if (pending) track('solution_outcome_pending_created', { source: pending.source, category: pending.category, action: pending.action, route: pending.recommendedPath });
  }

  function injectPromptStyles() {
    if (!root.document || root.document.getElementById('alo186OutcomePromptStyles')) return;
    const style = root.document.createElement('style');
    style.id = 'alo186OutcomePromptStyles';
    style.textContent = '.alo186-outcome-prompt{margin:16px auto 24px;max-width:1120px;padding:18px 20px;border:2px solid #4f7fdc;border-radius:18px;background:#f0f5ff;color:#132238;font:16px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}.alo186-outcome-prompt strong{display:block;color:#071631;font-size:1.16rem}.alo186-outcome-prompt p{margin:.35rem 0 1rem;color:#40526b}.alo186-outcome-actions{display:flex;flex-wrap:wrap;gap:9px}.alo186-outcome-actions a,.alo186-outcome-actions button{display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:9px 13px;border:2px solid #071631;border-radius:11px;background:#fff;color:#071631;font:inherit;font-weight:850;text-decoration:none;cursor:pointer}.alo186-outcome-actions a:first-child{background:#071631;color:#fff}.alo186-outcome-meta{display:block;margin-top:10px;color:#5d6b7d;font-size:.8rem}@media(max-width:640px){.alo186-outcome-prompt{margin:12px 16px 20px}.alo186-outcome-actions{display:grid}.alo186-outcome-actions a,.alo186-outcome-actions button{width:100%}}';
    root.document.head.appendChild(style);
  }

  function renderPrompt(nowValue = new Date()) {
    if (!root.document || !root.location) return null;
    const currentPath = sanitizePath(root.location.pathname);
    if (currentPath.includes(OUTCOME_PATH)) return null;
    const candidates = eligible(nowValue);
    const pending = candidates.find((record) => record.originPath !== currentPath) || candidates[0];
    const existing = root.document.getElementById('alo186OutcomePrompt');
    if (!pending) {
      if (existing) existing.remove();
      return null;
    }
    injectPromptStyles();
    if (existing) existing.remove();
    const aside = root.document.createElement('aside');
    aside.id = 'alo186OutcomePrompt';
    aside.className = 'alo186-outcome-prompt';
    aside.setAttribute('aria-labelledby', 'alo186OutcomePromptTitle');
    aside.innerHTML = `<strong id="alo186OutcomePromptTitle">Bu çözüm işe yaradı mı?</strong><p>${CATEGORY_LABELS[pending.category]} için izlediğiniz yolun sonucunu kişisel veri vermeden kaydedin. Çözüldüyse yeni ürün önerilmez; tekrar ediyorsa doğru teknik veya profesyonel rota açılır.</p><div class="alo186-outcome-actions"><a href="${buildOutcomeUrl(pending, 'resolved')}" data-prompt-outcome="resolved">Çözüldü</a><a href="${buildOutcomeUrl(pending, 'partial')}" data-prompt-outcome="partial">Kısmen</a><a href="${buildOutcomeUrl(pending, 'unresolved')}" data-prompt-outcome="unresolved">Çözülmedi</a><button type="button" data-prompt-dismiss>Sonra sor</button></div><small class="alo186-outcome-meta">Yalnız kategori, kullanılan yol ve tarihler bu tarayıcıda tutulur.</small>`;
    const main = root.document.querySelector('main');
    if (main) main.insertBefore(aside, main.firstChild);
    else root.document.body.insertBefore(aside, root.document.body.firstChild);
    aside.querySelectorAll('[data-prompt-outcome]').forEach((link) => link.addEventListener('click', () => track('solution_outcome_prompt_opened', { source: pending.source, category: pending.category, action: pending.action, outcome: link.dataset.promptOutcome })));
    aside.querySelector('[data-prompt-dismiss]').addEventListener('click', () => {
      dismiss(pending.id, nowValue);
      aside.remove();
      track('solution_outcome_prompt_dismissed', { source: pending.source, category: pending.category, action: pending.action });
    });
    return pending;
  }

  function init() {
    if (initialized || !root.document) return;
    initialized = true;
    const path = (root.location && root.location.pathname) || '/';
    activeContext = { source: inferSourceFromPath(path), category: inferCategoryFromPath(path), action: 'free_tool', originPath: path };
    root.addEventListener('alo186:event', updateActiveContext);
    root.document.addEventListener('click', clickHandler, true);
    if (root.document.readyState === 'loading') root.document.addEventListener('DOMContentLoaded', () => renderPrompt(), { once: true });
    else renderPrompt();
  }

  return {
    STORAGE_KEY,
    MAX_PENDING,
    TTL_DAYS,
    DISMISS_DAYS,
    OUTCOME_PATH,
    SOURCES,
    CATEGORIES,
    ACTIONS,
    CATEGORY_LABELS,
    sanitizePath,
    inferSourceFromPath,
    inferCategoryFromPath,
    inferActionFromTarget,
    sanitizeContext,
    isValid,
    prune,
    start,
    get,
    complete,
    clear,
    dismiss,
    eligible,
    buildOutcomeUrl,
    renderPrompt,
    init
  };
});
