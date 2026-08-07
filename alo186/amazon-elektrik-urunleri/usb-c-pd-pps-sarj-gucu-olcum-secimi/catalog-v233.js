(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root && typeof root === 'object') root.Alo186UsbCPdPpsChargerCatalogV233 = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const version = 233;
  const affiliateTag = 'alo186rehber-21';
  const verificationMaxAgeDays = 45;
  const verifiedAt = '2026-08-03';
  const category = Object.freeze({
    id: 'consumer_usb_c_pd_pps_wall_charger_power_measurement',
    risk: 'consumer-medium',
    affiliatePolicy: 'after_tool',
    requiredTool: 'embedded-usbc-pd-pps-charger-measurement-v233',
    professionalOnly: false,
    excludes: Object.freeze([
      'damaged-outlet', 'loose-outlet', 'burn-smell', 'overheating',
      'medical-device-power', 'life-safety-device', 'industrial-control', 'fixed-installation'
    ])
  });
  const products = Object.freeze([
    {
      id: 'spigen-ach08448-30w', asin: 'B0DFX1N74Z', mpn: 'ACH08448', brand: 'Spigen',
      name: 'Spigen ACH08448 30W USB-C GaN Pro PD/PPS Güç Adaptörü', verifiedAt,
      userNeed: 'Tek bir telefon, tablet veya düşük güç isteyen USB-C dizüstünü; cihazın gerçek watt ve protokol ihtiyacına uygun kompakt bir adaptörle şarj etmek.',
      strengths: ['Tek USB-C porttan 30W’a kadar çıkış','USB Power Delivery 3.0 ve PPS desteği','GaN Pro tabanlı kompakt gövde ve çoklu şarj protokolü desteği'],
      limitations: ['Kutuda USB-C kablo bulunmaz','İki cihazı aynı anda şarj etmez','45W veya daha yüksek isteyen dizüstülerde tam performans sağlamaz'],
      noBuyWhen: 'Mevcut adaptör cihazın istediği watt ve protokolü güvenle sağlıyorsa, birden fazla port gerekiyorsa veya cihaz 30W’tan fazla güç istiyorsa satın alma yapmayın.',
      technicalSource: 'https://www.spigen.com.tr/urun/spigen-30w-usb-c-mini-adaptor-samsung-pps-destekli-hizli-sarj-aleti-iphone-android-ipad-macbook-type-c-ee301-black-ach08448'
    },
    {
      id: 'spigen-ach03714-35w', asin: 'B0B4DL9XSV', mpn: 'ACH03714', brand: 'Spigen',
      name: 'Spigen ACH03714 35W Çift USB-C GaN PD/PPS Güç Adaptörü', verifiedAt,
      userNeed: 'Telefon ve ikinci düşük güçlü USB-C cihazı tek adaptörde toplarken, tek port kullanımında 35W’a kadar güç elde etmek.',
      strengths: ['İki USB-C port ve tek port kullanımında 35W’a kadar çıkış','USB PD 3.0 ve Samsung PPS desteği','GaN tabanlı kompakt tasarım ve akıllı güç dağıtımı'],
      limitations: ['Kablo kutuya dahil değildir','İki port birlikte kullanıldığında güç cihazlar arasında bölüşülür','45W veya üzeri sürekli güç isteyen dizüstüler için uygun değildir'],
      noBuyWhen: 'Tek 30W port yeterliyse, 45W üstü dizüstü gücü gerekiyorsa veya iki USB-C porta ihtiyaç yoksa satın alma yapmayın.',
      technicalSource: 'https://www.spigen.com.tr/urun/spigen-powerarc-arcstation-35w-hizli-sarj-cihazi-2-port-gallium-nitride-gan-usb-c-pd-3-0-30w-pps-30w-samsung-hizli-sarj-destekli-iphone-android-sarj-adaptoru-pe2104-white'
    },
    {
      id: 'spigen-ach03717-45w', asin: 'B0B4K26Z58', mpn: 'ACH03717', brand: 'Spigen',
      name: 'Spigen ACH03717 45W Çift USB-C GaN PD/PPS Güç Adaptörü', verifiedAt,
      userNeed: 'Telefon, tablet veya uyumlu USB-C dizüstü için 45W’a kadar güç ile iki USB-C portu tek adaptörde toplamak.',
      strengths: ['İki USB-C port ve tek port kullanımında 45W’a kadar çıkış','PD 3.0 ile Samsung PPS 2.0 desteği','GaN tabanlı kompakt tasarım ve akıllı güç dağıtımı'],
      limitations: ['Kablo kutuya dahil değildir','İki port birlikte kullanıldığında güç cihazlar arasında bölüşülür','65W ve üzeri sürekli güç isteyen dizüstüler için uygun değildir'],
      noBuyWhen: '35W yeterliyse, 65W üstü dizüstü gücü gerekiyorsa veya uygun e-marker/PPS kablosu yoksa satın alma yapmayın.',
      technicalSource: 'https://www.spigen.com.tr/urun/spigen-powerarc-arcstation-45w-hizli-sarj-cihazi-2-port-gallium-nitride-gan-usb-c-pd-3-0-45w-pps-45w-samsung-hizli-sarj-destekli-iphone-android-sarj-adaptoru-pe2105-white'
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