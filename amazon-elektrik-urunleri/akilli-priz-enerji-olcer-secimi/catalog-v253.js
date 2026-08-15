(function (root, factory) {
  const catalog = factory();
  if (typeof module === 'object' && module.exports) module.exports = catalog;
  else root.ALO186SmartPlugCatalogV253 = catalog;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const DAY_MS = 24 * 60 * 60 * 1000;
  const catalog = {
    version: 253,
    affiliateTag: 'alo186rehber-21',
    verifiedAt: '2026-08-03',
    maxVerificationAgeDays: 45,
    category: {
      id: 'consumer_smart_plug_control_monitoring_fit',
      slug: 'akilli-priz-enerji-olcer-secimi',
      risk: 'consumer-medium',
      affiliatePolicy: 'after_tool',
      professionalOnly: false,
      highRiskDirectCta: false,
      excludes: [
        'topraksız, gevşek, kararmış, ısınan, fiziksel olarak hasarlı veya nemli priz',
        'elektrikli araç şarjı, sabit tesisat, pano, UPS, jeneratör, medikal cihaz veya yaşam güvenliği yükü',
        'ısıtıcı, ütü, su ısıtıcı, klima, pompa, kompresör, buzdolabı veya yüksek kalkış akımlı yük',
        'gözetimsiz kritik yük, yangın alarmı, güvenlik sistemi veya erişim kontrolü',
        'çoklu prizleri zincirleme ya da adaptör üstüne adaptör takma'
      ]
    },
    products: [
      {
        id: 'meross-mss315-eu',
        asin: 'B0C4LHP7G3',
        mpn: 'MSS315 EU',
        brand: 'Meross',
        name: 'Meross MSS315 EU Matter akıllı priz ve enerji monitörü',
        verifiedAt: '2026-08-03',
        userNeed: 'Tek bir düşük veya orta güçlü fişli cihazı uzaktan açıp kapatmak ve gerçek zamanlı ya da tarihsel tüketimini izlemek isteyen; 2,4 GHz Wi-Fi ve Matter uyumunu doğrulayabilen kullanıcı.',
        strengths: [
          'Üretici beyanıyla gerçek zamanlı ve tarihsel enerji izleme',
          'Matter ve yaygın akıllı ev ekosistemleriyle birlikte çalışabilme',
          '16 A maksimum çıkış üretici beyanı'
        ],
        limitations: [
          '16 A etiketi duvar prizi, tesisat ve bağlı cihazın otomatik olarak uygun olduğu anlamına gelmez',
          'Matter kurulumu için seçilen platforma göre uyumlu merkez ve güncel ağ gerekebilir',
          'Enerji ölçümü faturalandırma, kalibrasyonlu kabul veya yaşam güvenliği izleme cihazı değildir'
        ],
        noBuyWhen: 'Mevcut zamanlayıcı veya enerji ölçer ihtiyacınızı karşılıyorsa, uzaktan kontrol ya da ölçüm verisini düzenli kullanmayacaksanız yeni ürün satın almayın.',
        technical: {
          input: '100-240 V~, 50/60 Hz',
          output: '16 A maksimum üretici beyanı',
          energyMonitor: 'Var',
          wireless: '2,4 GHz Wi-Fi ve Bluetooth Low Energy',
          ecosystems: 'Matter / Meross / Apple Home / Alexa / Google',
          environment: '0-40 °C, yoğuşmasız iç ortam'
        },
        amazonAsinSource: 'https://www.amazon.com.tr/dp/B0C4LHP7G3',
        technicalSource: 'https://www.meross.com/en-gc/mTerminal/smart_plug_and_switch/matter-smart-plug/159'
      },
      {
        id: 'shelly-plus-plug-s-v1',
        asin: 'B0BTJ1DTBX',
        mpn: 'SNPL-00112EU',
        brand: 'Shelly',
        name: 'Shelly Plus Plug S V1 akıllı priz ve güç ölçer',
        verifiedAt: '2026-08-03',
        userNeed: 'Yerel web arayüzü, otomasyon entegrasyonu ve güç/enerji ölçümü isteyen; bağlı yükü 12 A sınırında tutabilen kullanıcı.',
        strengths: [
          'Üretici dokümanında gerilim, akım, güç ve enerji ölçümü',
          'Aşırı sıcaklık, gerilim, akım ve güç koruma işlevleri',
          'Wi-Fi, Bluetooth, yerel web arayüzü, MQTT ve betik desteği'
        ],
        limitations: [
          'Maksimum anahtarlama akımı 12 A’dır; bağlı yük etiketi ve ilk kalkış akımı ayrıca kontrol edilmelidir',
          'Koruma işlevleri uygun topraklama, RCD, tesisat koruması veya profesyonel ölçümün yerine geçmez',
          'Bulut, yerel ağ ve üçüncü taraf entegrasyonların gizlilik ve süreklilik koşulları ayrıca değerlendirilmelidir'
        ],
        noBuyWhen: 'Yalnız basit aç-kapa ihtiyacınız varsa ve mevcut güvenli çözüm yeterliyse gelişmiş ölçüm ve otomasyon özellikleri için ek ürün satın almayın.',
        technical: {
          supply: '230 V ±10 %, 50/60 Hz',
          maxCurrent: '12 A',
          socket: 'CEE 7/3 Type F / Schuko',
          metering: 'Gerilim, akım, güç ve enerji',
          protection: 'Aşırı sıcaklık, gerilim, akım ve güç',
          wireless: '2,4 GHz Wi-Fi ve Bluetooth 4.2'
        },
        amazonAsinSource: 'https://www.amazon.com.tr/dp/B0BTJ1DTBX',
        technicalSource: 'https://kb.shelly.cloud/knowledge-base/shelly-plus-plug-s'
      },
      {
        id: 'tp-link-tapo-p100',
        asin: 'B07Z5JD3T4',
        mpn: 'Tapo P100',
        brand: 'TP-Link Tapo',
        name: 'TP-Link Tapo P100 mini akıllı Wi-Fi priz',
        verifiedAt: '2026-08-03',
        userNeed: 'Enerji ölçümü gerekmeyen, tek bir uygun fişli cihaz için uygulama, zamanlama, sesli komut ve uzaktan aç-kapa isteyen kullanıcı.',
        strengths: [
          'Hub gerektirmeyen 2,4 GHz Wi-Fi bağlantısı',
          'Uzaktan kontrol, program, zamanlayıcı ve cihaz paylaşımı',
          'Kompakt gövde ve Alexa/Google Assistant uyumluluğu'
        ],
        limitations: [
          'P100 enerji tüketimi ölçmez; tüketim analizi gerekiyorsa bu model satın alınmamalıdır',
          '10 A ve 2300 W üretici sınırı bağlı yük etiketi ve priz güvenliğiyle birlikte doğrulanmalıdır',
          'İnternet veya bulut erişimi kaybolduğunda uzaktan işlevler sınırlanabilir; kritik yük için kullanılmaz'
        ],
        noBuyWhen: 'Enerji tüketimi görmek istiyorsanız, mevcut zamanlayıcı yeterliyse veya uzaktan kontrol gerçek bir ihtiyacı çözmüyorsa bu modeli satın almayın.',
        technical: {
          supply: '220-240 V~, 50/60 Hz',
          maxCurrent: '10 A',
          maxPower: '2300 W üretici beyanı',
          energyMonitor: 'Yok',
          wireless: '2,4 GHz Wi-Fi',
          functions: 'Uzaktan kontrol, program, zamanlayıcı ve sesli kontrol'
        },
        amazonAsinSource: 'https://www.amazon.com.tr/dp/B07Z5JD3T4',
        technicalSource: 'https://www.tapo.com/en/product/smart-plug/tapo-p100/'
      }
    ]
  };

  catalog.verificationStatus = function verificationStatus(product, now) {
    const checked = Date.parse(`${product.verifiedAt}T00:00:00Z`);
    const current = now instanceof Date ? now.getTime() : Date.parse(String(now || new Date().toISOString()));
    const ageDays = Math.floor((current - checked) / DAY_MS);
    return {
      ageDays,
      fresh: Number.isFinite(ageDays) && ageDays >= 0 && ageDays <= catalog.maxVerificationAgeDays
    };
  };

  catalog.amazonProductUrl = function amazonProductUrl(product, now) {
    if (!catalog.verificationStatus(product, now).fresh) return null;
    return `https://www.amazon.com.tr/dp/${encodeURIComponent(product.asin)}?tag=${encodeURIComponent(catalog.affiliateTag)}`;
  };

  return Object.freeze(catalog);
});
