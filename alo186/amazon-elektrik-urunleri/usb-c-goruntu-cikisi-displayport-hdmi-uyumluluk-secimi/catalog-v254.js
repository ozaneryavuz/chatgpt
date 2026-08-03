(function (root, factory) {
  const catalog = factory();
  if (typeof module === "object" && module.exports) module.exports = catalog;
  else root.ALO186UsbCDisplayCatalogV254 = catalog;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";
  const DAY_MS = 24 * 60 * 60 * 1000;
  const catalog = {
    version: 254,
    affiliateTag: "alo186rehber-21",
    verifiedAt: "2026-08-03",
    maxVerificationAgeDays: 45,
    category: {
      id: "consumer_usb_c_display_output_fit",
      slug: "usb-c-goruntu-cikisi-displayport-hdmi-uyumluluk-secimi",
      risk: "consumer-low",
      affiliatePolicy: "after_tool",
      requiredTool: "embedded-usb-c-display-readiness-v254",
      professionalOnly: false,
      highRiskDirectCta: false,
      excludes: [
        "hasarlı, gevşek, ıslak, aşırı ısınan veya yanık kokusu bulunan USB-C, DisplayPort ya da HDMI bağlantısı",
        "medikal, yaşam güvenliği, yangın alarmı, güvenlik merkezi veya kesintisiz kritik görüntüleme görevi",
        "USB-C portunda DisplayPort Alt Mode veya Thunderbolt görüntü çıkışı bulunmayan cihaz",
        "ürünün yön, çözünürlük, yenileme hızı, HDR ve HDCP sınırları doğrulanmadan kullanım",
        "şarj, USB veri aktarımı, görüntü yakalama veya HDMI-DisplayPort ters dönüşümü beklenen kullanım",
        "sabit tesisat, duvar içi kablolama, enerjili ekipman müdahalesi veya profesyonel yayın altyapısı"
      ]
    },
    products: [
      {
        id: "ugreen-cm556-25158",
        asin: "B0C4DB8MLL",
        mpn: "25158",
        brand: "UGREEN",
        name: "UGREEN CM556 25158 USB-C - DisplayPort 1.4 kablo",
        verifiedAt: "2026-08-03",
        userNeed: "DisplayPort Alt Mode destekli USB-C veya Thunderbolt cihazını DisplayPort girişli monitöre tek yönlü bağlamak ve yüksek yenileme hızını cihaz zinciriyle doğrulamak isteyen kullanıcı.",
        strengths: [
          "USB-C kaynak cihazdan DisplayPort ekrana doğrudan tek kablolu bağlantı",
          "Üretici kaynağında 8K 60 Hz ve 4K 240 Hz'e kadar sınıf desteği",
          "DisplayPort 1.4, HDR, VRR ve 32,4 Gbit/s sınıfı teknik tanım"
        ],
        limitations: [
          "Tek yönlüdür; DisplayPort kaynaktan USB-C ekrana ters yönde çalışmaz",
          "USB-C şekli tek başına görüntü çıkışı sağlamaz; DP Alt Mode veya Thunderbolt zorunludur",
          "Gerçek çözünürlük ve yenileme hızı kaynak cihaz, ekran, işletim sistemi ve DSC desteğiyle sınırlıdır"
        ],
        noBuyWhen: "Mevcut kablonuz hedef çözünürlükte kararlı çalışıyorsa veya cihazınızın USB-C portu görüntü çıkışı desteklemiyorsa satın almayın.",
        technical: {
          direction: "USB-C kaynak -> DisplayPort ekran, tek yönlü",
          displayStandard: "DisplayPort 1.4 sınıfı",
          maxClass: "8K 60 Hz / 4K 240 Hz sınıfı üretici beyanı",
          bandwidth: "32,4 Gbit/s sınıfı",
          features: "HDR, VRR, ALLM; zincire göre değişir",
          length: "2 m"
        },
        amazonAsinSource: "https://www.amazon.com.tr/dp/B0C4DB8MLL",
        technicalSource: "https://www.ugreenindia.com/products/ugreen-2m-usb-c-to-displayport-1-4-cable-8k-60hz-4k-240hz-2k-240hzthunderbolt-to-dp-with-hdr-vrr-allm-for-macbook-mac-mini-ipad-xps-surface-iphone-15-series-galaxy-etc-25158"
      },
      {
        id: "veggieg-z623",
        asin: "B0DK6QPTFQ",
        mpn: "V-Z623",
        brand: "VegGieg",
        name: "VegGieg Z623 USB-C - DisplayPort 1.4 çift yönlü kablo",
        verifiedAt: "2026-08-03",
        userNeed: "USB-C görüntü çıkışı ile DisplayPort arasında yön esnekliği isteyen ve her iki uçtaki kaynak/ekran yeteneklerini doğrulayabilen kullanıcı.",
        strengths: [
          "Ürün kaynağında USB-C ve DisplayPort arasında çift yönlü görüntü aktarımı",
          "8K 60 Hz, 4K 144 Hz ve 2K 165 Hz sınıfı teknik tanım",
          "Örgülü yapı, altın kaplama konnektör ve parazit önleyici katman beyanı"
        ],
        limitations: [
          "Çift yönlü kablo, USB-C cihazın DP Alt Mode desteği bulunmadığında görüntü oluşturmaz",
          "Her yön ve çözünürlük kombinasyonu kaynak ile ekranın ortak desteklediği modla sınırlıdır",
          "Şarj, genel USB veri aktarımı veya görüntü yakalama cihazı değildir"
        ],
        noBuyWhen: "Yalnız tek yönlü standart bağlantı yeterliyse veya USB-C cihazınız görüntü çıkışı vermiyorsa çift yön özelliği için satın almayın.",
        technical: {
          direction: "USB-C <-> DisplayPort, ürün kaynağında çift yönlü",
          displayStandard: "DisplayPort 1.4 sınıfı",
          maxClass: "8K 60 Hz / 4K 144 Hz / 2K 165 Hz sınıfı",
          connectors: "USB-C ve DisplayPort",
          construction: "Örgülü kablo ve parazit önleyici katman",
          length: "2 m"
        },
        amazonAsinSource: "https://www.amazon.com.tr/dp/B0DK6QPTFQ",
        technicalSource: "https://www.teknostore.com/veggieg-8k/60hz-4k/144hz/120hz-type-c-31-to-displayport-14-cift-yonlu-kablo-2-metre"
      },
      {
        id: "daytona-hc-01",
        asin: "B096G51911",
        mpn: "HC-01",
        brand: "Daytona",
        name: "Daytona HC-01 USB-C - HDMI görüntü aktarım kablosu",
        verifiedAt: "2026-08-03",
        userNeed: "DisplayPort yerine HDMI girişli televizyon, monitör veya projektöre USB-C görüntü çıkışı bağlamak isteyen ve cihaz uyumluluğunu önceden doğrulayabilen kullanıcı.",
        strengths: [
          "USB-C kaynak cihazdan HDMI ekrana doğrudan görüntü ve ses aktarımı",
          "Güvenilir ürün kaynaklarında 4K sınıfı görüntü desteği",
          "Haricî güç ve sürücü gerektirmeyen kablolu kullanım tanımı"
        ],
        limitations: [
          "USB-C portunda DP Alt Mode görüntü çıkışı yoksa çalışmaz",
          "4K yenileme hızı kaynak, ekran, işletim sistemi ve kablo zincirine göre ayrıca doğrulanmalıdır",
          "USB-C cihazı şarj etmez; ters HDMI kaynak -> USB-C ekran dönüşümü veya görüntü yakalama yapmaz"
        ],
        noBuyWhen: "Cihazınız kablolu görüntü çıkışı desteklemiyorsa, mevcut kablosuz aktarım ihtiyacınızı karşılıyorsa veya HDMI yerine DisplayPort gerekiyorsa satın almayın.",
        technical: {
          direction: "USB-C kaynak -> HDMI ekran, tek yönlü",
          displayClass: "4K sınıfı ürün tanımı",
          dataClass: "5 Gbit/s sınıfı ürün verisi",
          connectors: "USB-C ve HDMI",
          power: "Haricî güç gerektirmeyen kullanım tanımı",
          length: "Yaklaşık 1,8-2 m; fiziksel etiketi doğrulayın"
        },
        amazonAsinSource: "https://www.amazon.com.tr/dp/B096G51911",
        technicalSource: "https://www.epey.com/donusturucu/daytona-hc-01-type-c-to-hdmi.html"
      }
    ]
  };

  catalog.verificationStatus = function (product, now) {
    const checked = Date.parse(product.verifiedAt + "T00:00:00Z");
    const current = now instanceof Date ? now.getTime() : Date.parse(String(now || new Date().toISOString()));
    const ageDays = Math.floor((current - checked) / DAY_MS);
    return { ageDays, fresh: Number.isFinite(ageDays) && ageDays >= 0 && ageDays <= catalog.maxVerificationAgeDays };
  };

  catalog.amazonProductUrl = function (product, now) {
    if (!catalog.verificationStatus(product, now).fresh) return null;
    return "https://www.amazon.com.tr/dp/" + encodeURIComponent(product.asin) + "?tag=" + encodeURIComponent(catalog.affiliateTag);
  };

  return Object.freeze(catalog);
});
