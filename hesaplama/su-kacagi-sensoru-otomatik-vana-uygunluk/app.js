(() => {
  'use strict';

  const truthy = (value) => Boolean(value === true || value === 'on' || value === 'true');
  const unique = (items) => [...new Set(items.filter(Boolean))];

  function recommendationFor(data) {
    if (data.goal === 'shutoff' || data.source === 'whole_home') {
      return { code: 'flow-shutoff', label: 'Akış izleme ve tesisatçı tarafından doğrulanmış otomatik kapatma çözümü' };
    }
    if (data.goal === 'remote') {
      return { code: 'smart-leak-sensor', label: 'Yerel alarmı da bulunan uzaktan bildirimli su kaçağı sensörü' };
    }
    if (['sink', 'washer', 'dishwasher', 'heater', 'fridge', 'boiler'].includes(data.source)) {
      return { code: 'point-leak-alarm', label: 'Risk noktasına uygun yerel su kaçağı alarmı' };
    }
    return { code: 'leak-detection', label: 'Risk noktası belirlendikten sonra uygun su kaçağı algılama sınıfı' };
  }

  function evaluate(raw) {
    const data = { ...raw };
    const recommendation = recommendationFor(data);
    const stops = [];
    const professional = [];
    const evidence = [];
    const actions = [];
    const strengths = [];

    if (truthy(data.emergency)) {
      stops.push('Su elektrikli ekipmana ulaştıysa ıslak zeminde priz, pano, anahtar veya cihaz kullanmayın. Elektrik çarpması, duman veya yangın riski varsa güvenli alandan 112’yi arayın.');
    }
    if (['common', 'commercial', 'critical'].includes(data.useCase)) {
      professional.push('Ortak alan, otel, işyeri, server, sağlık veya kritik tesis; tüketici tipi tek sensörle çözülemez. Tesisat, BMS/alarm, elektrik güvenliği ve bakım planı profesyonel kapsam gerektirir.');
    }
    if (data.goal === 'shutoff' || data.source === 'whole_home') {
      if (data.valve !== 'verified') professional.push('Ana su hattında otomatik kapatma için vana tipi, ölçü, basınç, boru malzemesi, manuel kullanım ve bakım erişimi tesisatçı tarafından doğrulanmalıdır.');
      if (data.shutoffTest === 'fail') professional.push('Otomatik vana kontrollü testte kapanmadı veya manuel açma başarısız. Sistemi güvenilir kabul etmeyin; tesisatçı kontrolü gerekir.');
    }
    if (data.valve === 'incompatible') professional.push('Uyumsuz veya manuel kullanımı engelleyen vana aktüatörü kullanılmamalıdır.');
    if (data.source === 'unknown') evidence.push('Kaçağın en olası kaynağı ve suyun ilk birikeceği nokta belirlenmedi.');
    if (data.existing === 'unknown') evidence.push('Mevcut sensörün yerel alarm, bildirim veya vana işlevi bilinmiyor.');
    if (data.coverage === 'unknown') evidence.push('Çamaşır/bulaşık makinesi, lavabo, termosifon, buzdolabı hattı ve kombi çevresi kapsamı doğrulanmadı.');
    if (data.test === 'unknown') evidence.push('Üreticinin izin verdiği kontrollü su testi yapılmadı.');
    if (data.power === 'unknown') evidence.push('Pil, şebeke veya yedek enerji durumu bilinmiyor.');
    if (data.placement === 'unknown') evidence.push('Sensörün suyun ilk birikeceği noktaya yerleşimi doğrulanmadı.');
    if (data.notification === 'unknown') evidence.push('Yerel sesli alarm veya uzaktan bildirim yolu test edilmedi.');
    if (data.offline === 'unknown') evidence.push('İnternet kesildiğinde gereken yerel alarm işlevi belirlenmedi.');
    if ((data.goal === 'shutoff' || data.source === 'whole_home') && data.shutoffTest === 'unknown') evidence.push('Otomatik kapatma ve manuel yeniden açma kontrollü test edilmedi.');

    if (data.test === 'fail') actions.push('Alarm veya bildirim başarısız cihazı güvenilir kabul etmeyin; pil, temas noktası, uygulama ve tam model kılavuzunu kontrol edin.');
    if (data.power === 'low') actions.push('Düşük pil veya güç sorununu giderin ve ardından gerçek su testini tekrarlayın.');
    if (data.placement === 'blocked') actions.push('Sensörü zeminden koparan ayak, halı, kablo veya yanlış yükseklik varsa suyun ilk birikeceği noktaya göre yeniden yerleştirin.');
    if (data.coverage === 'none' || data.coverage === 'partial') actions.push('Risk noktalarını tek tek haritalayın; bir sensörün farklı odalardaki kaçakları algılayacağı varsayılmamalıdır.');
    if (data.goal === 'remote' && !['remote', 'both'].includes(data.notification)) actions.push('Uzaktan bildirim ihtiyacı için uygulama, internet ve bulut hizmeti kesildiğinde ne olacağını tam modelde doğrulayın.');
    if (data.offline === 'local' && !['local', 'both'].includes(data.notification)) actions.push('İnternet olmadan da çalışan yerel sesli alarmı doğrulayın.');
    if (data.goal === 'shutoff' && data.shutoffTest !== 'pass') actions.push('Otomatik kapatmayı güvenli ve kontrollü koşulda, tesisatçıyla birlikte gerçek vana üzerinde test edin.');

    const existingPass = data.existing !== 'none'
      && data.existing !== 'unknown'
      && data.coverage === 'full'
      && data.test === 'pass'
      && ['good', 'mains_backup'].includes(data.power)
      && data.placement === 'verified'
      && (
        (data.offline === 'remote_only' && ['remote', 'both'].includes(data.notification))
        || (data.offline === 'local' && ['local', 'both'].includes(data.notification))
        || (data.offline === 'both' && data.notification === 'both')
      )
      && (!(data.goal === 'shutoff' || data.source === 'whole_home') || (data.valve === 'verified' && data.shutoffTest === 'pass'));

    if (data.test === 'pass') strengths.push('Kontrollü su testinde alarm veya bildirim çalıştı.');
    if (data.coverage === 'full') strengths.push('Kritik risk noktalarının kapsamı doğrulandı.');
    if (['good', 'mains_backup'].includes(data.power)) strengths.push('Pil veya güç durumu normal.');
    if (data.placement === 'verified') strengths.push('Sensör suyun ilk birikeceği noktada.');
    if (data.notification === 'both') strengths.push('Yerel ve uzaktan uyarı birlikte test edildi.');
    if (data.valve === 'verified' && data.shutoffTest === 'pass') strengths.push('Vana uyumu, otomatik kapatma ve manuel yeniden açma test edildi.');

    let status = 'recommend';
    let headline = `${recommendation.label} için ön seçim hazır`;
    if (stops.length) {
      status = 'stop';
      headline = 'Önce su-elektrik tehlikesini güvenli biçimde ayırın';
    } else if (professional.length) {
      status = 'professional';
      headline = 'Tüketici sensörü yerine profesyonel tesisat ve elektrik güvenliği planı gerekli';
    } else if (existingPass) {
      status = 'no-buy';
      headline = 'Mevcut kaçak algılama kanıtları yeterli — yeni ürün almayın';
    } else if (evidence.length && data.existing !== 'none') {
      status = 'evidence';
      headline = 'Yeni cihaz almadan önce eksik test ve kapsam kanıtlarını tamamlayın';
    }

    const confirmations = truthy(data.confirmNeed) && truthy(data.confirmSpecs) && truthy(data.confirmAffiliate);
    const affiliateAllowed = status === 'recommend'
      && ['home', 'second_home'].includes(data.useCase)
      && data.source !== 'unknown'
      && confirmations
      && !(data.goal === 'shutoff' && data.valve !== 'verified');

    return {
      ok: true,
      status,
      headline,
      recommendation,
      stops: unique(stops),
      professional: unique(professional),
      evidence: unique(evidence),
      actions: unique(actions),
      strengths: unique(strengths),
      existingPass,
      confirmations,
      affiliateAllowed,
      privacy: 'Hesap tarayıcıda yapılır; ad, adres, konum, tesisat fotoğrafı veya hesap kaydı kullanılmaz.'
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
    error.hidden = true;
    output.hidden = false;
    output.dataset.status = result.status;
    const affiliate = result.affiliateAllowed
      ? `<div class="affiliate"><strong>Koşullu ürün sınıfı</strong><p>Bu bağlantı Amazon satış ortaklığı içerebilir. ALO186 fiyat, stok, puan, satıcı veya garanti yayımlamaz. Tam model pil, yerel alarm, bağlantı ve tesisat uyumunu mağazada yeniden doğrulayın.</p><a href="/akilli-urun-secimi?niyet=su-kacagi&sinif=${result.recommendation.code}" rel="sponsored nofollow noopener">${result.recommendation.label} sınıfını karşılaştır</a></div>`
      : `<div class="affiliate"><strong>Ürün bağlantısı kapalı</strong><p>Aktif su-elektrik tehlikesi, profesyonel kapsam, yeterli mevcut çözüm veya eksik teknik kanıt varken satın alma önerilmez.</p></div>`;
    output.innerHTML = `<h2>${result.headline}</h2><div class="summary-grid"><div class="metric"><span>Önerilen görev</span><strong>${result.recommendation.label}</strong></div><div class="metric"><span>Sonuç</span><strong>${result.status}</strong></div><div class="metric"><span>Affiliate</span><strong>${result.affiliateAllowed ? 'Açık ve etiketli' : 'Kapalı'}</strong></div></div>${list('Acil durdurma', result.stops)}${list('Profesyonel kapsam', result.professional)}${list('Eksik kanıt', result.evidence)}${list('Yapılacaklar', result.actions)}${list('Korunan mevcut kanıtlar', result.strengths)}${affiliate}<p class="hint">${result.privacy}</p><div class="actions"><button type="button" id="printResult">Yazdır / PDF</button><button type="button" class="ghost" id="downloadResult">JSON sonucu indir</button></div>`;
    output.querySelector('#printResult').addEventListener('click', () => window.print());
    output.querySelector('#downloadResult').addEventListener('click', () => {
      const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = 'alo186-su-kacagi-sensoru-sonucu.json';
      link.click();
      URL.revokeObjectURL(link.href);
    });
    output.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
  }

  if (typeof module !== 'undefined' && module.exports) module.exports = { evaluate };
  if (typeof document !== 'undefined') {
    const form = document.querySelector('#leakForm');
    if (form) {
      form.addEventListener('submit', (event) => { event.preventDefault(); render(evaluate(fromForm(form))); });
      form.addEventListener('reset', () => setTimeout(() => { document.querySelector('#result').hidden = true; document.querySelector('#error').hidden = true; }, 0));
    }
  }
})();