(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root && typeof root === 'object') root.Alo186UsbFlashCatalogV226 = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const version = 226;
  const affiliateTag = 'alo186rehber-21';
  const verificationMaxAgeDays = 45;
  const verifiedAt = '2026-08-03';
  const category = Object.freeze({
    id: 'consumer_usb_flash_offline_transfer',
    risk: 'consumer-low',
    affiliatePolicy: 'after_tool',
    requiredTool: 'embedded-usb-flash-transfer-fit-v226',
    professionalOnly: false,
    excludes: Object.freeze([
      'sole-backup-copy',
      'regulated-sensitive-data',
      'forensic-evidence-storage',
      'industrial-control-firmware',
      'hardware-encrypted-compliance-media',
    ]),
  });

  const products = Object.freeze([
    Object.freeze({
      id: 'sandisk-ultra-dual-drive-go-64',
      asin: 'B07YYK13LF',
      mpn: 'SDDDC3-064G-G46',
      brand: 'SanDisk',
      name: 'SanDisk Ultra Dual Drive Go 64 GB USB-C / USB-A',
      verifiedAt,
      userNeed: 'USB-C telefon veya tablet ile USB-A bilgisayar arasında çevrimdışı dosya taşımak ve geçici ikinci kopya oluşturmak.',
      strengths: Object.freeze([
        'Aynı gövdede USB-C ve USB-A bağlantısı',
        '64 GB kapasite ve USB 3.2 Gen 1 arayüz',
        'Üretici teknik sayfasında 150 MB/s sınıfına kadar sıralı okuma bilgisi',
        'Döner gövde bağlantı uçlarını taşıma sırasında örter',
      ]),
      limitations: Object.freeze([
        'Telefon veya tabletin USB OTG ve harici depolama desteği ayrıca doğrulanmalıdır',
        'Okuma sınıfı yazma hızını ifade etmez; gerçek aktarım dosya boyutu, cihaz ve bağlantıya göre değişir',
        'Tek USB bellek tek başına yedekleme stratejisi değildir',
      ]),
      noBuyWhen: 'Mevcut USB-C / USB-A belleğiniz görevi kararlı biçimde karşılıyorsa, yalnız USB-A kullanıyorsanız veya dosyaların tek kopyasını bu bellekte tutacaksanız satın almayın.',
      technicalSource: 'https://www.sandisk.com/products/usb-flash-drives/sandisk-ultra-dual-drive-go-usb-3-1-type-c?sku=SDDDC3-064G-G46',
      amazonVerification: 'Amazon Türkiye ürün kaydı ASIN ve tam MPN ile 2026-08-03 tarihinde doğrulandı.',
      attributes: Object.freeze({ capacityGB: 64, connectors: 'USB-C + USB-A', interface: 'USB 3.2 Gen 1', readClass: '150 MB/s sınıfına kadar' }),
    }),
    Object.freeze({
      id: 'kingston-datatraveler-exodia-m-64',
      asin: 'B0B1JNDZ5J',
      mpn: 'DTXM/64GB',
      brand: 'Kingston',
      name: 'Kingston DataTraveler Exodia M 64 GB',
      verifiedAt,
      userNeed: 'USB-A bağlantılı bilgisayar, televizyon veya benzeri tüketici cihazları arasında günlük belge ve medya dosyası taşımak.',
      strengths: Object.freeze([
        '64 GB kapasite ve USB 3.2 Gen 1 Type-A bağlantı',
        'Hareketli kapak USB-A ucunu kullanılmadığında örter',
        'Anahtarlık halkalı hafif taşınabilir gövde',
        'Kingston parça numarası DTXM/64GB ile doğrulanmış model',
      ]),
      limitations: Object.freeze([
        'Üretici bu model için belirli bir sürdürülebilir okuma veya yazma hızı yayımlamaz',
        'USB-C cihazlar için ayrı, veri destekli bir adaptör gerekebilir',
        'İşletim sistemi biçimlendirme sınırı ve hedef cihazın dosya sistemi desteği kontrol edilmelidir',
      ]),
      noBuyWhen: 'Belirli bir minimum yazma hızı, doğrudan USB-C bağlantısı veya donanımsal şifreleme gerekiyorsa; mevcut belleğiniz ihtiyacı karşılıyorsa satın almayın.',
      technicalSource: 'https://www.kingston.com/tr/memory/search?partid=DTXM%2F64GB',
      amazonVerification: 'Amazon Türkiye ürün kaydı ASIN ve tam MPN ile 2026-08-03 tarihinde doğrulandı.',
      attributes: Object.freeze({ capacityGB: 64, connectors: 'USB-A', interface: 'USB 3.2 Gen 1', speedClaim: 'Üretici belirli hız yayımlamıyor' }),
    }),
    Object.freeze({
      id: 'sandisk-ultra-flair-64',
      asin: 'B015CH1NAQ',
      mpn: 'SDCZ73-064G-G46',
      brand: 'SanDisk',
      name: 'SanDisk Ultra Flair 64 GB',
      verifiedAt,
      userNeed: 'USB-A bilgisayarda kompakt metal gövdeli bir bellekle günlük belge, fotoğraf ve medya aktarımı yapmak.',
      strengths: Object.freeze([
        '64 GB kapasite ve USB-A bağlantı',
        'USB 3.0 arayüz ve üretici kaynağında 150 MB/s sınıfına kadar sıralı okuma',
        'Kompakt metal gövde',
        'Tam model kodu SDCZ73-064G-G46 ile doğrulanan varyant',
      ]),
      limitations: Object.freeze([
        'Metal gövde yoğun aktarım sırasında ısınabilir; bu tek başına aktarım hatası anlamına gelmez ancak kullanım ortamı izlenmelidir',
        '150 MB/s ifadesi okuma sınıfıdır; yazma performansı ve küçük dosya aktarımı daha düşük olabilir',
        'USB-C cihazlara doğrudan bağlanmaz ve tek kopyalı arşiv için uygun değildir',
      ]),
      noBuyWhen: 'USB-C bağlantısı zorunluysa, uzun süreli yüksek hacimli yazma işi için taşınabilir SSD gerekiyorsa veya mevcut bellek görevi karşılıyorsa satın almayın.',
      technicalSource: 'https://shop.sandisk.com/de-de/products/usb-flash-drives/sandisk-ultra-flair-usb-3-0?sku=SDCZ73-064G-A46',
      amazonVerification: 'Amazon Türkiye ürün kaydı ASIN ve tam MPN ile 2026-08-03 tarihinde doğrulandı.',
      attributes: Object.freeze({ capacityGB: 64, connectors: 'USB-A', interface: 'USB 3.0', readClass: '150 MB/s sınıfına kadar' }),
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
