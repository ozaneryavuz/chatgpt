(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root && typeof root === 'object') root.Alo186RfRemoteSocketCatalogV237 = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const version = 237;
  const affiliateTag = 'alo186rehber-21';
  const verificationMaxAgeDays = 45;
  const verifiedAt = '2026-08-03';
  const category = Object.freeze({
    id: 'consumer_electrical_load_rf_remote_socket_selection',
    risk: 'consumer-medium',
    affiliatePolicy: 'after_tool',
    requiredTool: 'embedded-rf-remote-socket-load-safety-v237',
    professionalOnly: false,
    excludes: Object.freeze([
      'medical-or-life-safety-load',
      'ev-charging',
      'space-heater-or-heating-load',
      'motor-compressor-pump',
      'industrial-control',
      'unattended-high-power-load'
    ])
  });
  const products = Object.freeze([
    {
      id: 'brennenstuhl-comfort-line-mini-1507070',
      asin: 'B099653MQ4',
      mpn: '1507070',
      brand: 'Brennenstuhl',
      name: 'Brennenstuhl Comfort-Line Mini 3+1 Uzaktan Kumandalı Priz Seti',
      verifiedAt,
      userNeed: 'İç mekânda erişilmesi zor, kritik olmayan düşük güçlü lambaları veya elektronik cihazları üç ayrı priz üzerinden uzaktan açıp kapatmak.',
      strengths: Object.freeze([
        '3 adet IP20 iç mekân alıcısı ve 3 kanallı el kumandası',
        '433,92 MHz radyo kontrolü ve açık alanda 25 metreye kadar üretici beyanı',
        'Her alıcı için 2300 W üst sınırı ve artırılmış temas koruması'
      ]),
      limitations: Object.freeze([
        'Yalnız kuru iç mekân kullanımı için IP20 sınıfındadır',
        'Enerji ölçümü, Wi-Fi, uygulama veya aşırı gerilim koruması sunmaz',
        'Menzil duvar, metal yüzey ve parazite göre düşebilir'
      ]),
      noBuyWhen: 'Mevcut anahtar veya erişim düzeni yeterliyse; yük 2300 W sınırına yaklaşıyorsa; cihaz ısıtıcı, motor, pompa, kompresör, tıbbi veya yaşam güvenliği yüküyse satın alma yapmayın.',
      technicalSource: 'https://www.brennenstuhl.com/de-DE/produkte/funksteckdosen/comfort-line-mini-funkschalt-set-3x-ip20'
    },
    {
      id: 'brennenstuhl-comfort-line-outdoor-1507030',
      asin: 'B074DW5YV1',
      mpn: '1507030',
      brand: 'Brennenstuhl',
      name: 'Brennenstuhl RC CE1 0201 Comfort-Line 2’li Dış Mekân Uzaktan Kumandalı Priz Seti',
      verifiedAt,
      userNeed: 'Korunaklı dış mekânda kritik olmayan aydınlatma gibi düşük riskli elektrik yüklerini iki ayrı IP44 alıcı üzerinden uzaktan açıp kapatmak.',
      strengths: Object.freeze([
        '2 adet IP44 dış mekân alıcısı ve 4 kanallı el kumandası',
        '433,92 MHz radyo kontrolü ve 25 metreye kadar üretici beyanı',
        'Her alıcı için 1000 W üst sınırı ve artırılmış temas koruması'
      ]),
      limitations: Object.freeze([
        'IP44 sınıfı suya daldırma veya açıkta sürekli yağmur kullanımı anlamına gelmez',
        'Enerji ölçümü, Wi-Fi, uygulama veya aşırı gerilim koruması sunmaz',
        'Pompa, ısıtıcı, kompresör ve yüksek kalkış akımlı yükler için seçim aracı değildir'
      ]),
      noBuyWhen: 'Priz su birikintisi, açık yağmur veya tozlu endüstriyel ortamdaysa; yük 1000 W sınırına yaklaşıyorsa; motor, pompa, ısıtıcı, tıbbi veya yaşam güvenliği yüküyse satın alma yapmayın.',
      technicalSource: 'https://www.brennenstuhl.com/en-DE/products/remote-controllers/comfort-line-remote-control-set-2x-ip44'
    },
    {
      id: 'brennenstuhl-comfort-line-1507040',
      asin: 'B074DVCXWM',
      mpn: '1507040',
      brand: 'Brennenstuhl',
      name: 'Brennenstuhl RC CE1 3001 Comfort-Line 3’lü İç Mekân Uzaktan Kumandalı Priz Seti',
      verifiedAt,
      userNeed: 'İç mekânda üç kritik olmayan elektrik yükünü tek el kumandasıyla bağımsız veya birlikte kontrol etmek.',
      strengths: Object.freeze([
        '3 adet IP20 iç mekân alıcısı ve 4 kanallı el kumandası',
        '433,92 MHz radyo kontrolü ve 25 metreye kadar üretici beyanı',
        'Her alıcı için 1000 W üst sınırı ve kendi kendine öğrenen kodlama'
      ]),
      limitations: Object.freeze([
        'Yalnız kuru iç mekân kullanımı için IP20 sınıfındadır',
        'Enerji tüketimi ölçmez ve internet üzerinden uzaktan erişim sağlamaz',
        '1000 W üst sınırı nedeniyle yüksek güçlü cihazlara uygun değildir'
      ]),
      noBuyWhen: 'Mevcut çözüm yeterliyse; yük 1000 W sınırına yaklaşıyorsa; cihaz ısıtıcı, motor, pompa, kompresör, EV şarjı, tıbbi veya yaşam güvenliği yüküyse satın alma yapmayın.',
      technicalSource: 'https://www.brennenstuhl.com/en-DE/products/remote-controllers/comfort-line-remote-control-set-3x-ip20'
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
