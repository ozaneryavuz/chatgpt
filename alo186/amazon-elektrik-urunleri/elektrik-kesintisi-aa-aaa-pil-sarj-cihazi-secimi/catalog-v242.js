(function (root, factory) {
  const catalog = factory();
  if (typeof module === "object" && module.exports) module.exports = catalog;
  else root.ALO186NiMHBatteryChargerCatalogV242 = catalog;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";
  const DAY_MS = 24 * 60 * 60 * 1000;
  const catalog = {
    version: 242,
    affiliateTag: "alo186rehber-21",
    verifiedAt: "2026-08-03",
    maxVerificationAgeDays: 45,
    amazonTurkeyListingSource: "https://www.amazon.com.tr/panasonic-eneloop-pil/s?k=panasonic+eneloop+pil",
    category: {
      id: "nimh_aa_aaa_battery_charger_outage",
      slug: "elektrik-kesintisi-aa-aaa-pil-sarj-cihazi-secimi",
      risk: "consumer-medium",
      affiliatePolicy: "after_tool",
      requiredTool: "embedded-nimh-battery-charger-readiness-v242",
      professionalOnly: false,
      excludes: [
        "alkalin, lityum iyon, LiFePO4, NiCd veya üreticinin desteklemediği hücreleri şarj etme",
        "akmış, şişmiş, aşırı ısınmış, ezilmiş ya da kutupları korozyonlu pil",
        "ıslak ortam, kapalı hava almayan yüzey veya hasarlı kablo ve adaptör",
        "yaşam güvenliği veya tıbbi cihaz için tek enerji kaynağı",
        "doğrulanmamış ASIN, fiş tipi, kutu içeriği veya ürün varyantı"
      ]
    },
    products: [
      {
        id: "duracell-cef14-ion-speed-1000",
        asin: "B07BFDVNSJ",
        mpn: "CEF14",
        brand: "Duracell",
        name: "Duracell CEF14 Ion Speed 1000 AA/AAA NiMH şarj cihazı seti",
        verifiedAt: "2026-08-03",
        userNeed: "Kesinti hazırlığında radyo, fener veya düşük gerilimli ev cihazları için kullanılan AA/AAA NiMH pilleri ikili ya da dörtlü gruplar halinde şarj etmek isteyen kullanıcı.",
        strengths: [
          "AA ve AAA NiMH pilleri destekleyen yaygın biçim uyumluluğu",
          "İki veya dört pili birlikte şarj etme ve LED durum göstergesi",
          "Otomatik kapanma ile tamamlanan şarjdan sonra enerji vermeyi durdurma"
        ],
        limitations: [
          "Tek bir pili veya üç pili bağımsız yuva mantığıyla şarj etmez",
          "Yaklaşık şarj süresi pil kapasitesi ve durumuna göre değişir",
          "Alkalin, lityum veya hasarlı piller için uygun değildir; kutu içeriği ASIN sayfasında yeniden kontrol edilmelidir"
        ],
        noBuyWhen: "Mevcut NiMH şarj cihazınız doğru pil kimyasını, hedef pil sayısını ve güvenli kapanmayı karşılıyorsa yeni satın alma yapmayın.",
        technical: {
          chemistry: "AA/AAA NiMH",
          slotRule: "2 veya 4 pil",
          chargeTime: "Yaklaşık 4–8 saat",
          indication: "LED şarj durumu",
          termination: "Otomatik kapanma"
        },
        amazonAsinSource: "https://teknoseyir.com/durum/1745075",
        technicalSource: "https://duracell.com/products/cef14"
      },
      {
        id: "gp-recyko-e411-aa-set",
        asin: "B09DPKNDBX",
        mpn: "E411",
        brand: "GP Batteries",
        name: "GP ReCyko E411 USB dört yuvalı AA/AAA NiMH şarj cihazı seti",
        verifiedAt: "2026-08-03",
        userNeed: "USB güç kaynağıyla iki veya dört AA/AAA NiMH pili şarj ederek kesinti radyosu, el feneri ve benzeri düşük gerilimli cihazlar için dönüşümlü pil seti hazırlamak isteyen kullanıcı.",
        strengths: [
          "5 V USB girişiyle taşınabilir güç kaynaklarından beslenebilme",
          "İki kanallı yapıda iki veya dört AA/AAA NiMH pili şarj etme",
          "Eksi delta-V ve zamanlayıcı kesmesi ile hatalı, alkalin veya kötü pili LED üzerinden bildirme"
        ],
        limitations: [
          "Piller çiftler halinde şarj edilir; her yuva bağımsız değildir",
          "Uygun ve sağlam 5 V / 1 A USB güç kaynağı gerekir",
          "Amazon setindeki pil kapasitesi ve kutu içeriği tam ASIN üzerinden yeniden doğrulanmalıdır"
        ],
        noBuyWhen: "Mevcut USB NiMH şarj cihazınız iki/dört pil kuralını, 5 V giriş ihtiyacını ve güvenli kesmeyi karşılıyorsa yeni satın alma yapmayın.",
        technical: {
          chemistry: "AA/AAA NiMH",
          slotRule: "2 veya 4 pil; iki şarj kanalı",
          input: "DC 5 V / 1 A",
          output: "DC 2,8 V; 0,3 A x2",
          termination: "Eksi delta-V ve zamanlayıcı"
        },
        amazonAsinSource: "https://teknoseyir.com/durum/1575870",
        technicalSource: "https://intls.gpbatteries.com/products/gp-recyko-4-slot-e411-usb-charger-w-4s-2100mah-aa-batteries"
      },
      {
        id: "panasonic-eneloop-bq-cc65",
        asin: "B0B5X37472",
        mpn: "BQ-CC65",
        brand: "Panasonic",
        name: "Panasonic eneloop BQ-CC65 LCD ekranlı AA/AAA NiMH şarj cihazı",
        verifiedAt: "2026-08-03",
        userNeed: "Farklı kapasitedeki bir ila dört AA/AAA eneloop veya eneloop pro pili yuva bazında izlemek, yenileme döngüsü uygulamak ve kesinti hazırlık setini ölçümle yönetmek isteyen kullanıcı.",
        strengths: [
          "Bir ila dört AA/AAA pili bağımsız yuva kontrolüyle şarj etme",
          "LCD üzerinde gerilim, kalan süre, durum ve anormallik bilgileri",
          "Refresh işlevi, akıllı şarj kesmesi ve 100–240 V otomatik giriş"
        ],
        limitations: [
          "Üretici uyumluluğu eneloop ve eneloop pro AA/AAA NiMH pillerle tanımlar",
          "USB OUT yalnız cihaz şebekeye bağlıyken çalışır; takılı piller powerbank gibi kullanılamaz",
          "Fiş ve güç kablosu bölgesel varyanta göre değişebilir; tam ASIN ve kutu içeriği yeniden kontrol edilmelidir"
        ],
        noBuyWhen: "Mevcut bağımsız yuvalı NiMH şarj cihazınız pil durumunu güvenle izliyor ve refresh veya LCD ölçümüne gerçek ihtiyacınız yoksa yeni satın alma yapmayın.",
        technical: {
          chemistry: "AA/AAA eneloop veya eneloop pro NiMH",
          slotRule: "1–4 pil; bağımsız yuva kontrolü",
          input: "AC 100–240 V",
          display: "3 inç LCD",
          functions: "Smart Charge, Refresh, AC bağlıyken DC 5 V USB OUT"
        },
        amazonAsinSource: "https://forum.donanimhaber.com/amazon-turkiye-ve-firsatlari-ana-konu--135048063-11250",
        technicalSource: "https://www.panasonic.com/global/energy/products/eneloop/en/lineup/charger-bq-cc65.html"
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
