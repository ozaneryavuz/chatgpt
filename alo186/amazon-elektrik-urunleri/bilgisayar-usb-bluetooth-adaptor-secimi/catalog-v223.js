(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root && typeof root === 'object') root.Alo186BluetoothAdapterCatalogV223 = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const version = 223;
  const affiliateTag = 'alo186rehber-21';
  const verificationMaxAgeDays = 45;
  const verifiedAt = '2026-08-02';
  const category = Object.freeze({
    id: 'consumer_pc_usb_bluetooth_adapter',
    risk: 'consumer-low',
    affiliatePolicy: 'after_tool',
    requiredTool: 'embedded-pc-bluetooth-compatibility-v223',
    professionalOnly: false,
    excludes: Object.freeze([
      'medical-device',
      'life-safety-system',
      'industrial-control',
      'vehicle-safety-system',
      'managed-enterprise-radio',
    ]),
  });

  const products = Object.freeze([
    Object.freeze({
      id: 'tp-link-ub500',
      asin: 'B098K3H92Z',
      mpn: 'UB500',
      brand: 'TP-Link',
      name: 'TP-Link UB500 Nano USB Bluetooth Adaptör',
      verifiedAt,
      userNeed: 'Bluetooth donanımı bulunmayan veya sürücüsü artık çalışmayan Windows masaüstü ya da dizüstü bilgisayara kulaklık, klavye, fare ve oyun kumandası bağlantısı eklemek.',
      strengths: Object.freeze([
        'Nano boyutlu USB adaptör; bilgisayarda takılı bırakmaya uygun kompakt yapı',
        'Amazon Türkiye kaydı Bluetooth 5.3 sınıfını, TP-Link Türkiye güncel donanım sayfaları ise sürüme bağlı Bluetooth sınıfını açıklar',
        'TP-Link Türkiye kaynaklarında Windows 11/10/8.1/7 desteği',
        'Üretici kaynağında aynı anda yedi adede kadar Bluetooth cihazı desteği beyanı',
      ]),
      limitations: Object.freeze([
        'UB500 donanım sürümüne göre Bluetooth 5.0, 5.3 veya 5.4 teknik sayfalarına sahip olabilir; kutu etiketi ve donanım sürümü satın almadan önce doğrulanmalıdır',
        'Bluetooth sürümü tek başına kulaklık gecikmesi, codec, mikrofon kalitesi veya menzil garantisi vermez',
        'Windows sürümüne göre üretici sürücüsü gerekebilir; macOS, Linux, televizyon ve oyun konsolu uyumu varsayılmamalıdır',
      ]),
      noBuyWhen: 'Bilgisayarın mevcut Bluetooth bağlantısı kararlı çalışıyorsa, gerekli işletim sistemi sürücüsü bulunamıyorsa veya amaç yalnız oyun konsoluna özel düşük gecikmeli ses aktarmaksa satın almayın.',
      technicalSource: 'https://www.tp-link.com/tr/home-networking/adapter/ub500/v2/',
    }),
    Object.freeze({
      id: 'tp-link-ub500-plus',
      asin: 'B0DKFXGR21',
      mpn: 'UB500 Plus',
      brand: 'TP-Link',
      name: 'TP-Link UB500 Plus Antenli USB Bluetooth Adaptör',
      verifiedAt,
      userNeed: 'Bilgisayar kasasının masa altında veya sinyalin zayıfladığı bir konumda bulunduğu senaryoda ayarlanabilir haricî antenli Bluetooth bağlantısı kullanmak.',
      strengths: Object.freeze([
        'Bluetooth 5.3 sınıfı ve ayarlanabilir haricî anten',
        'Üretici kaynağında Windows 11/10/8.1/7 sistem desteği',
        'USB bağlantılı, sürüme bağlı tak-çalıştır kurulum ve üretici sürücü desteği',
        'Anten yönünün masa düzenine göre ayarlanabilmesi',
      ]),
      limitations: Object.freeze([
        'Haricî anten, duvar, metal kasa, USB 3 paraziti veya radyo yoğunluğu kaynaklı bütün bağlantı sorunlarını çözmez',
        'Gerçek menzil ve kararlılık bağlı cihazın antenine, ortamına ve Bluetooth profiline bağlıdır',
        'Model ve donanım sürümü bölgeye göre değişebileceğinden kutu etiketi ile üretici indirme sayfası eşleştirilmelidir',
      ]),
      noBuyWhen: 'Nano adaptör veya bilgisayarın mevcut Bluetooth’u ihtiyacı karşılıyorsa, anten için masa üzerinde uygun konum yoksa ya da işletim sistemi üretici desteği dışında kalıyorsa satın almayın.',
      technicalSource: 'https://www.tp-link.com/us/home-networking/usb-adapter/ub500-plus/',
    }),
    Object.freeze({
      id: 'asus-usb-bt400',
      asin: 'B00CM83SC0',
      mpn: 'USB-BT400',
      brand: 'ASUS',
      name: 'ASUS USB-BT400 Bluetooth 4.0 USB Adaptör',
      verifiedAt,
      userNeed: 'Bluetooth 4.0 profilleriyle uyumlu eski veya temel Windows bilgisayarda düşük enerjili klavye, fare, kulaklık ve benzeri çevre birimlerini kullanmak.',
      strengths: Object.freeze([
        'Bluetooth 4.0 ve Bluetooth Low Energy desteği',
        'USB 2.0 arayüz ve ultra küçük gövde',
        'ASUS Türkiye teknik kaynağında Windows 10/8/7 desteği',
        'Üretici kaynağında açık alanda 10 metrenin üzerinde kullanım mesafesi ve 3 Mbps’ye kadar teknik veri oranı',
      ]),
      limitations: Object.freeze([
        'Bluetooth 4.0 sınıfı yeni nesil Bluetooth özelliklerini veya belirli ses codec’lerini garanti etmez',
        'Windows 11 desteği resmî teknik tabloda açıkça listelenmediği için varsayılmamalıdır',
        'Açık alan mesafe beyanı gerçek ev/ofis menzili değildir; duvar, kasa ve parazit performansı düşürebilir',
      ]),
      noBuyWhen: 'Bluetooth 5.x özelliği zorunluysa, Windows 11 için açık üretici desteği gerekiyorsa veya bilgisayarın mevcut Bluetooth’u görevi kararlı biçimde yerine getiriyorsa satın almayın.',
      technicalSource: 'https://www.asus.com/tr/networking-iot-servers/adapters/all-series/usbbt400/techspec/',
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
