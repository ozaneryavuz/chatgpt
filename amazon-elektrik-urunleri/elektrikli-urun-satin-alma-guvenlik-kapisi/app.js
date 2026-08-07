(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.ALO186ProductSafetyGate = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const PROFESSIONAL = new Set(["fixed", "medical", "lifeSafety", "highPower", "ev"]);

  function yes(value) { return value === true || value === "yes" || value === "on"; }

  function evaluate(input) {
    const data = input || {};
    if (yes(data.damage)) {
      return {
        status: "stop",
        title: "Kullanımı durdurun; satın alma bağlantısı kapalı",
        summary: "Isınma, erime, şişme, çatlak, gevşeklik, yanık kokusu veya sıvı teması ürün seçimiyle çözülecek bir alışveriş konusu değildir.",
        actions: ["Ürünün enerjisini güvenli biçimde kesin.", "Tam model için üretici ve resmî ürün güvenliği bildirimlerini kontrol edin.", "Gerekirse yetkili servis veya elektrik uzmanına başvurun."],
        affiliate: false
      };
    }

    if (PROFESSIONAL.has(data.category)) {
      return {
        status: "stop",
        title: "Profesyonel uygunluk gerekli; affiliate yolu kapalı",
        summary: "Sabit tesisat, yüksek güç, elektrikli araç, tıbbi veya can güvenliği ekipmanı genel tüketici ürün listesiyle seçilmemelidir.",
        actions: ["Proje, koruma, kablo, bağlantı ve üretici şartlarını yetkili uzmanla doğrulayın.", "ALO186 bu sınıfta ürün veya marka önermez."],
        affiliate: false
      };
    }

    if (yes(data.existingSufficient)) {
      return {
        status: "ok",
        title: "Mevcut ürün ihtiyacı karşılıyor — yeni ürün almayın",
        summary: "Güvenli, hasarsız ve gerçek görevi karşılayan mevcut ekipman varken satın alma gereksizdir.",
        actions: ["Kılavuzdaki bakım ve test aralığını uygulayın.", "Model ve geri çağırma kontrolünü periyodik olarak yenileyin."],
        affiliate: false
      };
    }

    const missing = [];
    if (!yes(data.exactModel)) missing.push("tam model / varyant");
    if (!yes(data.manual)) missing.push("üretici kılavuzu");
    if (!yes(data.label)) missing.push("gerilim, akım, güç veya batarya etiketi");
    if (!yes(data.voltageMatch)) missing.push("Türkiye kullanım gerilimi ve fiş uyumu");
    if (!yes(data.traceability)) missing.push("üretici / ithalatçı / satıcı izlenebilirliği");
    if (!yes(data.recallChecked)) missing.push("GÜBİS ve uygun resmî geri çağırma kaynağı");
    if (!yes(data.needConfirmed)) missing.push("mevcut ekipmanla çözülemeyen gerçek ihtiyaç");

    if (missing.length) {
      return {
        status: "warn",
        title: "Önce kanıtları tamamlayın; ürün bağlantısı açılmadı",
        summary: "Eksik kanıtlar: " + missing.join(", ") + ".",
        actions: ["Ürün ilanı yerine ürünün kendi etiketi ve kılavuzunu esas alın.", "Tam model eşleşmeden puan, yorum veya benzer görünüme göre karar vermeyin."],
        affiliate: false
      };
    }

    if (!yes(data.affiliateAware)) {
      return {
        status: "warn",
        title: "Satış ortaklığı açıklamasını onaylayın",
        summary: "ALO186 ürün satmaz. Sonraki ticari rehberlerde açıkça işaretlenen Amazon satış ortaklığı bağlantıları bulunabilir.",
        actions: ["Bağlantıdan önce teknik ölçütleri yeniden kontrol edin.", "Fiyat, stok, satıcı, teslimat ve garanti bilgisini yalnız mağazanın güncel sayfasında doğrulayın."],
        affiliate: false
      };
    }

    return {
      status: "ok",
      title: "Teknik ürün rehberine geçebilirsiniz",
      summary: "Bu sonuç belirli bir ürünü onaylamaz; yalnız temel güven ve ihtiyaç kanıtlarının tamamlandığını gösterir.",
      actions: ["Yalnız doğrulanan ürün sınıfına ilerleyin.", "Çalışan bileşeni değiştirmeyin; yalnız gerçek eksik parçayı değerlendirin.", "Mağaza bağlantısının satış ortaklığı niteliğini bağlantı öncesinde kontrol edin."],
      affiliate: true
    };
  }

  function formData(form) {
    const raw = Object.fromEntries(new FormData(form).entries());
    ["damage", "exactModel", "manual", "label", "voltageMatch", "traceability", "recallChecked", "existingSufficient", "needConfirmed", "affiliateAware"].forEach((key) => {
      raw[key] = form.elements[key] && form.elements[key].checked;
    });
    return raw;
  }

  function render(target, result) {
    target.className = "result " + result.status;
    const items = result.actions.map((item) => "<li>" + item + "</li>").join("");
    const next = result.affiliate
      ? '<p><a class="cta" href="/amazon-elektrik-urunleri/">Satış ortaklığı içerebilen teknik ürün rehberlerine geç</a></p><p class="fine"><strong>Açıklama:</strong> Sonraki sayfalardaki Amazon bağlantıları bağlantıdan önce satış ortaklığı olarak işaretlenir. ALO186 fiyat, stok, puan veya garanti yayımlamaz.</p>'
      : "";
    target.innerHTML = "<h2>" + result.title + "</h2><p>" + result.summary + "</p><ul>" + items + "</ul>" + next;
    target.hidden = false;
    target.focus();
  }

  function mount() {
    const form = document.getElementById("safetyGateForm");
    const result = document.getElementById("result");
    if (!form || !result) return;
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      render(result, evaluate(formData(form)));
    });
    form.addEventListener("reset", function () {
      setTimeout(function () { result.hidden = true; result.innerHTML = ""; }, 0);
    });
  }

  if (typeof document !== "undefined") {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mount);
    else mount();
  }

  return { evaluate };
});
