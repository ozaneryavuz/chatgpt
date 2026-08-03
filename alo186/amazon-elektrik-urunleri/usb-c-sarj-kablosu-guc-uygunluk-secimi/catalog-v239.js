(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root && typeof root === 'object') root.Alo186UsbCChargeCableCatalogV239 = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const version = 239;
  const affiliateTag = 'alo186rehber-21';
  const verificationMaxAgeDays = 45;
  const verifiedAt = '2026-08-03';

  const category = Object.freeze({
    id: 'consumer_usb_c_charge_cable_power_compatibility',
    risk: 'consumer-low',
    affiliatePolicy: 'after_tool',
    requiredTool: 'embedded-usb-c-charge-cable-power-compatibility-v239',
    professionalOnly: false,
    excludes: Object.freeze([
      'damaged-or-overheating-connector',
      'mains-voltage-repair',
      'medical-or-life-safety-device',
      'industrial-control',
      'video-or-high-speed-data-cable-selection',
      'charger-or-device-fault-diagnosis'
    ])
  });

  const products = Object.freeze([
    Object.freeze({
      id: 'baseus-crystal-shine-100w-12m',
      asin: 'B0B46N4SK5',
      mpn: 'CAJY000601',
      brand: 'Baseus',
      name: 'Baseus Crystal Shine USB-C–USB-C 100 W 1,2 m Şarj Kablosu',
      verifiedAt,
      userNeed: 'USB-C PD destekli telefon, tablet veya dizüstü bilgisayarı kısa mesafede şarj etmek ve yalnız USB 2.0 düzeyinde veri aktarmak.',
      strengths: Object.freeze([
        'Üretici beyanına göre 20 V / 5 A ve 100 W’a kadar şarj desteği',
        '1,2 metre örgülü kablo ve alüminyum konektör gövdesi',
        '480 Mb/s’ye kadar USB 2.0 veri aktarımı'
      ]),
      limitations: Object.freeze([
        '100 W etiketi, şarj cihazı ve bağlı cihaz aynı gücü desteklemiyorsa bu gücün alınacağı anlamına gelmez',
        'Görüntü çıkışı veya USB 3.x yüksek hızlı veri ihtiyacı için uygun seçim değildir',
        'Konektörde ısınma, gevşeklik, kararma veya sıvı teması varsa kullanılmamalıdır'
      ]),
      noBuyWhen: 'Mevcut kablo sağlam ve gerekli gücü sağlıyorsa; cihazınız USB-C PD kullanmıyorsa; görüntü aktarımı gerekiyorsa veya konektörde ısınma ve hasar varsa satın alma yapmayın.',
      technicalSource: 'https://cz.baseus.com/en/products/cajy000601'
    }),
    Object.freeze({
      id: 'baseus-crystal-shine-100w-2m',
      asin: 'B0B46PHW14',
      mpn: 'CAJY000701',
      brand: 'Baseus',
      name: 'Baseus Crystal Shine USB-C–USB-C 100 W 2 m Şarj Kablosu',
      verifiedAt,
      userNeed: 'USB-C PD destekli cihazı prizden veya adaptörden daha uzak bir kullanım noktasında şarj etmek ve yalnız temel veri aktarımı yapmak.',
      strengths: Object.freeze([
        'Üretici beyanına göre 20 V / 5 A ve 100 W’a kadar şarj desteği',
        'İki metre uzunlukla masa, yatak yanı veya çanta kullanımında daha geniş erişim',
        'Örgülü dış yüzey ve 480 Mb/s’ye kadar USB 2.0 veri aktarımı'
      ]),
      limitations: Object.freeze([
        'İki metre uzunluk, gereksizse kablo dolaşıklığı ve mekanik zorlanma oluşturabilir',
        'Gerçek şarj gücü adaptör, cihaz, protokol ve bağlantı koşullarının ortak sınırıyla belirlenir',
        'Görüntü çıkışı veya USB 3.x yüksek hızlı veri için tasarlanmış bir kablo değildir'
      ]),
      noBuyWhen: 'Bir metrelik sağlam kablo ihtiyacı karşılıyorsa; cihaz 100 W sınıfına ihtiyaç duymuyorsa; yüksek hızlı veri veya görüntü aktarımı gerekiyorsa satın alma yapmayın.',
      technicalSource: 'https://cz.baseus.com/en/products/cajy000701'
    }),
    Object.freeze({
      id: 'baseus-cafule-60w-1m',
      asin: 'B0144AE0V6',
      mpn: 'CATKLF-GG1',
      brand: 'Baseus',
      name: 'Baseus Cafule USB-C–USB-C 60 W 1 m Şarj Kablosu',
      verifiedAt,
      userNeed: 'En fazla 60 W sınıfında USB-C PD kullanan telefon, tablet veya uyumlu dizüstü bilgisayarı kısa kabloyla şarj etmek.',
      strengths: Object.freeze([
        'Üretici beyanına göre 20 V / 3 A ve 60 W’a kadar şarj desteği',
        'Bir metre uzunluk ve naylon örgülü dış yüzey',
        '480 Mb/s’ye kadar USB 2.0 veri aktarımı'
      ]),
      limitations: Object.freeze([
        '60 W üzeri güç isteyen cihazlarda hedeflenen şarj performansını sağlayamaz',
        'Yüksek hızlı veri veya görüntü aktarımı için uygun değildir',
        'Kablo ve konektör fiziksel hasar, gevşeklik veya aşırı ısınma gösterirse kullanılmamalıdır'
      ]),
      noBuyWhen: 'Cihazınız 60 W üzerinde güç istiyorsa; mevcut kablo sağlam ve yeterliyse; video veya yüksek hızlı veri gerekiyorsa ya da bağlantıda ısınma varsa satın alma yapmayın.',
      technicalSource: 'https://cz.baseus.com/en/products/catklf-gg1'
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
