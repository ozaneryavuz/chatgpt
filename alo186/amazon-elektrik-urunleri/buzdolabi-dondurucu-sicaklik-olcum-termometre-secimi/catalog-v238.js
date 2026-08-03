(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root && typeof root === 'object') root.Alo186ColdTemperatureCatalogV238 = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const version = 238;
  const affiliateTag = 'alo186rehber-21';
  const verificationMaxAgeDays = 45;
  const verifiedAt = '2026-08-03';
  const category = Object.freeze({
    id: 'consumer_refrigerator_freezer_temperature_measurement_selection',
    risk: 'consumer-low',
    affiliatePolicy: 'after_tool',
    requiredTool: 'embedded-cold-temperature-measurement-safety-v238',
    professionalOnly: false,
    excludes: Object.freeze([
      'medical-or-pharmaceutical-cold-chain',
      'laboratory-or-regulated-monitoring',
      'calibration-certificate-required',
      'remote-notification-required',
      'appliance-repair-diagnosis'
    ])
  });
  const products = Object.freeze([
    {
      id: 'tfa-dostmann-30-1042',
      asin: 'B004A0UPTW',
      mpn: '30.1042',
      brand: 'TFA Dostmann',
      name: 'TFA Dostmann 30.1042 Dijital Buzdolabı ve Dondurucu Termometresi',
      verifiedAt,
      userNeed: 'Elektrik kesintisi, açık kalan kapı veya ayar değişikliği sonrasında buzdolabı ve dondurucudaki en düşük ve en yüksek sıcaklığı bağımsız olarak görmek.',
      strengths: Object.freeze([
        '-30 ile +50 °C ölçüm aralığı',
        'Mevcut, en düşük ve en yüksek sıcaklığı birlikte gösterme',
        'Ayakta, asılı veya çerçeveyle yüzeye yerleştirme seçenekleri'
      ]),
      limitations: Object.freeze([
        'Sesli alarm veya uzaktan bildirim sunmaz',
        'Kapı açılma süresini veya elektrik kesintisinin başlangıç saatini kaydetmez',
        'Okuma doğruluğu yerleşim, hava akışı ve kapı açma sıklığından etkilenebilir'
      ]),
      noBuyWhen: 'Cihazın güvenilir bağımsız sıcaklık geçmişi zaten varsa veya uzaktan bildirim gerekiyorsa satın alma yapmayın.',
      technicalSource: 'https://www.tfa-dostmann.de/en/product/digital-fridge-freezer-thermometer-30-1042/'
    },
    {
      id: 'tfa-dostmann-14-4006',
      asin: 'B001F8MRFM',
      mpn: '14.4006',
      brand: 'TFA Dostmann',
      name: 'TFA Dostmann 14.4006 Analog Buzdolabı ve Dondurucu Termometresi',
      verifiedAt,
      userNeed: 'Pil gerektirmeden buzdolabı veya dondurucu iç sıcaklığını hızlı ve kolay okunur bir referansla kontrol etmek.',
      strengths: Object.freeze([
        '-30 ile +30 °C ölçüm aralığı',
        'Pil gerektirmeyen bimetal ölçüm yapısı',
        'Soğutma bölgelerini gösteren okunabilir analog kadran'
      ]),
      limitations: Object.freeze([
        'En düşük ve en yüksek değeri kaydetmez',
        'Sesli alarm veya uzaktan bildirim sunmaz',
        'Anlık okuma sağlar; kısa süreli sıcaklık yükselmelerini sonradan göstermez'
      ]),
      noBuyWhen: 'Kesinti sonrası sıcaklık geçmişi, alarm veya uzaktan takip gerekiyorsa satın alma yapmayın.',
      technicalSource: 'https://www.tfa-dostmann.de/en/product/analogue-fridge-freezer-thermometer-14-4006/'
    },
    {
      id: 'tfa-dostmann-lt-102-30-1034',
      asin: 'B001386MUK',
      mpn: '30.1034',
      brand: 'TFA Dostmann',
      name: 'TFA Dostmann LT-102 Kablolu Problu Dijital Sıcaklık Termometresi',
      verifiedAt,
      userNeed: 'Dolap kapağını sık açmadan kablolu probla sıcaklığı izlemek ve belirlenen alt veya üst sınır aşıldığında yerel sesli-görsel uyarı almak.',
      strengths: Object.freeze([
        '-40 ile +70 °C ölçüm aralığı ve 300 cm kablolu prob',
        'Ayarlanabilir alt ve üst sınır için sesli ve görsel uyarı',
        'En düşük-en yüksek değer, veri tutma ve IP65 ön yüz'
      ]),
      limitations: Object.freeze([
        'Uyarı yalnız cihazın bulunduğu yerde duyulur; telefona bildirim göndermez',
        'Prob kablosunun yanlış geçirilmesi kapı contasını bozabilir',
        'Tıbbi, farmasötik, laboratuvar veya mevzuata tabi kayıt sistemi yerine geçmez'
      ]),
      noBuyWhen: 'Kalibrasyon sertifikalı kayıt, uzaktan alarm, otomatik veri günlüğü veya mevzuata tabi soğuk zincir izleme gerekiyorsa satın alma yapmayın.',
      technicalSource: 'https://www.tfa-dostmann.de/en/product/professional-digital-thermometer-with-cable-sensor-probe-lt-102-30-1034/'
    }
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
      verifiedAt
    });
  }
  return Object.freeze({version, affiliateTag, verificationMaxAgeDays, verifiedAt, category, products, amazonProductUrl, verificationStatus});
});
