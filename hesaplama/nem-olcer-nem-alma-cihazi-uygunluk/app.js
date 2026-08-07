(() => {
  'use strict';

  const truthy = (value) => Boolean(value === true || value === 'on' || value === 'true');
  const unique = (items) => [...new Set(items.filter(Boolean))];
  const number = (value, fallback = 0) => Number.isFinite(Number(value)) ? Number(value) : fallback;

  function evaluate(raw) {
    const data = { ...raw };
    const stops = [];
    const professional = [];
    const evidence = [];
    const actions = [];
    const strengths = [];

    const rh = Math.max(0, Math.min(100, number(data.rh, 0)));
    const days = Math.max(0, Math.min(30, number(data.days, 0)));
    const persistentHigh = data.rhKnown === 'yes' && rh >= 60 && days >= 3;
    const healthyRange = data.rhKnown === 'yes' && rh >= 30 && rh <= 55 && data.condensation === 'no' && data.mold === 'none';
    const sourceResolved = ['resolved', 'seasonal'].includes(data.source);
    const safeHomeScope = ['room', 'basement', 'laundry', 'bathroom'].includes(data.scope);

    if (truthy(data.electricalWaterRisk)) {
      stops.push('Su birikintisi, ıslak priz/fiş, elektrikli cihazla su teması, kıvılcım veya elektrik çarpması riski varsa alana yaklaşmayın; güvenli alandan 112 ve yetkili uzman rotasına geçin.');
    }
    if (data.source === 'active-leak') {
      actions.push('Aktif su kaçağını veya sızıntıyı önce kaynağında giderin. Nem alma cihazı su kaynağını onarmaz.');
    }
    if (['whole-home', 'commercial', 'medical'].includes(data.scope)) {
      professional.push('Tüm konut, ticari alan, sağlık/ilaç, arşiv veya kritik depolama koşulları tüketici tipi oda cihazı sonucuna dönüştürülmez; HVAC/tesisat ve kullanım gereksinimi profesyonel olarak doğrulanmalıdır.');
    }
    if (data.mold === 'large') {
      professional.push('Geniş yüzeyli veya tekrarlayan küf, yalnız cihaz satın alma konusu değildir. Nem kaynağı, malzeme hasarı ve sağlık etkisi için uygun uzman değerlendirmesi gerekir.');
    }
    if (data.mold === 'small') {
      actions.push('Küf görülen yüzeyi yalnız nem alma cihazıyla gizlemeyin; nem kaynağını giderin, yüzeyi uygun yöntemle temizleyip tamamen kurutun.');
    }

    if (data.rhKnown !== 'yes') evidence.push('Bağıl nem yüzdesi doğrulanmadı. En az birkaç gün, sabah-akşam aynı noktada güvenilir bir higrometreyle kayıt alın.');
    if (data.rhKnown === 'yes' && days < 3) evidence.push('Tek ölçüm kalıcı nem problemi kanıtı değildir. En az 3 gün aynı konum ve benzer kullanım koşulunda ölçüm yapın.');
    if (data.source === 'unknown') evidence.push('Nem kaynağı bilinmiyor. Sızıntı, yoğuşma, yetersiz havalandırma, çamaşır kurutma ve dış hava koşulları ayrı ayrı kontrol edilmelidir.');
    if (data.outletSafe !== 'yes') evidence.push('Priz, fiş, topraklama ve üretici bağlantı talimatı doğrulanmadı. Nemli ortamda uzatma kablosu veya grup priz kullanmayın.');
    if (data.existingGauge === 'yes') strengths.push('Mevcut nem ölçeriniz var; yeni ölçer almadan 7 günlük kayıt yapılabilir.');
    if (data.existingDehumidifier === 'yes' && data.existingPass === 'yes') strengths.push('Mevcut nem alma cihazı hedef nemi, drenajı ve gerçek çalışma testini karşılıyor.');
    if (healthyRange) strengths.push('Ölçülen bağıl nem, yoğuşma ve görünür küf bulgusu olmadan izleme aralığında.');

    const existingPass = data.existingDehumidifier === 'yes' && data.existingPass === 'yes' && data.outletSafe === 'yes';
    const needsGauge = data.rhKnown !== 'yes' && data.existingGauge !== 'yes' && !truthy(data.electricalWaterRisk);
    const needsDehumidifier = persistentHigh && sourceResolved && safeHomeScope && !existingPass && data.outletSafe === 'yes' && data.mold !== 'large';

    let status = 'monitor';
    let headline = 'Önce nemi ve kaynağı doğrulayın';
    if (stops.length) {
      status = 'stop';
      headline = 'Ürün seçimini durdurun — önce su ve elektrik güvenliği';
    } else if (professional.length) {
      status = 'professional';
      headline = 'Oda tipi ürün yerine profesyonel değerlendirme gerekli';
    } else if (existingPass || healthyRange) {
      status = 'no-buy';
      headline = 'Mevcut plan yeterli — yeni ürün almayın';
    } else if (needsGauge) {
      status = 'recommend';
      headline = 'Önce yalnız nem ölçümü için higrometre sınıfını değerlendirin';
    } else if (needsDehumidifier) {
      status = 'recommend';
      headline = 'Kalıcı yüksek nem için oda tipi nem alma cihazı ön seçimi yapılabilir';
    } else if (evidence.length || data.source === 'active-leak') {
      status = 'evidence';
      headline = 'Satın almadan önce eksik nem ve kaynak kanıtlarını tamamlayın';
    }

    const categories = [];
    if (status === 'recommend' && needsGauge) categories.push('hygrometer');
    if (status === 'recommend' && needsDehumidifier) categories.push('portable_dehumidifier');

    const confirmations = truthy(data.confirmNeed) && truthy(data.confirmSpecs) && truthy(data.confirmAffiliate);
    const affiliateAllowed = status === 'recommend' && categories.length > 0 && confirmations;

    if (persistentHigh && !sourceResolved) actions.push('Yüksek nem ölçülse bile sızıntı, yoğuşma veya havalandırma nedeni giderilmeden cihazı tek çözüm saymayın.');
    if (persistentHigh && sourceResolved) actions.push('Oda alanı, sıcaklık, başlangıç nemi, su boşaltma/drenaj yöntemi ve üretici kapasite test koşullarını tam model belgesinde doğrulayın.');
    if (data.condensation === 'yes') actions.push('Pencere, duvar veya borudaki yoğuşmayı kaydedin; soğuk yüzey, yalıtım ve havalandırma nedenlerini ayrıca değerlendirin.');

    return {
      ok: true,
      status,
      headline,
      rh,
      days,
      persistentHigh,
      stops: unique(stops),
      professional: unique(professional),
      evidence: unique(evidence),
      actions: unique(actions),
      strengths: unique(strengths),
      categories,
      affiliateAllowed,
      confirmations,
      existingPass,
      privacy: 'Hesap cihazınızda yapılır; ad, adres, konum, sağlık kaydı, oda fotoğrafı veya seri numarası istenmez.'
    };
  }

  function fromForm(form) {
    const data = Object.fromEntries(new FormData(form).entries());
    for (const name of ['electricalWaterRisk', 'confirmNeed', 'confirmSpecs', 'confirmAffiliate']) {
      data[name] = Boolean(form.elements[name]?.checked);
    }
    return data;
  }

  const list = (title, items) => items.length ? `<section><h3>${title}</h3><ul>${items.map((item) => `<li>${item}</li>`).join('')}</ul></section>` : '';
  const categoryLabel = (id) => id === 'hygrometer' ? 'Dijital higrometre / sıcaklık-nem ölçer' : 'Oda tipi nem alma cihazı';

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
      ? `<div class="affiliate"><strong>Şeffaf satış ortaklığı ürün sınıfı</strong><p>Sonraki ürün merkezinde Amazon satış ortaklığı bağlantıları bulunabilir. ALO186 fiyat, stok, puan, satıcı, teslimat veya garanti yayımlamaz. Oda koşulu, ölçüm aralığı, kapasite, gürültü, drenaj ve elektrik bağlantısını mağazada ve üretici belgesinde yeniden doğrulayın.</p>${result.categories.map((id) => `<a href="/amazon-elektrik-urunleri/" rel="sponsored nofollow noopener">${categoryLabel(id)} sınıfını karşılaştır</a>`).join(' ')}</div>`
      : `<div class="affiliate"><strong>Ürün bağlantısı kapalı</strong><p>Aktif su kaynağı, elektrik riski, geniş kapsam, eksik ölçüm veya yeterli mevcut ekipman varken satın alma önerilmez.</p></div>`;
    output.innerHTML = `<h2>${result.headline}</h2><div class="summary-grid"><div class="metric"><span>Ölçülen nem</span><strong>${result.rh ? `${result.rh}% RH` : 'Doğrulanmadı'}</strong></div><div class="metric"><span>Kayıt süresi</span><strong>${result.days} gün</strong></div><div class="metric"><span>Affiliate</span><strong>${result.affiliateAllowed ? 'Açık ve etiketli' : 'Kapalı'}</strong></div></div>${list('Durdurma', result.stops)}${list('Profesyonel kapsam', result.professional)}${list('Eksik kanıt', result.evidence)}${list('Yapılacaklar', result.actions)}${list('Korunan mevcut kanıtlar', result.strengths)}${affiliate}<p class="hint">${result.privacy}</p><div class="actions"><button type="button" id="printResult">Yazdır / PDF</button><button type="button" class="ghost" id="downloadResult">JSON sonucu indir</button></div>`;
    output.querySelector('#printResult').addEventListener('click', () => window.print());
    output.querySelector('#downloadResult').addEventListener('click', () => {
      const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = 'alo186-nem-uygunluk-sonucu.json';
      link.click();
      URL.revokeObjectURL(link.href);
    });
    output.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
  }

  if (typeof module !== 'undefined' && module.exports) module.exports = { evaluate };
  if (typeof document !== 'undefined') {
    const form = document.querySelector('#humidityForm');
    if (form) {
      form.addEventListener('submit', (event) => { event.preventDefault(); render(evaluate(fromForm(form))); });
      form.addEventListener('reset', () => setTimeout(() => { document.querySelector('#result').hidden = true; document.querySelector('#error').hidden = true; }, 0));
    }
  }
})();
