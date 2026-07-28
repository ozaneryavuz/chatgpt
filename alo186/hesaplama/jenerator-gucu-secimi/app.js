(function () {
  'use strict';

  const core = window.ALO186GeneratorSizing;
  if (!core) return;

  const state = { loads: [], nextId: 1 };
  const $ = function (id) { return document.getElementById(id); };

  function escapeHtml(value) {
    return String(value == null ? '' : value).replace(/[&<>"']/g, function (char) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char];
    });
  }

  function emit(name, params) {
    if (typeof window.Alo186Track === 'function') window.Alo186Track(name, params || {});
  }

  function addLoad(source) {
    const preset = source || { name: 'Özel cihaz', runningW: 100, startingW: 100, motor: false };
    state.loads.push({
      id: 'load-' + state.nextId++,
      name: preset.name,
      runningW: preset.runningW,
      startingW: preset.startingW,
      quantity: 1,
      motor: Boolean(preset.motor)
    });
    renderLoads();
    $('loadStatus').textContent = preset.name + ' listeye eklendi.';
  }

  function removeLoad(id) {
    state.loads = state.loads.filter(function (load) { return load.id !== id; });
    renderLoads();
    $('loadStatus').textContent = 'Yük listeden kaldırıldı.';
  }

  function updateLoad(id, field, value) {
    const load = state.loads.find(function (item) { return item.id === id; });
    if (!load) return;
    if (field === 'name') load.name = value;
    else if (field === 'motor') load.motor = Boolean(value);
    else load[field] = Number(value);
  }

  function renderPresets() {
    $('presetGrid').innerHTML = core.PRESETS.map(function (preset) {
      return '<button type="button" class="preset" data-preset="' + escapeHtml(preset.id) + '"><strong>' +
        escapeHtml(preset.name) + '</strong><span>' + core.formatWatts(preset.runningW) +
        (preset.startingW > preset.runningW ? ' · kalkış ' + core.formatWatts(preset.startingW) : '') + '</span></button>';
    }).join('');

    $('presetGrid').querySelectorAll('[data-preset]').forEach(function (button) {
      button.addEventListener('click', function () {
        const preset = core.PRESETS.find(function (item) { return item.id === button.dataset.preset; });
        if (preset) addLoad(preset);
      });
    });
  }

  function renderLoads() {
    const body = $('loadRows');
    if (!state.loads.length) {
      body.innerHTML = '<tr><td colspan="6" class="empty-row">Henüz yük eklenmedi. Hazır cihazlardan birini veya “Özel cihaz ekle” seçeneğini kullanın.</td></tr>';
      return;
    }

    body.innerHTML = state.loads.map(function (load) {
      return '<tr data-load="' + escapeHtml(load.id) + '">' +
        '<td><label class="sr-only" for="name-' + escapeHtml(load.id) + '">Cihaz adı</label><input id="name-' + escapeHtml(load.id) + '" data-field="name" value="' + escapeHtml(load.name) + '" maxlength="80"></td>' +
        '<td><label class="sr-only" for="qty-' + escapeHtml(load.id) + '">Adet</label><input id="qty-' + escapeHtml(load.id) + '" data-field="quantity" type="number" inputmode="numeric" min="1" max="20" step="1" value="' + load.quantity + '"></td>' +
        '<td><label class="sr-only" for="run-' + escapeHtml(load.id) + '">Sürekli güç watt</label><input id="run-' + escapeHtml(load.id) + '" data-field="runningW" type="number" inputmode="decimal" min="1" max="50000" step="1" value="' + load.runningW + '"></td>' +
        '<td><label class="sr-only" for="start-' + escapeHtml(load.id) + '">Kalkış veya tepe gücü watt</label><input id="start-' + escapeHtml(load.id) + '" data-field="startingW" type="number" inputmode="decimal" min="1" max="150000" step="1" value="' + load.startingW + '"></td>' +
        '<td><label class="motor-check"><input data-field="motor" type="checkbox"' + (load.motor ? ' checked' : '') + '><span>Var</span></label></td>' +
        '<td><button type="button" class="remove-load" data-remove="' + escapeHtml(load.id) + '" aria-label="' + escapeHtml(load.name) + ' yükünü kaldır">Kaldır</button></td>' +
        '</tr>';
    }).join('');

    body.querySelectorAll('tr[data-load]').forEach(function (row) {
      const id = row.dataset.load;
      row.querySelectorAll('[data-field]').forEach(function (input) {
        input.addEventListener('input', function () {
          updateLoad(id, input.dataset.field, input.type === 'checkbox' ? input.checked : input.value);
        });
      });
    });
    body.querySelectorAll('[data-remove]').forEach(function (button) {
      button.addEventListener('click', function () { removeLoad(button.dataset.remove); });
    });
  }

  function optionsFromForm() {
    return {
      connection: $('connection').value,
      phase: $('phase').value,
      startPolicy: $('startPolicy').value,
      reservePct: Number($('reservePct').value),
      powerFactor: Number($('powerFactor').value),
      medical: $('medical').checked
    };
  }

  function listMarkup(items) {
    return items.map(function (item) { return '<li>' + escapeHtml(item) + '</li>'; }).join('');
  }

  function renderResult(result) {
    $('runningTotal').textContent = core.formatWatts(result.runningW);
    $('peakTotal').textContent = core.formatWatts(result.peakW);
    $('recommendedRunning').textContent = core.formatWatts(result.recommendedRunningW);
    $('recommendedStarting').textContent = core.formatWatts(result.recommendedStartingW);
    $('approximateKva').textContent = result.approximateKva.toLocaleString('tr-TR') + ' kVA';
    $('bandLabel').textContent = result.band.label;
    $('bandNote').textContent = result.band.note;

    const assumptions = [
      'Kapasite rezervi: %' + result.options.reservePct.toLocaleString('tr-TR'),
      'kVA gösterimi için güç faktörü varsayımı: ' + result.options.powerFactor.toLocaleString('tr-TR'),
      result.options.startPolicy === 'simultaneous' ? 'Motorların aynı anda kalkabileceği varsayıldı.' : 'En ağır tek motor kalkışı varsayıldı.',
      result.motorLoadCount + ' motor/kompresör yükü işaretlendi.'
    ];
    $('assumptionList').innerHTML = listMarkup(assumptions);
    $('warningList').innerHTML = listMarkup(result.warnings);

    const professional = $('professionalResult');
    const product = $('productResult');
    professional.classList.toggle('hidden', result.productRouteAllowed);
    product.classList.toggle('hidden', !result.productRouteAllowed);
    if (!result.productRouteAllowed) {
      $('professionalReasons').innerHTML = listMarkup(result.professionalReasons);
    }

    $('results').classList.remove('hidden');
    $('results').focus();
    $('results').scrollIntoView({ behavior: 'smooth', block: 'start' });
    emit('generator_sizing_completed', {
      load_count: result.loads.length,
      running_band: result.band.key,
      product_route_allowed: result.productRouteAllowed,
      connection: result.options.connection,
      phase: result.options.phase,
      medical: result.options.medical
    });
  }

  function calculate(event) {
    event.preventDefault();
    $('validation').textContent = '';
    try {
      const result = core.calculate(state.loads, optionsFromForm());
      renderResult(result);
    } catch (error) {
      $('validation').textContent = error.message;
      $('validation').focus();
    }
  }

  function resetAll() {
    state.loads = [];
    $('generatorForm').reset();
    $('reservePct').value = '20';
    $('powerFactor').value = '0.8';
    $('results').classList.add('hidden');
    $('validation').textContent = '';
    renderLoads();
    $('arac').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function init() {
    renderPresets();
    addLoad(core.PRESETS[0]);
    addLoad(core.PRESETS[1]);
    addLoad(core.PRESETS[2]);
    $('loadStatus').textContent = 'Örnek temel yükler eklendi; değerleri cihaz etiketinize göre düzenleyin.';
    $('addCustomBtn').addEventListener('click', function () { addLoad(); });
    $('generatorForm').addEventListener('submit', calculate);
    $('resetBtn').addEventListener('click', resetAll);
    const productLink = $('productGuideLink');
    productLink.href = productLink.href + '&hesaplandi=1';
    productLink.addEventListener('click', function () {
      emit('generator_product_route_opened', { category: 'generator', placement: 'generator_sizing_result' });
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();