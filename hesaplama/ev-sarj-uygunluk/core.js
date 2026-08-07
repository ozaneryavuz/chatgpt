(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.ALO186EVSuitability = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const LEVELS = Object.freeze([
    { key: 'portable-10a', label: '2,3 kW kontrollü priz tipi', powerKw: 2.3, phase: 'single', currentA: 10, productClass: 'portable' },
    { key: 'ac-3-7', label: '3,7 kW AC wallbox', powerKw: 3.7, phase: 'single', currentA: 16, productClass: 'wallbox' },
    { key: 'ac-7-4', label: '7,4 kW AC wallbox', powerKw: 7.4, phase: 'single', currentA: 32, productClass: 'wallbox' },
    { key: 'ac-11', label: '11 kW AC wallbox', powerKw: 11, phase: 'three', currentA: 16, productClass: 'wallbox' },
    { key: 'ac-22', label: '22 kW AC wallbox', powerKw: 22, phase: 'three', currentA: 32, productClass: 'wallbox' }
  ]);

  function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
  }

  function number(value, fallback) {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : fallback;
  }

  function round(value, digits) {
    const factor = Math.pow(10, digits == null ? 1 : digits);
    return Math.round(value * factor) / factor;
  }

  function normalize(raw) {
    const source = raw || {};
    const phase = ['single', 'three', 'unknown'].includes(source.phase) ? source.phase : 'unknown';
    const mainCurrentA = number(source.mainCurrentA, NaN);
    const otherLoadKw = number(source.otherLoadKw, NaN);
    const reservePct = clamp(number(source.reservePct, 20), 0, 50);
    const vehicleMaxKw = number(source.vehicleMaxKw, NaN);
    const dailyKm = number(source.dailyKm, NaN);
    const consumptionKwh100 = number(source.consumptionKwh100, NaN);
    const availableHours = number(source.availableHours, NaN);
    const efficiencyPct = clamp(number(source.efficiencyPct, 90), 70, 100);
    const dedicatedCircuit = ['yes', 'no', 'unknown'].includes(source.dedicatedCircuit) ? source.dedicatedCircuit : 'unknown';
    const protection = ['verified', 'partial', 'unknown'].includes(source.protection) ? source.protection : 'unknown';
    const parking = ['private', 'common', 'workplace'].includes(source.parking) ? source.parking : 'private';
    const loadManagement = Boolean(source.loadManagement);

    if (!Number.isFinite(mainCurrentA) || mainCurrentA < 10 || mainCurrentA > 250) {
      throw new Error('Ana besleme akımını 10–250 A arasında girin. Değeri bilmiyorsanız pano etiketini yetkili elektrikçiye kontrol ettirin.');
    }
    if (!Number.isFinite(otherLoadKw) || otherLoadKw < 0 || otherLoadKw > 150) {
      throw new Error('Şarj dışındaki eşzamanlı yükü 0–150 kW arasında girin.');
    }
    if (!Number.isFinite(vehicleMaxKw) || vehicleMaxKw < 1 || vehicleMaxKw > 43) {
      throw new Error('Aracın azami AC şarj gücünü 1–43 kW arasında girin.');
    }
    if (!Number.isFinite(dailyKm) || dailyKm < 1 || dailyKm > 1000) {
      throw new Error('Günlük sürüşü 1–1.000 km arasında girin.');
    }
    if (!Number.isFinite(consumptionKwh100) || consumptionKwh100 < 5 || consumptionKwh100 > 80) {
      throw new Error('Araç tüketimini 5–80 kWh/100 km arasında girin.');
    }
    if (!Number.isFinite(availableHours) || availableHours < 1 || availableHours > 24) {
      throw new Error('Şarj için kullanılabilir süreyi 1–24 saat arasında girin.');
    }

    return {
      phase,
      mainCurrentA,
      otherLoadKw,
      reservePct,
      vehicleMaxKw,
      dailyKm,
      consumptionKwh100,
      availableHours,
      efficiencyPct,
      dedicatedCircuit,
      protection,
      parking,
      loadManagement
    };
  }

  function connectionPowerKw(phase, currentA) {
    if (phase === 'single') return 230 * currentA / 1000;
    if (phase === 'three') return Math.sqrt(3) * 400 * currentA / 1000;
    return 0;
  }

  function phaseCompatible(level, phase) {
    if (phase === 'unknown') return false;
    return level.phase === phase;
  }

  function selectHighest(levels) {
    return levels.length ? levels[levels.length - 1] : null;
  }

  function selectLowestMeeting(levels, requiredKw) {
    return levels.find(function (level) { return level.powerKw >= requiredKw; }) || selectHighest(levels);
  }

  function calculate(raw) {
    const options = normalize(raw);
    const connectionKw = connectionPowerKw(options.phase, options.mainCurrentA);
    const reserveKw = connectionKw * options.reservePct / 100;
    const staticSpareKw = Math.max(0, connectionKw - options.otherLoadKw - reserveKw);
    const dailyBatteryKwh = options.dailyKm * options.consumptionKwh100 / 100;
    const dailyGridKwh = dailyBatteryKwh / (options.efficiencyPct / 100);
    const averageRequiredKw = dailyGridKwh / options.availableHours;

    const phaseLevels = LEVELS.filter(function (level) {
      return phaseCompatible(level, options.phase) && level.powerKw <= options.vehicleMaxKw + 1e-9;
    });
    const staticLevels = phaseLevels.filter(function (level) {
      return level.powerKw <= staticSpareKw + 1e-9;
    });
    const managedCapacityKw = Math.max(0, connectionKw - reserveKw);
    const managedLevels = phaseLevels.filter(function (level) {
      return level.powerKw <= managedCapacityKw + 1e-9;
    });

    const staticMax = selectHighest(staticLevels);
    const managedMax = selectHighest(managedLevels);
    const dailyFitStatic = staticLevels.filter(function (level) { return level.powerKw >= averageRequiredKw - 1e-9; });
    const dailyFitManaged = managedLevels.filter(function (level) { return level.powerKw >= averageRequiredKw - 1e-9; });
    const recommendedStatic = dailyFitStatic.length ? selectLowestMeeting(dailyFitStatic, averageRequiredKw) : staticMax;
    const recommendedManaged = dailyFitManaged.length ? selectLowestMeeting(dailyFitManaged, averageRequiredKw) : managedMax;
    const staticMeetsDaily = Boolean(recommendedStatic && recommendedStatic.powerKw + 1e-9 >= averageRequiredKw);
    const selected = staticMeetsDaily
      ? recommendedStatic
      : (options.loadManagement && recommendedManaged ? recommendedManaged : recommendedStatic);

    let route = 'professional';
    const professionalReasons = [];
    if (options.phase === 'unknown') professionalReasons.push('Faz yapısı bilinmiyor; 7,4/11/22 kW sınıfı güvenle ayrılamaz.');
    if (options.dedicatedCircuit !== 'yes') professionalReasons.push('Şarj ünitesi için ayrı devre ve koruma düzeni doğrulanmamış.');
    if (options.protection !== 'verified') professionalReasons.push('RCD/RDC-DD ve devre koruması üretici ile proje verisine göre doğrulanmamış.');
    if (options.parking !== 'private') professionalReasons.push('Ortak veya işyeri otoparkında izin, ölçüm, yük paylaşımı ve işletme modeli birlikte değerlendirilmelidir.');
    if (!staticMax && !(options.loadManagement && managedMax)) professionalReasons.push('Girilen ana besleme ve eşzamanlı yükte standart bir AC şarj seviyesi için yeterli güç boşluğu görünmüyor.');

    if (professionalReasons.length === 0 && selected && selected.productClass === 'portable') route = 'portable-guide';
    else if (professionalReasons.length === 0 && selected) route = 'wallbox-guide';

    const achievableKw = selected ? selected.powerKw : Math.min(staticSpareKw, options.vehicleMaxKw);
    const estimatedDailyHours = achievableKw > 0 ? dailyGridKwh / achievableKw : null;
    const dailyNeedMet = Boolean(selected && selected.powerKw + 1e-9 >= averageRequiredKw);

    const warnings = [
      'Ana şalter akımı, sözleşme gücü ve kablo kapasitesi aynı kavram değildir; sonuç yetkili elektrikçi ve ilgili proje/dağıtım süreciyle doğrulanmalıdır.',
      'Araç ve şarj ünitesi gücü yüksek olsa bile gerçek şarj gücü araç, batarya durumu ve tesisat sınırları nedeniyle daha düşük olabilir.',
      'Sabit wallbox için ayrı devre, uygun otomatik koruma, RCD/RDC-DD, topraklama ve gerilim düşümü kontrolü gerekir.',
      'Dinamik yük yönetimi kapasite yaratmaz; bina yükü arttığında şarj gücünü sınırlayarak ana sınırın aşılmasını önlemeye yardımcı olur.'
    ];
    if (options.parking !== 'private') warnings.unshift('Apartman/site veya işyeri otoparkında teknik uygunluğa ek olarak malik/işletme kararı ve ilgili başvuru süreci gerekebilir.');

    return {
      options,
      connectionKw: round(connectionKw, 1),
      reserveKw: round(reserveKw, 1),
      staticSpareKw: round(staticSpareKw, 1),
      managedCapacityKw: round(managedCapacityKw, 1),
      dailyBatteryKwh: round(dailyBatteryKwh, 1),
      dailyGridKwh: round(dailyGridKwh, 1),
      averageRequiredKw: round(averageRequiredKw, 2),
      staticMax,
      managedMax,
      recommendedStatic,
      recommendedManaged,
      selected,
      achievableKw: round(achievableKw, 1),
      estimatedDailyHours: estimatedDailyHours == null ? null : round(estimatedDailyHours, 1),
      dailyNeedMet,
      route,
      professionalReasons,
      warnings
    };
  }

  function formatKw(value) {
    return Number(value).toLocaleString('tr-TR', { maximumFractionDigits: 2 }) + ' kW';
  }

  function formatKwh(value) {
    return Number(value).toLocaleString('tr-TR', { maximumFractionDigits: 1 }) + ' kWh';
  }

  return {
    LEVELS,
    clamp,
    normalize,
    connectionPowerKw,
    calculate,
    formatKw,
    formatKwh
  };
});