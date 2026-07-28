(function () {
  'use strict';

  const core = window.ALO186InverterSuitability;
  if (!core) return;
  const $ = function (id) { return document.getElementById(id); };
  let loads = [];
  let lastResult = null;

  function escapeHtml(value) {
    return String(value == null ? '' : value).replace(/[&<>"']/g, function (char) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char];
    });
  }

  function emit(name, params) {
    if (typeof window.Alo186Track === 'function') window.Alo186Track(name, params || {});
  }

  function setAffiliateEnabled(enabled) {
    const link = $('productGuideLink');
    link.setAttribute('aria-disabled', enabled ? 'false' : 'true');
    link.tabIndex = enabled ? 0 : -1;
    link.classList.toggle('is-disabled', !enabled);
  }

  function addLoad(preset) {
    loads.push({
      name: preset.name,
      quantity: 1,
      runningW: preset.runningW,
      surgeW: preset.surgeW,
      loadType: preset.loadType
    });
    renderLoads();
  }

  function renderPresets() {
    $('presetGrid').innerHTML = core.PRESETS.map(function (preset) {
      return '<button class="preset-btn" type="button" data-preset="' + escapeHtml(preset.key) + '"><strong>' + escapeHtml(preset.name) + '</strong><small>' + preset.runningW + ' W · tepe ' + preset.surgeW + ' W</small></button>';
    }).join('');
  }

  function renderLoads() {
    $('loadRows').innerHTML = loads.map(function (load, index) {
      return '<tr data-index="' + index + '">' +
        '<td><input class="row-name" aria-label="Cihaz adı" maxlength="80" value="' + escapeHtml(load.name) + '"></td>' +
        '<td><input class="row-quantity" aria-label="Adet" type="number" min="1" max="50" step="1" value="' + load.quantity + '"></td>' +
        '<td><input class="row-running" aria-label="Sürekli watt" type="number" min="1" max="20000" step="1" value="' + load.runningW + '"></td>' +
        '<td><input class="row-surge" aria-label="Tepe watt" type="number" min="1" max="60000" step="1" value="' + load.surgeW + '"></td>' +
        '<td><select class="row-type" aria-label="Yük türü"><option value="standard"' + (load.loadType === 'standard' ? ' selected' : '') + '>Standart</option><option value="sensitive"' + (load.loadType === 'sensitive' ? ' selected' : '') + '>Hassas / elektronik</option><option value="motor"' + (load.loadType === 'motor' ? ' selected' : '') + '>Motor / kompresör</option><option value="resistive"' + (load.loadType === 'resistive' ? ' selected' : '') + '>Rezistif</option></select></td>' +
        '<td><button class="remove-btn" type="button" aria-label="' + escapeHtml(load.name) + ' yükünü kaldır">Kaldır</button></td>' +
        '</tr>';
    }).join('');
    $('loadStatus').textContent = loads.length ? loads.length + ' yük eklendi.' : 'Henüz yük eklenmedi.';
  }

  function syncLoads() {
    loads = Array.from($('loadRows').querySelectorAll('tr')).map(function (row) {
      return {
        name: row.querySelector('.row-name').value,
        quantity: Number(row.querySelector('.row-quantity').value),
        runningW: Number(row.querySelector('.row-running').value),
        surgeW: Number(row.querySelector('.row-surge').value),
        loadType: row.querySelector('.row-type').value
      };
    });
  }

  function values() {
    syncLoads();
    return {
      loads,
      dcVoltage: Number($('dcVoltage').value),
      batteryAh: Number($('batteryAh').value),
      desiredHours: Number($('desiredHours').value),
      efficiencyPct: Number($('efficiencyPct').value),
      reservePct: Number($('reservePct').value),
      chemistry: $('chemistry').value,
      depthOfDischargePct: Number($('depthOfDischargePct').value),
      startPolicy: $('startPolicy').value,
      usage: $('usage').value,
      bms: $('bms').value,
      dcProtection: $('dcProtection').value,
      medical: $('medical').checked
    };
  }

  function list(target, items) {
    $(target).innerHTML = items.map(function (item) { return '<li>' + escapeHtml(item) + '</li>'; }).join('');
  }

  function renderResult(result) {
    lastResult = result;
    $('bandLabel').textContent = result.band.label;
    $('bandNote').textContent = result.band.note;
    $('runningTotal').textContent = core.formatW(result.totals.runningW);
    $('peakTotal').textContent = core.formatW(result.totals.peakW);
    $('recommendedContinuous').textContent = core.formatW(result.recommendedContinuousW);
    $('recommendedSurge').textContent = core.formatW(result.recommendedSurgeW);
    $('dcCurrent').textContent = core.formatA(result.dcCurrentAtRecommendedA);
    $('runtime').textContent = core.formatHours(result.estimatedRuntimeHours);
    $('requiredBattery').textContent = result.requiredBatteryAh.toLocaleString('tr-TR') + ' Ah';
    $('usableEnergy').textContent = result.usableAcWh.toLocaleString('tr-TR') + ' Wh';

    $('waveformStatus').textContent = result.waveform === 'pure-sine-required' ? 'Saf sinüs gerekli' : 'Saf sinüs tercih edilmeli';
    $('waveformStatus').className = 'status ' + (result.waveform === 'pure-sine-required' ? 'danger-status' : 'warn');
    list('assumptionList', [
      'Toplam sürekli yük: ' + core.formatW(result.totals.runningW) + '.',
      'Seçilen kalkış senaryosu: ' + (result.options.startPolicy === 'simultaneous' ? 'motorlar eşzamanlı kalkabilir' : 'en ağır tek kalkış') + '.',
      'Kapasite rezervi: %' + result.options.reservePct + '.',
      'İnverter verimi varsayımı: %' + result.options.efficiencyPct + '.',
      'Batarya kullanılabilirlik varsayımı: %' + result.options.depthOfDischargePct + '.',
      'Hedef süre: ' + result.options.desiredHours.toLocaleString('tr-TR') + ' saat; mevcut batarya tahmini ' + core.formatHours(result.estimatedRuntimeHours) + '.'
    ]);
    list('warningList', result.warnings.concat(result.pureSineReasons));

    $('runtimeStatus').textContent = result.runtimeMeetsTarget
      ? 'Girilen batarya hedef süreyi teorik olarak karşılıyor.'
      : 'Girilen batarya hedef sürenin altında kalıyor; yaklaşık ' + result.requiredBatteryAh.toLocaleString('tr-TR') + ' Ah kullanılabilir tasarım hesabı gerekir.';
    $('runtimeStatus').className = result.runtimeMeetsTarget ? 'info success-note' : 'warning';

    $('productResult').classList.toggle('hidden', result.route !== 'product-guide');
    $('professionalResult').classList.toggle('hidden', result.route !== 'professional');
    if (result.route === 'professional') list('professionalReasons', result.professionalReasons);
    $('affiliateConfirm').checked = false;
    setAffiliateEnabled(false);

    $('results').classList.remove('hidden');
    $('results').focus();
    emit('inverter_suitability_calculated', {
      band: result.band.key,
      route: result.route,
      waveform: result.waveform,
      dc_voltage: result.options.dcVoltage,
      runtime_met: result.runtimeMeetsTarget
    });
  }

  function reset() {
    loads = [];
    $('inverterForm').reset();
    $('depthOfDischargePct').value = 50;
    $('bms').disabled = true;
    $('bms').value = 'not-applicable';
    $('results').classList.add('hidden');
    $('validation').textContent = '';
    $('affiliateConfirm').checked = false;
    setAffiliateEnabled(false);
    renderLoads();
  }

  renderPresets();
  renderLoads();
  setAffiliateEnabled(false);

  $('presetGrid').addEventListener('click', function (event) {
    const button = event.target.closest('[data-preset]');
    if (!button) return;
    const preset = core.PRESETS.find(function (item) { return item.key === button.dataset.preset; });
    if (preset) addLoad(preset);
  });

  $('addCustomBtn').addEventListener('click', function () {
    addLoad({ name: 'Özel cihaz', runningW: 100, surgeW: 100, loadType: 'standard' });
  });

  $('loadRows').addEventListener('click', function (event) {
    const button = event.target.closest('.remove-btn');
    if (!button) return;
    const row = button.closest('tr');
    loads.splice(Number(row.dataset.index), 1);
    renderLoads();
  });

  $('chemistry').addEventListener('change', function () {
    const lithium = $('chemistry').value === 'lithium';
    $('depthOfDischargePct').value = lithium ? 80 : 50;
    $('bms').disabled = !lithium;
    $('bms').value = lithium ? 'unknown' : 'not-applicable';
  });

  $('inverterForm').addEventListener('submit', function (event) {
    event.preventDefault();
    try {
      $('validation').textContent = '';
      renderResult(core.calculate(values()));
    } catch (error) {
      $('validation').textContent = error.message;
      $('validation').focus();
    }
  });

  $('resetBtn').addEventListener('click', reset);
  $('affiliateConfirm').addEventListener('change', function () {
    setAffiliateEnabled(this.checked && lastResult && lastResult.route === 'product-guide');
    if (this.checked) emit('inverter_affiliate_checklist_acknowledged', { source: 'inverter_suitability' });
  });
  $('productGuideLink').addEventListener('click', function (event) {
    if (this.getAttribute('aria-disabled') === 'true') {
      event.preventDefault();
      return;
    }
    emit('inverter_product_route_opened', {
      band: lastResult ? lastResult.band.key : 'unknown',
      source: 'inverter_suitability'
    });
  });
  $('professionalLink').addEventListener('click', function () {
    emit('inverter_professional_route_opened', { source: 'inverter_suitability' });
  });
})();