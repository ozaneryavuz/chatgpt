(function () {
  'use strict';
  const Core = window.ALO186BackupSolution;
  if (!Core) return;

  const STORAGE_KEY = 'alo186_backup_solution_v1';
  const MAX_AGE_MS = 30 * 24 * 60 * 60 * 1000;
  const PRODUCT_FALLBACK = '/akilli-urun-secimi?source=backup-solution';
  const $ = function (id) { return document.getElementById(id); };
  const form = $('solutionForm');
  const results = $('results');
  const restoreBtn = $('restoreBtn');
  let lastResult = null;

  function track(eventName, params) {
    const safeParams = Object.assign({ tool: 'backup-solution-selector' }, params || {});
    if (typeof window.gtag === 'function') window.gtag('event', eventName, safeParams);
    window.dispatchEvent(new CustomEvent('alo186:analytics', { detail: { event: eventName, params: safeParams } }));
  }

  function escapeHtml(value) {
    return String(value == null ? '' : value).replace(/[&<>"']/g, function (char) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char];
    });
  }

  function collect() {
    return Core.sanitizeInput({
      context: $('context').value,
      loadProfile: $('loadProfile').value,
      powerBand: $('powerBand').value,
      continuity: $('continuity').value,
      duration: $('duration').value,
      installation: $('installation').value,
      outdoorFuel: $('outdoorFuel').value,
      threePhase: $('threePhase').checked
    });
  }

  function save(input) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ savedAt: Date.now(), input: Core.sanitizeInput(input) }));
      restoreBtn.hidden = false;
    } catch (_) {}
  }

  function load() {
    try {
      const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null');
      if (!stored || !stored.savedAt || Date.now() - stored.savedAt > MAX_AGE_MS) {
        localStorage.removeItem(STORAGE_KEY);
        return null;
      }
      return Core.sanitizeInput(stored.input || {});
    } catch (_) {
      return null;
    }
  }

  function apply(input) {
    ['context', 'loadProfile', 'powerBand', 'continuity', 'duration', 'installation', 'outdoorFuel'].forEach(function (key) {
      if ($(key) && input[key]) $(key).value = input[key];
    });
    $('threePhase').checked = Boolean(input.threePhase);
  }

  function list(items) {
    return items.map(function (item) { return '<li>' + escapeHtml(item) + '</li>'; }).join('');
  }

  function disableProductLink(link) {
    link.href = PRODUCT_FALLBACK;
    link.setAttribute('aria-disabled', 'true');
    link.setAttribute('tabindex', '-1');
    link.classList.add('disabled');
  }

  function enableProductLink(link) {
    if (!link.dataset.href) return;
    link.href = link.dataset.href;
    link.removeAttribute('aria-disabled');
    link.removeAttribute('tabindex');
    link.classList.remove('disabled');
  }

  function render(result, input) {
    lastResult = result;
    $('validation').textContent = '';
    $('primaryLabel').textContent = result.primary.solution.label;
    $('primarySummary').textContent = result.primary.solution.summary;
    $('secondaryLabel').textContent = result.secondary.solution.label;
    $('secondarySummary').textContent = result.secondary.solution.summary;
    $('reasonList').innerHTML = list(result.reasons.length ? result.reasons : ['Seçimleriniz güç, süre, geçiş ve kullanım biçimi birlikte değerlendirilerek sıralandı.']);
    $('checkList').innerHTML = list(result.checks);

    const warning = $('professionalWarning');
    if (result.professional) {
      warning.hidden = false;
      $('professionalList').innerHTML = list(result.professionalReasons.concat(result.cautions));
      track('backup_solution_professional_route_shown', {
        context: input.context,
        power_band: input.powerBand,
        installation: input.installation,
        primary: result.primary.key
      });
    } else {
      warning.hidden = true;
      $('professionalList').innerHTML = '';
    }

    const calculatorLink = $('calculatorLink');
    calculatorLink.href = result.calculatorUrl;
    calculatorLink.textContent = result.primary.key === 'hybrid' ? 'Süreklilik planını aç' : 'Teknik hesabı tamamla';

    const commercial = $('commercialRoute');
    const productLink = $('productLink');
    const productAck = $('productAck');
    productAck.checked = false;
    disableProductLink(productLink);
    if (result.showCommercial) {
      commercial.hidden = false;
      productLink.dataset.href = result.productUrl;
    } else {
      commercial.hidden = true;
      productLink.removeAttribute('data-href');
    }

    $('resultStatus').textContent = result.professional ? 'Profesyonel doğrulama gerekli' : 'Tüketici seviyesinde ön karşılaştırma';
    results.hidden = false;
    results.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
  }

  function calculate(input, restored) {
    const result = Core.evaluate(input);
    if (!result.ok) {
      $('validation').textContent = result.errors.join(' ');
      results.hidden = true;
      return;
    }
    render(result, input);
    save(input);
    track(restored ? 'backup_solution_restored' : 'backup_solution_assessed', {
      context: input.context,
      load_profile: input.loadProfile,
      power_band: input.powerBand,
      duration: input.duration,
      installation: input.installation,
      primary: result.primary.key,
      commercial_route: result.showCommercial
    });
  }

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    calculate(collect(), false);
  });

  $('exampleBtn').addEventListener('click', function () {
    const example = {
      context: 'homeoffice',
      loadProfile: 'electronics',
      powerBand: 'p600',
      continuity: 'zero',
      duration: 'd2',
      installation: 'portable',
      outdoorFuel: 'no',
      threePhase: false
    };
    apply(example);
    calculate(example, false);
  });

  $('clearBtn').addEventListener('click', function () {
    form.reset();
    results.hidden = true;
    lastResult = null;
    $('validation').textContent = '';
    track('backup_solution_form_cleared');
  });

  restoreBtn.addEventListener('click', function () {
    const input = load();
    if (!input) {
      restoreBtn.hidden = true;
      return;
    }
    apply(input);
    calculate(input, true);
  });

  $('productAck').addEventListener('change', function (event) {
    const link = $('productLink');
    if (event.target.checked && link.dataset.href) enableProductLink(link);
    else disableProductLink(link);
  });

  $('productLink').addEventListener('click', function (event) {
    if (event.currentTarget.getAttribute('aria-disabled') === 'true') {
      event.preventDefault();
      return;
    }
    track('backup_solution_product_center_opened', { primary: lastResult ? lastResult.primary.key : 'unknown' });
  });

  $('calculatorLink').addEventListener('click', function () {
    track('backup_solution_calculator_opened', { primary: lastResult ? lastResult.primary.key : 'unknown' });
  });

  $('copyBtn').addEventListener('click', function () {
    if (!lastResult) return;
    const text = [
      'ALO186 Yedek Güç Çözümü Ön Değerlendirmesi',
      'Birincil seçenek: ' + lastResult.primary.solution.label,
      'İkinci seçenek: ' + lastResult.secondary.solution.label,
      'Durum: ' + (lastResult.professional ? 'Profesyonel doğrulama gerekli' : 'Tüketici seviyesinde ön karşılaştırma'),
      'Not: Fiyat, stok, garanti veya kesin ürün uygunluğu içermez.'
    ].join('\n');
    navigator.clipboard.writeText(text).then(function () {
      $('copyBtn').textContent = 'Kopyalandı';
      setTimeout(function () { $('copyBtn').textContent = 'Özeti kopyala'; }, 1800);
      track('backup_solution_summary_copied', { primary: lastResult.primary.key });
    }).catch(function () {});
  });

  $('printBtn').addEventListener('click', function () {
    track('backup_solution_printed', { primary: lastResult ? lastResult.primary.key : 'unknown' });
    window.print();
  });

  restoreBtn.hidden = !load();
})();
