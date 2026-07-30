(() => {
  'use strict';
  const TAG = 'alo186rehber-21';
  const state = { catalog: null, intent: 'all', query: '' };
  const $ = (id) => document.getElementById(id);
  const riskText = { consumer: 'Tüketici', 'consumer-gated': 'Koşullu tüketici', 'professional-gated': 'Profesyonel sınır' };

  function affiliateUrl(item) {
    if (!item || item.risk === 'professional-gated') return null;
    return `https://www.amazon.com.tr/s?k=${encodeURIComponent(item.search)}&tag=${TAG}`;
  }

  function mergeCatalog(base, extension) {
    const intentMap = new Map(base.intents.map((item) => [item.id, { ...item, productClasses: [...(item.productClasses || [])] }]));
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

  function matches(item) {
    const intentMatch = state.intent === 'all' || item.needs.includes(state.intent);
    const text = [item.label, item.search, ...item.requiredEvidence, ...(item.symptoms || item.signals || []), ...(item.avoidWhen || []), ...(item.profiles || []), ...(item.environments || []), ...item.needs].join(' ').toLocaleLowerCase('tr-TR');
    return intentMatch && (!state.query || text.includes(state.query));
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

  function renderProducts() {
    const list = state.catalog.productClasses.filter(matches);
    const host = $('products');
    host.replaceChildren();
    $('resultCount').textContent = `${list.length} ürün sınıfı`;
    const selected = state.catalog.intents.find((item) => item.id === state.intent);
    $('resultTitle').textContent = selected ? selected.label : 'Bütün güvenli ürün sınıfları';

    if (!list.length) {
      const empty = document.createElement('div');
      empty.className = 'empty';
      empty.innerHTML = '<strong>Eşleşme bulunamadı.</strong><p>Belirtiyi sadeleştirin veya ücretsiz Akıllı Ürün Merkezi üzerinden ihtiyacı yeniden sınıflandırın.</p><a class="button" href="/akilli-urun-secimi">Akıllı ürün merkezini aç</a>';
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
      const symptomItems = item.symptoms || item.signals || [];
      if (symptomItems.length) appendList(symptoms.querySelector('ul'), symptomItems); else symptoms.hidden = true;
      const avoid = card.querySelector('.avoid');
      if (item.avoidWhen?.length) appendList(avoid.querySelector('ul'), item.avoidWhen); else avoid.hidden = true;
      const context = card.querySelector('.context');
      const contextItems = [...(item.profiles || []), ...(item.environments || [])];
      if (contextItems.length) appendList(context.querySelector('ul'), contextItems); else context.hidden = true;
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
    const [base, v103, v104] = await Promise.all([
      loadJson('./catalog.json'),
      loadJson('./catalog-extension-v103.json'),
      loadJson('./catalog-v104-extension.json')
    ]);
    state.catalog = [v103, v104].reduce((catalog, extension) => mergeCatalog(catalog, extension), base);
    $('intentCount').textContent = state.catalog.intents.length;
    $('productCount').textContent = state.catalog.productClasses.length;
    $('search').addEventListener('input', (event) => {
      state.query = event.target.value.trim().toLocaleLowerCase('tr-TR');
      renderProducts();
    });
    renderIntents();
    renderProducts();
  }

  boot().catch((error) => {
    $('products').innerHTML = `<div class="empty"><strong>Ürün grafiği açılamadı.</strong><p>${error.message}</p><a class="button" href="/amazon-elektrik-urunleri/">Ürün merkezine dön</a></div>`;
  });
})();