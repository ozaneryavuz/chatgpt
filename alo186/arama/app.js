(() => {
  'use strict';

  const core = window.Alo186SearchCore;
  const byId = (id) => document.getElementById(id);
  const TYPE_LABELS = {
    article: 'Teknik rehber',
    tool: 'Karar / uygunluk aracı',
    calculator: 'Hesaplayıcı',
    business: 'İşletme / mühendislik',
    collection: 'İçerik merkezi'
  };

  let index = [];
  let currentFilter = 'all';
  let debounceTimer = 0;

  function createResult(entry) {
    const article = document.createElement('article');
    article.className = 'result-card';
    const type = document.createElement('span');
    type.className = 'type';
    type.textContent = TYPE_LABELS[entry.bucket] || TYPE_LABELS[entry.type] || 'ALO186 içeriği';
    const title = document.createElement('h3');
    title.textContent = entry.title;
    const description = document.createElement('p');
    description.textContent = entry.description || entry.excerpt || 'Teknik içeriği açın.';
    const topicWrap = document.createElement('div');
    topicWrap.className = 'topics';
    (entry.topics || []).slice(0, 4).forEach((topic) => {
      const chip = document.createElement('span');
      chip.textContent = topic;
      topicWrap.appendChild(chip);
    });
    const link = document.createElement('a');
    link.href = entry.url;
    link.textContent = ['tool','calculator'].includes(entry.bucket) ? 'Aracı aç →' : 'İçeriği aç →';
    article.append(type, title, description, topicWrap, link);
    return article;
  }

  function updateIntentCards(intents) {
    byId('emergencyCard').classList.toggle('hidden', !intents.safety);
    byId('officialCard').classList.toggle('hidden', intents.safety || !intents.official);
  }

  function trackSearch(intents, resultCount) {
    if (typeof window.Alo186Track !== 'function') return;
    window.Alo186Track('technical_search_used', {
      query_length: byId('searchInput').value.length,
      token_count: intents.queryTokens.length,
      result_count: resultCount,
      content_filter: currentFilter
    });
  }

  function render(queryValue, shouldTrack = false) {
    const intents = core.detectIntents(queryValue);
    updateIntentCards(intents);
    const results = byId('results');
    results.replaceChildren();
    const ranked = core.searchEntries(index, queryValue, currentFilter, queryValue.trim() ? 20 : 12);
    ranked.forEach((entry) => results.appendChild(createResult(entry)));
    byId('emptyState').classList.toggle('hidden', ranked.length > 0);
    byId('resultStatus').textContent = queryValue.trim()
      ? `${ranked.length} güvenli sonuç bulundu.`
      : `${ranked.length} öne çıkan araç ve rehber gösteriliyor.`;
    if (shouldTrack && queryValue.trim()) trackSearch(intents, ranked.length);
  }

  function readHashQuery() {
    const match = location.hash.match(/^#q=(.*)$/);
    if (!match) return '';
    try { return decodeURIComponent(match[1]).slice(0, 120); }
    catch (_) { return ''; }
  }

  function writeHashQuery(value) {
    const clean = String(value || '').slice(0, 120);
    const next = clean ? `#q=${encodeURIComponent(clean)}` : `${location.pathname}${location.search}`;
    history.replaceState({}, '', next);
  }

  async function loadIndex() {
    try {
      const response = await fetch('./search-index.json', { cache: 'no-cache' });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const payload = await response.json();
      index = Array.isArray(payload.entries) ? payload.entries : [];
      const initial = readHashQuery();
      byId('searchInput').value = initial;
      render(initial);
    } catch (_) {
      byId('resultStatus').textContent = 'Teknik arama indeksi yüklenemedi. Karar Motoru ve Hesaplama Merkezi kullanılabilir.';
      byId('emptyState').classList.remove('hidden');
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    if (!core) {
      byId('resultStatus').textContent = 'Teknik arama motoru yüklenemedi. Karar Motoru ve Hesaplama Merkezi kullanılabilir.';
      byId('emptyState').classList.remove('hidden');
      return;
    }
    byId('searchInput').addEventListener('input', (event) => {
      clearTimeout(debounceTimer);
      const value = event.target.value.slice(0, 120);
      debounceTimer = setTimeout(() => {
        writeHashQuery(value);
        render(value, true);
      }, 180);
    });
    byId('typeFilter').addEventListener('change', (event) => {
      currentFilter = event.target.value;
      render(byId('searchInput').value, Boolean(byId('searchInput').value));
    });
    byId('clearButton').addEventListener('click', () => {
      byId('searchInput').value = '';
      currentFilter = 'all';
      byId('typeFilter').value = 'all';
      writeHashQuery('');
      render('');
      byId('searchInput').focus();
    });
    document.querySelectorAll('[data-query]').forEach((button) => button.addEventListener('click', () => {
      const value = button.dataset.query || '';
      byId('searchInput').value = value;
      writeHashQuery(value);
      render(value, true);
      byId('searchInput').focus();
    }));
    addEventListener('hashchange', () => {
      const value = readHashQuery();
      byId('searchInput').value = value;
      render(value);
    });
    loadIndex();
  });
})();
