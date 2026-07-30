(() => {
  'use strict';

  const TAG = 'alo186rehber-21';
  const state = { catalog: null, intent: 'all', query: '' };
  const productCatalog = globalThis.Alo186ProductCatalog || null;
  const $ = (id) => document.getElementById(id);
  const riskText = {
    consumer: 'Tüketici',
    'consumer-gated': 'Koşullu tüketici',
    'professional-gated': 'Profesyonel sınır'
  };
  const attributeLabels = {
    capacityMah: 'Kapasite', energyWh: 'Enerji', capacityWh: 'Kapasite', maxOutputW: 'Azami çıkış',
    maxSingleDeviceW: 'Tek cihaz gücü', totalOutputW: 'Toplam güç', continuousW: 'Sürekli güç', surgeW: 'Tepe güç',
    usbCPorts: 'USB-C portu', usbAPorts: 'USB-A portu', ports: 'Toplam port', lengthM: 'Uzunluk',
    maxCurrentA: 'Akım', maxPowerW: 'Etiket gücü', dataTransferGbps: 'Veri hızı', dataTransferMbps: 'Veri hızı',
    maxDataGbps: 'Bant genişliği', hdmiVersion: 'HDMI', displayPortVersion: 'DisplayPort', maxResolution: 'Azami çözünürlük',
    maxResolutionClaim: 'Çözünürlük beyanı', max4KRefreshHz: '4K yenileme', max2KRefreshHz: '2K yenileme',
    pdPassThroughW: 'PD geçişi', includedCableW: 'Dahil kablo', includedCableM: 'Dahil kablo uzunluğu',
    pd31: 'USB PD 3.1', pps: 'PPS', gan: 'GaN', bidirectional: 'Çift yön', powerDelivery: 'Güç aktarımı'
  };
  const attributeSuffix = {
    capacityMah: ' mAh', energyWh: ' Wh', capacityWh: ' Wh', maxOutputW: ' W', maxSingleDeviceW: ' W',
    totalOutputW: ' W', continuousW: ' W', surgeW: ' W', lengthM: ' m', maxCurrentA: ' A', maxPowerW: ' W',
    dataTransferGbps: ' Gbps', dataTransferMbps: ' Mbps', maxDataGbps: ' Gbps', max4KRefreshHz: ' Hz',
    max2KRefreshHz: ' Hz', pdPassThroughW: ' W', includedCableW: ' W', includedCableM: ' m'
  };
  const intentCategories = {
    'mobil-enerji': ['powerbank', 'usb_c_charger', 'usb_c_cable', 'car_charger'],
    'telefon-hizli-sarj': ['usb_c_charger', 'usb_c_cable', 'powerbank'],
    'dizustu-yuksek-guc': ['usb_c_charger', 'usb_c_cable', 'usb_c_hub', 'display_cable', 'powerbank', 'car_charger'],
    'harici-ekran': ['usb_c_hub', 'display_cable'],
    'seyahat-calisma-seti': ['usb_c_charger', 'usb_c_cable', 'usb_c_hub', 'display_cable', 'powerbank', 'car_charger'],
    'ev-ofis-konforu': ['usb_c_hub', 'display_cable', 'smart_plug', 'surge_strip'],
    'seyahat-karavan': ['car_charger', 'powerbank', 'power_station', 'usb_c_charger', 'usb_c_cable'],
    'evde-elektrik-kesintisi': ['mini_ups', 'power_station', 'emergency_light', 'powerbank'],
    'kesinti-hazirligi': ['mini_ups', 'power_station', 'emergency_light', 'powerbank'],
    'internet-surekliligi': ['mini_ups', 'power_station'],
    'cihaz-koruma': ['surge_strip', 'smart_plug'],
    'enerji-olcumu': ['smart_plug', 'outlet_tester'],
    'ev-guvenligi': ['smoke_alarm', 'co_alarm', 'emergency_light'],
    'cocuk-ve-yasli-guvenligi': ['smoke_alarm', 'co_alarm', 'emergency_light'],
    'ev-sarj': ['ev_cable', 'portable_evse'],
    'ups-bakim': ['ups_battery', 'smart_plug'],
    'olcum-ve-bakim': ['outlet_tester', 'smart_plug'],
    'kablo-duzeni': ['usb_c_cable', 'usb_c_hub', 'display_cable', 'extension_cord']
  };

  function affiliateUrl(item) {
    if (!item || item.risk === 'professional-gated') return null;
    return `https://www.amazon.com.tr/s?k=${encodeURIComponent(item.search)}&tag=${TAG}`;
  }

  function mergeCatalog(base, ...extensions) {
    let merged = {
      ...base,
      intents: base.intents.map((item) => ({ ...item, productClasses: [...(item.productClasses || [])] })),
      productClasses: [...base.productClasses]
    };
    for (const extension of extensions) {
      const intentMap = new Map(merged.intents.map((item) => [item.id, item]));
      for (const item of extension.intents || []) {
        const current = intentMap.get(item.id);
        intentMap.set(item.id, current
          ? { ...current, ...item, productClasses: [...new Set([...(current.productClasses || []), ...(item.productClasses || [])])] }
          : { ...item, productClasses: [...(item.productClasses || [])] });
      }
      const productMap = new Map(merged.productClasses.map((item) => [item.id, item]));
      for (const item of extension.productClasses || []) productMap.set(item.id, item);
      const productClasses = [...productMap.values()];
      const byIntent = new Map();
      for (const product of productClasses) for (const need of product.needs || []) {
        if (!byIntent.has(need)) byIntent.set(need, []);
        byIntent.get(need).push(product.id);
      }
      const intents = [...intentMap.values()].map((intent) => ({
        ...intent,
        productClasses: [...new Set([...(intent.productClasses || []), ...(byIntent.get(intent.id) || [])])]
      }));
      merged = { ...merged, version: extension.version, generatedAt: extension.generatedAt, intents, productClasses };
    }
    return merged;
  }

  function genericMatches(item) {
    const intentMatch = state.intent === 'all' || (item.needs || []).includes(state.intent);
    const text = [item.label, item.search, ...(item.requiredEvidence || []), ...(item.symptoms || []), ...(item.avoidWhen || []), ...(item.needs || [])]
      .join(' ').toLocaleLowerCase('tr-TR');
    return intentMatch && (!state.query || text.includes(state.query));
  }

  function exactIntentMatch(product) {
    if (state.intent === 'all') return true;
    if ((product.intentIds || []).includes(state.intent)) return true;
    const categories = intentCategories[state.intent] || [];
    return categories.includes(product.category);
  }

  function exactMatches(product) {
    if (!exactIntentMatch(product)) return false;
    if (!state.query) return true;
    const text = [
      product.name, product.brand, product.model, product.mpn, product.asin, product.category,
      product.userNeed, ...(product.bestFor || []), ...(product.noBuyWhen || []), ...(product.requiredEvidence || []),
      ...(product.strengths || []), ...(product.limits || []), ...Object.keys(product.attributes || {}), ...Object.values(product.attributes || {})
    ].filter((value) => value !== null && value !== undefined).join(' ').toLocaleLowerCase('tr-TR');
    return text.includes(state.query);
  }

  function renderIntents() {
    const host = $('intents');
    host.replaceChildren();
    const all = [{ id: 'all', label: 'Tüm ürün sınıfları' }, ...state.catalog.intents];
    for (const intent of all) {
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
        renderExactProducts();
      });
      host.appendChild(button);
    }
  }

  function appendList(host, items) {
    host.replaceChildren();
    for (const text of items || []) {
      const li = document.createElement('li');
      li.textContent = text;
      host.appendChild(li);
    }
  }

  function renderProducts() {
    const list = state.catalog.productClasses.filter(genericMatches);
    const host = $('products');
    host.replaceChildren();
    $('resultCount').textContent = `${list.length} ürün sınıfı`;
    const selected = state.catalog.intents.find((item) => item.id === state.intent);
    $('resultTitle').textContent = selected ? selected.label : 'Bütün güvenli ürün sınıfları';

    if (!list.length) {
      const empty = document.createElement('div');
      empty.className = 'empty';
      empty.innerHTML = '<strong>Eşleşme bulunamadı.</strong><p>Arama ifadesini sadeleştirin veya Akıllı Ürün Merkezi üzerinden ihtiyacı yeniden sınıflandırın.</p><a class="button" href="/akilli-urun-secimi">Akıllı ürün merkezini aç</a>';
      host.appendChild(empty);
      return;
    }

    for (const item of list) {
      const card = $('productTemplate').content.firstElementChild.cloneNode(true);
      card.dataset.risk = item.risk;
      card.querySelector('.risk').textContent = riskText[item.risk] || item.risk;
      card.querySelector('.nodes').textContent = `${(item.needs || []).length} ihtiyaç bağlantısı`;
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
    }
  }

  function humanValue(key, input) {
    if (input === true) return 'Var';
    if (input === false) return 'Yok';
    if (input === null || input === undefined) return 'Bilinmiyor';
    return `${input}${attributeSuffix[key] || ''}`;
  }

  function exactStatus(product, category, fresh, direct) {
    if (!fresh) return { risk: 'Yenilenmeli', verified: '45 günlük doğrulama süresi geçti' };
    if (category?.affiliatePolicy === 'professional_only') return { risk: 'Profesyonel', verified: 'Mağaza yolu kapalı' };
    if (direct) return { risk: 'Doğrudan', verified: 'Doğrulanmış ASIN · güncel' };
    if (product.status === 'manufacturer_verified_search') return { risk: 'Teknik kapılı', verified: 'Üretici verisi · tam model araması' };
    return { risk: 'Teknik kapılı', verified: 'Doğrulanmış ASIN · araç sonrası' };
  }

  function exactProducts() {
    if (!productCatalog || !Array.isArray(productCatalog.products)) return [];
    const allowed = typeof productCatalog.isCatalogProduct === 'function'
      ? (product) => productCatalog.isCatalogProduct(product)
      : (product) => ['verified_listing', 'manufacturer_verified_search'].includes(product.status);
    return productCatalog.products.filter(allowed);
  }

  function addProperty(host, key, input) {
    const box = document.createElement('div');
    box.className = 'property';
    const label = document.createElement('small');
    label.textContent = attributeLabels[key] || key;
    const value = document.createElement('strong');
    value.textContent = humanValue(key, input);
    box.append(label, value);
    host.appendChild(box);
  }

  function renderExactProducts() {
    const now = new Date();
    const all = exactProducts();
    const visible = all.filter(exactMatches);
    const direct = all.filter((product) => productCatalog.publicAffiliateEligible(product, { now })).length;
    const stale = all.filter((product) => !productCatalog.verificationStatus(product, now).fresh).length;
    const gated = all.length - direct - stale;
    $('exactCount').textContent = all.length;
    $('directCount').textContent = direct;
    $('gatedCount').textContent = Math.max(0, gated);
    $('staleCount').textContent = stale;
    const host = $('exactProducts');
    host.replaceChildren();

    if (!visible.length) {
      const empty = document.createElement('div');
      empty.className = 'empty';
      empty.innerHTML = '<strong>Bu filtrede güncel ürün düğümü bulunamadı.</strong><p>Teknik gereksinimi düşürmeyin; ürün sınıfı kartındaki ücretsiz aracı kullanın veya filtreyi temizleyin.</p>';
      host.appendChild(empty);
      return;
    }

    for (const product of visible) {
      const category = productCatalog.getCategory(product.category);
      const freshness = productCatalog.verificationStatus(product, now);
      const isDirect = productCatalog.publicAffiliateEligible(product, { now });
      const status = exactStatus(product, category, freshness.fresh, isDirect);
      const card = $('exactProductTemplate').content.firstElementChild.cloneNode(true);
      card.dataset.risk = category?.affiliatePolicy === 'professional_only' ? 'professional-gated' : isDirect ? 'consumer' : 'consumer-gated';
      card.querySelector('.risk').textContent = status.risk;
      card.querySelector('.verified').textContent = status.verified;
      card.querySelector('h3').textContent = product.name;
      card.querySelector('.model-line').textContent = `${product.brand} · ${product.model || product.mpn || product.id} · ${product.asin ? `ASIN ${product.asin}` : 'tam model araması'}`;
      card.querySelector('.user-need').textContent = product.userNeed || product.strengths?.[0] || category?.description || '';
      appendList(card.querySelector('.best ul'), product.bestFor?.length ? product.bestFor : (product.strengths || []).slice(0, 3));
      appendList(card.querySelector('.evidence ul'), product.requiredEvidence?.length ? product.requiredEvidence : []);
      const noBuy = product.noBuyWhen?.length
        ? product.noBuyWhen
        : (product.limits || []).filter((item) => /yeterli|almayın|uygun değil|doğrulan/i.test(item)).slice(0, 3);
      appendList(card.querySelector('.avoid ul'), noBuy.length ? noBuy : ['Mevcut güvenli ürün aynı ihtiyacı karşılıyorsa yeni ürün almayın.']);
      const properties = card.querySelector('.properties');
      for (const [key, input] of Object.entries(product.attributes || {}).slice(0, 12)) addProperty(properties, key, input);
      appendList(card.querySelector('.limits ul'), product.limits || []);
      const guide = card.querySelector('.guide');
      guide.href = product.relatedTools?.[0] || category?.nextStepUrl || '/akilli-urun-secimi';
      const gate = card.querySelector('.exact-gate');
      const affiliate = card.querySelector('.affiliate');
      const blocked = card.querySelector('.blocked-note');
      const professional = category?.affiliatePolicy === 'professional_only';
      if (!freshness.fresh || professional) {
        gate.hidden = true;
        affiliate.hidden = true;
        blocked.hidden = false;
        blocked.textContent = !freshness.fresh
          ? 'Teknik doğrulama 45 günlük sınırı geçti. Ürün bağlantısı veri yenilenene kadar kapalıdır.'
          : 'Ölçüm, sabit tesisat veya can güvenliği nedeniyle bu kategoride mağaza yönlendirmesi kapalıdır.';
      } else {
        affiliate.textContent = product.linkMode === 'exact_model_search' ? 'Amazon’da tam modeli ara' : 'Amazon ürün sayfasını aç';
        const target = product.url;
        const checkboxes = [...gate.querySelectorAll('input[type=checkbox]')];
        const sync = () => {
          const ready = checkboxes.every((input) => input.checked);
          affiliate.setAttribute('aria-disabled', ready ? 'false' : 'true');
          affiliate.tabIndex = ready ? 0 : -1;
          if (ready) affiliate.href = target; else affiliate.removeAttribute('href');
        };
        gate.addEventListener('change', sync);
        affiliate.addEventListener('click', (event) => {
          if (!checkboxes.every((input) => input.checked)) event.preventDefault();
        });
        sync();
      }
      host.appendChild(card);
    }
  }

  async function loadJson(path) {
    const response = await fetch(path, { cache: 'no-store' });
    if (!response.ok) throw new Error(`Katalog yüklenemedi: ${response.status}`);
    return response.json();
  }

  async function boot() {
    const [base, extension103, extension104] = await Promise.all([
      loadJson('./catalog.json'),
      loadJson('./catalog-extension-v103.json'),
      loadJson('./catalog-extension-v104.json')
    ]);
    state.catalog = mergeCatalog(base, extension103, extension104);
    $('intentCount').textContent = state.catalog.intents.length;
    $('productCount').textContent = state.catalog.productClasses.length;
    $('search').addEventListener('input', (event) => {
      state.query = event.target.value.trim().toLocaleLowerCase('tr-TR');
      renderProducts();
      renderExactProducts();
    });
    renderIntents();
    renderProducts();
    renderExactProducts();
  }

  boot().catch((error) => {
    $('products').innerHTML = `<div class="empty"><strong>Ürün grafiği açılamadı.</strong><p>${error.message}</p><a class="button" href="/amazon-elektrik-urunleri/">Ürün merkezine dön</a></div>`;
    $('exactProducts').innerHTML = '<div class="empty"><strong>Doğrulanmış model grafiği açılamadı.</strong><p>Affiliate bağlantıları güvenli biçimde kapalı tutuldu.</p></div>';
  });
})();