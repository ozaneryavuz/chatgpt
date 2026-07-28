(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.ALO186GeneratorSizing = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const PRESETS = Object.freeze([
    { id: 'internet', name: 'Modem + fiber ONT', runningW: 25, startingW: 25, motor: false },
    { id: 'lighting', name: 'LED aydınlatma grubu', runningW: 100, startingW: 100, motor: false },
    { id: 'refrigerator', name: 'Buzdolabı', runningW: 200, startingW: 1200, motor: true },
    { id: 'television', name: 'Televizyon', runningW: 120, startingW: 120, motor: false },
    { id: 'laptop', name: 'Dizüstü bilgisayar', runningW: 90, startingW: 90, motor: false },
    { id: 'boiler-pump', name: 'Kombi / sirkülasyon pompası', runningW: 120, startingW: 360, motor: true },
    { id: 'water-pump', name: 'Su pompası', runningW: 750, startingW: 2250, motor: true },
    { id: 'air-conditioner', name: '12.000 BTU klima', runningW: 1200, startingW: 3600, motor: true },
    { id: 'kettle', name: 'Su ısıtıcı / kettle', runningW: 1800, startingW: 1800, motor: false }
  ]);

  function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
  }

  function roundUp(value, step) {
    return Math.ceil(value / step) * step;
  }

  function asNumber(value, fallback) {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : fallback;
  }

  function normalizeOptions(raw) {
    const source = raw || {};
    const connection = ['appliances', 'selected-circuits', 'whole-building'].includes(source.connection)
      ? source.connection
      : 'appliances';
    const phase = ['single', 'three', 'unknown'].includes(source.phase) ? source.phase : 'single';
    const startPolicy = source.startPolicy === 'simultaneous' ? 'simultaneous' : 'largest';
    return {
      connection,
      phase,
      startPolicy,
      reservePct: clamp(asNumber(source.reservePct, 20), 0, 80),
      powerFactor: clamp(asNumber(source.powerFactor, 0.8), 0.5, 1),
      medical: Boolean(source.medical)
    };
  }

  function normalizeLoad(raw, index) {
    const source = raw || {};
    const runningW = asNumber(source.runningW, NaN);
    const startingW = asNumber(source.startingW, NaN);
    const quantity = Math.trunc(asNumber(source.quantity, 1));
    const name = String(source.name || ('Yük ' + (index + 1))).trim().slice(0, 80);

    if (!name) throw new Error((index + 1) + '. yük için cihaz adı girin.');
    if (!Number.isFinite(runningW) || runningW <= 0 || runningW > 50000) {
      throw new Error(name + ' için sürekli güç 1–50.000 W arasında olmalıdır.');
    }
    if (!Number.isFinite(startingW) || startingW < runningW || startingW > 150000) {
      throw new Error(name + ' için kalkış/tepe gücü sürekli güçten küçük olamaz ve 150.000 W sınırını aşamaz.');
    }
    if (!Number.isInteger(quantity) || quantity < 1 || quantity > 20) {
      throw new Error(name + ' için adet 1–20 arasında tam sayı olmalıdır.');
    }

    return {
      id: String(source.id || ('load-' + (index + 1))),
      name,
      runningW,
      startingW,
      quantity,
      motor: Boolean(source.motor || startingW > runningW)
    };
  }

  function classifyBand(recommendedRunningW) {
    if (recommendedRunningW <= 2500) return {
      key: 'compact',
      label: 'Kompakt taşınabilir sınıf',
      note: 'Düşük güçlü temel cihazlar için inverter jeneratör kategorisi ön değerlendirilebilir.'
    };
    if (recommendedRunningW <= 5500) return {
      key: 'medium',
      label: 'Orta kapasiteli taşınabilir sınıf',
      note: 'Birden fazla temel yük ve sınırlı motorlu cihaz için orta kapasite sınıfı değerlendirilir.'
    };
    if (recommendedRunningW <= 7500) return {
      key: 'large-portable',
      label: 'Yüksek kapasiteli taşınabilir sınıf',
      note: 'Kablo, koruma, yakıt, gürültü ve kalkış gücü profesyonel olarak doğrulanmalıdır.'
    };
    return {
      key: 'professional',
      label: 'Sabit / profesyonel sistem',
      note: 'Bu güç seviyesi taşınabilir ürün karşılaştırmasından önce keşif, yük yönetimi ve proje gerektirir.'
    };
  }

  function calculate(rawLoads, rawOptions) {
    if (!Array.isArray(rawLoads) || rawLoads.length === 0) {
      throw new Error('En az bir cihaz veya yük ekleyin.');
    }

    const loads = rawLoads.map(normalizeLoad);
    const options = normalizeOptions(rawOptions);
    const runningW = loads.reduce(function (total, load) {
      return total + load.runningW * load.quantity;
    }, 0);

    const surgeExtras = loads.map(function (load) {
      return (load.startingW - load.runningW) * (options.startPolicy === 'simultaneous' ? load.quantity : 1);
    });
    const surgeExtraW = options.startPolicy === 'simultaneous'
      ? surgeExtras.reduce(function (total, value) { return total + value; }, 0)
      : Math.max.apply(null, surgeExtras);
    const peakW = runningW + surgeExtraW;
    const reserveFactor = 1 + options.reservePct / 100;
    const recommendedRunningW = roundUp(runningW * reserveFactor, 100);
    const recommendedStartingW = roundUp(peakW * reserveFactor, 100);
    const approximateKva = Math.ceil((recommendedRunningW / (options.powerFactor * 1000)) * 10) / 10;
    const band = classifyBand(recommendedRunningW);
    const motorLoads = loads.filter(function (load) { return load.motor; });

    const professionalReasons = [];
    if (options.connection !== 'appliances') professionalReasons.push('Bina panosu veya seçili devre bağlantısı transfer sistemi ve yetkili elektrikçi gerektirir.');
    if (options.phase !== 'single') professionalReasons.push('Üç faz veya bilinmeyen faz yapısında faz dengesi, nötr ve motor kalkışı projelendirilmelidir.');
    if (options.medical) professionalReasons.push('Tıbbi veya yaşam destek yüklerinde ürün yönlendirmesi yapılmaz; üretici ve yetkili uzman doğrulaması gerekir.');
    if (recommendedRunningW > 7500 || recommendedStartingW > 10000) professionalReasons.push('Hesaplanan güç taşınabilir tüketici sınıfının üzerinde veya sınırındadır.');
    if (motorLoads.some(function (load) { return load.runningW >= 1500 || load.startingW >= 5000; })) {
      professionalReasons.push('Yüksek kalkış gücüne sahip motor/kompresör bulunuyor.');
    }

    const productRouteAllowed = professionalReasons.length === 0;
    const warnings = [
      'Etiket ve üretici dokümanındaki sürekli W ile kalkış/tepe W değerlerini satın alma öncesi yeniden doğrulayın.',
      'Rakım, sıcaklık, yakıt türü, harmonikli yükler ve aynı anda devreye giren motorlar gerçek kapasiteyi etkileyebilir.',
      'Jeneratörü bina prizine ters besleme amacıyla bağlamayın; bina devreleri için uygun transfer ekipmanı yetkili elektrikçi tarafından kurulmalıdır.',
      'Yakıtlı taşınabilir jeneratörü yalnız açık havada, kapı, pencere ve havalandırma açıklıklarından en az yaklaşık 6 metre uzakta çalıştırın; içeride veya garajda kullanmayın.'
    ];
    if (options.medical) warnings.unshift('Tıbbi/yaşam destek cihazında bu sonuç ürün seçimi değildir; cihaz üreticisi, sağlık hizmeti sağlayıcısı ve yetkili elektrik uzmanıyla acil durum planı oluşturun.');

    return {
      loads,
      options,
      runningW,
      surgeExtraW,
      peakW,
      recommendedRunningW,
      recommendedStartingW,
      approximateKva,
      band,
      motorLoadCount: motorLoads.length,
      professionalReasons,
      productRouteAllowed,
      warnings
    };
  }

  function formatWatts(value) {
    return Math.round(value).toLocaleString('tr-TR') + ' W';
  }

  return {
    PRESETS,
    clamp,
    roundUp,
    normalizeOptions,
    normalizeLoad,
    classifyBand,
    calculate,
    formatWatts
  };
});
