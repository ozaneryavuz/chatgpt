(() => {
  'use strict';

  const truthy = (value) => Boolean(value === true || value === 'on' || value === 'true');
  const unique = (items) => [...new Set(items.filter(Boolean))];

  function evaluate(raw) {
    const data = { ...raw };
    const stops = [];
    const professional = [];
    const evidence = [];
    const actions = [];
    const strengths = [];

    if (truthy(data.symptoms)) {
      stops.push('CO alarmı veya baş ağrısı, baş dönmesi, halsizlik, bulantı ya da bilinç değişikliği varsa güvenli biçimde dışarı çıkın ve 112’yi arayın. Ürünü test etmeye veya kaynağı aramaya çalışmayın.');
    }
    if (truthy(data.gasSmell)) {
      stops.push('Gaz kokusunda elektrik anahtarı, priz, telefon veya kıvılcım oluşturabilecek cihaz kullanmayın; dışarı çıkıp güvenli alandan 187 Doğalgaz Acil hattını arayın. Sağlık belirtisinde 112 de aranmalıdır.');
    }
    if (data.combustionSafety === 'problem') {
      stops.push('Baca geri tepmesi, kapalı menfez, arızalı yanma cihazı veya bakım sorunu alarm satın alarak çözülemez; cihazı kullanmayın ve yetkili servis/tesisat kontrolü sağlayın.');
    }

    if (['common', 'commercial', 'medical'].includes(data.useCase)) {
      professional.push('Ortak alan, otel, işyeri, sağlık veya bakım tesisi; yangın/CO algılama, tahliye, bakım ve kayıt planı gerektirir. Tüketici tipi tek alarm yeterli kabul edilemez.');
    }
    if (data.useCase === 'mobile') {
      professional.push('Karavan, tekne veya mobil yaşam alanında kullanım çevresi ve EN 50291-2 benzeri özel ürün uygunluğu tam model belgesiyle doğrulanmalıdır.');
    }
    if (data.existing === 'system') {
      professional.push('Bina sistemine bağlı CO dedektörü; panel, zon/adres, güç kaynağı ve bakım kabulüyle birlikte yetkili kuruluşça değerlendirilmelidir.');
    }
    if (data.source === 'generator') {
      professional.push('Jeneratör CO alarmı, jeneratörün yalnız dışarıda ve güvenli uzaklıkta kullanımının yerine geçmez; egzoz ve bina açıklıkları profesyonel güvenlik planıyla doğrulanmalıdır.');
    }

    const hasSource = ['fuel', 'garage', 'generator', 'multiple'].includes(data.source);
    if (data.source === 'unknown') evidence.push('Yakıtla çalışan cihaz, bitişik garaj, jeneratör veya komşu kaynak riski bilinmiyor.');
    if (data.source === 'none') evidence.push('Bilinen CO kaynağı seçilmedi. Yerel gereklilik, bitişik alanlar ve komşu kaynak riski doğrulanmadan otomatik satın alma veya satın almama kararı verilmez.');
    if (data.combustionSafety === 'unknown') evidence.push('Yakıtlı cihaz bakımı, baca, menfez ve havalandırma kanıtı yok. CO alarmı bu bakımın yerine geçmez.');
    if (data.coverage === 'unknown') evidence.push('Kat ve uyku alanı kapsamı bilinmiyor.');
    if (data.standard !== 'verified') evidence.push('Tam model CO alarm standardı doğrulanmadı. Konut için EN 50291-1 veya uygun eşdeğer belgeyi kontrol edin.');
    if (data.life === 'unknown') evidence.push('Üretim tarihi, ömür sonu sinyali veya üreticinin değiştirme tarihi bilinmiyor.');
    if (data.test === 'unknown') evidence.push('Aylık test düğmesi sonucu doğrulanmadı.');
    if (data.battery === 'unknown') evidence.push('Pil veya yedek enerji durumu bilinmiyor.');
    if (data.placement === 'unknown') evidence.push('Üretici montaj yüksekliği, mesafe ve engel şartı doğrulanmadı.');
    if (data.signal === 'unknown') evidence.push('CO alarmı, düşük pil, arıza ve ömür sonu sinyalleri hane halkınca ayırt edilmiyor.');
    if (data.interconnect === 'unknown') evidence.push('Birbirine bağlı alarm ihtiyacı değerlendirilmedi.');

    if (data.existing === 'gas') actions.push('Yanıcı gaz alarmı CO alarmının yerine geçmez. Her iki tehlike varsa ayrı uygun ürün işlevleri gerekir.');
    if (data.standard === 'wrong') actions.push('CO alarmı için uygun ürün standardı bulunmayan cihazı CO koruması olarak kabul etmeyin.');
    if (data.life === 'expired') actions.push('Ömür sonu sinyali veya üretici değiştirme tarihi geçen CO alarmını yalnız pil değiştirerek kullanmaya devam etmeyin.');
    if (data.test === 'fail') actions.push('Test düğmesi başarısız alarmı güvenilir kabul etmeyin; üretici talimatına göre değiştirin veya yetkili kontrol sağlayın.');
    if (data.battery === 'low') actions.push('Düşük pil/arıza sinyalini susturmayın; üretici talimatına göre pili veya mühürlü alarmı değiştirin.');
    if (data.placement === 'wrong') actions.push('Alarmı kapalı dolap, engelli hava bölgesi veya üretici talimatına aykırı yerde bırakmayın; doğru konumu belgeyle doğrulayın.');
    if (['partial', 'none'].includes(data.coverage)) actions.push('Eksik kat veya uyku alanı kapsamını üretici ve yerel gerekliliğe göre tamamlayın.');
    if (data.interconnect === 'missing') actions.push('Birden fazla alarm gereken planda uyumlu birbirine bağlı uyarı ihtiyacını doğrulayın.');

    const existingTypePass = ['co', 'combo'].includes(data.existing);
    if (existingTypePass) strengths.push('Mevcut cihaz CO alarmı işlevi taşıyor.');
    if (data.standard === 'verified') strengths.push('Tam model CO alarm standardı doğrulanmış.');
    if (data.test === 'pass') strengths.push('Aylık testte sesli/görsel uyarı çalışmış.');
    if (['good', 'sealed'].includes(data.battery)) strengths.push('Pil veya yedek enerji durumu normal.');
    if (data.placement === 'verified') strengths.push('Yerleşim tam model üretici kılavuzuyla doğrulanmış.');
    if (data.signal === 'verified') strengths.push('CO, düşük pil ve ömür sonu sinyalleri biliniyor.');

    const existingPass = existingTypePass
      && data.coverage === 'full'
      && data.standard === 'verified'
      && data.life === 'valid'
      && data.test === 'pass'
      && ['good', 'sealed'].includes(data.battery)
      && data.placement === 'verified'
      && data.signal === 'verified'
      && ['verified', 'not_needed'].includes(data.interconnect)
      && data.combustionSafety === 'verified';

    let status = 'recommend';
    let headline = 'Ev tipi CO alarmı sınıfı için ön seçim hazır';
    if (stops.length) {
      status = 'stop';
      headline = 'Önce temiz hava, 112 ve gerekiyorsa 187';
    } else if (professional.length) {
      status = 'professional';
      headline = 'Tüketici alarmı yerine profesyonel CO güvenliği planı gerekli';
    } else if (existingPass) {
      status = 'no-buy';
      headline = 'Mevcut CO alarmı kanıtları yeterli — yeni ürün almayın';
    } else if (evidence.length && data.existing !== 'none' && !['fail', 'expired', 'low', 'wrong'].includes(data.test)) {
      status = 'evidence';
      headline = 'Alarm değiştirmeden önce eksik teknik kanıtları tamamlayın';
    } else if (!hasSource) {
      status = 'evidence';
      headline = 'Önce CO kaynağı ve yerel gerekliliği doğrulayın';
    }

    const confirmations = truthy(data.confirmNeed) && truthy(data.confirmSpecs) && truthy(data.confirmAffiliate);
    const affiliateAllowed = status === 'recommend'
      && data.useCase === 'home'
      && hasSource
      && confirmations;

    return {
      ok: true,
      status,
      headline,
      recommendation: {
        code: 'co-alarm',
        label: 'EN 50291-1 veya Türkiye’de uygun eşdeğer belgesi doğrulanmış ev tipi CO alarmı',
        source: data.source,
        coverage: data.coverage
      },
      stops: unique(stops),
      professional: unique(professional),
      evidence: unique(evidence),
      actions: unique(actions),
      strengths: unique(strengths),
      affiliateAllowed,
      confirmations,
      existingPass,
      privacy: 'Hesap tarayıcıda yapılır; ad, adres, konum, sağlık kaydı veya hesap bilgisi kullanılmaz.'
    };
  }

  function fromForm(form) {
    const data = Object.fromEntries(new FormData(form).entries());
    for (const name of ['symptoms', 'gasSmell', 'confirmNeed', 'confirmSpecs', 'confirmAffiliate']) data[name] = Boolean(form.elements[name]?.checked);
    return data;
  }

  const list = (title, items) => items.length ? `<section><h3>${title}</h3><ul>${items.map((item) => `<li>${item}</li>`).join('')}</ul></section>` : '';

  function render(result) {
    const output = document.querySelector('#result');
    const error = document.querySelector('#error');
    if (!result.ok) {
      error.textContent = result.error || 'Sonuç üretilemedi.';
      error.hidden = false;
      output.hidden = true;
      return;
    }
    error.hidden = true;
    output.hidden = false;
    output.dataset.status = result.status;
    const affiliate = result.affiliateAllowed
      ? `<div class="affiliate"><strong>Koşullu ürün sınıfı</strong><p>Bu bağlantı Amazon satış ortaklığı içerebilir. ALO186 fiyat, stok, puan, satıcı veya garanti yayımlamaz. EN 50291 uygunluğunu, kullanım alanını, pil/yedek enerji biçimini ve üretici yerleşimini mağazada yeniden doğrulayın.</p><a href="/akilli-urun-secimi?niyet=karbonmonoksit-alarmi&sinif=ev-tipi" rel="sponsored nofollow noopener">Ev tipi CO alarmı sınıfını karşılaştır</a></div>`
      : `<div class="affiliate"><strong>Ürün bağlantısı kapalı</strong><p>Belirti, alarm, gaz/baca sorunu, profesyonel kapsam, yeterli mevcut cihaz veya eksik teknik kanıt varken satın alma önerilmez.</p></div>`;
    output.innerHTML = `<h2>${result.headline}</h2><div class="summary-grid"><div class="metric"><span>Ürün görevi</span><strong>${result.recommendation.label}</strong></div><div class="metric"><span>Sonuç</span><strong>${result.status}</strong></div><div class="metric"><span>Affiliate</span><strong>${result.affiliateAllowed ? 'Açık ve etiketli' : 'Kapalı'}</strong></div></div>${list('Acil durdurma', result.stops)}${list('Profesyonel kapsam', result.professional)}${list('Eksik kanıt', result.evidence)}${list('Yapılacaklar', result.actions)}${list('Korunan mevcut kanıtlar', result.strengths)}${affiliate}<p class="hint">${result.privacy}</p><div class="actions"><button type="button" id="printResult">Yazdır / PDF</button><button type="button" class="ghost" id="downloadResult">JSON sonucu indir</button></div>`;
    output.querySelector('#printResult').addEventListener('click', () => window.print());
    output.querySelector('#downloadResult').addEventListener('click', () => {
      const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = 'alo186-karbonmonoksit-alarmi-sonucu.json';
      link.click();
      URL.revokeObjectURL(link.href);
    });
    output.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
  }

  if (typeof module !== 'undefined' && module.exports) module.exports = { evaluate };
  if (typeof document !== 'undefined') {
    const form = document.querySelector('#coForm');
    if (form) {
      form.addEventListener('submit', (event) => { event.preventDefault(); render(evaluate(fromForm(form))); });
      form.addEventListener('reset', () => setTimeout(() => { document.querySelector('#result').hidden = true; document.querySelector('#error').hidden = true; }, 0));
    }
  }
})();