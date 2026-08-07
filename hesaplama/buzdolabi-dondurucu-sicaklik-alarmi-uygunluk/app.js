(() => {
  'use strict';

  const truthy = (value) => Boolean(value === true || value === 'on' || value === 'true');
  const unique = (items) => [...new Set(items.filter(Boolean))];

  function recommendationFor(data) {
    if (data.goal === 'remote') return { code: 'remote-temperature-alarm', label: 'Yerel kayıt ve alarmı da bulunan uzaktan sıcaklık izleme sınıfı' };
    if (data.goal === 'alarm') return { code: 'fridge-freezer-temperature-alarm', label: 'Yüksek sıcaklık alarmı ve min/max hafızalı cihaz termometresi' };
    return { code: 'appliance-thermometer', label: 'Buzdolabı/dondurucu için bağımsız cihaz termometresi' };
  }

  function evaluate(raw) {
    const data = { ...raw };
    const recommendation = recommendationFor(data);
    const stops = [];
    const professional = [];
    const evidence = [];
    const actions = [];
    const strengths = [];

    if (truthy(data.activeOutage)) {
      stops.push('Aktif kesinti veya arızada yeni ürün teslimatı çözüm değildir. Kapıları gereksiz açmayın, mevcut sıcaklık kanıtını okuyun ve resmî gıda güvenliği rehberini uygulayın.');
    }
    if (['commercial', 'medical'].includes(data.useCase)) {
      professional.push('Restoran, otel, ticari mutfak, ilaç, aşı, laboratuvar veya sağlık ürünü için tüketici tipi termometre tek başına yeterli değildir; kayıt, kalibrasyon, alarm, mevzuat ve yedek güç profesyonel kapsam gerektirir.');
    }

    const fridgeRelevant = ['fridge', 'both'].includes(data.appliance);
    const freezerRelevant = ['freezer', 'both'].includes(data.appliance);
    if (fridgeRelevant && data.fridgeTemp === 'borderline') actions.push('Buzdolabı 4°C üzerinde ölçüldüyse ürün seçmeden önce resmî gıda güvenliği rehberine göre süre ve gıda durumunu değerlendirin; koku veya görünüşe güvenmeyin.');
    if (freezerRelevant && data.freezerTemp === 'warmer') actions.push('Dondurucu -18°C üzerinde ölçüldüyse sıcaklık, buz kristali ve kesinti süresini resmî gıda güvenliği rehberiyle değerlendirin.');
    if (fridgeRelevant && data.fridgeTemp === 'unknown') evidence.push('Buzdolabında bağımsız sıcaklık ölçümü yok.');
    if (freezerRelevant && data.freezerTemp === 'unknown') evidence.push('Dondurucuda bağımsız sıcaklık ölçümü yok.');
    if (data.outageKnowledge === 'unknown') evidence.push('Kesinti başlangıcı ve süresi bilinmiyor; min/max hafıza veya olay kaydı ihtiyacı artıyor.');
    if (data.existing === 'unknown') evidence.push('Mevcut ekran/termometrenin neyi ölçtüğü ve kesintide çalışıp çalışmadığı bilinmiyor.');
    if (data.validation === 'unknown') evidence.push('Termometre veya cihaz ekranı bağımsız bir yöntemle doğrulanmadı.');
    if (data.power === 'unknown') evidence.push('Termometre/alarm pil durumu bilinmiyor.');
    if (data.placement === 'unknown') evidence.push('Sensörün kapı, soğuk hava çıkışı veya duvar etkisinden uzak yerleşimi doğrulanmadı.');
    if (data.realTest === 'unknown') evidence.push('Gerçek kesinti veya kontrollü kapı/açılma testinde kayıt davranışı doğrulanmadı.');
    if (data.goal === 'alarm' && data.alarmTest === 'unknown') evidence.push('Yüksek sıcaklık alarmı üretici yönteminde test edilmedi.');
    if (data.goal === 'remote' && data.remote === 'unknown') evidence.push('İnternet, modem veya bulut kesildiğinde bildirim ve yerel hafıza davranışı bilinmiyor.');
    if (['alarm', 'remote'].includes(data.goal) && data.memory === 'unknown') evidence.push('Min/max hafıza veya olay kaydı işlevi bilinmiyor.');

    if (data.validation === 'fail') actions.push('Belirgin sapma gösteren termometreyi güvenilir karar kaynağı saymayın; üretici talimatı, pil ve bağımsız referansla yeniden kontrol edin.');
    if (data.alarmTest === 'fail') actions.push('Yüksek sıcaklık alarmı başarısız cihazı güvenilir kabul etmeyin.');
    if (data.memory === 'missing' && ['alarm', 'remote'].includes(data.goal)) actions.push('Evden uzakta veya kesinti kanıtında min/max hafıza ya da olay kaydı ihtiyacını değerlendirin.');
    if (data.power === 'low') actions.push('Düşük pili değiştirin ve ardından alarm/ölçüm testini tekrarlayın.');
    if (data.placement === 'blocked') actions.push('Sensörü kapıya, doğrudan hava çıkışına veya duvara yapışık yanlış noktadan çıkarıp üretici kılavuzuna göre yerleştirin.');
    if (data.remote === 'fail') actions.push('Uzaktan bildirim başarısızsa ürünü tek güvenlik katmanı saymayın; yerel alarm ve hafıza işlevini koruyun.');
    if (data.realTest === 'fail') actions.push('Gerçek kesinti veya kapı testinde ihtiyacı karşılamayan sistemi yeniden yapılandırın; yalnız uygulama ekranına güvenmeyin.');

    const localMeasurementPass = data.existing !== 'none'
      && data.existing !== 'unknown'
      && data.validation === 'pass'
      && data.power === 'good'
      && data.placement === 'verified'
      && data.realTest === 'pass';

    const goalPass = data.goal === 'check'
      || (data.goal === 'alarm' && data.alarmTest === 'pass' && ['pass', 'not_needed'].includes(data.memory))
      || (data.goal === 'remote' && data.remote === 'pass' && data.memory === 'pass')
      || (data.goal === 'replace' && data.alarmTest === 'pass');

    const temperaturePass = (!fridgeRelevant || data.fridgeTemp === 'safe')
      && (!freezerRelevant || data.freezerTemp === 'safe');

    const existingPass = localMeasurementPass && goalPass && temperaturePass;

    if (data.validation === 'pass') strengths.push('Termometre veya ekran bağımsız yöntemle makul sonuç verdi.');
    if (temperaturePass) strengths.push('Seçilen cihazlarda hedef sıcaklık ölçümü doğrulandı.');
    if (data.alarmTest === 'pass') strengths.push('Yüksek sıcaklık alarmı üretici yönteminde çalıştı.');
    if (data.memory === 'pass') strengths.push('Min/max hafıza veya olay kaydı çalışıyor.');
    if (data.remote === 'pass') strengths.push('Uzaktan bildirim ve bağlantı kaybı davranışı test edildi.');
    if (data.realTest === 'pass') strengths.push('Kontrollü gerçek kullanım testinde sıcaklık kaydı alındı.');

    let status = 'recommend';
    let headline = `${recommendation.label} için ön seçim hazır`;
    if (stops.length) {
      status = 'stop';
      headline = 'Önce aktif kesinti ve gıda güvenliği kararını tamamlayın';
    } else if (professional.length) {
      status = 'professional';
      headline = 'Tüketici termometresi yerine profesyonel soğuk zincir planı gerekli';
    } else if (existingPass) {
      status = 'no-buy';
      headline = 'Mevcut sıcaklık izleme kanıtları yeterli — yeni ürün almayın';
    } else if (evidence.length && data.existing !== 'none') {
      status = 'evidence';
      headline = 'Yeni cihaz almadan önce eksik sıcaklık ve alarm kanıtlarını tamamlayın';
    }

    const confirmations = truthy(data.confirmNeed) && truthy(data.confirmSpecs) && truthy(data.confirmAffiliate);
    const affiliateAllowed = status === 'recommend'
      && ['home', 'second_home'].includes(data.useCase)
      && confirmations
      && !truthy(data.activeOutage);

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
      thresholds: { refrigeratorC: 4, freezerC: -18 },
      privacy: 'Hesap tarayıcıda yapılır; ad, adres, gıda listesi, sağlık kaydı veya hesap bilgisi kullanılmaz.'
    };
  }

  function fromForm(form) {
    const data = Object.fromEntries(new FormData(form).entries());
    for (const name of ['activeOutage', 'confirmNeed', 'confirmSpecs', 'confirmAffiliate']) data[name] = Boolean(form.elements[name]?.checked);
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
      ? `<div class="affiliate"><strong>Koşullu ürün sınıfı</strong><p>Bu bağlantı Amazon satış ortaklığı içerebilir. ALO186 fiyat, stok, puan, satıcı veya garanti yayımlamaz. Sıcaklık aralığı, alarm gecikmesi, hafıza, pil ve internet bağımlılığını mağazada yeniden doğrulayın.</p><a href="/akilli-urun-secimi?niyet=soguk-zincir&sinif=${result.recommendation.code}" rel="sponsored nofollow noopener">${result.recommendation.label} sınıfını karşılaştır</a></div>`
      : `<div class="affiliate"><strong>Ürün bağlantısı kapalı</strong><p>Aktif kesinti, profesyonel soğuk zincir, yeterli mevcut ölçüm veya eksik teknik kanıt varken satın alma önerilmez.</p></div>`;
    output.innerHTML = `<h2>${result.headline}</h2><div class="summary-grid"><div class="metric"><span>Önerilen görev</span><strong>${result.recommendation.label}</strong></div><div class="metric"><span>Hedefler</span><strong>≤4°C · ≤-18°C</strong></div><div class="metric"><span>Affiliate</span><strong>${result.affiliateAllowed ? 'Açık ve etiketli' : 'Kapalı'}</strong></div></div>${list('Önce yapılacaklar', result.stops)}${list('Profesyonel kapsam', result.professional)}${list('Eksik kanıt', result.evidence)}${list('Yapılacaklar', result.actions)}${list('Korunan mevcut kanıtlar', result.strengths)}${affiliate}<p class="hint">${result.privacy}</p><div class="actions"><button type="button" id="printResult">Yazdır / PDF</button><button type="button" class="ghost" id="downloadResult">JSON sonucu indir</button></div>`;
    output.querySelector('#printResult').addEventListener('click', () => window.print());
    output.querySelector('#downloadResult').addEventListener('click', () => {
      const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = 'alo186-sicaklik-alarmi-sonucu.json';
      link.click();
      URL.revokeObjectURL(link.href);
    });
    output.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
  }

  if (typeof module !== 'undefined' && module.exports) module.exports = { evaluate };
  if (typeof document !== 'undefined') {
    const form = document.querySelector('#coldForm');
    if (form) {
      form.addEventListener('submit', (event) => { event.preventDefault(); render(evaluate(fromForm(form))); });
      form.addEventListener('reset', () => setTimeout(() => { document.querySelector('#result').hidden = true; document.querySelector('#error').hidden = true; }, 0));
    }
  }
})();