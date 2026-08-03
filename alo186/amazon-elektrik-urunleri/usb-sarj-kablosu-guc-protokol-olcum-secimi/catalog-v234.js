(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root && typeof root === 'object') root.Alo186UsbChargeCableCatalogV234 = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const version = 234;
  const affiliateTag = 'alo186rehber-21';
  const verificationMaxAgeDays = 45;
  const verifiedAt = '2026-08-03';
  const category = Object.freeze({
    id: 'consumer_usb_charge_cable_power_protocol_measurement',
    risk: 'consumer-medium',
    affiliatePolicy: 'after_tool',
    requiredTool: 'embedded-usb-charge-cable-power-protocol-measurement-v234',
    professionalOnly: false,
    excludes: Object.freeze(['damaged-connector','life-safety-device','medical-device','industrial-control','fixed-electrical-installation'])
  });
  const products = Object.freeze([
    {
      id: 'spigen-aca08719-60w-2m', asin: 'B0F2ML9GYM', mpn: 'ACA08719', brand: 'Spigen',
      name: 'Spigen ACA08719 USB-C–USB-C 60W 2 m Şarj Kablosu', verifiedAt,
      userNeed: 'USB-C adaptör ile telefon, tablet veya 60 W’a kadar destekleyen dizüstü bilgisayarı daha uzak bir prizden şarj etmek için 2 metrelik kablo gerektiğinde.',
      strengths: ['USB-C–USB-C bağlantı ve 60 W (20 V / 3 A) sınıfı','PPS 2.0 uyumlu cihazlarda protokol desteği','480 Mbps veri aktarımı ve 2 metre uzunluk'],
      limitations: ['100 W veya 240 W isteyen cihazlarda tam güç vermez','480 Mbps yalnız USB 2.0 veri sınıfıdır; görüntü çıkışı sağlamaz','2 metre uzunluk kısa masaüstü kullanımında gereksiz kablo kalabalığı oluşturabilir'],
      noBuyWhen: 'Mevcut USB-C kablonuz ölçümde gerekli gücü veriyorsa, 1 metre yeterliyse, cihazınız 60 W üstü istiyorsa veya görüntü/yüksek hızlı veri gerekiyorsa satın alma yapmayın.',
      technicalSource: 'https://www.spigen.com.tr/urun/spigen-usb-c-to-usb-c-2-metre-kablo-60w-guc-pps-2-0-super-hizli-sarj-480-mbps-data-aktarim-hizi-type-c-ekstra-dayanikli-white'
    },
    {
      id: 'spigen-aca08717-60w', asin: 'B0F2MH3GFW', mpn: 'ACA08717', brand: 'Spigen',
      name: 'Spigen ACA08717 USB-C–USB-C 60W 1 m Şarj Kablosu', verifiedAt,
      userNeed: 'USB-C adaptörle telefon, tablet veya 60 W’a kadar destekleyen dizüstü bilgisayar için kısa ve günlük bir kablo gerektiğinde.',
      strengths: ['USB-C–USB-C bağlantı ve 60 W (20 V / 3 A) sınıfı','PPS 2.0 uyumlu cihazlarda protokol desteği','480 Mbps veri aktarımı ve 1 metre uzunluk'],
      limitations: ['100 W veya 240 W isteyen cihazlarda tam güç vermez','480 Mbps yalnız USB 2.0 veri sınıfıdır; görüntü çıkışı sağlamaz','PPS sonucu adaptör ve cihaz desteğine bağlıdır'],
      noBuyWhen: 'Mevcut USB-C kablonuz ölçümde gerekli gücü veriyorsa, cihazınız 60 W üstü istiyorsa veya görüntü/yüksek hızlı veri aktarımı gerekiyorsa satın alma yapmayın.',
      technicalSource: 'https://www.spigen.com.tr/urun/spigen-usb-c-to-usb-c-1-metre-kablo-60w-guc-pps-2-0-super-hizli-sarj-480-mbps-data-aktarim-hizi-type-c-ekstra-dayanikli-white'
    },
    {
      id: 'spigen-aca08715-usba-usbc', asin: 'B0F2M377PZ', mpn: 'ACA08715', brand: 'Spigen',
      name: 'Spigen ACA08715 USB-A–USB-C 60W 1 m Şarj Kablosu', verifiedAt,
      userNeed: 'USB-A çıkışlı mevcut adaptör, araç portu veya bilgisayar ile USB-C cihaz arasında şarj ve temel veri bağlantısı gerektiğinde.',
      strengths: ['USB-A–USB-C bağlantı ile eski tip çıkışlara uyum','Üretici beyanına göre 60 W’a kadar cihaz/çıkış uyumlu hızlı şarj','480 Mbps veri aktarımı ve 1 metre uzunluk'],
      limitations: ['USB-C Power Delivery ve PPS 2.0 yolu değildir','Gerçek güç USB-A çıkışın üreticiye özgü protokolüne ve kablo/cihaz eşleşmesine bağlıdır','Dizüstü bilgisayarların çoğunda beklenen USB-C PD gücünü sağlamayabilir'],
      noBuyWhen: 'USB-C PD/PPS gerekiyorsa, USB-A çıkışınız ölçümde yeterli güç vermiyorsa veya mevcut kablo kararlı çalışıyorsa satın alma yapmayın.',
      technicalSource: 'https://www.spigen.com.tr/urun/spigen-usb-a-to-usb-c-1-metre-kablo-60w-guc-hizli-sarj-480-mbps-data-aktarim-hizi-type-c-ekstra-dayanikli-white'
    }
  ].map((item) => Object.freeze({...item, strengths: Object.freeze(item.strengths), limitations: Object.freeze(item.limitations)})));
  function amazonProductUrl(asin) {
    if (!products.some((item) => item.asin === asin)) throw new Error('Unknown ASIN');
    return `https://www.amazon.com.tr/dp/${encodeURIComponent(asin)}?tag=${encodeURIComponent(affiliateTag)}`;
  }
  function verificationStatus(now = new Date()) {
    const verified = new Date(`${verifiedAt}T00:00:00Z`);
    const current = now instanceof Date ? now : new Date(now);
    const ageDays = Math.floor((current.getTime() - verified.getTime()) / 86400000);
    return Object.freeze({fresh: Number.isFinite(ageDays) && ageDays >= 0 && ageDays <= verificationMaxAgeDays, ageDays, maxAgeDays: verificationMaxAgeDays, verifiedAt});
  }
  return Object.freeze({version, affiliateTag, verificationMaxAgeDays, verifiedAt, category, products, amazonProductUrl, verificationStatus});
});
