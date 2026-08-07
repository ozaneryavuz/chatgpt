(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.ALO186RecallCheck = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  function yes(value) { return value === true || value === "yes" || value === "on"; }

  function evaluate(input) {
    const data = input || {};
    if (yes(data.damage)) {
      return {
        status: "stop",
        title: "Kullanımı durdurun ve enerjiyi güvenli biçimde kesin",
        summary: "Fiziksel hasar veya olağandışı ısınma varken geri çağırma sonucu beklenmez; ürün güvenli kullanımda kabul edilmez.",
        actions: ["Üretici veya ithalatçının resmî destek kanalına başvurun.", "Ürünü satmayın, devretmeyin veya yeniden kullanıma vermeyin.", "Bataryalı ürünü yerel tehlikeli atık talimatına göre ayırın."],
        commerce: false
      };
    }

    if (data.match === "exact") {
      return {
        status: "stop",
        title: "Tam model eşleşti — resmî önlemi uygulayın",
        summary: "Geri çağırma/toplatma kaydındaki marka, model, seri/parti ve pazar bilgisi ürününüzle tam eşleşiyorsa kullanımı durdurun ve bildirimdeki resmî çözüm yolunu izleyin.",
        actions: ["Bildirim numarası ve yayın tarihini kaydedin.", "Üretici/ithalatçıya yalnız resmî iletişim kanalından başvurun.", "Yerine ürün satın almadan önce onarım, değişim veya iade çözümünü netleştirin."],
        commerce: false
      };
    }

    if (data.match === "possible") {
      return {
        status: "warn",
        title: "Olası eşleşme var — kullanımı askıya alın",
        summary: "Benzer marka veya ürün adı tam eşleşme değildir. Seri, parti, üretim tarihi, varyant ve pazar bilgisi tamamlanana kadar güvenli varsaymayın.",
        actions: ["Ürün etiketinin fotoğrafını kişisel veri içermeden saklayın.", "Üreticiden yazılı tam model teyidi isteyin.", "Satış ortaklığı ve yeni ürün yolu kapalıdır."],
        commerce: false
      };
    }

    const missing = [];
    if (!yes(data.brandModel)) missing.push("marka ve tam model");
    if (!yes(data.serialLot)) missing.push("seri/parti/üretim kodu");
    if (!yes(data.market)) missing.push("satış veya ithalat pazarı");
    if (!yes(data.manufacturer)) missing.push("üretici/ithalatçı bildirimi");
    if (!yes(data.gubis)) missing.push("GÜBİS kontrolü");
    if (data.origin === "eu" && !yes(data.safetyGate)) missing.push("EU Safety Gate kontrolü");
    if (data.origin === "us" && !yes(data.cpsc)) missing.push("CPSC kontrolü");

    if (missing.length) {
      return {
        status: "warn",
        title: "Kontrol tamamlanmadı",
        summary: "Eksik adımlar: " + missing.join(", ") + ".",
        actions: ["Ürün adıyla değil tam model/seri bilgisiyle arayın.", "İlan başlığı veya satıcı cevabını resmî geri çağırma kaydı yerine kullanmayın.", "Sonuç bulunmamasını güvenlik sertifikası saymayın."],
        commerce: false
      };
    }

    return {
      status: "ok",
      title: "Kontrol tamamlandı; eşleşme bulunmaması güvenlik garantisi değildir",
      summary: "Mevcut resmî kaynaklarda tam eşleşme bulmadınız. Fiziksel durum, kılavuz, doğru gerilim, gerçek kullanım ve üretici güncellemeleri ayrıca izlenmelidir.",
      actions: ["90 gün sonra veya yeni bir güvenlik duyurusunda kontrolü yenileyin.", "Ürün mevcut ihtiyacı karşılıyorsa yeni ürün almayın.", "Yeni alım gerekiyorsa önce satın alma güvenlik kapısını uygulayın."],
      commerce: false
    };
  }

  function formData(form) {
    const raw = Object.fromEntries(new FormData(form).entries());
    ["damage", "brandModel", "serialLot", "market", "manufacturer", "gubis", "safetyGate", "cpsc"].forEach((key) => {
      raw[key] = form.elements[key] && form.elements[key].checked;
    });
    return raw;
  }

  function render(target, result) {
    target.className = "result " + result.status;
    target.innerHTML = "<h2>" + result.title + "</h2><p>" + result.summary + "</p><ul>" + result.actions.map((x) => "<li>" + x + "</li>").join("") + "</ul>";
    target.hidden = false;
    target.focus();
  }

  function mount() {
    const form = document.getElementById("recallForm");
    const result = document.getElementById("result");
    const origin = form && form.elements.origin;
    if (!form || !result) return;
    function sync() {
      const value = origin.value;
      document.getElementById("euRow").hidden = value !== "eu";
      document.getElementById("usRow").hidden = value !== "us";
    }
    origin.addEventListener("change", sync); sync();
    form.addEventListener("submit", function (event) { event.preventDefault(); render(result, evaluate(formData(form))); });
    form.addEventListener("reset", function () { setTimeout(function () { result.hidden = true; result.innerHTML = ""; sync(); }, 0); });
  }

  if (typeof document !== "undefined") {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mount);
    else mount();
  }

  return { evaluate };
});
