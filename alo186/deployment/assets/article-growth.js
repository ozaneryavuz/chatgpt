(() => {
  'use strict';
  const KEY = 'alo186.articleFollowup.v1';
  const LIMIT = 12;
  const TTL_DAYS = 365;
  const ROOT = String.fromCharCode(47);

  function parse(value) {
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? null : date;
  }

  function clean(items) {
    const cutoff = Date.now() - TTL_DAYS * 86400000;
    const unique = new Map();
    (Array.isArray(items) ? items : []).forEach((item) => {
      if (!item || typeof item !== 'object') return;
      const saved = parse(item.savedAt);
      const due = parse(item.dueAt);
      const path = String(item.path || '').slice(0, 180);
      const title = String(item.title || '').slice(0, 180);
      if (!saved || !due || saved.getTime() < cutoff || !path.startsWith(ROOT) || !title) return;
      unique.set(path, {
        path,
        title,
        lane: ['official','consumer','professional'].includes(item.lane) ? item.lane : 'professional',
        savedAt: saved.toISOString(),
        dueAt: due.toISOString()
      });
    });
    return [...unique.values()].sort((a, b) => a.dueAt.localeCompare(b.dueAt)).slice(0, LIMIT);
  }

  function load() {
    try { return clean(JSON.parse(localStorage.getItem(KEY) || '[]')); }
    catch (_) { return []; }
  }

  function save(items) {
    localStorage.setItem(KEY, JSON.stringify(clean(items)));
  }

  function add(button) {
    const days = Math.max(1, Math.min(365, Number(button.dataset.days || 30)));
    const item = {
      path: String(button.dataset.path || location.pathname).slice(0, 180),
      title: String(button.dataset.title || document.title).replace(/\s*\|\s*ALO186.*$/i, '').slice(0, 180),
      lane: button.dataset.lane || 'professional',
      savedAt: new Date().toISOString(),
      dueAt: new Date(Date.now() + days * 86400000).toISOString()
    };
    const current = load().filter((candidate) => candidate.path !== item.path);
    current.unshift(item);
    save(current);
    button.textContent = 'Takip listesine eklendi';
    button.disabled = true;
    const status = button.closest('.alo186-next-step')?.querySelector('.alo186-followup-status');
    if (status) status.textContent = `${days} gün sonra yeniden kontrol için yalnız bu tarayıcıya kaydedildi.`;
    if (typeof window.Alo186Track === 'function') window.Alo186Track('article_followup_saved', { lane: item.lane, review_days: days });
  }

  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-alo186-followup-add]').forEach((button) => {
      const saved = load().some((item) => item.path === String(button.dataset.path || location.pathname));
      if (saved) {
        button.textContent = 'Takip listesinde';
        button.disabled = true;
      }
      button.addEventListener('click', () => add(button));
    });
    document.querySelectorAll('[data-alo186-next-step-link]').forEach((link) => link.addEventListener('click', () => {
      if (typeof window.Alo186Track === 'function') window.Alo186Track('article_next_step_clicked', { lane: link.dataset.lane || 'unknown', action: link.dataset.action || 'open' });
    }));
  });
})();
