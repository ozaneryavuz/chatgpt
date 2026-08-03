(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root && typeof root === 'object') root.Alo186VehicleUsbChargerCatalogV235 = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const version = 235;
  const affiliateTag = 'alo186rehber-21';
  const verificationMaxAgeDays = 45;
  const verifiedAt = '2026-08-03';
  const category = Object.freeze({
    id: 'consumer_vehicle_accessory_socket_usb_charger_power_measurement',
    risk: 'consumer-medium',
    affiliatePolicy: 'after_tool',
    requiredTool: 'embedded-vehicle-accessory-socket-usb-power-measurement-v235',
    professionalOnly: false,
    excludes: Object.freeze([
      'damaged-or-overheating-vehicle-socket',
      'vehicle-fixed-wiring',
      'ev-traction-battery-charging',
      'jump-starting',
      'medical-or-life-safety-equipment',
      'emergency-communications',
      'driver-assistance-power'
    ])
  });
  const products = Object.freeze([
    {
      id: 'spigen-acp08700', asin: 'B0DWT464C3', mpn: 'ACP08700', model: 'EV302', brand: 'Spigen',
      name: 'Spigen ACP08700 EV302 30W Çift USB-A Araç Şarj Adaptörü', verifiedAt,
      userNeed: 'Araç aksesuar prizinde iki USB-A kablolu telefonu veya düşük güçlü cihazı aynı anda şarj etmek.',
      strengths: ['İki USB-A çıkış ve toplam 30W güç sınıfı','Bir portta 18W Quick Charge 3.0, ikinci portta 12W sınıfı','USB-A kablo parkını değiştirmeden iki cihaz kullanımı'],
      limitations: ['USB-C Power Delivery veya PPS çıkışı yoktur','Toplam güç iki port arasında 18W + 12W olarak sınırlıdır','USB-C dizüstü bilgisayar ve yüksek güçlü tablet görevleri için uygun sınıf değildir'],
      noBuyWhen: 'Tek cihaz için mevcut USB-A adaptörünüz yeterliyse, USB-C PD/PPS gerekiyorsa veya araç prizi gevşek, kararmış ya da ısınıyorsa satın alma yapmayın.',
      technicalSource: 'https://www.spigen.com.tr/urun/spigen-30w-usb-a-2-port-arac-ici-hizli-sarj-aleti-18w-12w-akim-korumali-guc-adaptoru-iphone-android-ipad-type-c-pd-ev302-acp08700'
    },
    {
      id: 'spigen-acp08447', asin: 'B0DFWZSW3R', mpn: 'ACP08447', model: 'EV482', brand: 'Spigen',
      name: 'Spigen ACP08447 EV482 48W USB-C + USB-A Araç Şarj Adaptörü', verifiedAt,
      userNeed: 'USB-C PD/PPS telefon ile USB-A ikinci cihazı aynı araç prizinden birlikte şarj etmek.',
      strengths: ['USB-C 30W ve USB-A 18W olmak üzere toplam 48W sınıfı','USB-C portunda PD 3.0 ve PPS, USB-A portunda Quick Charge 3.0 desteği','Yeni USB-C ve mevcut USB-A kabloları birlikte kullanabilme'],
      limitations: ['USB-C portu tek başına 30W sınıfıyla sınırlıdır','45W veya 65W isteyen dizüstü bilgisayarlarda hedef gücü sağlamaz','Gerçek şarj gücü cihaz protokolü, kablo ve iki portun eşzamanlı kullanımına bağlıdır'],
      noBuyWhen: 'Cihazınız 30W üstü USB-C güç istiyorsa, yalnız USB-C portlarına ihtiyacınız varsa veya mevcut adaptör ölçümde yeterliyse satın alma yapmayın.',
      technicalSource: 'https://www.spigen.com.tr/urun/spigen-48w-usb-c-2-port-arac-ici-adaptor-samsung-pps-destekli-hizli-sarj-aleti-iphone-android-ipad-type-c-pd-3-0-30w-qc-3-0-18w-ev482'
    },
    {
      id: 'spigen-acp02562', asin: 'B08PRZ815M', mpn: 'ACP02562', model: 'PC2000', brand: 'Spigen',
      name: 'Spigen ACP02562 PC2000 65W Çift USB-C Araç Şarj Adaptörü', verifiedAt,
      userNeed: 'USB-C dizüstü bilgisayar veya tablet ile telefonu aynı araç aksesuar prizinden şarj etmek.',
      strengths: ['İki USB-C port ve toplam 65W güç sınıfı','Eşzamanlı kullanımda 45W + 20W port dağılımı','USB-C Power Delivery 3.0 cihazları için tek kablo ekosistemi'],
      limitations: ['Birinci USB-C portun üst sınırı 45W sınıfıdır','USB-A çıkışı bulunmaz','Yüksek güç için araç prizi, fiş teması ve kablo kapasitesi ayrıca doğrulanmalıdır'],
      noBuyWhen: 'Dizüstü bilgisayarınız 45W üstü sürekli giriş istiyorsa, USB-A gerekiyorsa, araç üreticisi aksesuar prizini bu görev için uygun görmüyorsa veya mevcut çözüm yeterliyse satın alma yapmayın.',
      technicalSource: 'https://www.spigen.com.tr/urun/spigen-powerarc-arcstation-65w-hizli-arac-sarj-cihazi-2-port-usb-c-pd3-0-45w-usb-c-pd3-0-20w-pc2000'
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
