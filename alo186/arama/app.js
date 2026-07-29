(() => {
  'use strict';

  const byId = (id) => document.getElementById(id);
  const TYPE_LABELS = {
    article: 'Teknik rehber',
    tool: 'Karar / uygunluk aracı',
    calculator: 'Hesaplayıcı',
    business: 'İşletme / mühendislik',
    collection: 'İçerik merkezi'
  };
  const SAFETY_TOKENS = new Set(['yangin','alev','duman','carpma','elektrikcarpmasi','kopmuskablo','kopukhat','kivilcim','patlama','erime']);
  const OFFICIAL_TOKENS = new Set(['edas','186','kesinti','sayac','fazkaybi','sokak','trafo','direk','teknikkalite','epdk']);
  const PRODUCT_TOKENS = new Set(['almak','urun','secim','uygun','powerbank','ups','jenerator','inverter','wallbox','kablo','parafudr','rcd','batarya']);
  const TOOL_INTENT = new Set(['hesapla','hesaplama','kac','sure','uygun','secim','test','kontrol','karsilastir']);

  let index = [];
  let currentFilter = 'all';
  let debounceTimer = 0;

  function normalize(value) {
    return String(value || '')
      .toLocaleLowerCase('tr-TR')
      .normalize('NFKD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/ı/g, 'i')
      .replace(/[^a-z0-9]+/g, ' ')
      .trim();
  }

  function tokens(value) {
    return [...new Set(normalize(value).split(/\s+/).filter((token) => token.length > 1))];
  }

  function compactTokens(value) {
    const list = tokens(value);
    const compact = [...list];
    for (let i = 0; i < list.length - 1; i += 1) compact.push(list[i] + list[i + 1]);
    return compact;
  }

  function hasIntent(queryTokens, set) {
    return queryTokens.some((token) => set.has(token));
  }

  function bucketMatches(entry, filter) {
    if (filter === 'all') return true;
    return entry.bucket === filter;
  }

  function scoreEntry(entry, query, queryTokens) {
    const title = normalize(entry.title);
    const description = normalize(entry.description);
    const h1 = normalize(entry.h1);
    const topics = normalize((entry.topics || []).join(' '));
    const excerpt = normalize(entry.excerpt);
    const path = normalize(entry.canonicalPath);
    let score = Number(entry.priority || 0);

    if (title === query || h1 === query) score += 160;
    if (title.includes(query)) score += 90;
    if (h1.includes(query)) score += 75;
    if (topics.includes(query)) score += 55;
    if (description.includes(query)) score += 35;

    for (const token of queryTokens) {
      if (title.split(' ').includes(token)) score += 24;
      else if (title.includes(token)) score += 14;
      if (h1.includes(token)) score += 12;
      if (topics.includes(token)) score += 14;
      if (description.includes(token)) score += 8;
      if (path.includes(token)) score += 6;
      if (excerpt.includes(token)) score += 2;
    }

    const matched = queryTokens.filter((token) => `${title} ${h1} ${topics} ${description} ${excerpt}`.includes(token)).length;
    if (matched === queryTokens.length) score += 35;
    else if (matched === 0) return 0;

    if (hasIntent(queryTokens, TOOL_INTENT) && ['tool','calculator'].includes(entry.bucket)) score += 28;
    if (hasIntent(queryTokens, PRODUCT_TOKENS) && ['tool','calculator'].includes(entry.bucket)) score += 20;
    if (hasIntent(queryTokens, OFFICIAL_TOKENS) && /\/(edas-bul|karar-motoru|kesinti-gunlugu)/.test(entry.canonicalPath)) score += 40;
    if (hasIntent(queryTokens, SAFETY_TOKENS) && entry.canonicalPath === '/karar-motoru') score += 100;
    return score;
  }

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

  function updateIntentCards(queryTokens) {
    byId('emergencyCard').classList.toggle('hidden', !hasIntent(queryTokens, SAFETY_TOKENS));
    byId('officialCard').classList.toggle('hidden', hasIntent(queryTokens, SAFETY_TOKENS) || !hasIntent(queryTokens, OFFICIAL_TOKENS));
  }

  function trackSearch(queryTokens, resultCount) {
    if (typeof window.Alo186Track !== 'function') return;
    window.Alo186Track('technical_search_used', {
      query_length: byId('searchInput').value.length,
      token_count: queryTokens.length,
      result_count: resultCount,
      content_filter: currentFilter
    });
  }

  function render(queryValue, shouldTrack = false) {
    const query = normalize(queryValue);
    const queryTokens = compactTokens(queryValue);
    updateIntentCards(queryTokens);
    const results = byId('results');
    results.replaceChildren();

    let ranked;
    if (!query) {
      ranked = index
        .filter((entry) => bucketMatches(entry, currentFilter))
        .filter((entry) => entry.featured)
        .sort((a, b) => Number(b.priority || 0) - Number(a.priority || 0))
        .slice(0, 12);
    } else {
      ranked = index
        .filter((entry) => bucketMatches(entry, currentFilter))
        .map((entry) => ({ entry, score: scoreEntry(entry, query, queryTokens) }))
        .filter((item) => item.score > 0)
        .sort((a, b) => b.score - a.score || a.entry.title.localeCompare(b.entry.title, 'tr'))
        .slice(0, 20)
        .map((item) => item.entry);
    }

    ranked.forEach((entry) => results.appendChild(createResult(entry)));
    byId('emptyState').classList.toggle('hidden', ranked.length > 0);
    byId('resultStatus').textContent = query
      ? `${ranked.length} güvenli sonuç bulundu.`
      : `${ranked.length} öne çıkan araç ve rehber gösteriliyor.`;
    if (shouldTrack && query) trackSearch(queryTokens, ranked.length);
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
