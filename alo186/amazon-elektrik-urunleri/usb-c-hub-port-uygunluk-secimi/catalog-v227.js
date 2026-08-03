(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root && typeof root === 'object') root.Alo186UsbCHubCatalogV227 = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const version = 227;
  const affiliateTag = 'alo186rehber-21';
  const verificationMaxAgeDays = 45;
  const verifiedAt = '2026-08-03';
  const category = Object.freeze({
    id: 'consumer_usb_c_multiport_hub',
    risk: 'consumer-medium',
    affiliatePolicy: 'after_tool',
    requiredTool: 'embedded-usb-c-hub-port-fit-v227',
    professionalOnly: false,
    excludes: Object.freeze([
      'medical-device-connectivity',
      'life-safety-communications',
      'industrial-control-network',
      'professional-broadcast-chain',
      'mains-wiring-or-charger-design',
      'mission-critical-dock',
    ]),
  });

  const products = Object.freeze([
    Object.freeze({
      id: 'ugreen-revodok-107-60515',
      asin: 'B093FKT9BF',
      mpn: '60515',
      brand: 'UGREEN',
      name: 'UGREEN Revodok 107 7-in-1 USB-C Hub',
      verifiedAt,
      amazonSource: 'https://www.amazon.com.tr/dp/B093FKT9BF',
      technicalSource: 'https://us.ugreen.com/products/7-in-1-multiport-adapter-with-4k-60hz',
      userNeed: 'Tek bir tam işlevli USB-C portundan HDMI görüntü, Gigabit Ethernet, iki USB-A veri portu ve SD/microSD kart erişimi almak.',
      strengths: Object.freeze([
        'Üretici kaynağında 7 bağlantı: HDMI, Gigabit Ethernet, iki USB-A 5 Gbps, SD, microSD ve USB-C PD girişi',
        'DisplayPort 1.4 destekli uygun ana cihazlarda HDMI üzerinden 4K 60 Hz sınıfı',
        '100 W PD giriş sınıfı ve üreticiye göre hub tüketimi sonrası ana cihaza en çok 95 W geçiş',
        'Amazon Türkiye ürün kaydında ASIN B093FKT9BF ile üretici model numarası 60515 birlikte yer alır',
      ]),
      limitations: Object.freeze([
        '4K 60 Hz için ana cihazın USB-C görüntü aktarımını ve DisplayPort 1.4 sınıfını desteklemesi gerekir',
        'USB-C PD portu veri portu değildir ve hub tek başına enerji kaynağı değildir',
        'Kart okuyucular, ağ, görüntü ve USB çevre birimleri aynı ana bağlantının bant genişliği ile güç bütçesini paylaşır',
      ]),
      noBuyWhen: 'Yalnız tek bir dönüştürücüye ihtiyacınız varsa, cihaz USB-C görüntü çıkışı sunmuyorsa, mevcut hub port ihtiyacını karşılıyorsa veya görev kritik bir profesyonel sistemse satın almayın.',
    }),
    Object.freeze({
      id: 'tp-link-uh6120c',
      asin: 'B0DCZY52K3',
      mpn: 'UH6120C',
      brand: 'TP-Link',
      name: 'TP-Link UH6120C 6-Port USB Type-C Hub',
      verifiedAt,
      amazonSource: 'https://www.amazon.com.tr/dp/B0DCZY52K3',
      technicalSource: 'https://www.tp-link.com/tr/home-networking/computer-accessory/uh6120c/',
      userNeed: 'Dizüstü bilgisayar veya tablette HDMI görüntü, kablolu Gigabit ağ ve üç adet 5 Gbps USB veri portunu tek USB-C bağlantıda toplamak.',
      strengths: Object.freeze([
        'Üretici kaynağında 4K 60 Hz HDMI, 1 Gbps RJ45, bir USB-C ve iki USB-A 5 Gbps veri portu',
        '100 W PD giriş sınıfı ve 180 mm örgülü ana bağlantı kablosu',
        'Alüminyum alaşımlı kasa ve konnektörü gövdede saklamaya yönelik taşınabilir tasarım',
        'Amazon Türkiye için güncel ürün kaydı ASIN B0DCZY52K3 ile UH6120C modelini eşler',
      ]),
      limitations: Object.freeze([
        'Görüntü çözünürlüğü ve yenileme hızı ana cihazın USB-C görüntü yeteneğine, kabloya ve ekrana bağlıdır',
        '100 W ifadesi PD giriş sınıfıdır; ana cihaza ulaşan gerçek güç şarj cihazı, kablo, protokol ve hub tüketimine göre değişir',
        'Birden fazla yüksek tüketimli çevre biriminde ortak güç ve 5 Gbps bağlantı bütçesi sınırlayıcı olabilir',
      ]),
      noBuyWhen: 'Ana cihaz yalnız veri amaçlı USB-C sunuyorsa, gerekli portlar daha basit bir adaptörle karşılanıyorsa, mevcut çözüm kararlı çalışıyorsa veya kurulum profesyonel ve kesintisiz işletme görevi taşıyorsa satın almayın.',
    }),
    Object.freeze({
      id: 'belkin-avc009btsgy',
      asin: 'B08XNG4ZKN',
      mpn: 'AVC009BTSGY',
      brand: 'Belkin',
      name: 'Belkin Connect USB-C 7-in-1 Multiport Hub',
      verifiedAt,
      amazonSource: 'https://www.amazon.com.tr/dp/B08XNG4ZKN',
      technicalSource: 'https://www.belkin.com/sg/p/usb-c-7-in-1-multiport-hub/P-AVC009.html',
      userNeed: 'USB-C dizüstü bilgisayar veya tablette HDMI, iki USB-A, SD, microSD, 3,5 mm ses ve PD geçişini tek taşınabilir hub üzerinde toplamak.',
      strengths: Object.freeze([
        'Üretici model kaynağında HDMI, USB-C PD, iki USB-A, SD, microSD ve 3,5 mm ses olmak üzere 7 bağlantı',
        '5 Gbps USB veri sınıfı ve HDMI üzerinden 4K 30 Hz görüntü sınıfı',
        '100 W PD giriş sınıfı; üretici açıklamasında hub çalışması için ayrılan güç sonrası geçiş mantığı belirtilir',
        'Amazon Türkiye kayıtları AVC009BTSGY modelini ASIN B08XNG4ZKN ile eşler',
      ]),
      limitations: Object.freeze([
        '4K görüntü sınıfı 30 Hz ile sınırlıdır; yüksek yenilemeli ekran görevi için uygun değildir',
        'Ana cihazın USB-C görüntü, ses ve PD özellikleri ayrı ayrı doğrulanmalıdır',
        'Hub tek başına şarj cihazı değildir; eşzamanlı kart, ses ve USB kullanımı ortak veri ve güç bütçesini paylaşır',
      ]),
      noBuyWhen: '4K 60 Hz veya daha yüksek yenileme gerekiyorsa, cihaz USB-C görüntü çıkışı sunmuyorsa, 3,5 mm ses ve kart yuvaları kullanılmayacaksa ya da mevcut hub görevi karşılıyorsa satın almayın.',
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
