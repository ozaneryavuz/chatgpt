(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root && typeof root === 'object') root.Alo186LaptopCoolingCatalogV229 = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const version = 229;
  const affiliateTag = 'alo186rehber-21';
  const verificationMaxAgeDays = 45;
  const verifiedAt = '2026-08-03';
  const category = Object.freeze({
    id: 'consumer_laptop_cooling_pad',
    risk: 'consumer-low',
    affiliatePolicy: 'after_tool',
    requiredTool: 'embedded-laptop-cooling-need-check-v229',
    professionalOnly: false,
    excludes: Object.freeze([
      'battery-swelling-or-burning-smell',
      'medical-device-computer',
      'industrial-control-workstation',
      'critical-safety-monitoring-system',
      'liquid-damaged-device',
    ]),
  });

  const products = Object.freeze([
    Object.freeze({
      id: 'havit-f2071',
      asin: 'B0CJRXQNPK',
      mpn: 'F2071',
      brand: 'HAVIT',
      name: 'HAVIT Gamenote F2071 Laptop Soğutucu Stand',
      verifiedAt,
      userNeed: 'Alt hava girişleri açık olan 17 inçe kadar kişisel dizüstü bilgisayarda, ölçülmüş sıcaklık artışı ve termal hız düşüşü için ayarlanabilir hava akışı sağlamak.',
      strengths: Object.freeze([
        'Altı adet 70 mm fan ve 2500 RPM ±%10 üretici değeri',
        'Altı kademeli yükseklik ayarı ve metal ağ hava geçiş yüzeyi',
        'İki USB 2.0 portu ve ayarlanabilir fan hızı',
      ]),
      limitations: Object.freeze([
        'Soğutma etkisi dizüstü bilgisayarın alt hava girişlerinin fanlarla hizalanmasına bağlıdır',
        'Tozlu fan, kurumuş termal macun veya arızalı iç fan sorununu çözmez',
        'Fan sesi, USB güç tüketimi ve RGB aydınlatma sessiz çalışma ortamına uygun olmayabilir',
      ]),
      noBuyWhen: 'Cihaz normal yükte termal sınıra ulaşmıyorsa, alt hava girişi yoksa, bakım yapılmamışsa veya batarya şişmesi, yanık kokusu ya da sıvı teması varsa satın almayın; cihazı kullanmayı bırakıp yetkili servise başvurun.',
      technicalSource: 'https://havitsmart.com/tr/products/havit-sogutma-ped-f2071',
    }),
    Object.freeze({
      id: 'classone-gt100',
      asin: 'B07KB3V62T',
      mpn: 'GT100',
      brand: 'Classone',
      name: 'Classone GT100 Gaming Laptop Soğutucu Stand',
      verifiedAt,
      userNeed: '13–17 inç kişisel dizüstü bilgisayarda tek büyük fanla yönlendirilmiş hava akışı, yükseklik ayarı ve masa kullanım açısı elde etmek.',
      strengths: Object.freeze([
        '300–2200 RPM aralığında hız kontrollü fan yapısı',
        'Yedi kademeli yükseklik ayarı ve 17,3 inçe kadar ürün sınıfı',
        'İki USB Type-A bağlantısı, RGB aydınlatma ve telefon tutucu',
      ]),
      limitations: Object.freeze([
        'Tek fanın konumu her dizüstü bilgisayarın hava girişleriyle eşleşmeyebilir',
        'Yüksek fan devrinde gürültü artabilir ve gerçek sıcaklık düşüşü cihaz tasarımına göre değişir',
        'İç soğutma sistemindeki toz, fan arızası veya termal arayüz sorununu gidermez',
      ]),
      noBuyWhen: 'Dizüstü bilgisayarın alt hava girişi fan alanıyla hizalanmıyorsa, mevcut yükseltici stand yeterliyse, sıcaklık ölçümü normal ise veya cihazda batarya şişmesi ya da yanık kokusu varsa satın almayın.',
      technicalSource: 'https://classonestore.com/urun/elektronik/notebook-sogutucu/classone-gt100-laptop-sogutucu/',
    }),
    Object.freeze({
      id: 'frisby-fnc-5230st',
      asin: 'B07C9S8DBD',
      mpn: 'FNC-5230ST',
      brand: 'Frisby',
      name: 'Frisby FNC-5230ST Gaming Notebook Soğutucu Stand',
      verifiedAt,
      userNeed: '10–17 inç kişisel dizüstü bilgisayarda dört fanı farklı modlarda çalıştırarak hava girişlerinin konumuna göre daha geniş soğutma alanı oluşturmak.',
      strengths: Object.freeze([
        'İki adet 125 mm ve iki adet 70 mm olmak üzere dört fan',
        'Altı hız seviyesi, üç fan çalışma modu ve LCD kontrol paneli',
        'Beş kademeli yükseklik ayarı, metal ızgara ve iki USB portu',
      ]),
      limitations: Object.freeze([
        'Fan yerleşimi ve 10–17 inç ürün sınıfı gerçek kasa ölçüsüyle ayrıca doğrulanmalıdır',
        'Yaklaşık 1500 RPM fan sınıfı yüksek ısı yükünde her cihaz için yeterli olmayabilir',
        'Harici hava akışı iç fan temizliği, termal bakım veya arızalı bileşen onarımının yerine geçmez',
      ]),
      noBuyWhen: 'Cihazın alt hava girişleri fanlarla örtüşmüyorsa, yalnız ergonomik yükseltme gerekiyorsa, sıcaklık sorunu ölçülmemişse veya batarya şişmesi, sıvı teması ya da yanık kokusu varsa satın almayın.',
      technicalSource: 'https://b2b.gunes.net/frisby-fnc-5230st-10--17-aras-4x-fan-5x-kademe-gaming-notebook-sogutucu-stand_p_19802',
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

  return Object.freeze({version,affiliateTag,verificationMaxAgeDays,verifiedAt,category,products,amazonProductUrl,verificationStatus});
});
