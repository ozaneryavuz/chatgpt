(() => {
  'use strict';

  const catalog = window.Alo186ProductCatalog;
  const byId = (id) => document.getElementById(id);
  const propertyLabels = {
    capacityMah: 'Kapasite', energyWh: 'Enerji', maxOutputW: 'Maks. çıkış', outlets: 'Priz', joules: 'Joule',
    maxCurrentA: 'Nominal akım', maxPowerW: 'Etiket gücü', usbPorts: 'USB portu', cableM: 'Kablo',
    energyMonitoring: 'Enerji izleme', wifiGHz: 'Wi-Fi', matter: 'Matter', motorHp: 'Motor sınırı',
    operatingTempMaxC: 'Maks. ortam', capacityWh: 'Kapasite', continuousW: 'Sürekli güç', surgeW: 'Tepe güç',
    pureSine: 'Dalga biçimi', chemistry: 'Kimya', solarVoltageMinV: 'PV min. V', solarVoltageMaxV: 'PV maks. V',
    solarCurrentMaxA: 'PV maks. A', solarPowerMaxW: 'PV maks. W', usbCMaxW: 'USB-C', epsTransferMs: 'EPS geçişi',
    sensor: 'Sensör', alarmDb: 'Alarm', batteryType: 'Pil', batteryLifeYearsClaim: 'Pil ömrü beyanı', standard: 'Standart'
  };
  let graph = null;
  let filters = { category: 'all', need: 'all', status: 'all' };

  const el = (tag, className, text) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = String(text);
    return node;
  };

  function publicValue(key, value) {
    if (value === true) return key === 'pureSine' ? 'Saf sinüs' : 'Var';
    if (value === false) return 'Yok';
    if (value === null || value === undefined) return 'Bilinmiyor';
    const suffixes = { capacityMah: ' mAh', energyWh: ' Wh', maxOutputW: ' W', outlets: '', joules: ' J', maxCurrentA: ' A', maxPowerW: ' W', usbPorts: '', cableM: ' m', wifiGHz: ' GHz', motorHp: ' HP', operatingTempMaxC: ' °C', capacityWh: ' Wh', continuousW: ' W', surgeW: ' W', solarVoltageMinV: ' V', solarVoltageMaxV: ' V', solarCurrentMaxA: ' A', solarPowerMaxW: ' W', usbCMaxW: ' W', epsTransferMs: ' ms', alarmDb: ' dB', batteryLifeYearsClaim: ' yıl' };
    return `${value}${suffixes[key] || ''}`;
  }

  function track(name, params = {}) {
    if (typeof window.Alo186Track !== 'function') return;
    const allowed = {};
    for (const key of ['product_id', 'category', 'status', 'link_mode', 'gate_state']) {
      if (typeof params[key] === 'string' && params[key].length < 90) allowed[key] = params[key];
    }
    window.Alo186Track(name, allowed);
  }

  function statusLabel(product) {
    if (product.verificationStatus === 'verified_listing') return 'Doğrulanmış ASIN';
    return 'Üretici verisi · tam model araması';
  }

  function statusClass(product, liveProduct) {
    const freshness = liveProduct ? catalog.verificationStatus(liveProduct, new Date()) : { fresh: false };
    if (!freshness.fresh) return 'status stale';
    return product.verificationStatus === 'manufacturer_verified_search' ? 'status search' : 'status';
  }

  function addRelationChips(container, product, category, needNames) {
    const relation = el('div', 'relation-line');
    relation.append(el('span', '', `İhtiyaç: ${needNames.join(', ') || 'Tanımsız'}`));
    relation.append(el('span', '', `Kategori: ${category ? category.name : product.categoryId}`));
    relation.append(el('span', '', `Politika: ${category ? category.affiliatePolicy : 'bilinmiyor'}`));
    container.append(relation);
  }

  function addProperties(container, product) {
    const grid = el('div', 'property-grid');
    Object.entries(product.technicalProperties || {}).slice(0, 10).forEach(([key, value]) => {
      const box = el('div');
      box.append(el('small', '', propertyLabels[key] || key));
      box.append(el('strong', '', publicValue(key, value)));
      grid.append(box);
    });
    container.append(grid);
  }

  function addList(container, title, items) {
    if (!Array.isArray(items) || !items.length) return;
    container.append(el('h4', '', title));
    const list = el('ul');
    items.forEach((item) => list.append(el('li', '', item)));
    container.append(list);
  }

  function addSources(container, product) {
    const links = el('div', 'source-links');
    if (product.officialSource) {
      const source = el('a', '', 'Üretici teknik kaynağı ↗');
      source.href = product.officialSource;
      source.target = '_blank';
      source.rel = 'noopener';
      links.append(source);
    }
    (product.relatedTools || []).slice(0, 1).forEach((url) => {
      const tool = el('a', '', 'Ücretsiz uygunluk aracı →');
      tool.href = url;
      links.append(tool);
    });
    (product.relatedGuides || []).slice(0, 1).forEach((url) => {
      const guide = el('a', '', 'Teknik rehber →');
      guide.href = url;
      links.append(guide);
    });
    container.append(links);
  }

  function gateReady(gate) {
    return [...gate.querySelectorAll('input[type="checkbox"]')].every((input) => input.checked);
  }

  function addCommerceGate(container, product, liveProduct, category) {
    if (!liveProduct || !catalog.isCatalogProduct(liveProduct)) {
      const blocked = el('div', 'professional-block');
      blocked.append(el('strong', '', 'Katalog düğümü doğrulanamadı.'));
      blocked.append(el('p', '', 'Affiliate bağlantısı gösterilmiyor; teknik kaynağı ve ücretsiz aracı kullanın.'));
      container.append(blocked);
      return;
    }
    const freshness = catalog.verificationStatus(liveProduct, new Date());
    if (!freshness.fresh) {
      const blocked = el('div', 'professional-block');
      blocked.append(el('strong', '', 'Teknik doğrulama süresi geçti.'));
      blocked.append(el('p', '', '45 günlük tazelik sınırı yenilenene kadar affiliate bağlantısı kapalıdır.'));
      container.append(blocked);
      return;
    }
    if (!category || category.affiliatePolicy === 'professional_only') {
      const blocked = el('div', 'professional-block');
      blocked.append(el('strong', '', 'Affiliate bağlantısı bu kategoride kapalı.'));
      blocked.append(el('p', '', 'Ölçüm, sabit tesisat veya can güvenliği nedeniyle yalnız güvenli yönlendirme ve profesyonel kapsam gösterilir.'));
      const tool = el('a', 'tool-link', 'Güvenli sonraki adımı aç');
      tool.href = (category && category.toolUrls && category.toolUrls[0]) || '/karar-motoru/';
      blocked.append(tool);
      container.append(blocked);
      return;
    }

    const gate = el('div', 'gate');
    gate.append(el('strong', '', 'Affiliate bağlantısı için üç doğrulama'));
    const checks = [
      'İlgili ücretsiz uygunluk aracını tamamladım.',
      'Mevcut ürünüm güvenli biçimde ihtiyacı karşılamıyor.',
      'Bağlantının satış ortaklığı bağlantısı olduğunu anladım.'
    ];
    checks.forEach((text) => {
      const label = el('label');
      const input = document.createElement('input');
      input.type = 'checkbox';
      label.append(input, el('span', '', text));
      gate.append(label);
    });
    const note = el('p', 'affiliate-note', product.linkMode === 'exact_model_search'
      ? 'Üretici teknik verisi doğrulandı; Amazon bağlantısı tek ürün önerisi değil, tam model aramasıdır. Liste içindeki model kodunu yeniden doğrulayın.'
      : 'Belirli ASIN kontrol edilmiştir; fiyat, stok, satıcı, teslimat ve garanti Amazon’da yeniden doğrulanır.');
    gate.append(note);
    const link = el('a', 'affiliate-link', liveProduct.linkMode === 'exact_model_search' ? 'Amazon’da tam model araması' : 'Amazon ürün sayfasını aç');
    link.href = liveProduct.url;
    link.target = '_blank';
    link.rel = 'sponsored nofollow noopener';
    link.setAttribute('aria-disabled', 'true');
    link.tabIndex = -1;
    gate.append(link);
    gate.addEventListener('change', () => {
      const ready = gateReady(gate);
      link.setAttribute('aria-disabled', ready ? 'false' : 'true');
      link.tabIndex = ready ? 0 : -1;
      track('affiliate_knowledge_graph_gate_changed', { product_id: product.id, category: product.categoryId, status: product.verificationStatus, link_mode: product.linkMode, gate_state: ready ? 'open' : 'closed' });
    });
    link.addEventListener('click', (event) => {
      if (!gateReady(gate)) {
        event.preventDefault();
        return;
      }
      track('affiliate_knowledge_graph_link_opened', { product_id: product.id, category: product.categoryId, status: product.verificationStatus, link_mode: product.linkMode, gate_state: 'open' });
    });
    container.append(gate);
  }

  function createCard(product) {
    const liveProduct = catalog.getProduct(product.id);
    const category = graph.categories.find((item) => item.id === product.categoryId);
    const needNames = (product.needIds || []).map((id) => graph.needs.find((need) => need.id === id)?.name || id);
    const article = el('article', 'product-card');
    article.id = `product-${product.id}`;
    const head = el('div', 'card-head');
    const heading = el('div');
    heading.append(el('span', statusClass(product, liveProduct), statusLabel(product)));
    heading.append(el('h3', '', product.name));
    heading.append(el('div', 'model', `${product.brand} · ${product.model} · ${product.identifier.type} ${product.identifier.value}`));
    head.append(heading);
    article.append(head);
    addRelationChips(article, product, category, needNames);
    addProperties(article, product);
    addList(article, 'Yeniden doğrulanacak kanıt', product.requiredEvidence);
    addSources(article, product);
    addCommerceGate(article, product, liveProduct, category);
    return article;
  }

  function matches(product) {
    if (filters.category !== 'all' && product.categoryId !== filters.category) return false;
    if (filters.need !== 'all' && !(product.needIds || []).includes(filters.need)) return false;
    if (filters.status !== 'all' && product.verificationStatus !== filters.status) return false;
    return true;
  }

  function render() {
    const products = graph.products.filter(matches);
    const grid = byId('productGrid');
    grid.replaceChildren(...products.map(createCard));
    byId('emptyState').classList.toggle('hidden', products.length > 0);
    byId('resultStatus').textContent = `${products.length} ürün düğümü gösteriliyor.`;
  }

  function populateFilters() {
    graph.categories.forEach((category) => {
      const option = document.createElement('option');
      option.value = category.id;
      option.textContent = category.name;
      byId('categoryFilter').append(option);
    });
    graph.needs.forEach((need) => {
      const option = document.createElement('option');
      option.value = need.id;
      option.textContent = need.name;
      byId('needFilter').append(option);
    });
  }

  function buildJsonLd() {
    const base = 'https://www.alo186.com/urun-bilgi-grafigi/';
    const nodes = [];
    graph.needs.forEach((need) => nodes.push({ '@type': 'DefinedTerm', '@id': `${base}#need-${need.id}`, name: need.name, inDefinedTermSet: `${base}#need-set` }));
    graph.categories.forEach((category) => nodes.push({ '@type': 'DefinedTerm', '@id': `${base}#category-${category.id}`, name: category.name, inDefinedTermSet: `${base}#category-set`, isRelatedTo: (category.needIds || []).map((id) => ({ '@id': `${base}#need-${id}` })) }));
    graph.products.forEach((product) => {
      const properties = Object.entries(product.technicalProperties || {}).map(([name, value]) => ({ '@type': 'PropertyValue', name, value: String(value) }));
      properties.push({ '@type': 'PropertyValue', name: 'Doğrulama durumu', value: product.verificationStatus });
      properties.push({ '@type': 'PropertyValue', name: 'Affiliate bağlantı biçimi', value: product.linkMode });
      nodes.push({
        '@type': 'Product',
        '@id': `${base}#product-${product.id}`,
        name: product.name,
        brand: { '@type': 'Brand', name: product.brand },
        model: product.model,
        identifier: { '@type': 'PropertyValue', propertyID: product.identifier.type, value: product.identifier.value },
        category: { '@id': `${base}#category-${product.categoryId}` },
        url: `${base}#product-${product.id}`,
        sameAs: product.officialSource || undefined,
        additionalProperty: properties,
        isRelatedTo: [
          ...(product.needIds || []).map((id) => ({ '@id': `${base}#need-${id}` })),
          ...(product.relatedTools || []).map((url) => ({ '@type': 'WebApplication', url: `https://www.alo186.com${url}` })),
          ...(product.relatedGuides || []).map((url) => ({ '@type': 'Article', url: `https://www.alo186.com${url}` }))
        ]
      });
    });
    const payload = { '@context': 'https://schema.org', '@graph': [
      { '@type': 'DefinedTermSet', '@id': `${base}#need-set`, name: 'ALO186 elektrik kullanıcı ihtiyaçları' },
      { '@type': 'DefinedTermSet', '@id': `${base}#category-set`, name: 'ALO186 affiliate ürün kategorileri' },
      { '@type': 'ItemList', '@id': `${base}#product-list`, name: 'ALO186 kaynak doğrulamalı affiliate ürün düğümleri', numberOfItems: graph.products.length, itemListElement: graph.products.map((product, index) => ({ '@type': 'ListItem', position: index + 1, item: { '@id': `${base}#product-${product.id}` } })) },
      ...nodes
    ] };
    byId('affiliateProductGraphJsonLd').textContent = JSON.stringify(payload);
  }

  async function init() {
    if (!catalog) throw new Error('Ürün kataloğu yüklenemedi.');
    const response = await fetch('./product-graph.json', { cache: 'no-cache' });
    if (!response.ok) throw new Error(`Bilgi grafiği HTTP ${response.status}`);
    graph = await response.json();
    const summary = catalog.knowledgeGraphSummary();
    byId('needCount').textContent = String(graph.needs.length);
    byId('categoryCount').textContent = String(graph.categories.length);
    byId('productCount').textContent = String(graph.products.length);
    byId('newModelCount').textContent = String(summary.manufacturerSearchCount);
    populateFilters();
    buildJsonLd();
    render();
    byId('categoryFilter').addEventListener('change', (event) => { filters.category = event.target.value; render(); });
    byId('needFilter').addEventListener('change', (event) => { filters.need = event.target.value; render(); });
    byId('statusFilter').addEventListener('change', (event) => { filters.status = event.target.value; render(); });
    byId('clearFilters').addEventListener('click', () => {
      filters = { category: 'all', need: 'all', status: 'all' };
      byId('categoryFilter').value = 'all';
      byId('needFilter').value = 'all';
      byId('statusFilter').value = 'all';
      render();
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    init().catch(() => {
      byId('resultStatus').textContent = 'Bilgi grafiği yüklenemedi; affiliate bağlantıları gösterilmiyor.';
      byId('emptyState').classList.remove('hidden');
    });
  });
})();
