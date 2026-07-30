(() => {
  'use strict';
  const TAG = 'alo186rehber-21';
  const state = { catalog: null, verified: null, intent: 'all', query: '' };
  const $ = (id) => document.getElementById(id);
  const riskText = { consumer: 'Tüketici', 'consumer-gated': 'Koşullu tüketici', 'professional-gated': 'Profesyonel sınır' };

  function affiliateUrl(item) {
    if (!item || item.risk === 'professional-gated') return null;
    return `https://www.amazon.com.tr/s?k=${encodeURIComponent(item.search)}&tag=${TAG}`;
  }

  function mergeCatalog(base, extension) {
    const intentMap = new Map(base.intents.map((item) => [item.id, { ...item, productClasses: [...item.productClasses] }]));
    extension.intents.forEach((item) => intentMap.set(item.id, item));
    const productMap = new Map(base.productClasses.map((item) => [item.id, item]));
    extension.productClasses.forEach((item) => productMap.set(item.id, item));
    const productClasses = [...productMap.values()];
    const byIntent = new Map();
    productClasses.forEach((product) => product.needs.forEach((need) => {
      if (!byIntent.has(need)) byIntent.set(need, []);
      byIntent.get(need).push(product.id);
    }));
    const intents = [...intentMap.values()].map((intent) => ({
      ...intent,
      productClasses: [...new Set([...(intent.productClasses || []), ...(byIntent.get(intent.id) || [])])]
    }));
    return { ...base, version: extension.version, generatedAt: extension.generatedAt, intents, productClasses };
  }

  function verifiedModels(classId) {
    return (state.verified?.products || []).filter((product) => product.classId === classId);
  }

  function matches(item) {
    const intentMatch = state.intent === 'all' || item.needs.includes(state.intent);
    const modelText = verifiedModels(item.id).flatMap((model) => [model.name, model.brand, model.userNeed, ...model.strengths, ...model.limits]).join(' ');
    const text = [item.label, item.search, ...item.requiredEvidence, ...(item.symptoms || []), ...(item.avoidWhen || []), ...item.needs, modelText].join(' ').toLocaleLowerCase('tr-TR');
    return intentMatch && (!state.query || text.includes(state.query));
  }

  function injectVerifiedProductGraph() {
    const products = state.verified.products.map((product) => ({
      '@type': 'Product',
      '@id': `https://alo186.com/affiliate-knowledge-graph/#${product.id}`,
      name: product.name,
      brand: { '@type': 'Brand', name: product.brand },
      sku: product.id,
      identifier: [
        { '@type': 'PropertyValue', propertyID: 'ASIN', value: product.asin },
        { '@type': 'PropertyValue', propertyID: 'MPN', value: product.mpn }
      ],
      category: product.classId,
      description: product.userNeed,
      sameAs: product.url,
      dateModified: state.verified.verifiedAt,
      additionalProperty: Object.entries(product.attributes).map(([name, value]) => ({ '@type': 'PropertyValue', name, value }))
    }));
    const script = document.createElement('script');
    script.type = 'application/ld+json';
    script.id = 'verified-affiliate-products';
    script.textContent = JSON.stringify({ '@context': 'https://schema.org', '@graph': products });
    document.head.appendChild(script);
  }

  function renderIntents() {
    const host = $('intents');
    host.replaceChildren();
    const all = [{ id: 'all', label: 'Tüm ürün sınıfları' }, ...state.catalog.intents];
    all.forEach((intent) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = `intent${state.intent === intent.id ? ' active' : ''}`;
      button.textContent = intent.label;
      button.dataset.intent = intent.id;
      button.setAttribute('aria-pressed', String(state.intent === intent.id));
      button.addEventListener('click', () => {
        state.intent = intent.id;
        renderIntents();
        renderProducts();
      });
      host.appendChild(button);
    });
  }

  function appendList(host, items) {
    host.replaceChildren();
    (items || []).forEach((text) => {
      const li = document.createElement('li');
      li.textContent = text;
      host.appendChild(li);
    });
  }

  function renderVerifiedModels(card, item, checkbox) {
    const models = verifiedModels(item.id);
    if (!models.length) return;
    const section = document.createElement('section');
    section.className = 'verified-models';
    const heading = document.createElement('strong');
    heading.textContent = `${models.length} doğrulanmış model`;
    section.appendChild(heading);
    models.forEach((model) => {
      const article = document.createElement('article');
      article.className = 'verified-model';
      const title = document.createElement('h4');
      title.textContent = model.name;
      const need = document.createElement('p');
      need.textContent = model.userNeed;
      const strengths = document.createElement('ul');
      appendList(strengths, model.strengths);
      const limits = document.createElement('p');
      limits.className = 'limit';
      limits.textContent = `Sınırlar: ${model.limits.join(' · ')}`;
      const noBuy = document.createElement('p');
      noBuy.className = 'no-buy-note';
      noBuy.textContent = model.doNotBuyWhen;
      const link = document.createElement('a');
      link.className = 'model-link';
      link.textContent = 'Doğrulanmış modeli Amazon’da incele';
      link.rel = 'sponsored nofollow noopener';
      link.target = '_blank';
      link.setAttribute('aria-disabled', 'true');
      checkbox.addEventListener('change', () => {
        if (checkbox.checked) {
          link.href = model.url;
          link.setAttribute('aria-disabled', 'false');
        } else {
          link.removeAttribute('href');
          link.setAttribute('aria-disabled', 'true');
        }
      });
      article.append(title, need, strengths, limits, noBuy, link);
      section.appendChild(article);
    });
    card.querySelector('.avoid').after(section);
  }

  function renderProducts() {
    const list = state.catalog.productClasses.filter(matches);
    const host = $('products');
    host.replaceChildren();
    $('resultCount').textContent = `${list.length} ürün sınıfı · ${state.verified.products.length} doğrulanmış model`;
    const selected = state.catalog.intents.find((item) => item.id === state.intent);
    $('resultTitle').textContent = selected ? selected.label : 'Bütün güvenli ürün sınıfları';

    if (!list.length) {
      const empty = document.createElement('div');
      empty.className = 'empty';
      empty.innerHTML = '<strong>Eşleşme bulunamadı.</strong><p>Arama ifadesini sadeleştirin veya ücretsiz Akıllı Ürün Merkezi üzerinden ihtiyacı yeniden sınıflandırın.</p><a class="button" href="/akilli-urun-secimi">Akıllı ürün merkezini aç</a>';
      host.appendChild(empty);
      return;
    }

    list.forEach((item) => {
      const card = $('productTemplate').content.firstElementChild.cloneNode(true);
      card.dataset.risk = item.risk;
      card.querySelector('.risk').textContent = riskText[item.risk] || item.risk;
      card.querySelector('.nodes').textContent = `${item.needs.length} ihtiyaç bağlantısı`;
      card.querySelector('h3').textContent = item.label;
      card.querySelector('.why').textContent = item.search;
      appendList(card.querySelector('.evidence ul'), item.requiredEvidence);
      const symptoms = card.querySelector('.symptoms');
      if (item.symptoms?.length) appendList(symptoms.querySelector('ul'), item.symptoms); else symptoms.hidden = true;
      const avoid = card.querySelector('.avoid');
      if (item.avoidWhen?.length) appendList(avoid.querySelector('ul'), item.avoidWhen); else avoid.hidden = true;
      const guide = card.querySelector('.guide');
      guide.href = item.guide;
      const confirm = card.querySelector('.confirm');
      const checkbox = confirm.querySelector('input');
      const affiliate = card.querySelector('.affiliate');
      const url = affiliateUrl(item);
      if (!url) {
        confirm.hidden = true;
        affiliate.textContent = 'Mağaza yönlendirmesi kapalı';
        affiliate.classList.add('disabled');
      } else {
        renderVerifiedModels(card, item, checkbox);
        checkbox.addEventListener('change', () => {
          if (checkbox.checked) {
            affiliate.href = url;
            affiliate.setAttribute('aria-disabled', 'false');
          } else {
            affiliate.removeAttribute('href');
            affiliate.setAttribute('aria-disabled', 'true');
          }
        });
      }
      host.appendChild(card);
    });
  }

  async function loadJson(path) {
    const response = await fetch(path, { cache: 'no-store' });
    if (!response.ok) throw new Error(`Katalog yüklenemedi: ${response.status}`);
    return response.json();
  }

  async function boot() {
    const [base, extension, verified] = await Promise.all([
      loadJson('./catalog.json'),
      loadJson('./catalog-extension-v103.json'),
      loadJson('./verified-products.json')
    ]);
    state.catalog = mergeCatalog(base, extension);
    state.verified = verified;
    $('intentCount').textContent = state.catalog.intents.length;
    $('productCount').textContent = `${state.catalog.productClasses.length} sınıf / ${verified.products.length} model`;
    $('search').addEventListener('input', (event) => {
      state.query = event.target.value.trim().toLocaleLowerCase('tr-TR');
      renderProducts();
    });
    injectVerifiedProductGraph();
    renderIntents();
    renderProducts();
  }

  boot().catch((error) => {
    $('products').innerHTML = `<div class="empty"><strong>Ürün grafiği açılamadı.</strong><p>${error.message}</p><a class="button" href="/amazon-elektrik-urunleri/">Ürün merkezine dön</a></div>`;
  });
})();
