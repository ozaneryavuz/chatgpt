(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root && typeof root === 'object') root.Alo186WebcamCatalogV232 = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const version = 232;
  const affiliateTag = 'alo186rehber-21';
  const verificationMaxAgeDays = 45;
  const verifiedAt = '2026-08-03';
  const category = Object.freeze({
    id: 'consumer_usb_webcam',
    risk: 'consumer-low',
    affiliatePolicy: 'after_tool',
    requiredTool: 'embedded-webcam-need-compatibility-v232',
    professionalOnly: false,
    excludes: Object.freeze(['security-surveillance', 'medical-imaging', 'life-safety-monitoring', 'industrial-machine-vision']),
  });

  const products = Object.freeze([
    Object.freeze({
      id: 'logitech-c270', asin: 'B003PAOAWG', mpn: '960-001063', brand: 'Logitech',
      name: 'Logitech C270 HD Webcam', verifiedAt,
      userNeed: 'Dizüstü veya masaüstü bilgisayarda temel görüntülü görüşme için dahili kameradan daha kararlı bir USB-A kamera kullanmak.',
      strengths: Object.freeze(['720p/30 fps görüntü', 'Sabit odak ve otomatik ışık düzeltme', 'Dahili mono mikrofon ve 1,5 m kablo']),
      limitations: Object.freeze(['1080p sağlamaz', 'Otomatik odak yoktur', 'Dar kadraj ve mikrofon kalitesi yayın/üretim işi için sınırlı olabilir']),
      noBuyWhen: 'Bilgisayarın dahili kamerası ve mikrofonu ihtiyacı karşılıyorsa, USB-A portu yoksa veya 1080p/otomatik odak gerekiyorsa satın almayın.',
      technicalSource: 'https://www.logitech.com/en-ae/products/webcams/c270-hd-webcam.960-001063.html',
    }),
    Object.freeze({
      id: 'logitech-c920s', asin: 'B07MM4V7NR', mpn: '960-001252', brand: 'Logitech',
      name: 'Logitech C920s Pro HD Webcam', verifiedAt,
      userNeed: 'Ev veya ofis toplantılarında 1080p görüntü, otomatik odak, stereo mikrofon ve fiziksel gizlilik kapağı kullanmak.',
      strengths: Object.freeze(['1080p/30 fps ve 720p/30 fps', 'Otomatik odaklı cam lens ve 78° görüş alanı', 'Çift mikrofon, tripod uyumlu klips ve gizlilik kapağı']),
      limitations: Object.freeze(['4K veya 1080p/60 fps sağlamaz', 'USB-A portu gerekir', 'Gerçek görüşme kalitesi internet, platform ve ışığa bağlıdır']),
      noBuyWhen: '720p yeterliyse, harici mikrofon ve mevcut kamera görevini karşılıyorsa veya USB-A bağlantısı bulunmuyorsa satın almayın.',
      technicalSource: 'https://www.logitech.com/en-ae/products/webcams/c920s-pro-hd-webcam.960-001252.html',
    }),
    Object.freeze({
      id: 'logitech-c920', asin: 'B00H2DK80U', mpn: '960-001055', brand: 'Logitech',
      name: 'Logitech C920 HD Pro Webcam', verifiedAt,
      userNeed: '1080p görüntülü görüşme ve kayıt için otomatik odaklı, çift mikrofonlu USB-A kamera kullanmak.',
      strengths: Object.freeze(['1080p/30 fps Full HD görüntü', '78° görüş alanı, cam lens ve otomatik odak', 'Çift mikrofonlu stereo ses ve otomatik ışık düzeltme']),
      limitations: Object.freeze(['Fiziksel gizlilik kapağı ürün paketine göre bulunmayabilir', '4K ve 1080p/60 fps sağlamaz', 'Tam MPN ve paket içeriği Amazon kaydında yeniden doğrulanmalıdır']),
      noBuyWhen: 'Gizlilik kapağı zorunluysa C920s gibi kapağı açıkça belirtilen modeli değerlendirin; mevcut kamera yeterliyse satın almayın.',
      technicalSource: 'https://www.logitech.com/en-eu/shop/p/c920-pro-hd-webcam.960-001055',
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
    return Object.freeze({ fresh: Number.isFinite(ageDays) && ageDays >= 0 && ageDays <= verificationMaxAgeDays, ageDays, maxAgeDays: verificationMaxAgeDays, verifiedAt });
  }

  return Object.freeze({ version, affiliateTag, verificationMaxAgeDays, verifiedAt, category, products, amazonProductUrl, verificationStatus });
});