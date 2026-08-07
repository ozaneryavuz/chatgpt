(function () {
  'use strict';

  const core = window.ALO186EVSuitability;
  if (!core) return;
  const $ = function (id) { return document.getElementById(id); };
  let lastResult = null;

  function escapeHtml(value) {
    return String(value == null ? '' : value).replace(/[&<>"']/g, function (char) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char];
    });
  }

  function emit(name, params) {
    if (typeof window.Alo186Track === 'function') window.Alo186Track(name, params || {});
  }

  function values() {
    return {
      phase: $('phase').value,
      mainCurrentA: Number($('mainCurrentA').value),
      otherLoadKw: Number($('otherLoadKw').value),
      reservePct: Number($('reservePct').value),
      vehicleMaxKw: Number($('vehicleMaxKw').value),
      dailyKm: Number($('dailyKm').value),
      consumptionKwh100: Number($('consumptionKwh100').value),
      availableHours: Number($('availableHours').value),
      efficiencyPct: Number($('efficiencyPct').value),
      dedicatedCircuit: $('dedicatedCircuit').value,
      protection: $('protection').value,
      parking: $('parking').value,
      loadManagement: $('loadManagement').checked
    };
  }

  function list(items) {
    return items.map(function (item) { return '<li>' + escapeHtml(item) + '</li>'; }).join('');
  }

  function selectedText(result) {
    if (!result.selected) return 'Uygun standart güç sınıfı belirlenemedi';
    const managed = result.options.loadManagement && result.recommendedStatic !== result.selected;
    return result.selected.label + (managed ? ' · dinamik yönetimli' : '');
  }

  function levelStatus(level, result) {
    const phaseOk = result.options.phase !== 'unknown' && level.phase === result.options.phase;
    const vehicleOk = level.powerKw <= result.options.vehicleMaxKw + 1e-9;
    const staticOk = phaseOk && vehicleOk && level.powerKw <= result.staticSpareKw + 1e-9;
    const managedOk = phaseOk && vehicleOk && level.powerKw <= result.managedCapacityKw + 1e-9;
    const dailyOk = level.powerKw >= result.averageRequiredKw - 1e-9;
    let outcome = 'Uygun değil';
    let cls = 'bad';
    if (staticOk && dailyOk) { outcome = 'Statik güçle yeterli'; cls = 'ok'; }
    else if (staticOk) { outcome = 'Çalışabilir; günlük hedef uzayabilir'; cls = 'warn'; }
    else if (result.options.loadManagement && managedOk && dailyOk) { outcome = 'Yük yönetimiyle değerlendirilebilir'; cls = 'warn'; }
    else if (!phaseOk) outcome = level.phase === 'three' ? 'Trifaze gerekir' : 'Monofaze gerekir';
    else if (!vehicleOk) outcome = 'Araç bu AC gücü kabul etmiyor';
    else if (managedOk) outcome = 'Yük yönetimi olmadan uygun değil';
    else outcome = 'Ana kapasite sınırını aşar';
    return { vehicleOk, dailyOk, outcome, cls };
  }

  function renderComparison(result) {
    $('comparisonBody').innerHTML = core.LEVELS.map(function (level) {
      const status = levelStatus(level, result);
      return '<tr' + (result.selected && result.selected.key === level.key ? ' class="selected-row"' : '') + '>' +
        '<th scope="row">' + escapeHtml(level.label) + '</th>' +
        '<td>' + level.currentA + ' A' + (level.phase === 'three' ? '/faz' : '') + '</td>' +
        '<td>' + (status.vehicleOk ? 'Evet' : 'Hayır') + '</td>' +
        '<td>' + (status.dailyOk ? 'Evet' : 'Hayır') + '</td>' +
        '<td><span class="status ' + status.cls + '">' + escapeHtml(status.outcome) + '</span></td></tr>';
    }).join('');
  }

  function affiliateUrl(result) {
    const selected = result.selected;
    const query = selected && selected.productClass === 'portable'
      ? 'Type 2 taşınabilir elektrikli araç şarj cihazı 10A sıcaklık korumalı'
      : ((selected ? selected.powerKw.toLocaleString('tr-TR') + ' kW ' : '') + 'Type 2 wallbox 6mA RDC-DD dinamik yük yönetimi');
    return 'https://www.amazon.com.tr/s?k=' + encodeURIComponent(query) + '&tag=alo186hazirlik-21';
  }

  function renderProductRoute(result) {
    const affiliate = $('affiliateResult');
    const professional = $('professionalResult');
    const allow = result.route !== 'professional' && Boolean(result.selected);
    affiliate.classList.toggle('hidden', !allow);
    professional.classList.toggle('hidden', allow);

    if (allow) {
      $('selectionChecklist').innerHTML = list([
        'Araç üreticisinin azami AC gücü: ' + core.formatKw(result.options.vehicleMaxKw) + ' veya üzeri ürün gerektirmiyor.',
        'Şarj ünitesinin fazı ve nominal akımı seçilen ' + result.selected.label + ' sınıfıyla eşleşmeli.',
        'Ayrı devre, kablo kesiti, otomatik koruma ve gerilim düşümü yetkili elektrikçi tarafından projeye göre doğrulanmalı.',
        'Üründeki 6 mA DC kaçak algılama (RDC-DD) ile haricî RCD gereksinimi üretici dokümanından birlikte kontrol edilmeli.',
        result.options.loadManagement ? 'Dinamik yük yönetimi için uyumlu sayaç/sensör ve gerçek zamanlı güç sınırlama özelliği doğrulanmalı.' : 'Binanın eşzamanlı yükü değişebiliyorsa dinamik yük yönetimi seçeneği ayrıca değerlendirilmelidir.'
      ]);
      const link = $('affiliateLink');
      link.href = affiliateUrl(result);
      link.dataset.power = result.selected.key;
      $('affiliateConfirm').checked = false;
      link.classList.add('disabled-link');
      link.setAttribute('aria-disabled', 'true');
      link.tabIndex = -1;
    } else {
      $('professionalReasons').innerHTML = list(result.professionalReasons.length ? result.professionalReasons : ['Kurulum ve koruma bilgileri uzman tarafından doğrulanmalıdır.']);
    }
  }

  function render(result) {
    lastResult = result;
    $('connectionPower').textContent = core.formatKw(result.connectionKw);
    $('staticSpare').textContent = core.formatKw(result.staticSpareKw);
    $('dailyEnergy').textContent = core.formatKwh(result.dailyGridKwh);
    $('requiredAverage').textContent = core.formatKw(result.averageRequiredKw);
    $('recommendation').textContent = selectedText(result);
    $('estimatedTime').textContent = result.estimatedDailyHours == null ? '—' : result.estimatedDailyHours.toLocaleString('tr-TR') + ' saat/gün';
    $('needStatus').textContent = result.dailyNeedMet ? 'Günlük enerji hedefi karşılanabilir.' : 'Seçilebilen güçle günlük hedef süresi uzayabilir.';
    $('needStatus').className = 'status ' + (result.dailyNeedMet ? 'ok' : 'warn');

    const assumptions = [
      'Bağlantı üst sınırı yaklaşık ' + core.formatKw(result.connectionKw) + ' olarak, ' + result.options.mainCurrentA.toLocaleString('tr-TR') + ' A ve seçilen faz yapısından hesaplandı.',
      'Şarj dışı eşzamanlı yük: ' + core.formatKw(result.options.otherLoadKw) + '; kapasite rezervi: %' + result.options.reservePct.toLocaleString('tr-TR') + '.',
      'Günlük sürüş enerjisi ' + core.formatKwh(result.dailyBatteryKwh) + '; şebekeden çekilecek tahmini enerji ' + core.formatKwh(result.dailyGridKwh) + '.',
      'Şarj verimi varsayımı: %' + result.options.efficiencyPct.toLocaleString('tr-TR') + '; kullanılabilir süre: ' + result.options.availableHours.toLocaleString('tr-TR') + ' saat.'
    ];
    $('assumptionList').innerHTML = list(assumptions);
    $('warningList').innerHTML = list(result.warnings);
    renderComparison(result);
    renderProductRoute(result);
    $('results').classList.remove('hidden');
    $('results').focus();
    $('results').scrollIntoView({ behavior: 'smooth', block: 'start' });
    emit('ev_suitability_completed', {
      phase: result.options.phase,
      selected_level: result.selected ? result.selected.key : 'none',
      route: result.route,
      daily_need_met: result.dailyNeedMet,
      load_management: result.options.loadManagement,
      parking: result.options.parking
    });
  }

  function calculate(event) {
    event.preventDefault();
    $('validation').textContent = '';
    try {
      render(core.calculate(values()));
    } catch (error) {
      $('validation').textContent = error.message;
      $('validation').focus();
    }
  }

  function reset() {
    $('evSuitabilityForm').reset();
    $('mainCurrentA').value = '40';
    $('otherLoadKw').value = '3';
    $('reservePct').value = '20';
    $('vehicleMaxKw').value = '11';
    $('dailyKm').value = '50';
    $('consumptionKwh100').value = '18';
    $('availableHours').value = '10';
    $('efficiencyPct').value = '90';
    $('results').classList.add('hidden');
    $('validation').textContent = '';
    lastResult = null;
    $('arac').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function init() {
    $('evSuitabilityForm').addEventListener('submit', calculate);
    $('resetBtn').addEventListener('click', reset);
    $('affiliateConfirm').addEventListener('change', function () {
      const link = $('affiliateLink');
      const enabled = $('affiliateConfirm').checked;
      link.classList.toggle('disabled-link', !enabled);
      link.setAttribute('aria-disabled', enabled ? 'false' : 'true');
      link.tabIndex = enabled ? 0 : -1;
      emit('ev_affiliate_checklist_acknowledged', { acknowledged: enabled, selected_level: lastResult && lastResult.selected ? lastResult.selected.key : 'none' });
    });
    $('affiliateLink').addEventListener('click', function (event) {
      if ($('affiliateLink').getAttribute('aria-disabled') === 'true') { event.preventDefault(); return; }
      emit('ev_affiliate_search_opened', { selected_level: $('affiliateLink').dataset.power || 'unknown', placement: 'ev_suitability_result' });
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();