(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root && typeof root === 'object') root.Alo186ModemWifiRangeCatalogV231 = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const version = 231;
  const affiliateTag = 'alo186rehber-21';
  const verificationMaxAgeDays = 45;
  const verifiedAt = '2026-08-03';
  const category = Object.freeze({
    id: 'consumer_modem_wifi_coverage_measurement_extender',
    risk: 'consumer-low',
    affiliatePolicy: 'after_tool',
    requiredTool: 'embedded-modem-wifi-range-measurement-v231',
    professionalOnly: false,
    excludes: Object.freeze([
      'life-safety-network',
      'medical-communications',
      'fire-alarm-network',
      'security-critical-network',
      'industrial-control-network',
    ]),
  });

  const products = Object.freeze([
    Object.freeze({
      id: "tp-link-re315",
      asin: "B08RHD97QY",
      mpn: "RE315",
      brand: "TP-Link",
      name: "TP-Link RE315 AC1200 Mesh Wi‑Fi Menzil Genişletici",
      verifiedAt,
      userNeed: "Modem çevresinde yeterli hız varken evin başka bir bölümünde ölçülmüş Wi‑Fi sinyal zayıflığını gidermek.",
      strengths: Object.freeze([
        "2,4 GHz’de 300 Mbps ve 5 GHz’de 867 Mbps sınıfında çift bant bağlantı",
        "İki harici anten, akıllı sinyal göstergesi ve uyarlanabilir yol seçimi",
        "Menzil genişletici ve erişim noktası çalışma modları",
        "TP-Link OneMesh uyumlu yönlendiricilerle tek ağ adı oluşturabilme",
      ]),
      limitations: Object.freeze([
        "Ethernet bağlantı noktası 10/100 Mbps sınıfındadır; gigabit kablolu uç değildir",
        "Kablosuz tekrarlama gerçek internet hızını artırmaz; yalnız mevcut bağlantıyı daha uygun noktaya taşır",
        "Mesh ve kesintisiz dolaşım işlevleri yönlendirici modeli, donanım sürümü ve yazılıma bağlıdır",
      ]),
      noBuyWhen: "Sorun internet servisinde, modem hattında veya aynı odada da görülüyorsa; mevcut yönlendiricinin konumu iyileştirilebiliyorsa ya da ölçüm yapılmadan yalnız daha yüksek hız beklentisi varsa satın almayın.",
      technicalSource: "https://www.tp-link.com/tr/home-networking/range-extender/re315/",
    }),
    Object.freeze({
      id: "tp-link-re305",
      asin: "B01MD1SKLL",
      mpn: "RE305",
      brand: "TP-Link",
      name: "TP-Link RE305 AC1200 Mesh Wi‑Fi Menzil Genişletici",
      verifiedAt,
      userNeed: "Çift bantlı modem veya yönlendiricinin kapsamadığı bir oda için yerleşim ölçümü sonrası düşük maliyetli kapsama uzatması yapmak.",
      strengths: Object.freeze([
        "2,4 GHz’de 300 Mbps ve 5 GHz’de 867 Mbps sınıfında çift bant bağlantı",
        "İki harici anten ve uygun yerleşim için akıllı sinyal ışığı",
        "Menzil genişletici ve erişim noktası çalışma modları",
        "Uygun donanım sürümünde EasyMesh/OneMesh desteği",
      ]),
      limitations: Object.freeze([
        "Ethernet bağlantı noktası 10/100 Mbps sınıfındadır",
        "Ürün donanım sürümleri arasında mesh ve yazılım özellikleri değişebilir; etiket kontrolü gerekir",
        "Yönlendiriciden alınan sinyal zayıfsa cihazın yayınladığı ağ da kararsız kalabilir",
      ]),
      noBuyWhen: "Modem yanında da bağlantı kopuyorsa, Ethernet kablosu çekmek mümkün ve daha kararlı çözüm gerekiyorsa veya ürün etiketindeki donanım sürümü ihtiyaç duyduğunuz mesh işlevini doğrulamıyorsa satın almayın.",
      technicalSource: "https://www.tp-link.com/tr/home-networking/range-extender/re305/",
    }),
    Object.freeze({
      id: "tp-link-re200",
      asin: "B00KXULGJQ",
      mpn: "RE200",
      brand: "TP-Link",
      name: "TP-Link RE200 AC750 Wi‑Fi Menzil Genişletici",
      verifiedAt,
      userNeed: "Hafif web, mesajlaşma ve düşük bant genişlikli cihazlar için küçük bir Wi‑Fi ölü noktasını ölçümle doğruladıktan sonra kapsamak.",
      strengths: Object.freeze([
        "2,4 GHz’de 300 Mbps ve 5 GHz’de 433 Mbps sınıfında çift bant bağlantı",
        "Kompakt priz tipi gövde ve üç dahili anten",
        "Akıllı sinyal göstergesiyle yerleşim desteği",
        "Kablolu cihaz için 10/100 Mbps Ethernet bağlantısı ve erişim noktası modu",
      ]),
      limitations: Object.freeze([
        "AC750 sınıfı yoğun çoklu cihaz, yüksek hızlı dosya aktarımı ve yüksek bant genişliği hedefleri için sınırlı olabilir",
        "Ethernet bağlantı noktası 10/100 Mbps sınıfındadır",
        "Donanım sürümü ve bölgesel ürün kodu satın alma öncesinde etiket üzerinden doğrulanmalıdır",
      ]),
      noBuyWhen: "Yüksek hızlı fiber bağlantının tamamını uzak odada kullanmak, yoğun oyun/iş istasyonu trafiği taşımak veya Ethernet omurgası kurmak mümkünse bu sınıfı satın almayın.",
      technicalSource: "https://www.tp-link.com/tr/home-networking/range-extender/re200/",
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
