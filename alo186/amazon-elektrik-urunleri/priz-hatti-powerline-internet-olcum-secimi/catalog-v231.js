(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root && typeof root === 'object') root.Alo186PowerlineInternetCatalogV231 = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const version = 231;
  const affiliateTag = 'alo186rehber-21';
  const verificationMaxAgeDays = 45;
  const verifiedAt = '2026-08-03';
  const category = Object.freeze({
    id: 'consumer_powerline_internet_measurement',
    risk: 'consumer-medium',
    affiliatePolicy: 'after_tool',
    requiredTool: 'embedded-powerline-circuit-and-speed-check-v231',
    professionalOnly: false,
    excludes: Object.freeze([
      'damaged-hot-loose-or-ungrounded-outlet',
      'medical-or-life-safety-network',
      'fire-alarm-elevator-or-access-control',
      'industrial-control-or-building-automation',
      'shared-building-meter-or-unknown-electrical-boundary',
      'energized-electrical-diagnostics',
    ]),
  });

  const products = Object.freeze([
    Object.freeze({
      id: 'tp-link-tl-pa7017p-kit',
      asin: 'B0859MDSFX',
      mpn: 'TL-PA7017P KIT',
      brand: 'TP-Link',
      name: 'TP-Link TL-PA7017P KIT AV1000 Gigabit Passthrough Powerline',
      verifiedAt,
      userNeed: 'Wi-Fi erişiminin zayıf olduğu kişisel ev/ofis noktasına, yeni kablo çekmeden duvar prizi hattı üzerinden tek Gigabit Ethernet bağlantısı taşımak.',
      strengths: Object.freeze([
        'HomePlug AV2 sınıfında 1000 Mbps teorik powerline bağlantı hızı',
        'Tek Gigabit Ethernet portu ve entegre EU geçişli elektrik prizi',
        'Pair düğmesi, 128-bit AES powerline şifreleme ve tak-çalıştır kurulum',
      ]),
      limitations: Object.freeze([
        'Gerçek hız elektrik tesisatı, ayrı devre/faz, AFCI, mesafe ve elektriksel gürültüye göre belirgin değişebilir',
        'Wi-Fi yayını yapmaz; hedef cihaz Ethernet ile bağlanmalıdır',
        'Çoklayıcı, aşırı gerilim koruyucu veya UPS arkasında performans düşebilir; doğrudan sağlam duvar prizi testi gerekir',
      ]),
      noBuyWhen: 'Mevcut Ethernet veya mesh bağlantısı hedef noktada yeterliyse, iki priz aynı kullanıcı tesisatı içinde değilse, doğrudan duvar prizi testi başarısızsa ya da prizde ısınma, gevşeklik, yanık kokusu veya hasar varsa satın alma yapmayın.',
      technicalSource: 'https://www.tp-link.com/tr/home-networking/powerline/tl-pa7017p-kit/',
    }),
    Object.freeze({
      id: 'tp-link-tl-wpa7617-kit',
      asin: 'B08XNLZLJ3',
      mpn: 'TL-WPA7617 KIT',
      brand: 'TP-Link',
      name: 'TP-Link TL-WPA7617 KIT AV1000 Gigabit Passthrough ac Wi-Fi',
      verifiedAt,
      userNeed: 'Elektrik hattı üzerinden uzak odaya hem Gigabit Ethernet hem de çift bantlı kişisel Wi-Fi erişimi taşımak.',
      strengths: Object.freeze([
        'HomePlug AV2 AV1000 sınıfı ve tek Gigabit Ethernet portu',
        'AC1200 çift bant Wi-Fi: 5 GHz 867 Mbps ve 2,4 GHz 300 Mbps teorik sınıf',
        'Geçişli elektrik prizi, Wi-Fi Auto-Sync ve pair düğmeli kurulum',
      ]),
      limitations: Object.freeze([
        'Powerline ve Wi-Fi hızları teoriktir; gerçek sonuç tesisat, gürültü, mesafe ve istemci yetenekleriyle sınırlanır',
        'Mesh dolaşımı veya kurumsal erişim noktası yönetimi yerine geçmez',
        'Donanım sürümü, bölgesel paket ve mevcut powerline uyumluluğu Amazon sayfası ile ürün etiketinde yeniden kontrol edilmelidir',
      ]),
      noBuyWhen: 'Mevcut mesh veya access point hedef noktada kararlı çalışıyorsa, yalnız kablolu bağlantı gerekiyorsa daha sade bir çözüm yeterliyse, elektrik sınırı bilinmiyorsa veya priz güvenli değilse satın alma yapmayın.',
      technicalSource: 'https://www.tp-link.com/tr/home-networking/powerline/tl-wpa7617-kit/',
    }),
    Object.freeze({
      id: 'tp-link-tl-wpa4220-kit',
      asin: 'B00C2ICYPC',
      mpn: 'TL-WPA4220 KIT',
      brand: 'TP-Link',
      name: 'TP-Link TL-WPA4220 KIT AV600 300 Mbps Wi-Fi Powerline',
      verifiedAt,
      userNeed: 'Yüksek Gigabit gereksinimi olmayan kişisel kullanımda, elektrik hattı üzerinden ulaşılması zor bir odaya temel Ethernet ve 2,4 GHz Wi-Fi erişimi taşımak.',
      strengths: Object.freeze([
        'HomePlug AV sınıfında 600 Mbps teorik powerline bağlantı hızı',
        '2,4 GHz bandında 300 Mbps teorik Wi-Fi ve Wi-Fi Clone/Auto-Sync işlevi',
        'Mevcut elektrik hattını kullanarak kablo çekmeden oda bazlı kapsama ekleme',
      ]),
      limitations: Object.freeze([
        'Gigabit ve 5 GHz gereksinimi için uygun değildir; Ethernet portu ve Wi-Fi sınıfı daha düşüktür',
        'Gerçek veri hızı tesisat kalitesi, elektriksel gürültü ve devre topolojisine bağlıdır',
        'Donanım sürümüne göre özellik ve yönetim yazılımı değişebilir; model etiketi yeniden doğrulanmalıdır',
      ]),
      noBuyWhen: 'Hedef kullanım 5 GHz, Gigabit, düşük gecikmeli yoğun trafik veya yönetilen kurumsal ağ gerektiriyorsa; mevcut Wi-Fi yeterliyse ya da priz güvenliği ve elektrik sınırı doğrulanamıyorsa satın alma yapmayın.',
      technicalSource: 'https://www.tp-link.com/tr/home-networking/powerline/tl-wpa4220-kit/',
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
