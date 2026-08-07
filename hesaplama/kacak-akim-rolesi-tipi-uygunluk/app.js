(() => {
  'use strict';

  const TYPE_RANK = { AC: 0, A: 1, F: 2, B: 3 };
  const RCCB_CLASSES = [25, 40, 63, 80, 100, 125];
  const LABELS = {
    AC: 'Type AC',
    A: 'Type A',
    F: 'Type F',
    B: 'Type B',
    professional: 'Üretici belgesi ve profesyonel tasarımla özel RCD çözümü'
  };

  const number = (value) => {
    const parsed = Number(String(value ?? '').replace(',', '.'));
    return Number.isFinite(parsed) ? parsed : 0;
  };
  const nextClass = (value) => RCCB_CLASSES.find((item) => item >= value) || null;

  function recommendedType(data) {
    if (data.manufacturerType && data.manufacturerType !== 'unknown') return data.manufacturerType;
    if (data.loadType === 'single_vfd') return 'F';
    if (data.loadType === 'ev') return data.dc6 === 'verified' ? 'A' : 'B';
    if (['pv', 'ups_vfd'].includes(data.loadType)) return 'B';
    return 'A';
  }

  function recommendedForm(data) {
    if (data.goal === 'nuisance' || data.circuitScope === 'single') return 'RCBO';
    return 'RCCB veya devre başına RCBO';
  }

  function recommendedSensitivity(data) {
    if (data.goal === 'personal' || data.goal === 'nuisance') return '30 mA';
    return '100/300 mA seçici üst kademe + alt devrelerde 30 mA';
  }

  function typeMeets(existingType, requiredType) {
    if (!TYPE_RANK.hasOwnProperty(existingType) || !TYPE_RANK.hasOwnProperty(requiredType)) return false;
    return TYPE_RANK[existingType] >= TYPE_RANK[requiredType];
  }

  function evaluate(raw) {
    const data = { ...raw };
    const breakerA = number(data.breakerA);
    const existingRatedA = number(data.existingRatedA);
    if (breakerA < 6 || breakerA > 125) {
      return { ok: false, error: 'Devreyi sınırlayan sigorta/MCB için 6–125 A aralığında geçerli değer girin.' };
    }

    const requiredType = recommendedType(data);
    const form = recommendedForm(data);
    const sensitivity = recommendedSensitivity(data);
    const rccbRatedClass = nextClass(breakerA);
    const stops = [];
    const professional = [];
    const diagnose = [];
    const evidence = [];
    const warnings = [];
    const strengths = [];

    if (data.emergency) stops.push('Duman, erime, su teması veya elektrik çarpması riski varken panoya dokunmayın; yangın veya yaralanmada 112 önceliklidir.');
    if (data.physical !== 'good') stops.push('Pano veya koruma cihazı fiziksel olarak güvenli değil. Enerjiyi zorlamadan yetkili elektrikçi kontrolü gerekir.');
    if (data.testButton === 'fail') stops.push('TEST düğmesi cihazı açtırmıyor. RCD güvenilir kabul edilemez; devre güvenli biçimde kontrol edilmelidir.');
    if (data.installationTest === 'fail') stops.push('İzolasyon, bağlantı veya açma testi başarısız. Ürün seçmeden önce arıza giderilmelidir.');

    if (data.mode === 'active_fault' || data.goal === 'nuisance' || data.taskTest === 'trip') {
      diagnose.push('RCD sürekli atıyorsa daha yüksek mA değeri takmak çözüm değildir; izolasyon, nötr-toprak karışması, cihaz kaçağı ve toplam arka plan kaçağı ölçülmelidir.');
      diagnose.push('Birden fazla devre aynı RCD altındaysa devre başına RCBO ayrımı, arızalı devrenin bulunmasını ve gereksiz toplu kesintinin azaltılmasını sağlayabilir.');
    }

    if (data.useCase === 'commercial' || data.useCase === 'medical') {
      professional.push('Ticari, medikal veya yaşam destek devresinde seçicilik, süreklilik, kaçak akım izleme ve test planı profesyonel projelendirme gerektirir.');
    }
    if (data.phase === 'three') {
      professional.push('Trifaze sistemde kutup sayısı, nötr düzeni, sürücü dalga biçimi ve seçicilik saha verisiyle doğrulanmalıdır.');
    }
    if (data.phase === 'unknown') evidence.push('Besleme fazı ve nötr düzeni bilinmiyor.');
    if (['ev', 'pv', 'ups_vfd'].includes(data.loadType)) {
      professional.push('EV, PV, enerji depolama, UPS veya üç faz sürücüde düzgün DC artık akım ve üretici koruma mimarisi profesyonel doğrulama gerektirir.');
    }
    if (data.loadType === 'ev') {
      if (data.dc6 === 'verified') {
        strengths.push('Şarj cihazında üretici belgesine göre entegre 6 mA DC algılama doğrulanmış; Type A seçeneği ancak üretici ve proje açıkça izin veriyorsa değerlendirilebilir.');
      } else {
        evidence.push('EV şarj cihazında entegre 6 mA DC algılama kanıtı yok; Type B veya üreticinin eşdeğer çözümü doğrulanmalıdır.');
      }
    }
    if (data.loadType === 'unknown') evidence.push('Yükün elektronik/inverter yapısı bilinmiyor; en düşük uygun RCD tipi güvenle belirlenemez.');
    if (data.manufacturerType === 'unknown' && ['single_vfd', 'ev', 'pv', 'ups_vfd'].includes(data.loadType)) {
      evidence.push('Tam model üretici RCD tipi şartı bulunamadı.');
    }

    if (data.goal === 'upstream_fire') {
      if (data.downstream30 !== 'verified') evidence.push('Üst kademe 100/300 mA koruma, alt devrelerdeki 30 mA kişisel korumanın yerine geçmez.');
      warnings.push('Üst kademede seçicilik ve zaman gecikmesi, alt RCD’lerle birlikte projelendirilmelidir.');
    }
    if ((data.goal === 'personal' || data.goal === 'nuisance') && ['100', '300'].includes(String(data.existingMa))) {
      evidence.push('100/300 mA mevcut cihaz, tek başına 30 mA kişisel koruma hedefini karşılamaz.');
    }

    if (data.existingForm === 'RCCB') {
      strengths.push('RCCB yapısı kaçak akım koruması sağlar; ayrı MCB/sigorta ile aşırı akım ve kısa devre koordinasyonu zorunludur.');
    }
    if (data.existingForm === 'RCBO') strengths.push('RCBO tek devrede kaçak akım ve aşırı akım korumasını birleştirir.');
    if (data.existingForm === 'unknown') evidence.push('Mevcut cihazın RCCB mi RCBO mu olduğu bilinmiyor.');

    if (data.existingForm === 'RCCB' && existingRatedA > 0 && existingRatedA < breakerA) {
      evidence.push(`Mevcut RCCB ${existingRatedA} A, devreyi sınırlayan ${breakerA} A korumadan düşük görünüyor; üretici koordinasyonu doğrulanmadan uygun kabul edilmez.`);
    }
    if (data.existingForm !== 'none' && existingRatedA <= 0) evidence.push('Mevcut cihazın anma akımı In bilinmiyor.');
    if (data.existingForm !== 'none' && data.existingMa === 'unknown') evidence.push('Mevcut cihazın IΔn hassasiyeti bilinmiyor.');
    if (data.existingForm !== 'none' && data.existingType === 'unknown') evidence.push('Mevcut cihazın Type AC/A/F/B sınıfı bilinmiyor.');
    if (data.existingForm !== 'none' && data.existingType !== 'unknown' && !typeMeets(data.existingType, requiredType)) {
      evidence.push(`Mevcut ${LABELS[data.existingType]} sınıfı, bu yük için gereken ${LABELS[requiredType]} ön seçimini karşılamıyor.`);
    }
    if (data.existingForm !== 'none' && data.testButton === 'unknown') evidence.push('TEST düğmesi sonucu doğrulanmadı.');
    if (data.existingForm !== 'none' && data.installationTest === 'unknown') evidence.push('Yetkili açma süresi, izolasyon ve bağlantı testi yok.');
    if (data.taskTest === 'not_tested' && data.existingForm !== 'none') evidence.push('Mevcut sistem gerçek kullanımda doğrulanmadı.');

    if (requiredType === 'A') strengths.push('Modern ev elektroniği ve darbeli DC bileşenleri nedeniyle genel ev devrelerinde Type A muhafazakâr ön seçimdir.');
    if (requiredType === 'F') strengths.push('Tek faz frekans kontrollü yük için Type F ön seçimi oluşturuldu; üretici Type A veya B şartı verebilir.');
    if (requiredType === 'B') warnings.push('Type B kararı pahalı bir “daha iyi” ürün seçimi değil, düzgün DC artık akım ihtimaline bağlı uygulama seçimidir.');

    const existingSensitivityPass =
      (data.goal === 'personal' || data.goal === 'nuisance')
        ? String(data.existingMa) === '30' || String(data.existingMa) === '10'
        : ['100', '300'].includes(String(data.existingMa)) && data.downstream30 === 'verified';
    const existingTypePass = data.existingType !== 'unknown' && typeMeets(data.existingType, requiredType);
    const existingRatedPass = data.existingForm === 'RCBO'
      ? existingRatedA === breakerA
      : data.existingForm === 'RCCB' && existingRatedA >= breakerA;
    const existingPass =
      data.existingForm !== 'none' &&
      existingSensitivityPass &&
      existingTypePass &&
      existingRatedPass &&
      data.testButton === 'pass' &&
      data.installationTest === 'pass' &&
      data.taskTest === 'pass' &&
      diagnose.length === 0;

    let status = 'recommend';
    let headline = 'RCD ürün sınıfı ön seçimi hazır';

    if (stops.length) {
      status = 'stop';
      headline = 'Önce enerjiyi güvenli biçimde yönetin ve arızayı giderin';
    } else if (professional.length) {
      status = 'professional';
      headline = 'Tüketici ürün seçimi yerine profesyonel RCD tasarımı gerekli';
    } else if (diagnose.length) {
      status = 'diagnose';
      headline = 'Daha yüksek mA değil, arıza ve kaçak teşhisi gerekli';
    } else if (existingPass && evidence.length === 0) {
      status = 'no-buy';
      headline = 'Mevcut koruma kanıtları yeterli — yeni ürün almayın';
      strengths.push('Tip, hassasiyet, anma akımı ve gerçek açma testleri hedefi karşılıyor.');
    } else if (
      data.loadType === 'unknown' ||
      (data.loadType === 'single_vfd' && data.manufacturerType === 'unknown') ||
      (data.existingForm !== 'none' && evidence.length)
    ) {
      status = 'evidence';
      headline = data.existingForm === 'none'
        ? 'Ürün seçmeden önce yük ve üretici RCD şartını doğrulayın'
        : 'Ürün değiştirmeden önce eksik teknik kanıtları tamamlayın';
    }

    const confirmations = Boolean(data.confirmNeed && data.confirmSpecs && data.confirmAffiliate);
    const affiliateAllowed =
      status === 'recommend' &&
      data.mode === 'planning' &&
      data.useCase === 'home' &&
      data.phase === 'single' &&
      !['ev', 'pv', 'ups_vfd'].includes(data.loadType) &&
      confirmations;

    return {
      ok: true,
      status,
      headline,
      recommendation: {
        type: LABELS[requiredType],
        typeCode: requiredType,
        sensitivity,
        form,
        rccbRatedClass: rccbRatedClass ? `${rccbRatedClass} A veya üstü; üretici koordinasyonuyla` : 'Profesyonel hesap',
        poles: data.phase === 'single' ? '2 kutuplu / 1P+N ürün sistemi ve nötr düzeni doğrulanmalı' : 'Kutup ve nötr düzeni profesyonel doğrulanmalı'
      },
      breakerA,
      existingRatedA,
      stops: [...new Set(stops)],
      professional: [...new Set(professional)],
      diagnose: [...new Set(diagnose)],
      evidence: [...new Set(evidence)],
      warnings: [...new Set(warnings)],
      strengths: [...new Set(strengths)],
      confirmations,
      affiliateAllowed,
      affiliateClass: `${requiredType.toLowerCase()}-${form.toLowerCase().replace(/\s+/g, '-')}`,
      privacy: 'Hesap tarayıcıda yapılır; kişisel veri, konum veya hesap kaydı kullanılmaz.'
    };
  }

  function formDataToObject(form) {
    const entries = Object.fromEntries(new FormData(form).entries());
    for (const name of ['emergency', 'confirmNeed', 'confirmSpecs', 'confirmAffiliate']) {
      entries[name] = Boolean(form.elements[name]?.checked);
    }
    return entries;
  }

  function list(title, items) {
    if (!items.length) return '';
    return `<section><h3>${title}</h3><ul>${items.map((item) => `<li>${item}</li>`).join('')}</ul></section>`;
  }

  function affiliateHref(result) {
    const type = result.recommendation.typeCode.toLowerCase();
    const form = result.recommendation.form.startsWith('RCBO') ? 'rcbo' : 'rccb';
    return `/akilli-urun-secimi?niyet=kacak-akim-koruma&tip=${type}&yapi=${form}`;
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
      ? `<div class="affiliate"><strong>Koşullu ürün sınıfı</strong><p>Yalnız tam model Type, IΔn, In, kutup, kısa devre kapasitesi ve üretici koordinasyonunu yetkili kişiyle yeniden doğrulayarak ilerleyin.</p><a href="${affiliateHref(result)}" rel="sponsored nofollow noopener">Şeffaf RCD ürün sınıfını aç →</a><small>Sonraki dış ürün bağlantılarından komisyon kazanılabilir; kullanıcıya ek maliyet yansımaz.</small></div>`
      : `<div class="affiliate"><strong>Ürün bağlantısı kapalı</strong><p>${result.status === 'no-buy' ? 'Mevcut koruma yeterli olduğu için yeni ürün yolu açılmadı.' : 'Güvenlik, profesyonel tasarım, teşhis veya eksik kanıt nedeniyle ürün yolu açılmadı.'}</p></div>`;

    resultEl.innerHTML = `
      <h2>${result.headline}</h2>
      <div class="summary-grid">
        <div class="metric"><span>RCD tipi</span><strong>${result.recommendation.type}</strong></div>
        <div class="metric"><span>Hassasiyet</span><strong>${result.recommendation.sensitivity}</strong></div>
        <div class="metric"><span>Yapı</span><strong>${result.recommendation.form}</strong></div>
        <div class="metric"><span>RCCB In ön kontrolü</span><strong>${result.recommendation.rccbRatedClass}</strong></div>
      </div>
      <div class="decision"><strong>Kutup ve bağlantı</strong><span>${result.recommendation.poles}</span></div>
      ${list('Acil durdurma', result.stops)}
      ${list('Profesyonel proje sınırı', result.professional)}
      ${list('Arıza ve gereksiz açma teşhisi', result.diagnose)}
      ${list('Eksik kanıtlar', result.evidence)}
      ${list('Uyarılar', result.warnings)}
      ${list('Doğrulanan güçlü yönler', result.strengths)}
      ${affiliate}
      <p class="hint">${result.privacy}</p>
    `;
    resultEl.hidden = false;
    resultEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  const api = { evaluate, recommendedType, recommendedForm, recommendedSensitivity, typeMeets };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;

  if (typeof document !== 'undefined') {
    const form = document.querySelector('#rcdForm');
    let lastResult = null;

    form?.addEventListener('submit', (event) => {
      event.preventDefault();
      lastResult = evaluate(formDataToObject(form));
      render(lastResult);
    });

    form?.addEventListener('reset', () => {
      setTimeout(() => {
        document.querySelector('#result').hidden = true;
        document.querySelector('#error').hidden = true;
        lastResult = null;
      }, 0);
    });

    document.querySelector('#printButton')?.addEventListener('click', () => window.print());

    document.querySelector('#jsonButton')?.addEventListener('click', () => {
      if (!lastResult?.ok) {
        render({ ok: false, error: 'Önce uygunluk değerlendirmesini çalıştırın.' });
        return;
      }
      const blob = new Blob([JSON.stringify(lastResult, null, 2)], { type: 'application/json' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = 'alo186-kacak-akim-rolesi-uygunluk.json';
      link.click();
      URL.revokeObjectURL(link.href);
    });
  }
})();
