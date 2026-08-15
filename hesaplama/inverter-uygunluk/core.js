(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.ALO186InverterSuitability = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const PRESETS = Object.freeze([
    { key: 'modem', name: 'Modem + fiber ONT', runningW: 25, surgeW: 25, loadType: 'sensitive' },
    { key: 'laptop', name: 'Dizüstü bilgisayar', runningW: 90, surgeW: 120, loadType: 'sensitive' },
    { key: 'tv', name: 'Televizyon', runningW: 120, surgeW: 180, loadType: 'sensitive' },
    { key: 'fridge', name: 'Buzdolabı', runningW: 150, surgeW: 800, loadType: 'motor' },
    { key: 'boiler', name: 'Kombi / sirkülasyon pompası', runningW: 120, surgeW: 350, loadType: 'motor' },
    { key: 'coffee', name: 'Kahve makinesi / rezistans', runningW: 1200, surgeW: 1200, loadType: 'resistive' },
    { key: 'pump', name: 'Su pompası', runningW: 750, surgeW: 2200, loadType: 'motor' }
  ]);

  function number(value, fallback) {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : fallback;
  }

  function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
  }

  function round(value, digits) {
    const factor = Math.pow(10, digits == null ? 1 : digits);
    return Math.round(value * factor) / factor;
  }

  function normalizeLoad(raw, index) {
    const source = raw || {};
    const runningW = number(source.runningW, NaN);
    const surgeW = number(source.surgeW, runningW);
    const quantity = number(source.quantity, 1);
    const loadType = ['resistive', 'standard', 'sensitive', 'motor'].includes(source.loadType)
      ? source.loadType
      : 'standard';

    if (!Number.isFinite(runningW) || runningW <= 0 || runningW > 20000) {
      throw new Error((source.name || (index + 1) + '. yük') + ' için sürekli gücü 1–20.000 W arasında girin.');
    }
    if (!Number.isFinite(surgeW) || surgeW < runningW || surgeW > 60000) {
      throw new Error((source.name || (index + 1) + '. yük') + ' için tepe gücü sürekli güçten düşük olmayacak şekilde 60.000 W altında girin.');
    }
    if (!Number.isFinite(quantity) || quantity < 1 || quantity > 50 || Math.floor(quantity) !== quantity) {
      throw new Error((source.name || (index + 1) + '. yük') + ' için adedi 1–50 arasında tam sayı girin.');
    }

    return {
      name: String(source.name || 'Özel cihaz').slice(0, 80),
      runningW,
      surgeW,
      quantity,
      loadType
    };
  }

  function defaultDod(chemistry) {
    return chemistry === 'lithium' ? 80 : 50;
  }

  function normalize(raw) {
    const source = raw || {};
    const loads = Array.isArray(source.loads) ? source.loads.map(normalizeLoad) : [];
    if (!loads.length) throw new Error('En az bir cihaz ekleyin.');

    const dcVoltage = number(source.dcVoltage, NaN);
    const batteryAh = number(source.batteryAh, NaN);
    const desiredHours = number(source.desiredHours, NaN);
    const efficiencyPct = clamp(number(source.efficiencyPct, 90), 70, 97);
    const reservePct = clamp(number(source.reservePct, 20), 0, 80);
    const chemistry = ['lead', 'lithium'].includes(source.chemistry) ? source.chemistry : 'lead';
    const depthOfDischargePct = clamp(number(source.depthOfDischargePct, defaultDod(chemistry)), 10, 95);
    const startPolicy = source.startPolicy === 'simultaneous' ? 'simultaneous' : 'largest';
    const usage = ['portable', 'vehicle', 'fixed', 'hybrid'].includes(source.usage) ? source.usage : 'portable';
    const bms = ['verified', 'unknown', 'not-applicable'].includes(source.bms) ? source.bms : 'unknown';
    const dcProtection = ['verified', 'unknown'].includes(source.dcProtection) ? source.dcProtection : 'unknown';
    const medical = Boolean(source.medical);

    if (![12, 24, 48].includes(dcVoltage)) throw new Error('DC sistem gerilimini 12, 24 veya 48 V seçin.');
    if (!Number.isFinite(batteryAh) || batteryAh < 1 || batteryAh > 5000) throw new Error('Batarya kapasitesini 1–5.000 Ah arasında girin.');
    if (!Number.isFinite(desiredHours) || desiredHours < 0.1 || desiredHours > 168) throw new Error('Hedef çalışma süresini 0,1–168 saat arasında girin.');

    return {
      loads,
      dcVoltage,
      batteryAh,
      desiredHours,
      efficiencyPct,
      reservePct,
      chemistry,
      depthOfDischargePct,
      startPolicy,
      usage,
      bms,
      dcProtection,
      medical
    };
  }

  function calculateTotals(loads, startPolicy) {
    const runningW = loads.reduce(function (sum, load) {
      return sum + load.runningW * load.quantity;
    }, 0);

    const extraSurges = loads.map(function (load) {
      const singleUnitExtra = Math.max(0, load.surgeW - load.runningW);
      return startPolicy === 'simultaneous'
        ? singleUnitExtra * load.quantity
        : singleUnitExtra;
    });
    const extraSurgeW = startPolicy === 'simultaneous'
      ? extraSurges.reduce(function (sum, value) { return sum + value; }, 0)
      : Math.max.apply(Math, [0].concat(extraSurges));

    return { runningW, peakW: runningW + extraSurgeW, extraSurgeW };
  }

  function inverterBand(recommendedContinuousW) {
    if (recommendedContinuousW <= 600) return { key: 'compact', label: '300–600 W saf sinüs sınıfı', note: 'Düşük güçlü taşınabilir elektronik yükler.' };
    if (recommendedContinuousW <= 1200) return { key: 'medium', label: '800–1.200 W saf sinüs sınıfı', note: 'Orta güçlü taşınabilir sistem; DC akımı ve kablo kesiti kritikleşir.' };
    if (recommendedContinuousW <= 2000) return { key: 'high', label: '1.500–2.000 W saf sinüs sınıfı', note: 'Yüksek DC akımı nedeniyle profesyonel kablo, sigorta ve bağlantı doğrulaması gerekir.' };
    return { key: 'professional', label: '2 kW üzeri profesyonel sistem', note: 'Sabit bağlantı, yüksek akım ve sistem tasarımı birlikte değerlendirilmelidir.' };
  }

  function calculate(raw) {
    const options = normalize(raw);
    const totals = calculateTotals(options.loads, options.startPolicy);
    const reserveFactor = 1 + options.reservePct / 100;
    const recommendedContinuousW = Math.ceil(totals.runningW * reserveFactor / 50) * 50;
    const recommendedSurgeW = Math.ceil(totals.peakW * reserveFactor / 50) * 50;
    const efficiency = options.efficiencyPct / 100;
    const dod = options.depthOfDischargePct / 100;
    const nominalBatteryWh = options.dcVoltage * options.batteryAh;
    const usableAcWh = nominalBatteryWh * dod * efficiency;
    const estimatedRuntimeHours = usableAcWh / totals.runningW;
    const requiredBatteryAh = totals.runningW * options.desiredHours / (options.dcVoltage * dod * efficiency);
    const dcCurrentAtRunningA = totals.runningW / (options.dcVoltage * efficiency);
    const dcCurrentAtRecommendedA = recommendedContinuousW / (options.dcVoltage * efficiency);
    const peakDcCurrentA = recommendedSurgeW / (options.dcVoltage * efficiency);

    const pureSineReasons = [];
    if (options.loads.some(function (load) { return load.loadType === 'sensitive'; })) {
      pureSineReasons.push('Bilgisayar, TV, modem veya kontrol kartı gibi hassas/aktif PFC içerebilen yük var.');
    }
    if (options.loads.some(function (load) { return load.loadType === 'motor'; })) {
      pureSineReasons.push('Motor veya kompresörlü yükte kalkış ve dalga şekli uyumu üretici verisiyle doğrulanmalıdır.');
    }
    const waveform = pureSineReasons.length ? 'pure-sine-required' : 'pure-sine-preferred';
    const band = inverterBand(recommendedContinuousW);

    const professionalReasons = [];
    if (options.medical) professionalReasons.push('Tıbbi veya yaşam destek cihazı için genel tüketici ürünü yönlendirmesi güvenli değildir.');
    if (options.usage !== 'portable') professionalReasons.push('Araç, sabit tesisat veya hibrit/GES bağlantısı; topraklama, nötr düzeni, transfer ve koruma tasarımı gerektirir.');
    if (recommendedContinuousW > 1200 || recommendedSurgeW > 3000) professionalReasons.push('Güç ve tepe akımı taşınabilir düşük riskli ürün sınırını aşıyor.');
    if (dcCurrentAtRecommendedA > 120) professionalReasons.push('Önerilen yükte DC akımı 120 A üzerinde; kablo, bağlantı ve aşırı akım koruması profesyonel doğrulanmalıdır.');
    if (options.dcProtection !== 'verified') professionalReasons.push('Batarya yakını DC sigorta/ayırma ve kablo koruması doğrulanmamış.');
    if (options.chemistry === 'lithium' && options.bms !== 'verified') professionalReasons.push('Lityum bataryanın BMS ve izin verilen sürekli/tepe deşarj akımı doğrulanmamış.');

    const route = professionalReasons.length === 0 ? 'product-guide' : 'professional';
    const runtimeMeetsTarget = estimatedRuntimeHours >= options.desiredHours;

    const warnings = [
      'İnverterin sürekli W ve kısa süreli tepe W değerleri ayrı ayrı yükünüzü karşılamalıdır; yalnız ürün adındaki VA/W değerine güvenmeyin.',
      'DC kablo kesiti ve sigorta değeri bu araçla seçilmez. Akım, kablo uzunluğu, sıcaklık, bağlantı biçimi ve üretici kılavuzu birlikte değerlendirilmelidir.',
      'İnverter çıkışını ev prizine geri beslemeyin. Sabit tesisat ve transfer bağlantıları yetkili elektrik uzmanına aittir.',
      'Batarya kapasitesi etiketi, izin verilen sürekli ve tepe deşarj akımını tek başına göstermez.'
    ];

    return {
      options,
      totals,
      recommendedContinuousW,
      recommendedSurgeW,
      nominalBatteryWh: round(nominalBatteryWh, 0),
      usableAcWh: round(usableAcWh, 0),
      estimatedRuntimeHours: round(estimatedRuntimeHours, 2),
      requiredBatteryAh: round(requiredBatteryAh, 0),
      dcCurrentAtRunningA: round(dcCurrentAtRunningA, 1),
      dcCurrentAtRecommendedA: round(dcCurrentAtRecommendedA, 1),
      peakDcCurrentA: round(peakDcCurrentA, 1),
      waveform,
      pureSineReasons,
      band,
      runtimeMeetsTarget,
      route,
      professionalReasons,
      warnings
    };
  }

  function formatW(value) {
    return Number(value).toLocaleString('tr-TR', { maximumFractionDigits: 0 }) + ' W';
  }

  function formatA(value) {
    return Number(value).toLocaleString('tr-TR', { maximumFractionDigits: 1 }) + ' A';
  }

  function formatHours(value) {
    return Number(value).toLocaleString('tr-TR', { maximumFractionDigits: 2 }) + ' saat';
  }

  return {
    PRESETS,
    normalize,
    calculateTotals,
    inverterBand,
    calculate,
    formatW,
    formatA,
    formatHours
  };
});
