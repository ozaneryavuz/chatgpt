(function (root, factory) {
  const catalog = factory();
  if (typeof module === "object" && module.exports) module.exports = catalog;
  else root.ALO186IRSurfaceTemperatureCatalogV246 = catalog;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";
  const DAY_MS = 24 * 60 * 60 * 1000;
  const catalog = {
    version: 246,
    affiliateTag: "alo186rehber-21",
    verifiedAt: "2026-08-03",
    maxVerificationAgeDays: 45,
    category: {
      id: "electrical_equipment_non_contact_surface_temperature_measurement",
      slug: "elektrik-ekipmani-temassiz-yuzey-sicaklik-olcum-secimi",
      risk: "consumer-medium",
      affiliatePolicy: "after_tool",
      requiredTool: "embedded-ir-surface-temperature-readiness-v246",
      professionalOnly: false,
      highRiskDirectCta: false,
      excludes: [
        "enerjili pano, UPS, inverter, EV şarj cihazı, trafo veya akü muhafazasını açarak ölçüm",
        "çıplak iletken, bara, klemens veya gerilim altındaki parçaya yaklaşma",
        "duman, yanık kokusu, ark sesi, alev, aşırı ısınma şüphesi veya acil durum",
        "patlayıcı ortam, tıbbi kullanım, vücut sıcaklığı veya gıda iç sıcaklığı ölçümü",
        "tesis kabulü, koruma ayarı, yangın incelemesi veya kalibrasyon gerektiren karar",
        "emisivite, hedef yüzey ve mesafe-nokta oranı doğrulanmadan kesin teşhis"
      ]
    },
    products: [
      {
        id: "temppro-tp30",
        asin: "B0BGGJH3G2",
        mpn: "TP30",
        brand: "TempPro",
        name: "TempPro TP30 temassız kızılötesi yüzey termometresi",
        verifiedAt: "2026-08-03",
        userNeed: "Kapalı ve güvenli erişimli elektrik ekipmanı dış yüzeylerinde, temas etmeden hızlı karşılaştırmalı sıcaklık kontrolü yapmak isteyen kullanıcı.",
        strengths: [
          "-50 ila 550 °C yüzey ölçüm aralığı",
          "12:1 mesafe-nokta oranı ve 500 ms tepki süresi",
          "0,1–1,0 ayarlanabilir emisivite ile maks/min/ortalama takibi"
        ],
        limitations: [
          "Yalnız yüzey sıcaklığını ölçer; iç sıcaklık veya elektriksel arıza teşhisi sağlamaz",
          "Parlak metal ve düşük emisiviteli yüzeylerde ayar ve referans yüzey gerekir",
          "12:1 optik oran küçük hedefleri uzaktan ayırmak için sınırlı olabilir"
        ],
        noBuyWhen: "Mevcut doğrulanmış kızılötesi termometre aynı sıcaklık aralığı, optik oran ve emisivite kontrolünü karşılıyorsa yeni satın alma yapmayın.",
        technical: {
          measurementType: "Temassız yüzey sıcaklığı",
          temperatureRange: "-50 ila 550 °C",
          accuracy: "±1,5 °C",
          responseTime: "500 ms",
          distanceSpotRatio: "12:1",
          emissivity: "0,1–1,0 ayarlanabilir",
          power: "2 × AAA pil"
        },
        amazonAsinSource: "https://www.amazon.com.tr/dp/B0BGGJH3G2",
        technicalSource: "https://temppro.com/products/tp30-infrared-thermometer-gun"
      },
      {
        id: "temppro-tp450",
        asin: "B099WXX9DL",
        mpn: "TP450",
        brand: "TempPro",
        name: "TempPro TP450 çift lazerli temassız kızılötesi yüzey termometresi",
        verifiedAt: "2026-08-03",
        userNeed: "Kapalı ekipman yüzeyinde daha dar hedef alanını iki lazerle sınırlandırmak ve 16:1 optik oranla karşılaştırmalı tarama yapmak isteyen kullanıcı.",
        strengths: [
          "-50 ila 550 °C yüzey ölçüm aralığı",
          "16:1 mesafe-nokta oranı ve çift lazer hedefleme",
          "500 ms tepki ve 0,1–1,0 ayarlanabilir emisivite"
        ],
        limitations: [
          "Lazerler ölçüm alanının sınırını gösterir; elektriksel güvenlik mesafesini belirlemez",
          "Parlak veya yansıtıcı metalde yüzey hazırlığı ya da uygun referans gerekir",
          "Termal kamera görüntüsü, sıcaklık dağılımı veya kalibreli kabul raporu üretmez"
        ],
        noBuyWhen: "Mevcut cihazınız küçük hedefi gerekli mesafeden ayırabiliyor ve emisivite ayarı doğrulanabiliyorsa yalnız çift lazer için yeni satın alma yapmayın.",
        technical: {
          measurementType: "Temassız yüzey sıcaklığı",
          temperatureRange: "-50 ila 550 °C",
          accuracy: "±1,5 °C",
          responseTime: "500 ms",
          distanceSpotRatio: "16:1",
          laserTargeting: "Çift lazer",
          emissivity: "0,1–1,0 ayarlanabilir",
          power: "2 × AAA pil"
        },
        amazonAsinSource: "https://www.amazon.com.tr/dp/B099WXX9DL",
        technicalSource: "https://temppro.com/products/tp450-dual-laser-thermometer-gun"
      },
      {
        id: "bosch-advancedtemp",
        asin: "B0CFVX6GT2",
        mpn: "0603683200",
        ean: "4059952613826",
        brand: "Bosch",
        name: "Bosch AdvancedTemp temassız yüzey sıcaklık ölçer",
        verifiedAt: "2026-08-03",
        userNeed: "Yüzey sıcaklığına ek olarak ortam sıcaklığı ve bağıl nem bağlamını görmek, malzeme grubu seçimiyle dış yüzey kontrolü yapmak isteyen kullanıcı.",
        strengths: [
          "-30 ila 500 °C yüzey sıcaklığı ölçüm aralığı",
          "12:1 optik oran; ortam sıcaklığı ve bağıl nem göstergesi",
          "Malzeme grubu seçimi ve trafik ışığı yorum desteği"
        ],
        limitations: [
          "Yaklaşık 1 m çalışma mesafesi ve 12:1 optik oran hedef boyutuna göre kontrol edilmelidir",
          "Trafik ışığı göstergesi profesyonel elektrik arıza teşhisi veya koruma kararı değildir",
          "Parlak metal, çok küçük hedef ve muhafaza içi sıcak nokta için uygun yöntem olmayabilir"
        ],
        noBuyWhen: "Mevcut ölçüm sisteminiz yüzey sıcaklığı, ortam koşulu ve hedef malzeme etkisini yeterli şekilde değerlendiriyorsa yeni satın alma yapmayın.",
        technical: {
          measurementType: "Temassız yüzey sıcaklığı ve ortam bağlamı",
          surfaceTemperatureRange: "-30 ila 500 °C",
          ambientTemperatureRange: "-5 ila 50 °C",
          humidityRange: "%10–90 RH",
          distanceSpotRatio: "12:1",
          approximateRange: "1 m",
          power: "2 × AA pil",
          autoOff: "5 dakika"
        },
        amazonAsinSource: "https://www.amazon.com.tr/dp/B0CFVX6GT2",
        technicalSource: "https://www.bosch-diy.com/gb/en/p/advancedtemp-0603683200"
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
