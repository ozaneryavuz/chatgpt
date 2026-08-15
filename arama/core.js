(function(root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root && typeof root === 'object') root.Alo186SearchCore = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function() {
  'use strict';

  const SAFETY_TOKENS = new Set(['yangin','alev','duman','carpma','elektrikcarpmasi','kopmuskablo','kopukhat','kivilcim','patlama','erime']);
  const OFFICIAL_TOKENS = new Set(['edas','186','kesinti','sayac','fazkaybi','sokak','trafo','direk','teknikkalite','epdk']);
  const PRODUCT_TOKENS = new Set(['almak','urun','secim','uygun','powerbank','ups','jenerator','inverter','wallbox','kablo','parafudr','rcd','batarya']);
  const TOOL_INTENT = new Set(['hesapla','hesaplama','kac','sure','uygun','secim','test','kontrol','karsilastir']);

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
    for (let index = 0; index < list.length - 1; index += 1) compact.push(list[index] + list[index + 1]);
    return compact;
  }

  function hasIntent(queryTokens, tokenSet) {
    return queryTokens.some((token) => tokenSet.has(token));
  }

  function detectIntents(value) {
    const queryTokens = compactTokens(value);
    return {
      queryTokens,
      safety: hasIntent(queryTokens, SAFETY_TOKENS),
      official: hasIntent(queryTokens, OFFICIAL_TOKENS),
      product: hasIntent(queryTokens, PRODUCT_TOKENS),
      tool: hasIntent(queryTokens, TOOL_INTENT)
    };
  }

  function bucketMatches(entry, filter) {
    if (filter === 'all') return true;
    return entry.bucket === filter;
  }

  function scoreEntry(entry, queryValue, queryTokens = compactTokens(queryValue)) {
    const query = normalize(queryValue);
    if (!query || !entry) return 0;
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

    const searchable = `${title} ${h1} ${topics} ${description} ${excerpt}`;
    const matched = queryTokens.filter((token) => searchable.includes(token)).length;
    if (matched === queryTokens.length) score += 35;
    else if (matched === 0) return 0;

    if (hasIntent(queryTokens, TOOL_INTENT) && ['tool','calculator'].includes(entry.bucket)) score += 28;
    if (hasIntent(queryTokens, PRODUCT_TOKENS) && ['tool','calculator'].includes(entry.bucket)) score += 20;
    if (hasIntent(queryTokens, OFFICIAL_TOKENS) && /\/(edas-bul|karar-motoru|kesinti-gunlugu)/.test(entry.canonicalPath)) score += 40;
    if (hasIntent(queryTokens, SAFETY_TOKENS) && entry.canonicalPath === '/karar-motoru') score += 100;
    return score;
  }

  function searchEntries(entries, queryValue, filter = 'all', limit = 20) {
    const list = Array.isArray(entries) ? entries : [];
    const query = normalize(queryValue);
    const queryTokens = compactTokens(queryValue);
    if (!query) {
      return list
        .filter((entry) => bucketMatches(entry, filter))
        .filter((entry) => entry.featured)
        .sort((left, right) => Number(right.priority || 0) - Number(left.priority || 0) || String(left.title).localeCompare(String(right.title), 'tr'))
        .slice(0, limit);
    }
    return list
      .filter((entry) => bucketMatches(entry, filter))
      .map((entry) => ({ entry, score: scoreEntry(entry, query, queryTokens) }))
      .filter((item) => item.score > 0)
      .sort((left, right) => right.score - left.score || String(left.entry.title).localeCompare(String(right.entry.title), 'tr'))
      .slice(0, limit)
      .map((item) => item.entry);
  }

  return {
    SAFETY_TOKENS,
    OFFICIAL_TOKENS,
    PRODUCT_TOKENS,
    TOOL_INTENT,
    normalize,
    tokens,
    compactTokens,
    hasIntent,
    detectIntents,
    scoreEntry,
    searchEntries
  };
});
