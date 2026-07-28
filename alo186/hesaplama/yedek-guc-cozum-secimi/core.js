(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.ALO186BackupSolution = api;
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  const SOLUTIONS = {
    mini_ups: {
      label: 'Modem / ONT mini UPS',
      summary: 'Düşük güçlü internet ekipmanında kesintisiz ve sessiz yedekleme.',
      calculator: '/hesaplama/modem-internet-yedekleme/',
      category: 'mini_ups',
      commercial: true
    },
    online_ups: {
      label: 'Online UPS',
      summary: 'Kesintiye toleransı düşük hassas elektronik için sürekli çift dönüşümlü koruma.',
      calculator: '/hesaplama/yedek-guc',
      category: 'ups',
      commercial: true
    },
    line_interactive_ups: {
      label: 'Line-interactive UPS',
      summary: 'Kısa süreli elektronik yüklerde ekonomik kesinti köprüsü ve gerilim düzenleme.',
      calculator: '/hesaplama/yedek-guc',
      category: 'ups',
      commercial: true
    },
    power_station: {
      label: 'Taşınabilir güç istasyonu',
      summary: 'Yakıt ve sabit bağlantı istemeyen taşınabilir AC/DC enerji çözümü.',
      calculator: '/hesaplama/yedek-guc',
      category: 'power_station',
      commercial: true
    },
    inverter_battery: {
      label: 'İnverter + batarya sistemi',
      summary: 'Uzun süreli ve yeniden şarj edilebilir yedekleme; DC koruma ve sistem tasarımı gerekir.',
      calculator: '/hesaplama/inverter-uygunluk/',
      category: 'inverter',
      commercial: false
    },
    generator: {
      label: 'Jeneratör + uygun transfer düzeni',
      summary: 'Uzun süreli veya yüksek güçlü yükler için yakıtlı çözüm; yalnız açık hava ve güvenli transferle.',
      calculator: '/hesaplama/jenerator-gucu-secimi/',
      category: 'generator',
      commercial: false
    },
    hybrid: {
      label: 'UPS / batarya + jeneratör hibrit mimarisi',
      summary: 'Kesintisiz geçiş ile uzun çalışma süresini farklı katmanlarda birleştiren profesyonel çözüm.',
      calculator: '/isletme-surekliligi',
      category: null,
      commercial: false
    }
  };

  const POWER_WATTS = { p150: 150, p600: 600, p1500: 1500, p3000: 3000, high_unknown: 99999 };
  const DURATION_HOURS = { d2: 2, d6: 6, d12: 12, long: 24 };

  function validate(input) {
    const errors = [];
    ['context', 'loadProfile', 'powerBand', 'continuity', 'duration', 'installation', 'outdoorFuel'].forEach(function (key) {
      if (!input || !input[key]) errors.push(key + ' seçimi eksik.');
    });
    return errors;
  }

  function scoreSolutions(input) {
    const scores = {
      mini_ups: 0,
      online_ups: 0,
      line_interactive_ups: 0,
      power_station: 0,
      inverter_battery: 0,
      generator: 0,
      hybrid: 0
    };
    const reasons = [];
    const cautions = [];
    const watts = POWER_WATTS[input.powerBand];
    const hours = DURATION_HOURS[input.duration];

    if (input.loadProfile === 'internet') {
      scores.mini_ups += 8;
      scores.online_ups += 3;
      scores.line_interactive_ups += 3;
      scores.power_station += 2;
      reasons.push('Yük profili düşük güçlü modem ve ağ ekipmanına odaklanıyor.');
    }
    if (input.loadProfile === 'electronics') {
      scores.online_ups += 6;
      scores.line_interactive_ups += 5;
      scores.power_station += 3;
      scores.inverter_battery += 2;
      reasons.push('Hassas elektronik yüklerde geçiş davranışı ve dalga biçimi önemlidir.');
    }
    if (input.loadProfile === 'refrigeration') {
      scores.power_station += 2;
      scores.inverter_battery += 5;
      scores.generator += 4;
      scores.hybrid += 2;
      cautions.push('Kompresör kalkış gücü, ortalama watt değerinden ayrı doğrulanmalıdır.');
    }
    if (input.loadProfile === 'motor') {
      scores.inverter_battery += 3;
      scores.generator += 7;
      scores.hybrid += 5;
      scores.power_station -= 3;
      scores.line_interactive_ups -= 3;
      cautions.push('Pompa, klima ve motorlarda kalkış akımı nedeniyle profesyonel tepe güç hesabı gerekir.');
    }
    if (input.loadProfile === 'mixed') {
      scores.inverter_battery += 4;
      scores.generator += 5;
      scores.hybrid += 6;
      reasons.push('Karışık yük profili tek cihaz sınıfından çok katmanlı çözüm gerektirebilir.');
    }

    if (input.continuity === 'zero') {
      scores.online_ups += 9;
      scores.mini_ups += 5;
      scores.hybrid += 5;
      scores.power_station -= 4;
      scores.generator -= 5;
      reasons.push('Kesintisiz veya sıfıra yakın geçiş beklentisi UPS katmanını öne çıkarır.');
    } else if (input.continuity === 'seconds') {
      scores.line_interactive_ups += 5;
      scores.power_station += 2;
      scores.inverter_battery += 2;
    } else {
      scores.power_station += 3;
      scores.generator += 3;
      scores.inverter_battery += 2;
    }

    if (hours <= 2) {
      scores.mini_ups += 3;
      scores.online_ups += 3;
      scores.line_interactive_ups += 3;
      scores.power_station += 2;
    } else if (hours <= 6) {
      scores.power_station += 5;
      scores.inverter_battery += 4;
      scores.online_ups += 1;
    } else if (hours <= 12) {
      scores.power_station += 3;
      scores.inverter_battery += 7;
      scores.generator += 4;
      scores.hybrid += 3;
    } else {
      scores.generator += 9;
      scores.inverter_battery += 4;
      scores.hybrid += 7;
      scores.online_ups -= 3;
      scores.line_interactive_ups -= 3;
      reasons.push('Uzun hedef süre, enerji kapasitesi ve yeniden yakıt/şarj planını belirleyici yapar.');
    }

    if (watts <= 150) {
      scores.mini_ups += 5;
      scores.power_station += 2;
    } else if (watts <= 600) {
      scores.online_ups += 3;
      scores.line_interactive_ups += 3;
      scores.power_station += 4;
    } else if (watts <= 1500) {
      scores.power_station += 4;
      scores.inverter_battery += 4;
      scores.generator += 2;
    } else if (watts <= 3000) {
      scores.inverter_battery += 5;
      scores.generator += 6;
      scores.hybrid += 4;
      scores.mini_ups -= 10;
    }

    if (input.installation === 'portable') {
      scores.power_station += 6;
      scores.mini_ups += 2;
      scores.generator += input.outdoorFuel === 'yes' ? 2 : -7;
    } else if (input.installation === 'selected') {
      scores.inverter_battery += 5;
      scores.generator += 4;
      scores.hybrid += 4;
      cautions.push('Seçili bina devrelerinin beslenmesi sabit tesisat ve ayırma/transfer tasarımı gerektirir.');
    } else {
      scores.generator += 7;
      scores.hybrid += 8;
      scores.inverter_battery += 4;
      cautions.push('Bütün bina beslemesi tüketici ürünü seçimi değil, proje ve yük yönetimi işidir.');
    }

    if (input.outdoorFuel === 'no') {
      scores.generator -= 12;
      scores.power_station += 3;
      scores.inverter_battery += 3;
      reasons.push('Yakıt, egzoz ve gürültü kısıtı bataryalı çözümleri öne çıkarır.');
    } else {
      scores.generator += 4;
    }

    if (input.context === 'business' || input.context === 'hotel_site') {
      scores.hybrid += 5;
      scores.generator += 3;
    }
    if (input.context === 'homeoffice') {
      scores.online_ups += 3;
      scores.power_station += 2;
    }

    return { scores: scores, reasons: reasons, cautions: cautions, watts: watts, hours: hours };
  }

  function evaluate(input) {
    const errors = validate(input);
    if (errors.length) return { ok: false, errors: errors };

    const model = scoreSolutions(input);
    const professionalReasons = [];
    if (input.context === 'medical') professionalReasons.push('Tıbbi veya yaşam destek yükü genel ürün eşleştirmesiyle seçilemez.');
    if (input.threePhase) professionalReasons.push('Trifaze sistem için faz dengesi, koruma ve transfer projesi gerekir.');
    if (input.installation !== 'portable') professionalReasons.push('Sabit tesisata bağlantı yetkili elektrikçi ve uygun ayırma/transfer düzeni gerektirir.');
    if (input.powerBand === 'high_unknown') professionalReasons.push('Güç değeri bilinmiyor veya 3 kW üzerindeyse ölçüm ve yük envanteri gerekir.');
    if (input.loadProfile === 'motor' || input.loadProfile === 'mixed') professionalReasons.push('Motorlu veya karışık yüklerde kalkış ve eşzamanlılık hesabı gerekir.');

    const ranked = Object.keys(model.scores)
      .map(function (key) { return { key: key, score: model.scores[key], solution: SOLUTIONS[key] }; })
      .sort(function (a, b) { return b.score - a.score; });

    let primary = ranked[0];
    let secondary = ranked[1];
    if (input.context === 'medical' || input.threePhase || input.installation === 'whole' || input.powerBand === 'high_unknown') {
      primary = { key: 'hybrid', score: model.scores.hybrid, solution: SOLUTIONS.hybrid };
      secondary = ranked.find(function (item) { return item.key !== 'hybrid'; }) || ranked[1];
    }

    const lowRiskCommercial = professionalReasons.length === 0 &&
      input.installation === 'portable' &&
      model.watts <= 1500 &&
      ['mini_ups', 'online_ups', 'line_interactive_ups', 'power_station'].indexOf(primary.key) >= 0;

    const checks = [
      'Cihaz etiketindeki sürekli W ve varsa kalkış/tepe W değerini doğrulayın.',
      'Hedef süre için Wh kapasitesini, verimi ve kullanılabilir batarya oranını ayrıca hesaplayın.',
      'Dalga biçimi, geçiş süresi, çıkış gerilimi ve priz standardını üretici dokümanından kontrol edin.'
    ];
    if (primary.key === 'generator' || primary.key === 'hybrid') {
      checks.push('Jeneratörü kapalı alanda çalıştırmayın; bina bağlantısını yalnız uygun transfer sistemiyle yaptırın.');
    }
    if (primary.key === 'inverter_battery') {
      checks.push('DC sigorta, ayırıcı, kablo, BMS ve batarya kısa devre akımı profesyonel olarak doğrulanmalıdır.');
    }

    return {
      ok: true,
      primary: primary,
      secondary: secondary,
      reasons: model.reasons,
      cautions: model.cautions,
      professional: professionalReasons.length > 0,
      professionalReasons: professionalReasons,
      showCommercial: lowRiskCommercial,
      productUrl: lowRiskCommercial ? '/akilli-urun-secimi?source=backup-solution&category=' + encodeURIComponent(primary.solution.category) : null,
      calculatorUrl: primary.solution.calculator,
      checks: checks,
      expiresInDays: 30
    };
  }

  function sanitizeInput(input) {
    const allowed = ['context', 'loadProfile', 'powerBand', 'continuity', 'duration', 'installation', 'outdoorFuel', 'threePhase'];
    const output = {};
    allowed.forEach(function (key) {
      if (Object.prototype.hasOwnProperty.call(input || {}, key)) output[key] = key === 'threePhase' ? Boolean(input[key]) : String(input[key]);
    });
    return output;
  }

  return { SOLUTIONS: SOLUTIONS, POWER_WATTS: POWER_WATTS, DURATION_HOURS: DURATION_HOURS, validate: validate, evaluate: evaluate, sanitizeInput: sanitizeInput };
});
