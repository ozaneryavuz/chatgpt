(() => {
  'use strict';

  const BTU_TABLE = [
    [14, 5000], [23, 6000], [28, 7000], [33, 8000], [37, 9000],
    [42, 10000], [51, 12000], [65, 14000], [93, 18000], [111, 21000], [140, 24000]
  ];
  const BTU_CLASSES = [5000, 6000, 7000, 8000, 9000, 10000, 12000, 14000, 18000, 21000, 24000];
  const LABELS = {
    fan: 'Vantilatör / hava dolaşımı',
    evaporative: 'Evaporatif hava soğutucu',
    portable_ac: 'Kompresörlü portatif klima',
    dehumidifier: 'Nem alma cihazı veya nem alma modlu klima',
    compare_evap_ac: 'Evaporatif soğutucu ile portatif klimayı teknik kanıtla karşılaştırma'
  };

  const number = (value) => {
    const parsed = Number(String(value ?? '').replace(',', '.'));
    return Number.isFinite(parsed) ? parsed : 0;
  };
  const round = (value, digits = 0) => Number(value.toFixed(digits));
  const nextBtuClass = (value) => BTU_CLASSES.find((item) => item >= value) || BTU_CLASSES.at(-1);

  function baseBtu(areaM2) {
    for (const [limit, btu] of BTU_TABLE) {
      if (areaM2 <= limit) return btu;
    }
    return BTU_TABLE.at(-1)[1];
  }

  function calculateCoolingLoad(data) {
    const area = number(data.areaM2);
    const ceiling = number(data.ceilingM);
    const people = Math.max(1, number(data.people));
    const electronicsW = Math.max(0, number(data.electronicsW));
    let load = baseBtu(area) * (ceiling / 2.44);
    if (data.sun === 'sunny') load *= 1.10;
    if (data.sun === 'shaded') load *= 0.90;
    if (people > 2) load += (people - 2) * 600;
    load += electronicsW * 3.412;
    return {
      volumeM3: round(area * ceiling, 1),
      estimatedBtu: Math.round(load),
      suggestedBtu: nextBtuClass(load),
      lowerBtu: Math.round(load * 0.90),
      upperBtu: Math.round(load * 1.15)
    };
  }

  function recommendedClass(data) {
    if (data.goal === 'personal_breeze') return 'fan';
    if (data.goal === 'humidity_relief') return 'dehumidifier';
    if (data.humidity === 'low' && data.ventilation === 'yes') return 'compare_evap_ac';
    if (data.humidity === 'medium' && data.ventilation === 'yes') return 'portable_ac';
    return 'portable_ac';
  }

  function deviceMatchesGoal(data) {
    if (data.deviceType === 'none') return null;
    if (data.deviceType === 'fan') return data.goal === 'personal_breeze';
    if (data.deviceType === 'evaporative') {
      return data.goal !== 'humidity_relief' && data.humidity !== 'high' && data.humidity !== 'unknown' && data.ventilation === 'yes';
    }
    if (data.deviceType === 'portable_ac') return data.goal === 'room_cooling' || data.goal === 'humidity_relief';
    return false;
  }

  function evaluate(raw) {
    const data = { ...raw };
    const requiredNumbers = ['areaM2', 'ceilingM'];
    const invalid = requiredNumbers.filter((key) => number(data[key]) <= 0);
    if (invalid.length) return { ok: false, error: 'Oda alanı ve tavan yüksekliği için geçerli değer girin.' };

    const load = calculateCoolingLoad(data);
    const inputW = Math.max(0, number(data.inputW));
    const ratedA = Math.max(0, number(data.ratedA));
    const calculatedA = inputW > 0 ? inputW / 230 : 0;
    const workingA = Math.max(calculatedA, ratedA);
    const candidateBtu = Math.max(0, number(data.candidateBtu));
    const candidateRatio = candidateBtu > 0 ? candidateBtu / load.estimatedBtu : 0;
    const targetClass = recommendedClass(data);
    const stops = [];
    const professional = [];
    const evidence = [];
    const warnings = [];
    const strengths = [];

    if (data.emergency) stops.push('Duman, erime, su-elektrik teması veya elektrik çarpması riski varken cihazı kullanmayın; yangın veya yaralanmada 112 önceliklidir.');
    if (data.physical !== 'good') stops.push('Priz, fiş veya kablo fiziksel olarak güvenli değil. Enerjiyi zorlamadan yetkili elektrikçi kontrolü gerekir.');
    if (data.gridSymptom !== 'none') professional.push('Birden fazla odadaki parlaklık veya reset belirtisi ürün seçimi değildir; 186/ilgili EDAŞ ve yetkili elektrikçi rotası gerekir.');
    if (data.mode === 'active_outage') stops.push('Aktif kesintide henüz satın alınmamış ürün anlık serinletme çözümü sayılmaz; güvenli mevcut yöntem ve sıcaklıkla ilgili sağlık önlemleri önceliklidir.');
    if (data.useCase !== 'home_room') professional.push('Çok odalı, ticari, medikal veya server odası için tüketici tipi ürün karşılaştırması yerine ısı yükü, havalandırma ve elektrik projesi gerekir.');

    if (data.deviceType === 'evaporative') {
      if (data.humidity === 'high' || data.humidity === 'unknown') warnings.push('Evaporatif ürün yüksek veya bilinmeyen nemde uygun kabul edilmedi; nem yükseldikçe serinletme etkisi azalabilir ve oda nemi artabilir.');
      if (data.ventilation !== 'yes') warnings.push('Evaporatif cihaz için sürekli dış hava çıkışı doğrulanmadı. Kapalı odada ürün yolu açılmaz.');
      if (data.protection !== 'verified') evidence.push('Su kullanan cihaz için topraklama ve RCD doğrulanmalıdır.');
      if (data.connection !== 'direct') evidence.push('Evaporatif cihaz üreticinin izin verdiği doğrudan, topraklı bağlantıyla kullanılmalıdır; adaptör ve çoklayıcı zinciri kabul edilmez.');
    }

    if (data.deviceType === 'portable_ac') {
      if (data.connection !== 'direct') stops.push('Portatif klima uzatma, çoklayıcı veya adaptör zincirinde kullanılmamalıdır; doğrudan uygun duvar prizi gerekir.');
      if (data.protection !== 'verified') evidence.push('Portatif klima için topraklama ve RCD kanıtı eksik.');
      if (data.hose !== 'verified') evidence.push('Sıcak hava hortumu ve pencere kiti uygun/sızdırmaz kurulmadan gerçek soğutma sonucu verilemez.');
      if (data.drainage !== 'verified') evidence.push('Yoğuşma suyu tahliyesi üretici talimatına göre doğrulanmalıdır.');
      if (data.manual !== 'verified') evidence.push('Tam model teknik kılavuz ve elektrik şartı doğrulanmalıdır.');
      if (inputW <= 0 && ratedA <= 0) evidence.push('Portatif klimanın gerçek INPUT W veya etiket A değeri gerekli.');
      if (candidateBtu <= 0) evidence.push('Portatif klimanın etiket soğutma kapasitesi gerekli.');
      if (workingA > 16 || inputW > 3500) professional.push('Cihaz fişli tüketici sınıfı akım sınırının dışında görünüyor; devre ve bağlantı uzman tarafından doğrulanmalıdır.');
      if (candidateRatio > 0 && candidateRatio < 0.85) warnings.push('Aday portatif klima yaklaşık yükün altında; sıcak günde hedefe ulaşamayabilir.');
      if (candidateRatio > 1.35) warnings.push('Aday kapasite gereğinden büyük görünüyor; maliyet ve nem alma performansı için kapasite yeniden doğrulanmalı.');
    }

    if (data.deviceType === 'fan') {
      if (data.goal !== 'personal_breeze') warnings.push('Vantilatör oda sıcaklığını veya nemi düşüren bir klima değildir; yalnız hava hareketi sağlar.');
      if (data.connection === 'adapter' || data.connection === 'strip') warnings.push('Adaptör/çoklayıcı zinciri yerine üretici talimatına uygun tek bağlantı kullanın.');
      if (data.protection === 'failed') evidence.push('Topraklama veya RCD testi başarısız; önce elektrik güvenliği düzeltilmelidir.');
    }

    if (data.deviceType !== 'none' && data.manual !== 'verified') evidence.push('Tam model kullanım ve elektrik talimatı henüz doğrulanmadı.');
    if (data.drainage === 'unsafe') stops.push('Yoğuşma veya su taşması elektrik riski oluşturuyor; cihazı kullanmayın.');

    const existingPass = data.existing === 'yes' && data.taskTest === 'pass';
    const match = deviceMatchesGoal(data);
    let status = 'recommend';
    let headline = 'İhtiyaca uygun çözüm sınıfı belirlendi';
    let recommendation = targetClass;

    if (stops.length) {
      status = 'stop';
      headline = 'Önce güvenli durdurma ve mevcut durum yönetimi';
    } else if (professional.length) {
      status = 'professional';
      headline = 'Tüketici ürünü yerine profesyonel değerlendirme gerekli';
    } else if (existingPass && match !== false && evidence.length === 0) {
      status = 'no-buy';
      headline = 'Mevcut cihaz hedefi karşılıyor — yeni ürün almayın';
      recommendation = data.deviceType;
      strengths.push('Gerçek sıcak/nemli gün testi hedeflenen görevi karşılamış.');
      strengths.push('Yeni model veya daha yüksek katalog değeri tek başına satın alma gerekçesi değildir.');
    } else if (data.deviceType !== 'none' && (evidence.length || match === false || warnings.length)) {
      status = 'evidence';
      headline = match === false ? 'Seçilen cihaz sınıfı hedefle eşleşmiyor' : 'Ürün karşılaştırmasından önce kanıt eksikleri var';
    }

    if (data.goal === 'personal_breeze') strengths.push('Oda sıcaklığını düşürmek gerekmiyorsa en düşük karmaşıklıktaki sınıf vantilatördür.');
    if (data.goal === 'room_cooling' && targetClass === 'portable_ac') strengths.push('Gerçek oda sıcaklığı düşüşü için kompresörlü soğutma gerekir.');
    if (targetClass === 'compare_evap_ac') strengths.push('Düşük nem ve sürekli dış hava varsa evaporatif çözüm değerlendirilebilir; portatif klima daha öngörülebilir gerçek soğutma sağlar.');
    if (data.goal === 'humidity_relief') strengths.push('Nem azaltma hedefinde evaporatif ürün ters etki yapabilir; nem alma cihazı veya kompresörlü klima sınıfı gerekir.');

    const confirmations = Boolean(data.confirmNeed && data.confirmSpecs && data.confirmAffiliate);
    const affiliateAllowed = status === 'recommend' && data.mode === 'planning' && confirmations;
    const affiliateClass = recommendation === 'compare_evap_ac' ? 'portable_ac' : recommendation;

    return {
      ok: true,
      status,
      headline,
      recommendation,
      recommendationLabel: LABELS[recommendation] || LABELS[targetClass],
      load,
      electrical: {
        inputW: round(inputW, 0),
        calculatedA: round(calculatedA, 2),
        workingA: round(workingA, 2),
        hourlyKwh: round(inputW / 1000, 3),
        candidateBtu: round(candidateBtu, 0),
        candidateRatio: round(candidateRatio, 2)
      },
      stops,
      professional,
      evidence: [...new Set(evidence)],
      warnings: [...new Set(warnings)],
      strengths: [...new Set(strengths)],
      affiliateAllowed,
      affiliateClass,
      confirmations,
      privacy: 'Hesap tarayıcıda yapılır; kişisel veri, konum veya hesap kaydı kullanılmaz.'
    };
  }

  function formDataToObject(form) {
    const entries = Object.fromEntries(new FormData(form).entries());
    for (const name of ['emergency', 'confirmNeed', 'confirmSpecs', 'confirmAffiliate']) entries[name] = Boolean(form.elements[name]?.checked);
    return entries;
  }

  function list(title, items) {
    if (!items.length) return '';
    return `<section><h3>${title}</h3><ul>${items.map((item) => `<li>${item}</li>`).join('')}</ul></section>`;
  }

  function affiliateHref(kind) {
    const slug = {
      fan: 'vantilator', evaporative: 'evaporatif-hava-sogutucu', portable_ac: 'portatif-klima', dehumidifier: 'nem-alma-cihazi'
    }[kind] || 'serinletme';
    return `/akilli-urun-secimi?niyet=serinletme&sinif=${slug}`;
  }

  function render(result) {
    const resultEl = document.querySelector('#result');
    const errorEl = document.querySelector('#error');
    if (!result.ok) {
      resultEl.hidden = true;
      errorEl.textContent = result.error;
      errorEl.hidden = false;
      return;
    }
    errorEl.hidden = true;
    resultEl.dataset.status = result.status;
    const affiliate = result.affiliateAllowed
      ? `<div class="affiliate"><strong>Koşullu ürün sınıfı</strong><p>Yalnız tam model elektrik, nem, havalandırma ve kurulum şartlarını yeniden doğrulayarak ilerleyin.</p><a href="${affiliateHref(result.affiliateClass)}" rel="sponsored nofollow noopener">Şeffaf ürün sınıfını aç →</a><small>Sonraki dış ürün bağlantılarından komisyon kazanılabilir; kullanıcıya ek maliyet yansımaz.</small></div>`
      : `<div class="affiliate"><strong>Ürün bağlantısı kapalı</strong><p>${result.status === 'no-buy' ? 'Mevcut cihaz yeterli olduğu için yeni ürün yolu açılmadı.' : result.confirmations ? 'Güvenlik, görev eşleşmesi veya teknik kanıt tamamlanmadan ürün yolu açılmaz.' : 'Gerçek ihtiyaç ve üç şeffaflık onayı tamamlanmadan ürün yolu açılmaz.'}</p></div>`;
    resultEl.innerHTML = `
      <h2>${result.headline}</h2>
      <div class="decision"><strong>${result.recommendationLabel}</strong><span>Önerilen karar sınıfı</span></div>
      <div class="summary-grid">
        <div class="metric"><span>Oda hacmi</span><strong>${result.load.volumeM3} m³</strong></div>
        <div class="metric"><span>Yaklaşık soğutma yükü</span><strong>${result.load.estimatedBtu.toLocaleString('tr-TR')} BTU/h</strong></div>
        <div class="metric"><span>Yakın portatif klima sınıfı</span><strong>${result.load.suggestedBtu.toLocaleString('tr-TR')} BTU/h</strong></div>
        <div class="metric"><span>Etiket/hesap akımı</span><strong>${result.electrical.workingA || '—'} A</strong></div>
      </div>
      ${list('Önce durdurun', result.stops)}
      ${list('Profesyonel sınır', result.professional)}
      ${list('Eksik teknik kanıt', result.evidence)}
      ${list('Karar uyarıları', result.warnings)}
      ${list('Bu sonucun gerekçesi', result.strengths)}
      <p><strong>Enerji notu:</strong> Girilen cihaz gücüyle yaklaşık saatlik tüketim ${result.electrical.hourlyKwh || '—'} kWh'dir. Bu değer tarife veya aylık maliyet içermez.</p>
      ${affiliate}
      <p class="hint">${result.privacy}</p>`;
    resultEl.hidden = false;
    resultEl.focus();
  }

  let lastResult = null;
  function init() {
    const form = document.querySelector('#coolingForm');
    if (!form) return;
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      lastResult = evaluate(formDataToObject(form));
      render(lastResult);
    });
    document.querySelector('#printButton')?.addEventListener('click', () => window.print());
    document.querySelector('#jsonButton')?.addEventListener('click', () => {
      if (!lastResult?.ok) {
        lastResult = evaluate(formDataToObject(form));
        render(lastResult);
      }
      if (!lastResult?.ok) return;
      const blob = new Blob([JSON.stringify(lastResult, null, 2)], { type: 'application/json' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = 'alo186-serinletme-cozumu-sonucu.json';
      link.click();
      URL.revokeObjectURL(link.href);
    });
  }

  const api = { calculateCoolingLoad, recommendedClass, evaluate, nextBtuClass };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (typeof document !== 'undefined') init();
})();
