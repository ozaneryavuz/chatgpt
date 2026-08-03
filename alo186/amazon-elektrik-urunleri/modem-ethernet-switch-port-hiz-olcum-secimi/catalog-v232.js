(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root && typeof root === 'object') root.Alo186ModemEthernetSwitchCatalogV232 = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const version = 232;
  const affiliateTag = 'alo186rehber-21';
  const verificationMaxAgeDays = 45;
  const verifiedAt = '2026-08-03';
  const category = Object.freeze({
    id: 'consumer_modem_ethernet_switch_port_speed_measurement',
    risk: 'consumer-medium',
    affiliatePolicy: 'after_tool',
    requiredTool: 'embedded-modem-ethernet-switch-measurement-v232',
    professionalOnly: false,
    excludes: Object.freeze(['poe-power-design','life-safety-network','medical-communications','fire-alarm-network','industrial-control-network'])
  });
  const products = Object.freeze([
    {
      id: 'tp-link-ls1005g', asin: 'B07RK6CVS3', mpn: 'LS1005G', brand: 'TP-Link',
      name: 'TP-Link LS1005G 5 Port Gigabit Masaüstü Switch', verifiedAt,
      userNeed: 'Modem veya yönlendiricide boş Ethernet portu kalmadığında, dört adede kadar ek gigabit kablolu uç bağlamak.',
      strengths: ['5 × 10/100/1000 Mbps otomatik anlaşmalı RJ45 port','Fansız ve tak-çalıştır tasarım','10 Gbps anahtarlama kapasitesi ve kompakt gövde'],
      limitations: ['PoE ile cihaz beslemez','VLAN, port önceliği veya yönetim arayüzü sunmaz','Beş porttan biri modem/yönlendirici uplink’i için kullanıldığında en fazla dört yeni uç kalır'],
      noBuyWhen: 'Dört ek porttan fazlası, PoE, VLAN veya trafik yönetimi gerekiyorsa; mevcut modem portları yeterliyse satın alma yapmayın.',
      technicalSource: 'https://www.tp-link.com/tr/business-networking/soho-switch-unmanaged/ls1005g/'
    },
    {
      id: 'tp-link-tl-sg108e', asin: 'B00K4DS5KU', mpn: 'TL-SG108E', brand: 'TP-Link',
      name: 'TP-Link TL-SG108E 8 Port Gigabit Easy Smart Switch', verifiedAt,
      userNeed: 'Modem arkasında daha fazla gigabit port ile VLAN, QoS, kablo tanılama veya port izleme ihtiyacını birlikte karşılamak.',
      strengths: ['8 × 10/100/1000 Mbps RJ45 port','VLAN, QoS, IGMP Snooping, port mirroring ve kablo tanılama özellikleri','Fansız metal kasa ve 16 Gbps anahtarlama kapasitesi'],
      limitations: ['PoE sağlamaz','2.5 Gigabit bağlantı sunmaz','Bazı yönetim yardımcıları ve özellikler donanım sürümüne göre değişebilir'],
      noBuyWhen: 'Yalnız basit dört port genişlemesi yeterliyse, 2.5G veya PoE gerekiyorsa ya da yönetim ayarlarını doğrulayamayacaksanız satın alma yapmayın.',
      technicalSource: 'https://www.tp-link.com/tr/business-networking/easy-smart-switch/tl-sg108e/v1/'
    },
    {
      id: 'tp-link-tl-sg108-m2', asin: 'B08WQ16H4N', mpn: 'TL-SG108-M2', brand: 'TP-Link',
      name: 'TP-Link TL-SG108-M2 8 Port 2.5G Masaüstü Switch', verifiedAt,
      userNeed: '2.5G portlu modem, NAS, bilgisayar veya Wi-Fi erişim noktaları arasında gigabit üstü yerel ağ aktarımı kurmak.',
      strengths: ['8 × 100 Mbps / 1 Gbps / 2.5 Gbps otomatik anlaşmalı port','40 Gbps anahtarlama kapasitesi','Fansız metal kasa ve tak-çalıştır kullanım'],
      limitations: ['PoE sağlamaz','Yönetilebilir VLAN arayüzü sunmaz','Gerçek 2.5G faydası için uç cihazların ve bağlantının da 2.5G desteklemesi gerekir'],
      noBuyWhen: 'Modem, NAS ve bilgisayar portları yalnız 1G ise; PoE veya yönetilebilir VLAN gerekiyorsa; ölçümde gigabit darboğazı yoksa satın alma yapmayın.',
      technicalSource: 'https://www.tp-link.com/tr/business-networking/unmanaged-switch/tl-sg108-m2/'
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
