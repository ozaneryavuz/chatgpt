(() => {
  'use strict';

  const ROUTE = '/hesaplama/jenerator-yakit-tuketimi-calisma-suresi/';
  const ROUTES = {
    sizing: '/hesaplama/jenerator-gucu-secimi/',
    safety: '/hesaplama/jenerator-guvenli-kullanim-testi/',
    professional: '/kurumsal-elektrik-surekliligi-on-degerlendirme',
    article: '/haberler/jenerator-saatte-kac-litre-yakar',
    products: '/akilli-urun-secimi?intent=tasinabilir-jenerator-karbonmonoksit-alarmi-yakit-olcumu'
  };

  const number = (value) => Number.isFinite(Number(value)) ? Math.max(0, Number(value)) : 0;
  const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
  const round = (value, digits = 0) => {
    if (!Number.isFinite(value)) return null;
    const factor = 10 ** digits;
    return Math.round(value * factor) / factor;
  };

  function curvePoints(input) {
    return [
      [25, number(input.fuel25)],
      [50, number(input.fuel50)],
      [75, number(input.fuel75)],
      [100, number(input.fuel100)]
    ].filter(([, rate]) => rate > 0).map(([pct, rate]) => ({ pct, rate }));
  }

  function interpolateFuelRate(loadPct, points) {
    const sorted = [...points].sort((a, b) => a.pct - b.pct);
    if (!sorted.length) return { rate: null, method: 'none', bounds: null };
    if (sorted.length === 1) {
      const point = sorted[0];
      if (Math.abs(loadPct - point.pct) <= 5) {
        return { rate: point.rate, method: 'single_nearby', bounds: [point.pct, point.pct] };
      }
      return { rate: null, method: 'single_insufficient', bounds: [point.pct, point.pct] };
    }
    if (loadPct <= sorted[0].pct) {
      return { rate: sorted[0].rate, method: 'conservative_low', bounds: [sorted[0].pct, sorted[0].pct] };
    }
    const last = sorted[sorted.length - 1];
    if (loadPct > last.pct) {
      return { rate: null, method: 'above_curve', bounds: [last.pct, last.pct] };
    }
    for (let index = 0; index < sorted.length - 1; index += 1) {
      const left = sorted[index];
      const right = sorted[index + 1];
      if (loadPct >= left.pct && loadPct <= right.pct) {
        const share = (loadPct - left.pct) / (right.pct - left.pct);
        return {
          rate: left.rate + ((right.rate - left.rate) * share),
          method: loadPct === left.pct || loadPct === right.pct ? 'table_point' : 'linear_interpolation',
          bounds: [left.pct, right.pct]
        };
      }
    }
    return { rate: null, method: 'none', bounds: null };
  }

  function calculate(input) {
    const continuousKW = number(input.continuousKW);
    const loadKW = number(input.loadKW);
    const loadPct = continuousKW > 0 ? (loadKW / continuousKW) * 100 : 0;
    const points = curvePoints(input);
    const fuel = interpolateFuelRate(loadPct, points);
    const usablePct = clamp(number(input.usablePct) || 90, 50, 100);
    const tankLiters = number(input.tankLiters);
    const usableFuelL = tankLiters * usablePct / 100;
    const targetHours = number(input.targetHours);
    const fuelRate = fuel.rate;
    const runtimeHours = fuelRate && usableFuelL ? usableFuelL / fuelRate : null;
    const requiredFuelL = fuelRate && targetHours ? fuelRate * targetHours : null;
    const extraFuelL = requiredFuelL === null ? null : Math.max(0, requiredFuelL - usableFuelL);
    const fuelPrice = number(input.fuelPrice);
    const estimatedCost = requiredFuelL !== null && fuelPrice > 0 ? requiredFuelL * fuelPrice : null;
    const generatedKWh = loadKW > 0 && targetHours > 0 ? loadKW * targetHours : null;
    const kWhPerLiter = fuelRate && loadKW > 0 ? loadKW / fuelRate : null;
    return {
      continuousKW: round(continuousKW, 2),
      loadKW: round(loadKW, 2),
      loadPct: round(loadPct, 1),
      points,
      fuelRate: round(fuelRate, 2),
      fuelMethod: fuel.method,
      curveBounds: fuel.bounds,
      tankLiters: round(tankLiters, 1),
      usablePct: round(usablePct),
      usableFuelL: round(usableFuelL, 1),
      targetHours: round(targetHours, 1),
      runtimeHours: round(runtimeHours, 1),
      requiredFuelL: round(requiredFuelL, 1),
      extraFuelL: round(extraFuelL, 1),
      estimatedCost: round(estimatedCost, 2),
      generatedKWh: round(generatedKWh, 1),
      kWhPerLiter: round(kWhPerLiter, 2)
    };
  }

  function decision(code, title, summary, tone = 'warn', actions = [], affiliate = null) {
    return { code, title, summary, tone, actions, affiliate };
  }

  function decide(input) {
    const metrics = calculate(input);
    const unsafeLocation = ['indoors', 'garage', 'balcony', 'near_opening'].includes(input.location);
    const curveTrusted = ['manufacturer', 'measured'].includes(input.curveEvidence);
    const transferVerified = input.connection === 'individual' || input.connection === 'manual_transfer' || input.connection === 'ats';
    const existing = input.existing === 'yes';

    if (input.emergency || ['alarm', 'symptoms'].includes(input.coStatus)) {
      return {
        ...decision(
          'emergency',
          'Jeneratörü durdurun ve temiz havaya çıkın',
          'Karbonmonoksit alarmı, baş ağrısı, baş dönmesi, bulantı, bilinç değişikliği, duman, yangın veya elektrik çarpması belirtisinde hesap ve ürün yolu kapanır. Kapalı alana geri dönmeyin; 112 önceliklidir.',
          'stop',
          ['Motoru kapatmak güvenli değilse yaklaşmayın', 'Herkesi temiz havaya çıkarın', '112 yönlendirmesini kullanın']
        ),
        metrics
      };
    }
    if (unsafeLocation) {
      return {
        ...decision(
          'unsafe_location',
          'Bu konumda jeneratör çalıştırmayın',
          'Jeneratör bina içinde, garajda, balkonda veya kapı, pencere ve hava girişine yakın çalıştırılamaz. Açık kapı ya da pencere kapalı alan riskini ortadan kaldırmaz.',
          'stop',
          ['Jeneratörü çalıştırmayın', 'Üretici talimatındaki güvenli açık alan mesafesini doğrulayın', 'CO alarmı ve egzoz yönünü ayrıca kontrol edin']
        ),
        metrics
      };
    }
    if (input.connection === 'backfeed') {
      return {
        ...decision(
          'backfeed',
          'Prizden binaya ters besleme yapmayın',
          'Erkek-erkek kablo, pano dışı ters besleme veya şebekeden güvenli ayırma olmadan bina tesisatını enerjilendirmek ölümcül geri besleme ve yangın riski oluşturur.',
          'stop',
          ['Bağlantıyı kullanmayın', 'Yükleri yalnız üreticinin izin verdiği doğrudan çıkıştan besleyin', 'Bina beslemesi için yetkili elektrikçi ve uygun transfer düzeni kullanın']
        ),
        metrics
      };
    }
    if (input.fuelType === 'lpg_ng') {
      return {
        ...decision(
          'gas_fuel_specialist',
          'Gaz yakıtlı sistem için bu litre hesabını kullanmayın',
          'LPG ve doğal gaz tüketimi, basınç, sıcaklık, kg/m³ birimi, regülatör ve sabit tesisat koşullarına bağlıdır. Dizel/benzin litre-saat eğrisiyle karşılaştırılamaz.',
          'stop',
          ['Üreticinin yakıt birimindeki eğriyi kullanın', 'Sabit gaz bağlantısını yetkili uzmanla değerlendirin']
        ),
        metrics
      };
    }
    if (!metrics.continuousKW || !metrics.loadKW || !metrics.targetHours) {
      return {
        ...decision(
          'missing_load',
          'Güç ve süre kanıtını tamamlayın',
          'Jeneratörün sürekli kW değeri, aynı anda beslenecek gerçek yük kW değeri ve hedef çalışma süresi olmadan yakıt veya süre sonucu üretilemez.',
          'warn',
          ['Standby/azami kVA yerine sürekli kW değerini bulun', 'Gerçek eşzamanlı yükü ölçün veya teknik föyden doğrulayın']
        ),
        metrics
      };
    }
    if (metrics.loadPct > 100) {
      return {
        ...decision(
          'overload',
          'Yük jeneratörün sürekli gücünü aşıyor',
          'Yakıt hesabı uygunluk kanıtı değildir. Sürekli kW sınırı aşılmış durumda; motor kalkışları ayrıca daha yüksek tepe yük oluşturabilir.',
          'stop',
          ['Yükleri azaltın', 'Jeneratör Gücü Ön Seçimi aracını kullanın', 'Sabit veya kritik sistemde profesyonel boyutlandırma yaptırın']
        ),
        metrics
      };
    }
    if (input.generatorType === 'fixed' || metrics.loadKW > 5) {
      if (!transferVerified || input.connection === 'unknown') {
        return {
          ...decision(
            'fixed_professional',
            'Sabit veya yüksek güçlü sistem profesyonel değerlendirme gerektirir',
            'Transfer, nötr-toprak düzeni, kısa devre koruması, egzoz, havalandırma, yakıt ve yangın güvenliği doğrulanmadan yalnız litre-saat hesabıyla kullanım kararı verilemez.',
            'warn',
            ['Tek hat şeması ve transfer düzenini doğrulayın', 'Yük adımlarını ve motor kalkışlarını inceletin', 'Profesyonel ön değerlendirmeye ilerleyin']
          ),
          metrics
        };
      }
    }
    if (input.fuelStorage === 'unsafe') {
      return {
        ...decision(
          'unsafe_fuel_storage',
          'Yakıt depolama koşulu güvenli değil',
          'Isı, kıvılcım, yaşam alanı, uygunsuz kap veya havalandırma riski çözülmeden çalışma süresini büyütmek için yakıt depolamayın.',
          'stop',
          ['Yakıtı çalışır veya sıcak jeneratöre eklemeyin', 'Üretici talimatı ve yerel yangın kurallarını doğrulayın']
        ),
        metrics
      };
    }
    if (input.mode === 'active' && !existing) {
      return {
        ...decision(
          'active_no_generator',
          'Yeni ürün teslimatı aktif kesintinin çözümü değildir',
          'Aktif kesintide henüz kurulmamış ve test edilmemiş jeneratörü anlık çözüm saymayın. Önce yük azaltma, güvenli mevcut kaynak ve resmî kesinti bilgisini kullanın.',
          'warn',
          ['Kritik yükleri azaltın', '186 ve ilgili EDAŞ kanalını kontrol edin', 'Sonraki kesinti için planlama modunda hesap yapın']
        ),
        metrics
      };
    }
    if (input.maintenance === 'no') {
      return {
        ...decision(
          'maintenance_failed',
          'Bakım ve gerçek yük testi tamamlanmadan süreye güvenmeyin',
          'Yakıt bulunsa bile start aküsü, yağ, soğutma, egzoz, kaçak, frekans/gerilim veya transfer sorunu görevi kesebilir.',
          'warn',
          ['Bakım kayıtlarını tamamlayın', 'Gündüz ve gözetimli gerçek yük testi yapın', 'Arıza varsa yetkili servise ilerleyin']
        ),
        metrics
      };
    }
    if (input.generatorType === 'portable' && input.coAlarm !== 'yes') {
      return {
        ...decision(
          'co_alarm_missing',
          'Karbonmonoksit güvenlik katmanı eksik',
          'Taşınabilir jeneratör yalnız dışarıda çalışsa bile yaşam alanında çalışan ve test edilmiş CO alarmı bulunmadan ürün veya uzun süre planı açılmaz.',
          'warn',
          ['CO alarmı yerleşim ve bakım aracını kullanın', 'Alarmın testini ve yaşını doğrulayın']
        ),
        metrics
      };
    }
    if (!transferVerified) {
      return {
        ...decision(
          'connection_unknown',
          'Bağlantı ve şebekeden ayırma kanıtı eksik',
          'Jeneratör çıkışının hangi yükleri nasıl beslediği ve bina tesisatında transfer düzeni bilinmeden yakıt süresi kullanım uygunluğu anlamına gelmez.',
          'warn',
          ['Doğrudan yük veya uygun transfer düzenini doğrulayın', 'Prizden binaya ters besleme yapmayın']
        ),
        metrics
      };
    }
    if (!curveTrusted || metrics.fuelRate === null) {
      return {
        ...decision(
          'fuel_curve_missing',
          'Üretici yakıt eğrisi veya gerçek ölçüm gerekli',
          'Tek bir pazaryeri değeri, boşta tüketim veya tahmini litre/saat bütün yük noktalarını temsil etmez. Mevcut yük oranını çevreleyen en az iki doğrulanmış yakıt noktası kullanın.',
          'warn',
          ['25/50/75/100% üretici yakıt tablosunu bulun', 'Gerçek ölçüm varsa yük kW ve süreyle birlikte kaydedin', 'Yakıt hesabını kanıt tamamlanınca yenileyin']
        ),
        metrics
      };
    }
    if (input.fuelType === 'diesel' && metrics.loadPct < 20) {
      return {
        ...decision(
          'very_low_load',
          'Dizel jeneratör uzun süre çok düşük yükte çalışmamalı',
          'Bu çalışma noktası yakıt verimini düşürebilir ve üreticiye göre düşük yük/wet stacking riski oluşturabilir. Daha fazla yük eklemek otomatik çözüm değildir.',
          'warn',
          ['Üreticinin minimum yük ve egzersiz talimatını doğrulayın', 'Yük profilini veya daha küçük kaynak seçeneğini profesyonel değerlendirin']
        ),
        metrics
      };
    }
    if (existing && metrics.runtimeHours !== null && metrics.runtimeHours >= metrics.targetHours && input.transferTest === 'yes' && input.maintenance === 'yes') {
      return {
        ...decision(
          'no_buy',
          'Mevcut jeneratör ve yakıt planı hedefi karşılıyor — yeni ürün almayın',
          'Sürekli güç, doğrulanmış yakıt eğrisi, kullanılabilir tank, bakım ve gerçek transfer testi hedef süreyi karşılıyor. Periyodik testi ve güvenli yakıt yönetimini sürdürün.',
          'ok',
          ['Yakıtı çalışır veya sıcak jeneratöre eklemeyin', 'Test tarihini ve gerçek tüketimi kaydedin', 'Yük değiştiğinde hesabı yenileyin']
        ),
        metrics
      };
    }
    if (existing && metrics.runtimeHours !== null && metrics.runtimeHours < metrics.targetHours) {
      return {
        ...decision(
          'runtime_shortfall',
          'Mevcut tank hedef süreyi karşılamıyor',
          `Hesaplanan kullanılabilir süre yaklaşık ${metrics.runtimeHours} saat. Hedef ${metrics.targetHours} saat için yaklaşık ${metrics.extraFuelL} litre ek görev yakıtı veya yük azaltma planı gerekiyor.`,
          'warn',
          ['Önce kritik olmayan yükleri çıkarın', 'Yakıt ikmalini yalnız motor durdurulmuş ve üretici koşulları sağlanmışken planlayın', 'Daha büyük sabit sistem kararını profesyonel değerlendirin']
        ),
        metrics
      };
    }
    if (input.generatorType === 'portable' && !existing && input.mode === 'planning' && metrics.loadKW <= 5 && input.location === 'outdoors_clear') {
      return {
        ...decision(
          'portable_planning',
          'Taşınabilir jeneratör sınıfı ancak güvenlik ve güç doğrulamasından sonra karşılaştırılabilir',
          'Yakıt eğrisi hedef süreyi hesaplıyor; fakat son seçimde sürekli kW, motor kalkışı, gürültü, CO, topraklama, çıkış koruması ve gerçek yük testi birlikte doğrulanmalıdır.',
          'ok',
          ['Önce Jeneratör Gücü Ön Seçimi sonucunu tamamlayın', 'CO alarmı ve güvenli dış ortam koşulunu doğrulayın', 'Tam model yakıt eğrisini yeniden kontrol edin'],
          { code: 'portable_generator', href: ROUTES.products }
        ),
        metrics
      };
    }
    return {
      ...decision(
        'verify_system',
        'Yakıt sonucu oluştu; sistem uygunluğu henüz tamamlanmadı',
        'Hesaplanan litre/saat ve tank süresi yalnız yakıt planıdır. Transfer, bakım, gerçek yük testi veya mevcut sistem bilgisi tamamlanmadan yeni ürün ya da çalışma onayı verilmez.',
        'warn',
        ['Eksik kanıtları tamamlayın', 'Jeneratör güvenli kullanım testine ilerleyin', 'Sabit sistemde profesyonel değerlendirme alın']
      ),
      metrics
    };
  }

  function summaryPayload(input, result) {
    return {
      schema: 'alo186-generator-fuel-runtime-v130',
      generatedAt: new Date().toISOString(),
      privacy: 'Kişisel veri içermez; tarayıcıda oluşturulur.',
      route: ROUTE,
      input: {
        mode: input.mode,
        generatorType: input.generatorType,
        fuelType: input.fuelType,
        continuousKW: number(input.continuousKW),
        loadKW: number(input.loadKW),
        targetHours: number(input.targetHours),
        tankLiters: number(input.tankLiters),
        usablePct: number(input.usablePct),
        curveEvidence: input.curveEvidence,
        connection: input.connection
      },
      decision: {
        code: result.code,
        title: result.title,
        summary: result.summary
      },
      metrics: result.metrics
    };
  }

  function icsText() {
    const start = new Date();
    start.setDate(start.getDate() + 90);
    const end = new Date(start.getTime() + 30 * 60 * 1000);
    const fmt = (date) => date.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}Z$/, 'Z');
    return [
      'BEGIN:VCALENDAR',
      'VERSION:2.0',
      'PRODID:-//ALO186//Jenerator Yakıt ve Güvenlik Kontrolü//TR',
      'BEGIN:VEVENT',
      `UID:alo186-generator-${Date.now()}@alo186.com`,
      `DTSTAMP:${fmt(new Date())}`,
      `DTSTART:${fmt(start)}`,
      `DTEND:${fmt(end)}`,
      'SUMMARY:Jeneratör yakıt eğrisi ve güvenlik kontrolü',
      'DESCRIPTION:Gerçek yük, yakıt tüketimi, CO alarmı, bakım ve transfer testini yeniden doğrulayın.',
      'END:VEVENT',
      'END:VCALENDAR'
    ].join('\r\n');
  }

  function download(name, type, text) {
    const blob = new Blob([text], { type });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = name;
    link.click();
    URL.revokeObjectURL(url);
  }

  function formInput(form) {
    return Object.fromEntries(new FormData(form).entries());
  }

  function metric(label, value) {
    return `<div class="metric"><span>${label}</span><strong>${value ?? '—'}</strong></div>`;
  }

  function render(result, input) {
    const resultBox = document.getElementById('result');
    const metrics = result.metrics;
    const methodLabels = {
      table_point: 'Üretici tablo noktası',
      linear_interpolation: 'İki tablo noktası arası',
      conservative_low: 'En düşük tablo noktasıyla muhafazakâr',
      single_nearby: 'Yakın tek ölçüm noktası',
      single_insufficient: 'Tek nokta yetersiz',
      above_curve: 'Eğri üstü — sonuç yok',
      none: 'Yakıt kanıtı yok'
    };
    resultBox.className = `result ${result.tone}`;
    resultBox.hidden = false;
    resultBox.innerHTML = `
      <div class="result-head"><span class="status">${result.code.replaceAll('_', ' ')}</span><h2>${result.title}</h2><p>${result.summary}</p></div>
      <div class="metrics">
        ${metric('Yük oranı', metrics.loadPct !== null ? `%${metrics.loadPct}` : null)}
        ${metric('Yakıt tüketimi', metrics.fuelRate !== null ? `${metrics.fuelRate} L/saat` : null)}
        ${metric('Kullanılabilir yakıt', metrics.usableFuelL !== null ? `${metrics.usableFuelL} L` : null)}
        ${metric('Yaklaşık çalışma', metrics.runtimeHours !== null ? `${metrics.runtimeHours} saat` : null)}
        ${metric('Hedef yakıt', metrics.requiredFuelL !== null ? `${metrics.requiredFuelL} L` : null)}
        ${metric('Hesap yöntemi', methodLabels[metrics.fuelMethod] || metrics.fuelMethod)}
        ${metric('Yaklaşık enerji', metrics.generatedKWh !== null ? `${metrics.generatedKWh} kWh` : null)}
        ${metric('Yakıt başına enerji', metrics.kWhPerLiter !== null ? `${metrics.kWhPerLiter} kWh/L` : null)}
        ${metric('Kullanıcı birim fiyatıyla maliyet', metrics.estimatedCost !== null ? `${metrics.estimatedCost} TL` : null)}
      </div>
      <div class="actions"><h3>Güvenli sonraki adımlar</h3><ol>${result.actions.map((item) => `<li>${item}</li>`).join('')}</ol></div>
      <div class="result-links">
        <a href="${ROUTES.safety}">Jeneratör güvenli kullanım testini aç</a>
        <a href="${ROUTES.sizing}">Jeneratör gücünü kontrol et</a>
        <a href="${ROUTES.article}">Yakıt tüketimi rehberini oku</a>
        ${input.generatorType === 'fixed' || metrics.loadKW > 5 ? `<a href="${ROUTES.professional}">Profesyonel ön değerlendirmeyi aç</a>` : ''}
      </div>
    `;
    const affiliate = document.getElementById('affiliate');
    affiliate.hidden = !result.affiliate;
    affiliate.dataset.category = result.affiliate?.code || '';
    document.querySelectorAll('[data-affiliate-check]').forEach((box) => { box.checked = false; });
    updateAffiliate(result);
    resultBox.focus();
    return result;
  }

  let latest = null;
  function updateAffiliate(result = latest) {
    const link = document.getElementById('affiliateLink');
    if (!link) return;
    const checks = [...document.querySelectorAll('[data-affiliate-check]')];
    const ready = Boolean(result?.affiliate) && checks.every((box) => box.checked);
    link.href = ready ? result.affiliate.href : '#';
    link.setAttribute('aria-disabled', String(!ready));
    link.tabIndex = ready ? 0 : -1;
    link.classList.toggle('disabled', !ready);
  }

  function init() {
    const form = document.getElementById('generatorForm');
    if (!form) return;
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      const input = formInput(form);
      latest = decide(input);
      render(latest, input);
    });
    form.addEventListener('reset', () => {
      setTimeout(() => {
        document.getElementById('result').hidden = true;
        document.getElementById('affiliate').hidden = true;
        latest = null;
      }, 0);
    });
    document.querySelectorAll('[data-affiliate-check]').forEach((box) => {
      box.addEventListener('change', () => updateAffiliate());
    });
    document.getElementById('affiliateLink')?.addEventListener('click', (event) => {
      if (event.currentTarget.getAttribute('aria-disabled') === 'true') event.preventDefault();
    });
    document.getElementById('downloadJson')?.addEventListener('click', () => {
      if (!latest) return;
      download('alo186-jenerator-yakit-plani.json', 'application/json', JSON.stringify(summaryPayload(formInput(form), latest), null, 2));
    });
    document.getElementById('calendar')?.addEventListener('click', () => {
      download('alo186-jenerator-90-gun-kontrol.ics', 'text/calendar;charset=utf-8', icsText());
    });
    document.getElementById('print')?.addEventListener('click', () => window.print());
  }

  globalThis.Alo186GeneratorFuel = {
    calculate,
    curvePoints,
    interpolateFuelRate,
    decide,
    summaryPayload,
    icsText,
    routes: ROUTES
  };
  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
    else init();
  }
})();
