(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root && typeof root === 'object') root.Alo186UsbWifiCatalogV228 = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const version = 228;
  const affiliateTag = 'alo186rehber-21';
  const verificationMaxAgeDays = 45;
  const verifiedAt = '2026-08-03';
  const category = Object.freeze({
    id: 'consumer_usb_wifi_adapter',
    risk: 'consumer-medium',
    affiliatePolicy: 'after_tool',
    requiredTool: 'embedded-usb-wifi-compatibility-v228',
    professionalOnly: false,
    excludes: Object.freeze([
      'enterprise-managed-network',
      'critical-infrastructure-network',
      'medical-or-life-safety-network',
      'industrial-control-network',
      'regulated-security-network',
    ]),
  });

  const products = Object.freeze([
    Object.freeze({
      id: 'tp-link-archer-t3u-plus',
      asin: 'B0859M539M',
      mpn: 'Archer T3U Plus',
      brand: 'TP-Link',
      name: 'TP-Link Archer T3U Plus AC1300 USB Wi-Fi Adaptörü',
      verifiedAt,
      userNeed: 'Dahili Wi-Fi kartı olmayan veya eski kalan kişisel bir masaüstü ya da dizüstü bilgisayarı çift bant Wi-Fi 5 ağına bağlamak.',
      strengths: Object.freeze([
        'Üretici kaynağında 5 GHz bandında 867 Mbps ve 2,4 GHz bandında 400 Mbps fiziksel bağlantı sınıfı',
        'USB 3.0 arabirimi ve çift yüksek kazançlı harici anten',
        'MU-MIMO desteği ve ayarlanabilir anten yapısı',
      ]),
      limitations: Object.freeze([
        'AC1300 değeri gerçek internet veya dosya aktarım hızını garanti etmez',
        'Gerçek sonuç router, kanal, mesafe, duvar, parazit, USB portu ve sürücüye bağlıdır',
        'İşletim sistemi ve donanım sürümü uyumu satın alma öncesinde üretici destek sayfasından doğrulanmalıdır',
      ]),
      noBuyWhen: 'Ethernet bağlantısı kullanılabiliyorsa, mevcut Wi-Fi bağlantısı ihtiyacı karşılıyorsa, işletim sistemi desteklenmiyorsa veya sorun internet servisinde ya da router yerleşimindeyse satın almayın.',
      technicalSource: 'https://www.tp-link.com/tr/home-networking/adapter/archer-t3u-plus/',
    }),
    Object.freeze({
      id: 'tp-link-archer-t2u-plus',
      asin: 'B07P5PRK7J',
      mpn: 'Archer T2U Plus',
      brand: 'TP-Link',
      name: 'TP-Link Archer T2U Plus AC600 USB Wi-Fi Adaptörü',
      verifiedAt,
      userNeed: 'Kişisel bilgisayarda temel internet, görüntülü görüşme ve çift bant bağlantı için uygun maliyetli harici Wi-Fi alıcısı kullanmak.',
      strengths: Object.freeze([
        'Üretici kaynağında 5 GHz bandında 433 Mbps ve 2,4 GHz bandında 200 Mbps fiziksel bağlantı sınıfı',
        '5 dBi ayarlanabilir yüksek kazançlı harici anten',
        '2,4 GHz ve 5 GHz çift bant Wi-Fi 5 desteği',
      ]),
      limitations: Object.freeze([
        'USB 2.0 arabirimi kullanır ve daha yüksek sınıf bağlantılarda sistem darboğazı oluşabilir',
        'AC600 değeri gerçek internet hızını veya kapsama alanını garanti etmez',
        'Sürücü desteği işletim sistemi ve bölgesel donanım sürümüne göre değişebilir',
      ]),
      noBuyWhen: 'Yüksek yerel ağ aktarımına ihtiyacınız varsa, cihazınızda kararlı çift bant Wi-Fi zaten varsa, işletim sistemi desteklenmiyorsa veya kök neden router ya da servis sağlayıcıysa satın almayın.',
      technicalSource: 'https://www.tp-link.com/tr/home-networking/adapter/archer-t2u-plus/',
    }),
    Object.freeze({
      id: 'tp-link-archer-t3u-nano',
      asin: 'B09KTDXPY3',
      mpn: 'Archer T3U Nano',
      brand: 'TP-Link',
      name: 'TP-Link Archer T3U Nano AC1300 USB Wi-Fi Adaptörü',
      verifiedAt,
      userNeed: 'Taşınabilir bilgisayarda USB portundan az çıkıntı yapan, sürekli takılı bırakılabilecek çift bant Wi-Fi 5 adaptörü kullanmak.',
      strengths: Object.freeze([
        'Üretici kaynağında 5 GHz bandında 867 Mbps ve 2,4 GHz bandında 400 Mbps fiziksel bağlantı sınıfı',
        'Kompakt nano tasarım ve MU-MIMO desteği',
        'WPA3 dahil güncel kişisel ağ güvenlik seçenekleri',
      ]),
      limitations: Object.freeze([
        'USB 2.0 arabirimi ve küçük dahili anten yapısı uzun mesafe veya yoğun parazitte sınır oluşturabilir',
        'Nano gövde yüksek kazançlı harici antenli modellerin konumlandırma esnekliğini sağlamaz',
        'İşletim sistemi güncellemesinden sonra sürücü güncellemesi gerekebilir',
      ]),
      noBuyWhen: 'Zayıf sinyal için yönlendirilebilir yüksek kazançlı anten gerekiyorsa, Ethernet kullanılabiliyorsa, mevcut Wi-Fi yeterliyse veya tam işletim sistemi sürümünüz desteklenmiyorsa satın almayın.',
      technicalSource: 'https://www.tp-link.com/tr/home-networking/adapter/archer-t3u-nano/',
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

  return Object.freeze({
    version,
    affiliateTag,
    verificationMaxAgeDays,
    verifiedAt,
    category,
    products,
    amazonProductUrl,
    verificationStatus,
  });
});
