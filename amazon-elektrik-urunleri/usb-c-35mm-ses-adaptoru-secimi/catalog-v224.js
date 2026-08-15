(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root && typeof root === 'object') root.Alo186UsbCAudioCatalogV224 = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const version = 224;
  const affiliateTag = 'alo186rehber-21';
  const verificationMaxAgeDays = 45;
  const verifiedAt = '2026-08-02';
  const category = Object.freeze({
    id: 'consumer_usb_c_35mm_audio_adapter',
    risk: 'consumer-low',
    affiliatePolicy: 'after_tool',
    requiredTool: 'embedded-usb-c-audio-compatibility-v224',
    professionalOnly: false,
    excludes: Object.freeze([
      'medical-audio-device',
      'hearing-assistance-system',
      'life-safety-communications',
      'industrial-audio-control',
      'professional-stage-system',
    ]),
  });

  const products = Object.freeze([
    Object.freeze({
      id: 'apple-mw2q3zm-a',
      asin: 'B0D7MN4W7H',
      mpn: 'MW2Q3ZM/A',
      brand: 'Apple',
      name: 'Apple USB-C - 3,5 mm Kulaklık Jakı Adaptörü',
      verifiedAt,
      userNeed: 'USB-C bağlantılı iPhone, iPad veya Mac üzerinde mevcut 3,5 mm kulaklık ya da hoparlörü kullanmak.',
      strengths: Object.freeze([
        'USB-C erkek ve standart 3,5 mm ses dişi bağlantısı',
        'Apple güncel ürün sayfasında iPhone, iPad ve Mac uyumluluk listesi bulunur',
        'Kompakt tek amaçlı yapı; ek şarj veya çoklayıcı işlevi içermez',
      ]),
      limitations: Object.freeze([
        'Android, Windows ve üretici dışı USB-C cihazlarda ses seviyesi, mikrofon ve kumanda işlevleri varsayılmamalıdır',
        'Adaptör yalnız ses bağlantısı içindir; aynı anda şarj geçişi sağlamaz',
        '3,5 mm kulaklığın empedansı, mikrofon standardı ve cihaz yazılımı gerçek sonucu etkileyebilir',
      ]),
      noBuyWhen: 'Cihazınızda çalışan bir 3,5 mm jak varsa, mevcut adaptör kararlı çalışıyorsa veya tam cihaz modeliniz Apple uyumluluk listesinde bulunmuyorsa satın almayın.',
      technicalSource: 'https://www.apple.com/tr/shop/product/mw2q3zm/a/usb-c-35-mm-kulaklik-jaki-adaptoru',
    }),
    Object.freeze({
      id: 'ugreen-80154',
      asin: 'B082WG5VTK',
      mpn: '80154',
      brand: 'UGREEN',
      name: 'UGREEN 80154 USB-C - 3,5 mm DAC Ses Adaptörü',
      verifiedAt,
      userNeed: 'USB-C dijital ses çıkışlı telefon, tablet veya bilgisayarda 3,5 mm kulaklık ve çağrı mikrofonunu kullanmak.',
      strengths: Object.freeze([
        'Üretici kaynağında dahili DAC ve 24 bit / 96 kHz teknik sınıfı',
        'USB-C erkek ve 3,5 mm dişi bağlantı',
        'Naylon örgülü kablo ve alüminyum konnektör yapısı',
        'Üretici kaynağında müzik ve çağrı kullanımına yönelik tak-çalıştır açıklaması',
      ]),
      limitations: Object.freeze([
        '24 bit / 96 kHz sınıfı her uygulama, kulaklık veya cihazda aynı gerçek çıkışı garanti etmez',
        'USB-C portunun dijital ses ve aksesuar desteği tam cihaz modeli üzerinden doğrulanmalıdır',
        'Kulaklık mikrofonu, düğmeler ve ses seviyesi kontrolü cihaz ve işletim sistemine bağlıdır',
      ]),
      noBuyWhen: 'Cihaz USB-C üzerinden dijital ses aksesuarını desteklemiyorsa, yalnız analog USB-C geçiş bekleniyorsa veya mevcut adaptör ses ve mikrofon görevini kararlı biçimde yerine getiriyorsa satın almayın.',
      technicalSource: 'https://ugreen.com.tr/urun/ugreen-usb-c-3-5mm-aux-donusturucu-kablo/',
    }),
    Object.freeze({
      id: 'baseus-l54-catl54-01',
      asin: 'B01LYUKQ0L',
      mpn: 'CATL54-01',
      brand: 'Baseus',
      name: 'Baseus L54 USB-C - 3,5 mm DAC Ses Adaptörü',
      verifiedAt,
      userNeed: '3,5 mm girişi bulunmayan uyumlu USB-C telefonda mevcut kablolu kulaklığı kısa ve taşınabilir bir adaptörle kullanmak.',
      strengths: Object.freeze([
        'Üretici kaynağında 24 bit / 48 kHz DAC teknik sınıfı',
        '9 cm kısa TPE kablo ve kompakt yapı',
        'USB-C erkek ve 3,5 mm dişi ses bağlantısı',
      ]),
      limitations: Object.freeze([
        'Baseus bölgesel ürün kaynağı belirli Samsung, Sony, HTC, Google ve Ulefone modellerinde uyumsuzluk sınırı bildirir',
        'Amazon Türkiye kaydındaki perakende model numarası 31051 iken üretici ürün kodu CATL54-01 olarak geçer; ürün adı ve kod birlikte doğrulanmalıdır',
        'Mikrofon, çağrı düğmeleri ve ses seviyesi bütün USB-C cihazlarda garanti edilmez',
      ]),
      noBuyWhen: 'Tam telefon modeliniz üreticinin uyumsuzluk sınırındaysa, cihazınızda 3,5 mm jak zaten varsa veya mevcut adaptör görevi kararlı biçimde karşılıyorsa satın almayın.',
      technicalSource: 'https://baseus.eu/pl/products/telefon-i-watch/adaptery/baseus-l54-adapter-do-sluchawek-przejsciowka-z-usb-c-na-gniazdo-audio-jack-3-5mm-dac-24-bit-48-khz-czarny-catl54-01-94062',
    }),
  ]);

  function amazonProductUrl(asin) {
    if (!products.some((item) => item.asin === asin)) throw new Error('Unknown ASIN');
    return `https://www.amazon.com.tr/dp/${encodeURIComponent(asin)}?tag=${encodeURIComponent(affiliateTag)}`;
  }

  function verificationStatus(now = new Date()) {
    const verified = new Date(`${verifiedAt}T00:00:00Z`);
    const current = now instanceof Date ? now : new Date(now);
    const ageDays = Math.floor((current.getTime() - verified.getTime()) / 86400000);
    return Object.freeze({
      fresh: Number.isFinite(ageDays) && ageDays >= 0 && ageDays <= verificationMaxAgeDays,
      ageDays,
      maxAgeDays: verificationMaxAgeDays,
      verifiedAt,
    });
  }

  return Object.freeze({
    version,
    affiliateTag,
    verificationMaxAgeDays,
    verifiedAt,
    category,
    products,
    amazonProductUrl,
    verificationStatus,
  });
});
