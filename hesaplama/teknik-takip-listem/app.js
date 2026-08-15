(() => {
  'use strict';
  const KEY = 'alo186.articleFollowup.v1';
  const LIMIT = 12;
  const TTL_DAYS = 365;
  const $ = (id) => document.getElementById(id);

  function parseDate(value) {
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? null : date;
  }

  function clean(items) {
    const cutoff = Date.now() - TTL_DAYS * 86400000;
    const unique = new Map();
    (Array.isArray(items) ? items : []).forEach((item) => {
      if (!item || typeof item !== 'object') return;
      const saved = parseDate(item.savedAt);
      const due = parseDate(item.dueAt);
      if (!saved || !due || saved.getTime() < cutoff) return;
      const path = String(item.path || '').slice(0, 180);
      const title = String(item.title || '').slice(0, 180);
      if (!path.startsWith('/') || !title) return;
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

  function formatDate(value) {
    const date = parseDate(value);
    return date ? new Intl.DateTimeFormat('tr-TR', { day: 'numeric', month: 'long', year: 'numeric' }).format(date) : 'Tarih yok';
  }

  function laneLabel(lane) {
    return lane === 'official' ? 'Resmî işlem / kanıt' : lane === 'consumer' ? 'Düşük riskli teknik seçim' : 'Teknik ölçüm / profesyonel kapsam';
  }

  function daysUntil(value) {
    const date = parseDate(value);
    return date ? Math.ceil((date.getTime() - Date.now()) / 86400000) : 9999;
  }

  function makeButton(label, className, handler) {
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = label;
    if (className) button.className = className;
    button.addEventListener('click', handler);
    return button;
  }

  function render() {
    const items = load();
    save(items);
    $('count').textContent = String(items.length);
    $('dueSoon').textContent = String(items.filter((item) => { const days = daysUntil(item.dueAt); return days >= 0 && days <= 30; }).length);
    $('overdue').textContent = String(items.filter((item) => daysUntil(item.dueAt) < 0).length);
    $('empty').hidden = items.length > 0;
    const root = $('items');
    root.replaceChildren();

    items.forEach((item) => {
      const article = document.createElement('article');
      article.className = `item${daysUntil(item.dueAt) < 0 ? ' overdue' : ''}`;
      const top = document.createElement('div');
      top.className = 'item-top';
      const copy = document.createElement('div');
      const badge = document.createElement('span');
      badge.className = 'badge';
      badge.textContent = laneLabel(item.lane);
      const title = document.createElement('h3');
      title.textContent = item.title;
      const due = document.createElement('p');
      due.textContent = `Yeniden kontrol: ${formatDate(item.dueAt)}`;
      copy.append(badge, title, due);
      top.append(copy);

      const actions = document.createElement('div');
      actions.className = 'item-actions';
      const open = document.createElement('a');
      open.href = item.path;
      open.textContent = 'Rehberi aç →';
      const postpone = makeButton('30 gün ertele', '', () => {
        const next = load().map((candidate) => candidate.path === item.path ? { ...candidate, dueAt: new Date(Date.now() + 30 * 86400000).toISOString() } : candidate);
        save(next); render();
      });
      const remove = makeButton('Kaldır', 'danger', () => { save(load().filter((candidate) => candidate.path !== item.path)); render(); });
      actions.append(open, postpone, remove);
      article.append(top, actions);
      root.appendChild(article);
    });
  }

  function download(name, type, content) {
    const blob = new Blob([content], { type });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = name;
    link.click();
    setTimeout(() => URL.revokeObjectURL(link.href), 1000);
  }

  function exportJson() {
    const payload = {
      schema: 'alo186.article-followup.v1',
      createdAt: new Date().toISOString(),
      containsPersonalData: false,
      items: load(),
      disclaimer: 'ALO186 bağımsız bilgi platformudur; resmî bakım veya EDAŞ kaydı değildir.'
    };
    download('alo186-teknik-takip-listem.json', 'application/json', JSON.stringify(payload, null, 2));
    if (typeof window.Alo186Track === 'function') window.Alo186Track('technical_followup_exported', { format: 'json', item_count: payload.items.length });
  }

  function icsDate(value) {
    return new Date(value).toISOString().replace(/[-:]/g, '').replace(/\.\d{3}Z$/, 'Z');
  }

  function escapeIcs(value) {
    return String(value).replace(/\\/g, '\\\\').replace(/\n/g, '\\n').replace(/,/g, '\\,').replace(/;/g, '\\;');
  }

  function exportIcs() {
    const items = load();
    const lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//ALO186//Teknik Takip Listem//TR'];
    items.forEach((item, index) => {
      const start = parseDate(item.dueAt) || new Date();
      const end = new Date(start.getTime() + 30 * 60000);
      lines.push('BEGIN:VEVENT', `UID:${start.getTime()}-${index}@alo186.com`, `DTSTAMP:${icsDate(new Date())}`, `DTSTART:${icsDate(start)}`, `DTEND:${icsDate(end)}`, `SUMMARY:${escapeIcs(`ALO186 teknik kontrol: ${item.title}`)}`, `DESCRIPTION:${escapeIcs('Rehberi yeniden açın; mevcut sistem yeterliyse yeni ürün almayın. Resmî veya güvenlik işlemlerinde yetkili kanalı kullanın.')}`, `URL:https://alo186.com${item.path}`, 'END:VEVENT');
    });
    lines.push('END:VCALENDAR');
    download('alo186-teknik-takip-listem.ics', 'text/calendar', lines.join('\r\n'));
    if (typeof window.Alo186Track === 'function') window.Alo186Track('technical_followup_exported', { format: 'ics', item_count: items.length });
  }

  document.addEventListener('DOMContentLoaded', () => {
    $('exportJson').addEventListener('click', exportJson);
    $('exportIcs').addEventListener('click', exportIcs);
    $('clearAll').addEventListener('click', () => { localStorage.removeItem(KEY); render(); });
    render();
  });
})();
