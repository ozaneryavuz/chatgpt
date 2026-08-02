(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root && typeof root === 'object') root.Alo186GigabitSwitchCatalogV222 = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const version = 222;
  const affiliateTag = 'alo186rehber-21';
  const verificationMaxAgeDays = 45;
  const verifiedAt = '2026-08-02';
  const category = Object.freeze({
    id: 'consumer_gigabit_ethernet_switch',
    risk: 'consumer-medium',
    affiliatePolicy: 'after_tool',
    requiredTool: 'embedded-gigabit-switch-compatibility-v222',
    professionalOnly: false,
    excludes: Object.freeze(['poe-switch', 'industrial-switch', 'rack-switch', 'managed-enterprise-switch']),
  });

  const products = Object.freeze([
    Object.freeze({
      id: 'tp-link-tl-sg105',
      asin: 'B00A128S24',
      mpn: 'TL-SG105',
      brand: 'TP-Link',
      name: 'TP-Link TL-SG105 5 Port Gigabit Masaüstü Switch',
      verifiedAt,
      userNeed: 'Modem veya yönlendiricideki tek Ethernet bağlantısını televizyon, bilgisayar, oyun konsolu ya da ağ depolama gibi birkaç kişisel cihaza kablolu olarak dağıtmak.',
      strengths: Object.freeze([
        '5 adet 10/100/1000 Mbps Auto-Negotiation ve Auto-MDI/MDIX RJ45 portu',
        'Fansız ve metal masaüstü/duvar montajına uygun gövde',
        'Tak-çalıştır kullanım; temel ev ve küçük ofis ağı için yapılandırma gerektirmez',
        '802.1p/DSCP QoS ve IGMP Snooping desteği; donanım sürümüne göre ayrıntılar değişebilir',
      ]),
      limitations: Object.freeze([
        'Yönetilmeyen switch sınıfındadır; VLAN yapılandırması, ayrıntılı izleme veya merkezi yönetim sunmaz',
        'PoE çıkışı yoktur; kamera veya erişim noktasını Ethernet kablosundan beslemez',
        'Güç adaptörü çıkışı ve bazı yazılım özellikleri donanım sürümüne göre değişebileceğinden ürün etiketi kontrol edilmelidir',
      ]),
      noBuyWhen: 'Yönlendiricinizde yeterli boş Gigabit port varsa, PoE gerekiyorsa veya VLAN/port yönetimi ihtiyacınız bulunuyorsa bu modeli satın almayın.',
      technicalSource: 'https://www.tp-link.com/tr/home-networking/soho-switch/tl-sg105/',
    }),
    Object.freeze({
      id: 'tp-link-tl-sg108',
      asin: 'B00A121WN6',
      mpn: 'TL-SG108',
      brand: 'TP-Link',
      name: 'TP-Link TL-SG108 8 Port Gigabit Masaüstü Switch',
      verifiedAt,
      userNeed: 'Ev veya küçük ofiste beşten fazla kablolu cihazı tek yerel ağda, ek yapılandırma yapmadan Gigabit bağlantıyla toplamak.',
      strengths: Object.freeze([
        '8 adet 10/100/1000 Mbps Auto-Negotiation ve Auto-MDI/MDIX RJ45 portu',
        'Fansız metal gövde ve masaüstü veya duvar montajı',
        'Tak-çalıştır yapı; 802.3x akış kontrolü',
        '802.1p/DSCP QoS ve IGMP Snooping ile temel trafik önceliklendirme ve multicast optimizasyonu',
      ]),
      limitations: Object.freeze([
        'Yönetilmeyen switch sınıfındadır; port bazlı erişim politikası veya ayrıntılı VLAN yönetimi yoktur',
        'PoE desteği bulunmaz',
        'Sekiz portun tamamının kullanılacağı kablolama, havalandırma ve adaptör priz alanı önceden planlanmalıdır',
      ]),
      noBuyWhen: 'Beş port yeterliyse, PoE cihaz beslemesi gerekiyorsa veya yönetilebilir ağ özellikleri zorunluysa daha büyük gövde ve port sayısı için ödeme yapmayın.',
      technicalSource: 'https://www.tp-link.com/tr/home-networking/soho-switch/tl-sg108/',
    }),
    Object.freeze({
      id: 'tp-link-tl-sg105e',
      asin: 'B00N0OHEMA',
      mpn: 'TL-SG105E',
      brand: 'TP-Link',
      name: 'TP-Link TL-SG105E 5 Port Gigabit Easy Smart Switch',
      verifiedAt,
      userNeed: 'Beş kablolu bağlantıyı korurken VLAN, trafik önceliği, port izleme veya kablo tanısı gibi temel yönetim işlevlerine ihtiyaç duymak.',
      strengths: Object.freeze([
        '5 adet 10/100/1000 Mbps RJ45 portu ve fansız metal gövde',
        'Web arayüzü ve yardımcı uygulama üzerinden temel yönetim',
        'VLAN, QoS, IGMP Snooping, port mirroring, kablo tanısı ve loop prevention özellikleri',
        'Tak-çalıştır çalışabilir; gelişmiş işlevler ihtiyaç halinde yapılandırılır',
      ]),
      limitations: Object.freeze([
        'Kurumsal tam yönetilebilir switch değildir; gelişmiş L3 yönlendirme ve merkezi kurumsal yönetim beklenmemelidir',
        'PoE çıkışı yoktur',
        'VLAN ve diğer özellikler yanlış yapılandırılırsa bağlantı kesilebilir; donanım sürümü ve kullanım kılavuzu doğrulanmalıdır',
      ]),
      noBuyWhen: 'VLAN veya izleme işlevlerini kullanmayacaksanız, mevcut yönetilmeyen switch yeterliyse ya da PoE/tam kurumsal yönetim gerekiyorsa bu modeli satın almayın.',
      technicalSource: 'https://www.tp-link.com/tr/business-networking/soho-switch-easy-smart/tl-sg105e/',
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

  return Object.freeze({ version, affiliateTag, verificationMaxAgeDays, verifiedAt, category, products, amazonProductUrl, verificationStatus });
});
