(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root && typeof root === 'object') root.Alo186PortableWorkLightCatalogV240 = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const version = 240;
  const affiliateTag = 'alo186rehber-21';
  const verificationMaxAgeDays = 45;
  const verifiedAt = '2026-08-03';

  const category = Object.freeze({
    id: 'consumer_portable_rechargeable_work_light_outage_inspection',
    risk: 'consumer-low',
    affiliatePolicy: 'after_tool',
    requiredTool: 'embedded-portable-work-light-outage-inspection-v240',
    professionalOnly: false,
    excludes: Object.freeze([
      'live-mains-or-panel-work',
      'gas-leak-or-explosive-atmosphere',
      'medical-or-life-safety-lighting',
      'traffic-or-emergency-signalling',
      'damaged-overheating-or-swollen-battery',
      'weather-exposure-beyond-ip54'
    ])
  });

  const products = Object.freeze([
    Object.freeze({
      id: 'ledlenser-w1r-work',
      asin: 'B0BY9KXWZX',
      mpn: '502810',
      brand: 'Ledlenser',
      name: 'Ledlenser W1R Work Şarjlı Klipsli Çalışma Feneri',
      verifiedAt,
      userNeed: 'Elektrik kesintisinde veya gerilimsiz, düşük riskli ev içi kontrolde iki eli serbest bırakacak yakın alan aydınlatması.',
      strengths: Object.freeze([
        'Üretici verisine göre 220 ve 60 lümen olmak üzere iki aydınlatma seviyesi',
        'Klips, mıknatıs, 360° döner mafsal ve hareketli lamba başlığı',
        'USB-C şarj, IP54 gövde ve 61 gram ağırlık'
      ]),
      limitations: Object.freeze([
        'Elektrik test cihazı değildir; gerilim varlığını veya tesisat güvenliğini göstermez',
        'Patlayıcı ortam, gaz kaçağı, trafik yönlendirmesi veya yaşam güvenliği aydınlatması için onaylı değildir',
        'IP54 koruma suya daldırma veya yoğun dış ortam maruziyeti anlamına gelmez'
      ]),
      noBuyWhen: 'Mevcut fener sağlam ve yeterliyse; sertifikalı acil aydınlatma, ATEX veya uzun süreli oda aydınlatması gerekiyorsa satın alma yapmayın.',
      technicalSource: 'https://www.ledlenser.com.tr/urun/w1r-sarjli-miknatisli-mini-calisma-feneri'
    }),
    Object.freeze({
      id: 'ledlenser-w2r-work',
      asin: 'B0BY9KCTRW',
      mpn: '502809',
      brand: 'Ledlenser',
      name: 'Ledlenser W2R Work Şarjlı Kalem Tipi Çalışma Feneri',
      verifiedAt,
      userNeed: 'Elektrik kesintisinde dar bir bölgeyi hem geniş ışıkla hem noktasal ışıkla görmek ve cebe takılabilen hafif bir fener kullanmak.',
      strengths: Object.freeze([
        'Üretici verisine göre 220/60 lümen geniş alan ve 100 lümen spot ışık',
        'Spot ışıkta 60 metreye kadar mesafe ve geniş alanda 1,5/7 saat kullanım beyanı',
        'Klipsli gövde, USB-C şarj, IP54 koruma ve 61 gram ağırlık'
      ]),
      limitations: Object.freeze([
        'Gerilim dedektörü veya elektriksel ölçüm aracı değildir',
        'Mıknatıslı sabitleme gerektiren kullanım için W1R veya W6R ile aynı montaj yapısına sahip değildir',
        'Patlayıcı ortam, gaz kaçağı, trafik veya yaşam güvenliği görevi için kullanılmamalıdır'
      ]),
      noBuyWhen: 'Mevcut küçük fener ihtiyacı karşılıyorsa; mıknatıslı sabitleme, sertifikalı acil aydınlatma veya geniş alanı uzun süre aydınlatma gerekiyorsa satın alma yapmayın.',
      technicalSource: 'https://www.ledlenser.com.tr/urun/w2r-work-kalem-tipi-sarjli-calisma-feneri'
    }),
    Object.freeze({
      id: 'ledlenser-w6r-work',
      asin: 'B0BY9N84B4',
      mpn: '502736',
      brand: 'Ledlenser',
      name: 'Ledlenser W6R Work Şarjlı Mıknatıslı Çalışma Feneri',
      verifiedAt,
      userNeed: 'Elektrik kesintisinde daha geniş bir çalışma alanını aydınlatmak ve feneri stant, mıknatıs veya kancayla sabitlemek.',
      strengths: Object.freeze([
        'Üretici verisine göre 500/220 lümen geniş alan ve 120 lümen spot ışık',
        '180° katlanan ve 270° dönen başlık; stant, mıknatıs ve metal kanca',
        '2500 mAh Li-ion batarya, USB-C şarj ve IP54 koruma'
      ]),
      limitations: Object.freeze([
        'En yüksek 500 lümen modunda üretici çalışma süresi iki saattir',
        'Elektrik panosu içinde gerilim altında çalışma veya ölçüm için güvenlik ekipmanı değildir',
        'Patlayıcı ortam, gaz kaçağı, kalıcı acil aydınlatma veya trafik sinyali için uygunluk iddiası taşımaz'
      ]),
      noBuyWhen: 'Mevcut fener yeterliyse; yalnız cep boyu ışık gerekiyorsa; uzun süreli sabit acil aydınlatma, ATEX veya yaşam güvenliği görevi aranıyorsa satın alma yapmayın.',
      technicalSource: 'https://www.ledlenser.com.tr/urun/w6r-work-miknatisli-calisma-feneri'
    })
  ]);

  function verificationStatus(now) {
    const current = now instanceof Date ? now : new Date(now);
    const verified = new Date(`${verifiedAt}T00:00:00Z`);
    const ageDays = Math.floor((current.getTime() - verified.getTime()) / 86400000);
    return Object.freeze({
      fresh: Number.isFinite(ageDays) && ageDays >= 0 && ageDays <= verificationMaxAgeDays,
      ageDays
    });
  }

  function amazonProductUrl(asin) {
    if (!products.some((item) => item.asin === asin)) throw new Error('Unknown ASIN');
    return `https://www.amazon.com.tr/dp/${asin}?tag=${affiliateTag}`;
  }

  return Object.freeze({
    version,
    affiliateTag,
    verificationMaxAgeDays,
    verifiedAt,
    category,
    products,
    verificationStatus,
    amazonProductUrl
  });
});
