(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.ALO186OutletTester = api;
  if (root.document) api.mount(root.document);
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const PRODUCT = {
    basic: {
      label: "230 V Type E/F temel priz bağlantı göstergesi",
      query: "230V Type E F priz test cihazı bağlantı göstergesi CAT II"
    },
    display: {
      label: "230 V Type E/F voltaj ekranlı priz test cihazı",
      query: "230V Type E F priz test cihazı voltaj ekranlı CAT II"
    },
    rcd: {
      label: "230 V Type E/F voltaj ekranlı ve RCD işlev düğmeli priz test cihazı",
      query: "230V Type E F priz test cihazı voltaj ekranlı RCD test CAT II"
    },
    professional: {
      label: "Profesyonel tesisat doğrulama ölçüm seti",
      query: ""
    }
  };

  const LIMITS = {
    basic: "Toprak kalitesi, PE direnci, çevrim empedansı ve RCD açma süresini ölçmez.",
    display: "Ekran yaklaşık gerilim gösterir; toprak kalitesi, çevrim empedansı ve RCD performansını kanıtlamaz.",
    rcd: "RCD düğmesi yalnız işlevsel açmayı dener; açma akımı ve süresini ölçmez.",
    professional: "Sonuç yalnız yetkin kişi, uygun yöntem ve kayıtlı ölçümle geçerlidir."
  };

  function bool(value) { return value === true; }
  function rank(type) { return ({ unknown: 0, basic: 1, display: 2, rcd: 3, mft: 4 })[type] || 0; }
  function numberOrNull(value) {
    const parsed = Number(value);
    return Number.isFinite(parsed) && parsed > 0 ? parsed : null;
  }
  function requiredType(input) {
    if (bool(input.rcdFunctional)) return "rcd";
    if (bool(input.voltageDisplay)) return "display";
    if (bool(input.commonFaults)) return "basic";
    return null;
  }
  function hasProfessionalTask(input) {
    return bool(input.earthQuality) || bool(input.loopImpedance) || bool(input.rcdTripTime);
  }
  function voltageMetric(value) {
    const voltage = numberOrNull(value);
    if (!voltage) return { text: "Girilmedi", voltage: null, deviationPercent: null };
    const deviation = ((voltage - 230) / 230) * 100;
    const sign = deviation > 0 ? "+" : "";
    return {
      text: `${Math.round(voltage)} V (${sign}${deviation.toFixed(1)}%)`,
      voltage,
      deviationPercent: Number(deviation.toFixed(2))
    };
  }
  function result(status, title, summary, productType, next, commerceEligible, extra) {
    const product = PRODUCT[productType] || { label: "Ürün önerisi yok", query: "" };
    return Object.assign({
      status,
      title,
      summary,
      productType,
      productClass: product.label,
      limitation: LIMITS[productType] || "Priz test cihazı tesisat kabulü değildir.",
      next,
      commerceEligible: Boolean(commerceEligible),
      searchQuery: product.query,
      personalData: false,
      reviewDays: 180
    }, extra || {});
  }

  function evaluate(raw) {
    const input = Object.assign({
      emergency: false,
      condition: "unknown",
      issue: "precheck",
      outageScope: "none",
      role: "general",
      installation: "unknown",
      plugStandard: "unknown",
      commonFaults: false,
      voltageDisplay: false,
      rcdFunctional: false,
      earthQuality: false,
      loopImpedance: false,
      rcdTripTime: false,
      measuredVoltage: "",
      ownership: "none",
      testerType: "unknown",
      plugCompatibility: "na",
      voltageRating: "na",
      safetyEvidence: "na",
      recall: "na",
      knownGood: "na"
    }, raw || {});
    const voltage = voltageMetric(input.measuredVoltage);
    const extra = { voltage };

    if (bool(input.emergency) || input.issue === "tingling") {
      return result("danger", "Test yapmayın; prizi kullanmayı bırakın", "Elektrik çarpması, karıncalanma, duman, kıvılcım, erime veya yanık kokusu ürün seçimi konusu değildir. Enerjiyi yalnız güvenli biçimde ayırın; yetkili elektrikçi ve gerektiğinde 112 önceliklidir.", null, "Prizi kullanmayın; güvenli alan ve profesyonel müdahale", false, extra);
    }
    if (["loose", "burnt", "wet", "cracked"].includes(input.condition)) {
      return result("danger", "Hasarlı prizi test cihazıyla denemeyin", "Gevşek, kararmış, ıslak veya kırık prizde prize takılan test cihazı kullanmak riski artırabilir. Prizi kullanım dışı bırakın ve elektrikçiye inceletin.", null, "Onarım ve tesisat kontrolü", false, extra);
    }
    if (input.recall === "recalled") {
      return result("danger", "Test cihazını kullanmayı bırakın", "Tam model için geri çağırma veya kullanım durdurma kaydı bulunuyor. Mevcut cihazla ölçüm yapmayın; üreticinin resmî talimatını izleyin.", null, "Üretici geri çağırma süreci", false, extra);
    }
    if (input.knownGood === "failed") {
      return result("danger", "Tutarsız test cihazına güvenmeyin", "Bilinen sağlam prizde çalışma kontrolünü geçmeyen cihaz yanlış güven hissi oluşturabilir. Cihazı kullanmayı bırakın ve üretici servisine yönelin.", null, "Cihaz doğrulaması veya servis", false, extra);
    }
    if (input.outageScope === "neighborhood") {
      return result("official", "Önce kesinti kaynağını doğrulayın", "Bina, sokak veya mahalle kapsamındaki enerji yokluğu priz test cihazıyla çözülmez. Dağıtım şirketinin kesinti kanalını ve 186'yı kontrol edin.", null, "EDAŞ kesinti doğrulaması / 186", false, extra);
    }
    if (["property", "room"].includes(input.outageScope) || input.issue === "no_power") {
      return result("professional", "Devre ve koruma düzeni kontrol edilmeli", "Tek priz, oda, devre veya tüm mülkte enerji yokluğu; sigorta, bağlantı, nötr, iletken sürekliliği veya besleme arızası olabilir. Prize takılan gösterge kök nedeni kanıtlamaz.", "professional", "Yetkili elektrikçiyle devre ölçümü", false, extra);
    }
    if (["repeated_rcd", "intermittent"].includes(input.issue)) {
      return result("professional", "Aralıklı arıza veya RCD açması profesyonel ölçüm ister", "Tekrarlayan RCD açması ve aralıklı enerji; izolasyon, kaçak akım, gevşek bağlantı veya yük kaynaklı olabilir. Basit priz test cihazı kök neden tespiti yapmaz.", "professional", "İzolasyon, kaçak akım ve bağlantı ölçümü", false, extra);
    }
    if (["outdoor", "industrial", "ev", "threephase"].includes(input.installation)) {
      return result("professional", "Bu kullanım tüketici tipi priz test cihazının dışında", "Dış ortam, endüstriyel tesis, EV şarj devresi ve trifaze/CEE prizlerde ölçüm kategorisi, prosedür ve koruyucu donanım saha koşuluna göre belirlenmelidir.", "professional", "Yetkin kişi ve uygun tesisat test cihazı", false, extra);
    }
    if (hasProfessionalTask(input)) {
      return result("professional", "İstenen kanıt profesyonel tesisat ölçümüdür", "Koruma iletkeni direnci, hata çevrim empedansı veya RCD açma akımı/süresi üç lambalı ya da ekranlı priz test cihazıyla doğrulanamaz.", "professional", "IEC 61557 sınıfı ölçüm ve kayıt", false, extra);
    }
    if (input.installation === "unknown" || input.plugStandard === "unknown") {
      return result("evidence", "Tesisat ve fiş standardını doğrulayın", "Ürün sınıfı seçmeden önce bunun 230 V konut/ofis prizi ve Türkiye'de kullanılan Type E/F uyumlu bağlantı olduğu doğrulanmalıdır.", null, "Tesisat ve priz standardı kanıtı", false, extra);
    }
    if (input.plugStandard === "other") {
      return result("evidence", "Adaptörle priz test cihazı kullanmayın", "Farklı ülke standardı veya dönüştürücü adaptör, gösterge mantığını ve koruma iletkeni temasını değiştirebilir. Hedef ülke ve priz standardına özgü cihaz gerekir.", null, "Doğrudan uyumlu ülke standardı cihazı", false, extra);
    }
    if (!bool(input.commonFaults) && !bool(input.voltageDisplay) && !bool(input.rcdFunctional)) {
      return result("evidence", "Düşük riskli ön kontrol görevini seçin", "Ürün sınıfı belirlemek için yaygın bağlantı göstergesi, voltaj ekranı veya RCD işlev kontrolünden en az biri seçilmelidir.", null, "İstenen kanıtı netleştirin", false, extra);
    }

    const need = requiredType(input);
    const needRank = rank(need);
    const currentRank = rank(input.testerType);

    if (input.ownership !== "none") {
      if (input.testerType === "unknown") {
        return result("evidence", "Cihaz sınıfı bilinmeden uygunluk verilemez", "Mevcut veya aday cihazın yalnız ışıklı, voltaj ekranlı, RCD düğmeli ya da profesyonel çok işlevli sınıfı tam model kılavuzundan doğrulanmalıdır.", need, "Tam model kılavuzunu kontrol edin", false, extra);
      }
      if (input.plugCompatibility === "no" || input.voltageRating === "no") {
        return result("replace", "Aday veya mevcut cihaz teknik olarak uyumsuz", "Fiş standardı ya da 230 V/50 Hz kullanım sınırı uyuşmuyor. Adaptörle kullanmayın; doğrudan Type E/F uyumlu sınıf arayın.", need, "Doğrudan uyumlu cihaz sınıfını karşılaştırın", true, extra);
      }
      if (input.safetyEvidence === "no") {
        return result("replace", "Yalnız pazar yeri beyanı yeterli değil", "Tam model, kılavuz, ölçüm kategorisi ve güvenlik belgesi izlenemeyen cihaz güvenilir ön kontrol aracı sayılmamalıdır.", need, "İzlenebilir tam model cihaz sınıfını karşılaştırın", true, extra);
      }
      if ([input.plugCompatibility, input.voltageRating, input.safetyEvidence, input.recall, input.knownGood].some((value) => ["unknown", "na"].includes(value))) {
        return result("evidence", "Mevcut cihaz için kanıt tamamlanmadı", "Fiş standardı, 230 V sınırı, güvenlik belgesi, geri çağırma ve bilinen sağlam prizde çalışma kontrolü tamamlanmadan yeni ürün kararı verilmemelidir.", need, "Eksik tam model kanıtlarını tamamlayın", false, extra);
      }
      if (currentRank < needRank) {
        return result("replace", "Mevcut cihaz istenen görevi kapsamıyor", `İstenen ön kontrol için ${PRODUCT[need].label} gerekir; mevcut sınıf gerekli özelliği sağlamıyor.`, need, "Yalnız eksik özelliği tamamlayan sınıfı karşılaştırın", true, extra);
      }
      if (input.ownership === "owned") {
        return result("no-buy", "Mevcut test cihazı yeterli; yeni ürün almayın", "Mevcut cihaz istenen düşük riskli ön kontrolü karşılıyor; fiş, gerilim sınırı, belge, geri çağırma ve çalışma kontrolü doğrulandı. Profesyonel ölçüm sınırları yine geçerlidir.", need, "Mevcut cihazı kılavuzuna göre kullanın", false, extra);
      }
      return result("candidate", "Aday cihaz teknik sınıfla uyumlu görünüyor", "Aday cihaz istenen düşük riskli görevi ve temel kanıtları karşılıyor. Son seçimde tam model kılavuzu, ölçüm kategorisi ve üretici uyarıları yeniden kontrol edilmelidir.", need, "Aynı teknik sınıftaki seçenekleri karşılaştırın", true, extra);
    }

    const summary = need === "rcd"
      ? "Yaygın bağlantı göstergesi, yaklaşık voltaj ekranı ve RCD işlev düğmesi olan Type E/F cihaz sınıfı uygundur. RCD düğmesi açma akımı veya süresini ölçmez."
      : need === "display"
        ? "Yaygın bağlantı durumlarına ek olarak yaklaşık L–N gerilimini gösteren Type E/F cihaz sınıfı uygundur. Ekran tesisat gerilim kalitesi raporu değildir."
        : "Yalnız yaygın açık/ters bağlantı ön kontrolü için Type E/F temel priz bağlantı göstergesi yeterli olabilir.";
    return result("recommend", "Düşük riskli ön kontrol için cihaz sınıfı belirlendi", summary, need, "Tam model teknik kanıtlarını karşılaştırın", true, extra);
  }

  function affiliateUrl(decision) {
    if (!decision || !decision.commerceEligible || !decision.searchQuery) return "";
    return `https://www.amazon.com.tr/s?k=${encodeURIComponent(decision.searchQuery)}&tag=alo186rehber-21`;
  }

  function collect(doc) {
    const value = (id) => doc.getElementById(id).value;
    const checked = (id) => doc.getElementById(id).checked;
    return {
      emergency: checked("emergency"), condition: value("condition"), issue: value("issue"), outageScope: value("outageScope"),
      role: value("role"), installation: value("installation"), plugStandard: value("plugStandard"),
      commonFaults: checked("commonFaults"), voltageDisplay: checked("voltageDisplay"), rcdFunctional: checked("rcdFunctional"),
      earthQuality: checked("earthQuality"), loopImpedance: checked("loopImpedance"), rcdTripTime: checked("rcdTripTime"),
      measuredVoltage: value("measuredVoltage"), ownership: value("ownership"), testerType: value("testerType"),
      plugCompatibility: value("plugCompatibility"), voltageRating: value("voltageRating"), safetyEvidence: value("safetyEvidence"),
      recall: value("recall"), knownGood: value("knownGood")
    };
  }

  function download(doc, name, type, content) {
    const view = doc.defaultView;
    if (!view || !view.Blob || !view.URL) return;
    const blob = new view.Blob([content], { type });
    const href = view.URL.createObjectURL(blob);
    const anchor = doc.createElement("a");
    anchor.href = href; anchor.download = name; doc.body.appendChild(anchor); anchor.click(); anchor.remove();
    view.URL.revokeObjectURL(href);
  }

  function ics(decision) {
    const date = new Date();
    date.setDate(date.getDate() + decision.reviewDays);
    const ymd = `${date.getFullYear()}${String(date.getMonth() + 1).padStart(2, "0")}${String(date.getDate()).padStart(2, "0")}`;
    return ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//ALO186//Priz Test Kontrolu//TR", "BEGIN:VEVENT", `DTSTART;VALUE=DATE:${ymd}`, "SUMMARY:Priz test cihazı ve güvenlik kontrolü", "DESCRIPTION:Priz fiziksel durumu, cihaz tam model belgesi, geri çağırma ve bilinen sağlam prizde çalışma kontrolünü yenileyin.", "END:VEVENT", "END:VCALENDAR"].join("\r\n");
  }

  function mount(doc) {
    const form = doc.getElementById("outletForm");
    if (!form) return;
    const state = { decision: null };
    const resultBox = doc.getElementById("result");
    const commerce = doc.getElementById("commerce");
    const affiliate = doc.getElementById("affiliate");
    const confirmations = Array.from(doc.querySelectorAll(".confirm"));

    function syncAffiliate() {
      const ready = state.decision && state.decision.commerceEligible && confirmations.every((item) => item.checked);
      const href = ready ? affiliateUrl(state.decision) : "";
      if (href) { affiliate.href = href; affiliate.setAttribute("aria-disabled", "false"); affiliate.tabIndex = 0; }
      else { affiliate.removeAttribute("href"); affiliate.setAttribute("aria-disabled", "true"); affiliate.tabIndex = -1; }
    }
    confirmations.forEach((item) => item.addEventListener("change", syncAffiliate));

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      confirmations.forEach((item) => { item.checked = false; });
      const decision = evaluate(collect(doc));
      state.decision = decision;
      doc.getElementById("status").textContent = decision.status;
      doc.getElementById("status").className = `status ${["danger"].includes(decision.status) ? "danger" : ["professional", "evidence", "official", "replace"].includes(decision.status) ? "warn" : ""}`;
      doc.getElementById("resultTitle").textContent = decision.title;
      doc.getElementById("summary").textContent = decision.summary;
      doc.getElementById("classMetric").textContent = decision.productClass;
      doc.getElementById("limitMetric").textContent = decision.limitation;
      doc.getElementById("voltageMetric").textContent = decision.voltage.text;
      doc.getElementById("nextMetric").textContent = decision.next;
      commerce.hidden = !decision.commerceEligible;
      resultBox.hidden = false;
      syncAffiliate();
      resultBox.focus();
    });

    form.addEventListener("reset", function () {
      state.decision = null;
      resultBox.hidden = true;
      commerce.hidden = true;
      confirmations.forEach((item) => { item.checked = false; });
      syncAffiliate();
    });

    doc.getElementById("downloadJson").addEventListener("click", function () {
      if (!state.decision) return;
      download(doc, "alo186-priz-test-karari.json", "application/json", JSON.stringify({ generatedAt: new Date().toISOString(), result: state.decision }, null, 2));
    });
    doc.getElementById("downloadIcs").addEventListener("click", function () {
      if (!state.decision) return;
      download(doc, "alo186-priz-test-kontrolu.ics", "text/calendar", ics(state.decision));
    });
    doc.getElementById("printResult").addEventListener("click", function () {
      const view = doc.defaultView;
      if (view && typeof view.print === "function") view.print();
    });
  }

  return { evaluate, affiliateUrl, voltageMetric, requiredType, hasProfessionalTask, mount };
});
