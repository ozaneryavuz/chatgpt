(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root && typeof root === 'object') root.Alo186MobileWifiCatalogV221 = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const version = 221;
  const affiliateTag = 'alo186rehber-21';
  const verificationMaxAgeDays = 45;
  const verifiedAt = '2026-08-02';
  const category = Object.freeze({
    id: 'portable_4g_mobile_wifi',
    risk: 'consumer-medium',
    affiliatePolicy: 'after_tool',
    requiredTool: 'embedded-mobile-wifi-compatibility-v221',
    professionalOnly: false,
  });

  const products = Object.freeze([
    Object.freeze({
      id: 'tp-link-m7200',
      asin: 'B079GZNQ2B',
      mpn: 'M7200',
      brand: 'TP-Link',
      name: 'TP-Link M7200 4G LTE Mobil Wi-Fi',
      verifiedAt,
      userNeed: 'Seyahatte veya sabit internet kesildiğinde, uygun bir mobil veri SIM kartını birden fazla kişisel cihaza paylaşmak.',
      strengths: [
        'LTE Cat 4 sınıfında 150 Mbps indirme ve 50 Mbps yükleme teknik üst sınırı',
        'Aynı anda 10 adede kadar kablosuz cihaz desteği',
        '2000 mAh çıkarılabilir batarya ve üretici beyanıyla 8 saate kadar çalışma',
        'Kompakt 2,4 GHz 802.11b/g/n mobil erişim noktası',
      ],
      limitations: [
        'Gerçek hız operatör kapsaması, şebeke yoğunluğu, tarife ve sinyal seviyesine bağlıdır',
        'Yalnız 2,4 GHz Wi-Fi sınıfındadır; 5 GHz ihtiyacını karşılamaz',
        'SIM kart, veri paketi ve kesinti sırasında çalışan mobil şebeke ayrıca gerekir',
      ],
      noBuyWhen: 'Telefonunuzun güvenli kişisel erişim noktası aynı cihaz sayısını ve süreyi karşılıyorsa veya kullanım yerinde doğrulanmış 4G kapsaması yoksa satın almayın.',
      technicalSource: 'https://www.tp-link.com/tr/home-networking/mifi/m7200/',
    }),
    Object.freeze({
      id: 'tp-link-m7350',
      asin: 'B01EK8CVHW',
      mpn: 'M7350',
      brand: 'TP-Link',
      name: 'TP-Link M7350 4G LTE-Advanced Mobil Wi-Fi',
      verifiedAt,
      userNeed: 'Bağlantı, veri kullanımı ve batarya durumunu cihaz ekranından izleyerek mobil interneti birden fazla kişisel cihazla paylaşmak.',
      strengths: [
        'LTE Cat 4 sınıfında 150 Mbps indirme ve 50 Mbps yükleme teknik üst sınırı',
        '10 adede kadar eşzamanlı kablosuz cihaz desteği',
        'Ekran üzerinden trafik, sinyal, Wi-Fi ve batarya durumunu izleme',
        '2000 mAh batarya ve üretici beyanıyla 8 saate kadar çalışma',
        '32 GB’a kadar microSD kart paylaşım desteği',
      ],
      limitations: [
        'Donanım sürümüne ve bölgesel modele göre ayrıntılar değişebileceğinden ürün etiketi yeniden kontrol edilmelidir',
        'microSD kapasitesi internet hızını veya mobil kapsama kalitesini artırmaz',
        'Gerçek çalışma süresi sinyal seviyesi, istemci sayısı ve trafik yüküne bağlıdır',
      ],
      noBuyWhen: 'Ekran ve dosya paylaşımı işlevlerine ihtiyacınız yoksa, mevcut telefon hotspot’u görevi güvenli biçimde karşılıyorsa veya operatör/SIM uyumu doğrulanmadıysa satın almayın.',
      technicalSource: 'https://www.tp-link.com/tr/home-networking/mifi/m7350/',
    }),
    Object.freeze({
      id: 'tp-link-m7000',
      asin: 'B08BS3SHZV',
      mpn: 'M7000',
      brand: 'TP-Link',
      name: 'TP-Link M7000 4G LTE Mobil Wi-Fi',
      verifiedAt,
      userNeed: 'Basit ve taşınabilir bir cihazla 4G mobil veriyi ev dışındaki veya geçici bağlantı senaryolarındaki kişisel cihazlara dağıtmak.',
      strengths: [
        'LTE Cat 4 sınıfında 150 Mbps indirme ve 50 Mbps yükleme teknik üst sınırı',
        '10 adede kadar kablosuz istemci desteği',
        '2000 mAh batarya ve üretici beyanıyla 8 saate kadar çalışma',
        '2,4 GHz 802.11b/g/n bağlantı ve micro-USB şarj',
      ],
      limitations: [
        'Yalnız 2,4 GHz Wi-Fi sınıfındadır',
        'SIM biçimi, operatör frekansları ve cihazın bölgesel sürümü satın almadan önce doğrulanmalıdır',
        'Elektrik kesintisinde baz istasyonu veya operatör şebekesi hizmet dışıysa bağlantı sağlayamaz',
      ],
      noBuyWhen: 'Telefon hotspot’u yeterliyse, 5 GHz gerekiyorsa, kullanım noktasında mobil şebeke sürekliliği yoksa veya yalnız sabit fiber/DSL hattını yedeklemek için SIM’siz çözüm arıyorsanız satın almayın.',
      technicalSource: 'https://www.tp-link.com/tr/home-networking/mifi/m7000/',
    }),
  ]);

  function amazonProductUrl(asin) {
    const known = products.some((item) => item.asin === asin);
    if (!known) throw new Error('Unknown ASIN');
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
