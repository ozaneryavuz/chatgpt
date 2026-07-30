(() => {
  'use strict';

  const catalog = window.Alo186ProductCatalog;
  const grid = document.getElementById('collectionGrid');
  const globalStatus = document.getElementById('collectionStatus');
  if (!catalog || !grid || !globalStatus) return;

  const collections = Array.isArray(catalog.purchaseCollections) ? catalog.purchaseCollections : [];
  const now = new Date();
  const ga4Pending = new Map();
  let ga4ConsentBridgeBound = false;
  const safeId = (value) => String(value || '').replace(/[^a-z0-9_-]/gi, '-');
  const productById = (id) => typeof catalog.getProduct === 'function'
    ? catalog.getProduct(id)
    : (catalog.products || []).find((item) => item.id === id);
  const categoryFor = (product) => typeof catalog.getCategory === 'function'
    ? catalog.getCategory(product && product.category)
    : (catalog.categories || []).find((item) => item.id === (product && product.category));

  function ga4Payload(name, safe) {
    const countLabel = typeof safe.missing_count === 'number'
      ? `missing_${safe.missing_count}_owned_${typeof safe.owned_count === 'number' ? safe.owned_count : 0}`
      : '';
    return {
      route_group: 'product_knowledge_graph',
      content_group: safe.collection || 'missing_parts_planner',
      action_type: safe.action_type || countLabel || safe.route_type || name.replace(/^sales_missing_parts_/, '').slice(0, 80),
      destination_type: safe.product_id || safe.route_type || 'planner',
    };
  }

  function flushGa4Pending() {
    const analytics = window.alo186Analytics;
    if (!analytics || typeof analytics.track !== 'function') return;
    if (typeof analytics.getConsent === 'function' && analytics.getConsent() !== 'granted') return;
    for (const [name, payload] of ga4Pending.values()) analytics.track(name, payload);
    ga4Pending.clear();
  }

  function bindGa4ConsentBridge() {
    if (ga4ConsentBridgeBound) return;
    ga4ConsentBridgeBound = true;
    document.addEventListener('click', (event) => {
      const target = event.target instanceof Element ? event.target : null;
      const button = target && target.closest('[data-alo186-consent-choice="granted"]');
      if (!button) return;
      setTimeout(flushGa4Pending, 0);
    });
  }

  function trackGa4(name, safe) {
    const analytics = window.alo186Analytics;
    if (!analytics || typeof analytics.track !== 'function') return;
    const payload = ga4Payload(name, safe);
    if (typeof analytics.getConsent === 'function' && analytics.getConsent() !== 'granted') {
      if (ga4Pending.size < 20) ga4Pending.set(JSON.stringify([name, payload]), [name, payload]);
      bindGa4ConsentBridge();
      return;
    }
    analytics.track(name, payload);
  }

  const track = (name, payload = {}) => {
    const safe = {};
    for (const key of ['collection', 'product_id', 'route_type', 'action_type']) {
      const value = payload[key];
      if (typeof value === 'string' && value.length < 100) safe[key] = value;
    }
    for (const key of ['missing_count', 'owned_count']) {
      const value = payload[key];
      if (typeof value === 'number' && Number.isFinite(value)) safe[key] = value;
    }
    if (typeof window.Alo186Track === 'function') {
      try { window.Alo186Track(name, safe); } catch (_error) {}
    }
    trackGa4(name, safe);
  };

  function isFresh(product) {
    return Boolean(product && typeof catalog.verificationStatus === 'function' && catalog.verificationStatus(product, now).fresh);
  }

  function isDirect(product) {
    return Boolean(
      product
      && isFresh(product)
      && typeof catalog.publicAffiliateEligible === 'function'
      && catalog.publicAffiliateEligible(product, { now })
      && product.url
    );
  }

  function fallbackRoute(product) {
    const category = categoryFor(product);
    return (product && Array.isArray(product.relatedTools) && product.relatedTools[0])
      || (category && (category.nextStepUrl || (Array.isArray(category.toolUrls) && category.toolUrls[0])))
      || '/akilli-urun-secimi';
  }

  function componentLabel(product) {
    const category = categoryFor(product);
    const verification = product.status === 'verified_listing'
      ? 'Doğrulanmış ASIN'
      : 'Üretici verisi · model araması';
    return `${category ? category.name : product.category} · ${verification}`;
  }

  function make(tag, className, text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined) element.textContent = String(text);
    return element;
  }

  function startCollection(card, collection, actionType) {
    if (card.dataset.analyticsStarted === 'true') return;
    card.dataset.analyticsStarted = 'true';
    track('sales_missing_parts_started', {
      collection: collection.id,
      action_type: actionType,
    });
  }

  function currentSelection(card, products) {
    const owned = new Set(
      [...card.querySelectorAll('[data-owned-product]:checked')].map((input) => input.value),
    );
    return { owned, missing: products.filter((product) => !owned.has(product.id)) };
  }

  function updateCardState(card, collection, products) {
    const confirm = card.querySelector('[data-compatibility-confirm]');
    const plan = card.querySelector('[data-mission-plan]');
    const status = card.querySelector('[data-mission-status]');
    const { owned, missing } = currentSelection(card, products);
    plan.textContent = missing.length
      ? `Yalnız ${missing.length} eksik parçayı göster`
      : 'Satın almama sonucunu göster';
    if (confirm.checked) {
      status.textContent = missing.length
        ? `${owned.size} parça mevcut; ${missing.length} eksik parça için sonuç hazır.`
        : 'Bütün parçalar mevcut işaretlendi; satın almama sonucunu açabilirsiniz.';
    } else if (owned.size) {
      status.textContent = `${owned.size} parça mevcut işaretlendi. Sonuç için uyum onayını tamamlayın.`;
    } else {
      status.textContent = 'Elinizde olan parçaları işaretleyin; ardından uyum onayını tamamlayın.';
    }
    return { owned, missing };
  }

  function linkFor(product, collectionId) {
    const direct = isDirect(product);
    const link = make('a', direct ? 'mission-link' : 'mission-link tool-link');
    link.href = direct ? product.url : fallbackRoute(product);
    link.target = direct ? '_blank' : '_self';
    if (direct) link.rel = 'sponsored nofollow noopener';
    const label = make('small', '', direct ? 'Satış ortaklığı bağlantısı' : 'Önce ücretsiz uygunluk kontrolü');
    const title = make('span', '', product.name);
    link.append(label, title);
    link.addEventListener('click', () => track('sales_missing_part_opened', {
      collection: collectionId,
      product_id: product.id,
      route_type: direct ? 'affiliate' : 'tool',
      action_type: 'missing_part_opened',
    }));
    return link;
  }

  function renderOutput(card, collection, products) {
    startCollection(card, collection, 'plan_button');
    const confirm = card.querySelector('[data-compatibility-confirm]');
    const output = card.querySelector('[data-mission-output]');
    const status = card.querySelector('[data-mission-status]');
    const { owned, missing } = currentSelection(card, products);

    output.replaceChildren();
    output.hidden = false;

    if (!confirm.checked) {
      const blockedSignature = `${collection.id}|${[...owned].sort().join(',')}`;
      if (card.dataset.lastBlockedSignature !== blockedSignature) {
        card.dataset.lastBlockedSignature = blockedSignature;
        track('sales_missing_parts_validation_blocked', {
          collection: collection.id,
          missing_count: missing.length,
          owned_count: owned.size,
          action_type: 'compatibility_confirmation_missing',
        });
      }
      output.append(make('div', 'mission-warning', 'Önce port, güç ve protokol uyumunu yeniden doğrulayacağınızı onaylayın.'));
      status.textContent = 'Uyum onayı olmadan mağaza veya model araması açılmaz.';
      return;
    }

    const planSignature = `${collection.id}|${[...owned].sort().join(',')}`;
    if (card.dataset.lastPlanSignature !== planSignature) {
      card.dataset.lastPlanSignature = planSignature;
      track('sales_missing_parts_planned', {
        collection: collection.id,
        missing_count: missing.length,
        owned_count: owned.size,
        action_type: missing.length ? 'missing_parts_result' : 'no_buy_result',
      });
    }

    if (!missing.length) {
      const noBuy = make('div', 'no-buy');
      noBuy.append(
        make('strong', '', 'Mevcut setiniz tamam görünüyor.'),
        make('p', '', 'Yeni ürün açılmadı. Mevcut parçaların etiket, kablo ve bağlantı durumunu periyodik olarak yeniden kontrol edin.'),
      );
      output.append(noBuy);
      status.textContent = 'Satın almama sonucu oluşturuldu.';
      output.focus({ preventScroll: true });
      return;
    }

    const intro = make('div', 'mission-warning');
    intro.textContent = `${missing.length} eksik parça belirlendi. Bağlantıları ayrı ayrı açın; paket, varyant, fiyat ve stok bilgisini mağazada yeniden doğrulayın.`;
    output.append(intro);
    missing.forEach((product) => output.append(linkFor(product, collection.id)));
    status.textContent = `${missing.length} eksik parça için güvenli sonraki yollar hazır.`;
    output.focus({ preventScroll: true });
  }

  function cardFor(collection) {
    const products = collection.productIds.map(productById).filter(Boolean);
    if (products.length < 2) return null;

    const card = make('article', 'mission-card');
    card.dataset.collection = collection.id;
    card.id = `collection-${safeId(collection.id)}`;
    card.append(
      make('span', 'mission-kicker', `${products.length} parçalık çözüm`),
      make('h3', '', collection.name),
      make('p', '', collection.description),
    );

    const checks = make('ul', 'mission-checks');
    (collection.checks || []).forEach((item) => checks.append(make('li', '', item)));
    card.append(checks);

    const components = make('div', 'component-list');
    products.forEach((product) => {
      const label = make('label', 'component-option');
      const input = document.createElement('input');
      input.type = 'checkbox';
      input.value = product.id;
      input.setAttribute('data-owned-product', 'true');
      input.setAttribute('aria-label', `${product.name} bende var`);
      input.addEventListener('change', () => {
        startCollection(card, collection, 'owned_product_changed');
        updateCardState(card, collection, products);
      });
      const copy = make('span');
      copy.append(make('b', '', product.name), make('small', '', componentLabel(product)));
      label.append(input, copy);
      components.append(label);
    });
    card.append(components);

    const confirmation = make('label', 'mission-confirm');
    const confirmInput = document.createElement('input');
    confirmInput.type = 'checkbox';
    confirmInput.setAttribute('data-compatibility-confirm', 'true');
    confirmInput.addEventListener('change', () => {
      startCollection(card, collection, 'compatibility_confirmation_changed');
      updateCardState(card, collection, products);
    });
    confirmation.append(
      confirmInput,
      make('span', '', 'Port, güç, protokol, ürün varyantı ve mevcut parçaların güvenli durumunu yeniden doğrulayacağım.'),
    );
    card.append(confirmation);

    const plan = make('button', 'mission-plan', 'Yalnız eksik parçaları göster');
    plan.type = 'button';
    plan.setAttribute('data-mission-plan', 'true');
    plan.addEventListener('click', () => renderOutput(card, collection, products));
    card.append(plan);

    const output = make('div', 'mission-output');
    output.hidden = true;
    output.tabIndex = -1;
    output.setAttribute('data-mission-output', 'true');
    output.setAttribute('aria-live', 'polite');
    card.append(output);

    const status = make('p', 'mission-status', 'Elinizde olan parçaları işaretleyin.');
    status.setAttribute('data-mission-status', 'true');
    card.append(status);
    updateCardState(card, collection, products);
    return card;
  }

  function focusRequestedCollection() {
    const params = new URLSearchParams(window.location.search);
    const requested = params.get('bundle') || params.get('collection');
    if (!requested) return;
    const card = document.querySelector(`[data-collection="${CSS.escape(requested)}"]`);
    if (!card) return;
    card.classList.add('is-focused');
    card.scrollIntoView({ behavior: 'smooth', block: 'center' });
    const first = card.querySelector('input,button,a');
    if (first) first.focus({ preventScroll: true });
  }

  function init() {
    if (!collections.length) {
      globalStatus.textContent = 'Güncel ve güvenli hazır set bulunamadı; tekil ürün grafiğini kullanın.';
      return;
    }
    const cards = collections.map(cardFor).filter(Boolean);
    grid.replaceChildren(...cards);
    globalStatus.textContent = `${cards.length} hazır çözüm seti gösteriliyor. Setler zorunlu toplu satın alma değildir.`;
    track('sales_missing_parts_collection_rendered', {
      missing_count: cards.length,
      route_type: 'product-knowledge-graph',
      action_type: 'collection_rendered',
    });
    focusRequestedCollection();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})();
