(function (root, factory) {
  const catalog = factory();
  if (typeof module === "object" && module.exports) module.exports = catalog;
  else root.ALO186EquipmentRoomClimateCatalogV245 = catalog;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";
  const DAY_MS = 24 * 60 * 60 * 1000;
  const catalog = {
    version: 245,
    affiliateTag: "alo186rehber-21",
    verifiedAt: "2026-08-03",
    maxVerificationAgeDays: 45,
    amazonTurkeyListingSource: "https://www.amazon.com.tr/gp/most-wished-for/home-improvement/12708413031",
    category: {
      id: "electrical_equipment_room_ambient_temperature_humidity_monitoring",
      slug: "elektrik-ekipman-odasi-sicaklik-nem-olcum-alarm-secimi",
      risk: "consumer-medium",
      affiliatePolicy: "after_tool",
      requiredTool: "embedded-equipment-room-climate-readiness-v245",
      professionalOnly: false,
      excludes: [
        "enerjili pano, UPS, akü kabini veya çıplak iletken bulunan muhafaza içine kullanıcı montajı",
        "yoğuşma, su sıçraması, patlayıcı ortam veya ürünün beyan edilen çalışma koşulları dışındaki alan",
        "yangın, duman, karbonmonoksit, tıbbi ya da yaşam güvenliği alarmının yerine kullanım",
        "kalibreli tesis kabul ölçümü, termal kamera incelemesi veya profesyonel çevresel izleme yerine kullanım",
        "hub, bölge, uygulama, kablosuz protokol, model veya ASIN eşleşmesi doğrulanmamış akıllı sensör",
        "sensör verisine tek başına dayanarak kritik soğutma, jeneratör, UPS veya pano enerjisini otomatik kesme"
      ]
    },
    products: [
      {
        id: "thermopro-tp50",
        asin: "B01H1R0K68",
        mpn: "TP50",
        brand: "ThermoPro",
        name: "ThermoPro TP50 dijital iç ortam termometre ve higrometre",
        verifiedAt: "2026-08-03",
        userNeed: "Elektrik ekipman odasının kuru ve erişilebilir bir noktasında, uygulama veya hub kurmadan ortam sıcaklığı ile bağıl nemi yerel ekrandan ve min–maks kayıtlarından izlemek isteyen kullanıcı.",
        strengths: [
          "Sıcaklık ve bağıl nemi aynı LCD ekranda gösteren bağımsız kullanım",
          "10 saniyelik yenileme ile min–maks kayıt ve konfor göstergesi",
          "Masa üstü, askı veya mıknatıslı yerleşime uygun kompakt yapı"
        ],
        limitations: [
          "Uzaktan bildirim, kayıt dışa aktarımı veya ağ bağlantısı sunmaz",
          "Elektrik panosu içi sıcaklık, iletken yüzeyi veya sıcak nokta ölçümü için uygun değildir",
          "Kuru iç ortam için kullanılmalı; yoğuşma ve su sıçramasına karşı korumalı endüstriyel sensör değildir"
        ],
        noBuyWhen: "Mevcut kalibreli bina otomasyonu, UPS çevre sensörü veya sağlam termo-higrometre aynı konumu yeterli doğrulukla izliyorsa yeni satın alma yapmayın.",
        technical: {
          temperatureRange: "-30 ila 60 °C",
          temperatureAccuracy: "0–60 °C aralığında ±0,5 °C; dışında ±1 °C",
          humidityRange: "%10–99 RH",
          humidityAccuracy: "%30–80 RH aralığında ±%2; dışında ±%3",
          refreshRate: "10 saniye",
          display: "LCD",
          power: "1 × AAA pil",
          dimensions: "79 × 66 × 24 mm"
        },
        amazonAsinSource: "https://www.amazon.com.tr/dp/B01H1R0K68",
        technicalSource: "https://buythermopro.com/products/tp50-digital-indoor-hygrometer-thermometer"
      },
      {
        id: "tapo-t315",
        asin: "B0BNYSVV3J",
        mpn: "Tapo T315",
        brand: "TP-Link Tapo",
        name: "TP-Link Tapo T315 akıllı sıcaklık ve nem sensörü",
        verifiedAt: "2026-08-03",
        userNeed: "Ekipman odasının ortam koşullarını E-ink ekrandan görmek, eşik aşımında uygulama bildirimi almak ve geçmiş veriyi izlemek isteyen, uyumlu Tapo Hub altyapısı bulunan kullanıcı.",
        strengths: [
          "2,7 inç E-ink ekranda sıcaklık, nem, konfor, pil ve sinyal bilgisi",
          "Üretici beyanına göre ±0,3 °C ve ±%3 bağıl nem ölçüm doğruluğu",
          "Uyumlu Tapo Hub ile eşik bildirimi, veri geçmişi ve otomasyon desteği"
        ],
        limitations: [
          "Uzaktan izleme, veri aktarımı ve akıllı özellikler için uyumlu Tapo Hub gerekir",
          "Ev otomasyonu çıkışı bağımsız emniyet rölesi veya profesyonel alarm sisteminin yerine geçmez",
          "Bölge, uygulama hesabı, hub modeli ve ürün varyantı satın almadan önce doğrulanmalıdır"
        ],
        noBuyWhen: "Mevcut Tapo sensörü veya bina otomasyonu aynı noktada güvenilir kayıt ve bildirim sağlıyorsa yalnız ekran veya ek grafik için yeni satın alma yapmayın.",
        technical: {
          temperatureRange: "-20 ila 60 °C",
          temperatureAccuracy: "±0,3 °C",
          humidityRange: "%0–99 RH",
          humidityAccuracy: "±%3 RH",
          refreshRate: "2 saniye",
          display: "2,7 inç E-ink",
          protocol: "Tapo düşük güçlü kablosuz bağlantı; akıllı özellikler için Tapo Hub",
          power: "2 × AAA pil",
          dimensions: "62 × 62 × 24,5 mm"
        },
        amazonAsinSource: "https://www.amazon.com.tr/dp/B0BNYSVV3J",
        technicalSource: "https://www.tp-link.com/tr/smart-home/smart-sensor/tapo-t315/"
      },
      {
        id: "aqara-wsdcgq11lm",
        asin: "B07D37FKGY",
        mpn: "WSDCGQ11LM",
        brand: "Aqara",
        name: "Aqara WSDCGQ11LM sıcaklık ve nem sensörü",
        verifiedAt: "2026-08-03",
        userNeed: "Kuru iç ortamda küçük, ekransız bir Zigbee sensörle sıcaklık, nem ve atmosfer basıncı eğilimini izlemek isteyen, uyumlu Aqara Hub ekosistemi bulunan kullanıcı.",
        strengths: [
          "36 × 36 × 9 mm ölçülerinde kompakt Zigbee sensör",
          "Üretici beyanına göre ±0,3 °C ve ±%3 bağıl nem doğruluğu",
          "Sıcaklık ve neme ek olarak atmosfer basıncı ölçümü"
        ],
        limitations: [
          "Yerel ekranı yoktur ve uzaktan kullanım için uyumlu Aqara Hub gerekir",
          "Çalışma aralığı -20 ila 50 °C ve yoğuşmasız iç ortamla sınırlıdır",
          "Kritik HVAC veya enerji kesme otomasyonu için tek sensör ve tek haberleşme yolu yeterli kabul edilmemelidir"
        ],
        noBuyWhen: "Mevcut Zigbee/Aqara sensörü aynı hacmi kapsıyor ve pil, bağlantı ile ölçüm geçmişi sağlıklıysa ikinci bir sensörü yalnız çoğaltma amacıyla satın almayın.",
        technical: {
          model: "WSDCGQ11LM",
          temperatureRange: "-20 ila 50 °C",
          temperatureAccuracy: "±0,3 °C",
          humidityRange: "%0–100 RH, yoğuşmasız",
          humidityAccuracy: "±%3 RH",
          pressureRange: "30–110 kPa",
          pressureAccuracy: "±0,12 kPa",
          protocol: "Zigbee",
          power: "CR2032 pil",
          dimensions: "36 × 36 × 9 mm"
        },
        amazonAsinSource: "https://www.amazon.com.tr/dp/B07D37FKGY",
        technicalSource: "https://www.aqara.com/en/product/temperature-humidity-sensor/specs/"
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
