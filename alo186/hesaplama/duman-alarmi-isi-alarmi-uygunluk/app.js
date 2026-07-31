(() => {
  'use strict';

  const ROOM_CLASS = {
    bedroom: { code: 'smoke', label: 'EN 14604 sınıfı bağımsız duman alarmı' },
    corridor: { code: 'smoke', label: 'EN 14604 sınıfı bağımsız duman alarmı' },
    living: { code: 'smoke', label: 'EN 14604 sınıfı bağımsız duman alarmı' },
    kitchen: { code: 'heat', label: 'Mutfak için üretici ve yerel tasarımla doğrulanmış ısı alarmı' },
    garage: { code: 'heat', label: 'Garaj/teknik hacim için profesyonel olarak doğrulanmış ısı alarmı' },
    bathroom: { code: 'special', label: 'Buhar ve neme uygun profesyonel alarm yerleşimi' },
    attic: { code: 'special', label: 'Sıcaklık, toz ve çevre sınıfı doğrulanmış profesyonel alarm' }
  };

  const truthy = (value) => Boolean(value === true || value === 'on' || value === 'true');
  const unique = (items) => [...new Set(items.filter(Boolean))];

  function evaluate(raw) {
    const data = { ...raw };
    const room = ROOM_CLASS[data.room] || ROOM_CLASS.living;
    const stops = [];
    const professional = [];
    const evidence = [];
    const actions = [];
    const strengths = [];

    if (truthy(data.emergency)) {
      stops.push('Aktif duman, alev, yoğun ısı veya gerçek alarm şüphesinde güvenli biçimde dışarı çıkın ve 112’yi arayın. Ürün seçimi yapmayın.');
    }
    if (['common', 'commercial', 'medical'].includes(data.useCase)) {
      professional.push('Ortak alan, otel, işyeri, okul, sağlık veya bakım tesisi bağımsız tüketici alarmıyla çözülemez; yangın algılama ve tahliye sistemi profesyonel tasarım ve periyodik test gerektirir.');
    }
    if (data.existing === 'system') {
      professional.push('Mevcut cihaz bina yangın alarm sistemine bağlı. Dedektör değişimi, adresleme, zon ve panel kabulü yetkili bakım kuruluşunca yapılmalıdır.');
    }
    if (data.accessibility !== 'none') {
      professional.push('İşitme kaybı, gece uyarısı veya tahliye desteği için flaşör, yatak titreştirici, düşük frekanslı uyarı ve birbirine bağlı alarm sistemi erişilebilirlik planıyla seçilmelidir.');
    }
    if (room.code === 'special') {
      professional.push(`${room.label}; sıradan ev tipi duman alarmı bu çevre için otomatik olarak uygun kabul edilmez.`);
    }
    if (data.room === 'garage') {
      professional.push('Kapalı garajda egzoz, sıcaklık ve yangın algılama görevi birlikte değerlendirilmelidir; duman alarmı CO alarmının yerine geçmez.');
    }

    if (data.standard !== 'verified') evidence.push('Tam model ürün standardı ve uygunluk belgesi doğrulanmadı. Duman alarmında EN 14604 veya yerel eşdeğer ürün standardını belge üzerinden kontrol edin.');
    if (data.life === 'unknown') evidence.push('Üretim tarihi, ömür sonu sinyali veya üreticinin değiştirme tarihi bilinmiyor.');
    if (data.test === 'unknown') evidence.push('Test düğmesi sonucu doğrulanmadı.');
    if (data.battery === 'unknown') evidence.push('Pil veya yedek enerji durumu bilinmiyor.');
    if (data.placement === 'unknown') evidence.push('Tam model yerleşim kılavuzu ve yerel gereklilik doğrulanmadı.');
    if (data.coverage === 'unknown') evidence.push('Uyku alanı ve kaçış rotası kapsamı bilinmiyor.');
    if (data.interconnect === 'unknown') evidence.push('Birbirine bağlı uyarı ihtiyacı değerlendirilmedi.');

    if (data.test === 'fail') actions.push('Test düğmesi başarısız alarmı güvenilir kabul etmeyin; üretici talimatına göre değişim veya yetkili kontrol planlayın.');
    if (data.life === 'expired') actions.push('Ömür sonu sinyali veya üretici değiştirme tarihi geçmiş cihazı yalnız pil değiştirerek kullanmaya devam etmeyin.');
    if (data.battery === 'low') actions.push('Düşük pil/arıza uyarısını susturmayın; üretici talimatına göre pili veya mühürlü cihazı değiştirin.');
    if (data.placement === 'blocked') actions.push('Alarmı buhar, hava akımı, köşe, kiriş veya engel etkisinden uzaklaştırmak için tam model kılavuzunu uygulayın.');
    if (data.coverage === 'none' || data.coverage === 'partial') actions.push('Eksik uyku alanı veya kat kapsamını tamamlayın; tek cihazın bütün konutu kapsadığı varsayılmamalıdır.');
    if (data.interconnect === 'missing') actions.push('Birden fazla alarm gereken planda uyumlu bağlantı ihtiyacını üretici ve yerel kuralla doğrulayın.');

    const expectedExisting = room.code === 'smoke'
      ? ['smoke', 'combo'].includes(data.existing)
      : room.code === 'heat' && data.existing === 'heat';

    if (data.goal === 'nuisance') {
      if (data.room === 'kitchen' && ['smoke', 'combo'].includes(data.existing)) {
        actions.push('Pişirme kaynaklı yanlış alarmı pili çıkararak çözmeyin; mutfak için uygun ısı alarmı veya üreticinin yanlış alarm azaltıcı çözümünü değerlendirin.');
      } else if (data.room === 'bathroom') {
        professional.push('Yoğun buhar alanında alarm türü ve mesafesi profesyonel yerleşim gerektirir.');
      } else {
        actions.push('Yanlış alarm kaynağı, kirlenme, konum ve tam model kılavuzu doğrulanmadan alarmı devre dışı bırakmayın.');
      }
    }

    if (expectedExisting) strengths.push('Mevcut alarm türü alanın temel görev sınıfıyla uyumlu görünüyor.');
    if (data.standard === 'verified') strengths.push('Tam model ürün standardı belgeden doğrulanmış.');
    if (data.test === 'pass') strengths.push('Aylık testte sesli/görsel uyarı çalışmış.');
    if (['good', 'sealed'].includes(data.battery)) strengths.push('Pil veya yedek enerji durumu normal.');
    if (data.placement === 'verified') strengths.push('Yerleşim tam model kılavuzu ve yerel gereklilikle doğrulanmış.');

    const existingPass = expectedExisting
      && data.coverage === 'full'
      && data.standard === 'verified'
      && data.life === 'valid'
      && data.test === 'pass'
      && ['good', 'sealed'].includes(data.battery)
      && data.placement === 'verified'
      && ['verified', 'not_needed'].includes(data.interconnect);

    let status = 'recommend';
    let headline = `${room.label} için ön seçim hazır`;
    if (stops.length) {
      status = 'stop';
      headline = 'Önce tahliye ve 112';
    } else if (professional.length) {
      status = 'professional';
      headline = 'Tüketici alarmı yerine profesyonel yangın güvenliği planı gerekli';
    } else if (existingPass) {
      status = 'no-buy';
      headline = 'Mevcut alarm kanıtları yeterli — yeni ürün almayın';
    } else if (evidence.length && !['fail', 'expired', 'low', 'blocked'].includes(data.test) && data.existing !== 'none') {
      status = 'evidence';
      headline = 'Alarm değiştirmeden önce eksik kanıtları tamamlayın';
    }

    const confirmations = truthy(data.confirmNeed) && truthy(data.confirmSpecs) && truthy(data.confirmAffiliate);
    const affiliateAllowed = status === 'recommend'
      && data.useCase === 'home'
      && ['smoke', 'heat'].includes(room.code)
      && confirmations;

    return {
      ok: true,
      status,
      headline,
      recommendation: room,
      stops: unique(stops),
      professional: unique(professional),
      evidence: unique(evidence),
      actions: unique(actions),
      strengths: unique(strengths),
      affiliateAllowed,
      confirmations,
      existingPass,
      privacy: 'Hesap tarayıcıda yapılır; ad, adres, konum veya hesap kaydı kullanılmaz.'
    };
  }

  function fromForm(form) {
    const data = Object.fromEntries(new FormData(form).entries());
    for (const name of ['emergency', 'confirmNeed', 'confirmSpecs', 'confirmAffiliate']) data[name] = Boolean(form.elements[name]?.checked);
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
      ? `<div class="affiliate"><strong>Koşullu ürün sınıfı</strong><p>Bu bağlantı Amazon satış ortaklığı içerebilir. ALO186 fiyat, stok, puan, satıcı veya garanti yayımlamaz. Tam model standardını ve yerleşim kılavuzunu mağazada yeniden doğrulayın.</p><a href="/akilli-urun-secimi?niyet=ev-alarmi&sinif=${result.recommendation.code}" rel="sponsored nofollow noopener">${result.recommendation.label} sınıfını karşılaştır</a></div>`
      : `<div class="affiliate"><strong>Ürün bağlantısı kapalı</strong><p>Tehlike, profesyonel kapsam, yeterli mevcut alarm veya eksik teknik kanıt varken satın alma önerilmez.</p></div>`;
    output.innerHTML = `<h2>${result.headline}</h2><div class="summary-grid"><div class="metric"><span>Alarm görevi</span><strong>${result.recommendation.label}</strong></div><div class="metric"><span>Sonuç</span><strong>${result.status}</strong></div><div class="metric"><span>Affiliate</span><strong>${result.affiliateAllowed ? 'Açık ve etiketli' : 'Kapalı'}</strong></div></div>${list('Acil durdurma', result.stops)}${list('Profesyonel kapsam', result.professional)}${list('Eksik kanıt', result.evidence)}${list('Yapılacaklar', result.actions)}${list('Korunan mevcut kanıtlar', result.strengths)}${affiliate}<p class="hint">${result.privacy}</p><div class="actions"><button type="button" id="printResult">Yazdır / PDF</button><button type="button" class="ghost" id="downloadResult">JSON sonucu indir</button></div>`;
    output.querySelector('#printResult').addEventListener('click', () => window.print());
    output.querySelector('#downloadResult').addEventListener('click', () => {
      const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = 'alo186-duman-isi-alarmi-sonucu.json';
      link.click();
      URL.revokeObjectURL(link.href);
    });
    output.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
  }

  if (typeof module !== 'undefined' && module.exports) module.exports = { evaluate };
  if (typeof document !== 'undefined') {
    const form = document.querySelector('#alarmForm');
    if (form) {
      form.addEventListener('submit', (event) => { event.preventDefault(); render(evaluate(fromForm(form))); });
      form.addEventListener('reset', () => setTimeout(() => { document.querySelector('#result').hidden = true; document.querySelector('#error').hidden = true; }, 0));
    }
  }
})();