(function (root, factory) {
  const catalog = factory();
  if (typeof module === "object" && module.exports) module.exports = catalog;
  else root.ALO186VehicleUSBChargerCatalogV247 = catalog;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";
  const DAY_MS = 24 * 60 * 60 * 1000;
  const catalog = {
    version: 247,
    affiliateTag: "alo186rehber-21",
    verifiedAt: "2026-08-03",
    maxVerificationAgeDays: 45,
    category: {
      id: "vehicle_usb_charger_power_compatibility",
      slug: "arac-usb-sarj-adaptoru-guc-uyumluluk-secimi",
      risk: "consumer-medium",
      affiliatePolicy: "after_tool",
      requiredTool: "embedded-vehicle-usb-charger-readiness-v247",
      professionalOnly: false,
      highRiskDirectCta: false,
      excludes: [
        "hasarlı, gevşek, ıslak, kararmış veya aşırı ısınan araç aksesuar prizi",
        "sigortası tekrarlayan biçimde açan ya da yanık kokusu oluşturan devre",
        "araca sabit kablolama, sigorta köprüleme veya tesisat müdahalesi",
        "marş takviyesi, araç aküsü şarjı veya elektrikli araç çekiş bataryası şarjı",
        "tıbbi cihaz, yaşam güvenliği ekipmanı veya tek acil iletişim kaynağı",
        "gözetimsiz yüksek yük ve üretici sınırını aşan kullanım"
      ]
    },
    products: [
      {
        id: "belkin-ccb001-24w",
        asin: "B08558MGST",
        mpn: "CCB001btBK",
        brand: "Belkin",
        name: "Belkin CCB001 24 W çift USB-A araç şarj adaptörü",
        verifiedAt: "2026-08-03",
        userNeed: "Araçtaki sağlam 12 V aksesuar prizinden iki düşük güçlü USB-A cihazı aynı anda şarj etmek isteyen kullanıcı.",
        strengths: [
          "Toplam 24 W çıkış ve iki USB-A bağlantı noktası",
          "Her bağlantı noktasında 12 W'a kadar güç",
          "Kompakt gövde ve güç durumunu gösteren LED"
        ],
        limitations: [
          "USB-C Power Delivery veya PPS desteği yoktur",
          "Dizüstü bilgisayar ve yüksek güçlü USB-C cihazlar için uygun değildir",
          "Gerçek şarj hızı cihaz ve kablonun desteklediği profile bağlıdır"
        ],
        noBuyWhen: "Mevcut araç adaptörünüz iki cihazın port, güç ve kablo ihtiyacını güvenli biçimde karşılıyorsa yeni satın alma yapmayın.",
        technical: {
          inputContext: "Araç aksesuar prizi",
          ports: "2 × USB-A",
          totalOutput: "24 W",
          perPortOutput: "12 W'a kadar",
          dimensions: "26 × 73 mm",
          indicator: "LED"
        },
        amazonAsinSource: "https://www.amazon.com.tr/dp/B08558MGST",
        technicalSource: "https://www.belkin.com/p/dual-usb-a-car-charger-24w/CCB001btBK.html"
      },
      {
        id: "belkin-cca004-30w",
        asin: "B0BTP9GF27",
        mpn: "CCA004btBK",
        brand: "Belkin",
        name: "Belkin BoostCharge CCA004 30 W USB-C araç şarj adaptörü",
        verifiedAt: "2026-08-03",
        userNeed: "Uyumlu telefon veya tabletini araç aksesuar prizinden tek USB-C PD/PPS bağlantısıyla şarj etmek isteyen kullanıcı.",
        strengths: [
          "USB-C bağlantısından 30 W'a kadar güç",
          "USB Power Delivery ve PPS desteği",
          "Tek portlu kompakt yapı"
        ],
        limitations: [
          "Aynı anda yalnız tek cihaz bağlanır",
          "Şarj kablosu ayrıca doğrulanmalı ve ürünle birlikte gelmeyebilir",
          "30 W üzeri güç isteyen dizüstü bilgisayarları tam hızda beslemez"
        ],
        noBuyWhen: "Mevcut USB-C araç adaptörünüz cihazın PD/PPS profilini ve gerekli gücü karşılıyorsa yeni satın alma yapmayın.",
        technical: {
          inputContext: "Araç aksesuar prizi",
          ports: "1 × USB-C",
          maximumOutput: "30 W",
          protocols: "USB Power Delivery ve PPS",
          certificationContext: "USB-IF uyumluluk beyanı",
          cableIncluded: "Hayır"
        },
        amazonAsinSource: "https://www.amazon.com.tr/dp/B0BTP9GF27",
        technicalSource: "https://www.belkin.com/p/30w-usb-c-car-charger/CCA004btBK.html"
      },
      {
        id: "bix-bxac65c",
        asin: "B0BT4GWMS3",
        mpn: "BXAC65C",
        ean: "8681820405156",
        brand: "Bix",
        name: "Bix BXAC65C 65 W USB-C PD ve 18 W USB-A araç şarj adaptörü",
        verifiedAt: "2026-08-03",
        userNeed: "12–24 V araç prizinde tek USB-C cihaz için daha yüksek güç ve gerektiğinde ikinci USB-A çıkışı isteyen kullanıcı.",
        strengths: [
          "Tek USB-C kullanımında 65 W'a kadar PD çıkışı",
          "Ek USB-A bağlantısında 18 W'a kadar QC çıkışı",
          "12–24 V giriş aralığı"
        ],
        limitations: [
          "65 W değeri USB-C portunun tek başına kullanımına aittir",
          "İki port birlikte kullanıldığında toplam profil 5 V / 4,8 A ile sınırlanır",
          "Araç prizi, cihaz ve kablo 20 V / 3,25 A profilini desteklemiyorsa 65 W elde edilmez"
        ],
        noBuyWhen: "Mevcut adaptörünüz cihazların port, protokol ve eşzamanlı güç ihtiyacını karşılıyorsa yalnız daha yüksek etiket gücü için yeni satın alma yapmayın.",
        technical: {
          inputVoltage: "12–24 V DC",
          ports: "1 × USB-C, 1 × USB-A",
          usbCMaximum: "65 W; 5 V/3 A, 9 V/3 A, 15 V/3 A, 20 V/3,25 A",
          usbAMaximum: "18 W; 5 V/3 A, 9 V/2 A, 12 V/1,5 A",
          simultaneousOutput: "5 V / 4,8 A",
          protocols: "PD ve QC"
        },
        amazonAsinSource: "https://www.amazon.com.tr/dp/B0BT4GWMS3",
        technicalSource: "https://bix.com.tr/65w-cift-portlu-pd-arac-sarji-beyaz/"
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
