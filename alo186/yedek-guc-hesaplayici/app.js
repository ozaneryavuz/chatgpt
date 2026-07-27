(() => {
  "use strict";

  const PRESETS = [
    { id:"modem", name:"Modem / router", watts:12, surge:1, pureSine:false, dcFriendly:true, critical:false },
    { id:"ont", name:"Fiber ONT", watts:8, surge:1, pureSine:false, dcFriendly:true, critical:false },
    { id:"laptop", name:"Laptop adaptörü", watts:65, surge:1.15, pureSine:false, dcFriendly:false, critical:false },
    { id:"tv", name:"LED televizyon", watts:90, surge:1.2, pureSine:false, dcFriendly:false, critical:false },
    { id:"led", name:"LED aydınlatma", watts:10, surge:1, pureSine:false, dcFriendly:false, critical:false },
    { id:"camera", name:"Güvenlik kamerası", watts:12, surge:1.1, pureSine:false, dcFriendly:true, critical:false },
    { id:"nvr", name:"Kamera kayıt cihazı", watts:25, surge:1.2, pureSine:false, dcFriendly:false, critical:false },
    { id:"pos", name:"POS / küçük ağ cihazı", watts:15, surge:1, pureSine:false, dcFriendly:true, critical:false },
    { id:"kombi", name:"Kombi", watts:120, surge:2, pureSine:true, dcFriendly:false, critical:true },
    { id:"fridge", name:"Buzdolabı", watts:150, surge:4, pureSine:true, dcFriendly:false, critical:true },
    { id:"custom", name:"Özel cihaz", watts:100, surge:1, pureSine:false, dcFriendly:false, critical:false }
  ];

  const BATTERIES = {
    lifepo4:{ label:"LiFePO₄ / modern power station", dod:.88, aging:.92 },
    lithium:{ label:"Lityum iyon / NMC", dod:.82, aging:.90 },
    agm:{ label:"AGM / GEL kurşun-asit", dod:.50, aging:.85 },
    leadacid:{ label:"Sulu kurşun-asit", dod:.50, aging:.80 }
  };

  const $ = (id) => document.getElementById(id);
  const loadList = $("loadList");
  let mode = "need";
  let rowCounter = 0;
  let lastResult = null;

  function emit(name, params = {}) {
    if (typeof window.gtag === "function") window.gtag("event", name, params);
  }

  function numberValue(input, fallback = null) {
    const raw = String(input?.value ?? "").trim().replace(/\s/g, "").replace(",", ".");
    if (!raw) return fallback;
    const value = Number(raw);
    return Number.isFinite(value) ? value : NaN;
  }

  function clamp(value, min, max) {
    return Math.min(max, Math.max(min, value));
  }

  function format(value, unit = "W", digits = 0) {
    return `${Number(value).toLocaleString("tr-TR", { maximumFractionDigits:digits })} ${unit}`;
  }

  function presetById(id) {
    return PRESETS.find(item => item.id === id) || PRESETS[PRESETS.length - 1];
  }

  function renderQuickAdd() {
    $("quickAdd").innerHTML = PRESETS.filter(p => p.id !== "custom").map(p =>
      `<button type="button" class="quick-button" data-preset="${p.id}">+ ${p.name}</button>`
    ).join("");
  }

  function addLoad(presetId = "custom", qty = 1, wattsOverride = null) {
    const preset = presetById(presetId);
    const id = ++rowCounter;
    const row = document.createElement("div");
    row.className = "load-row";
    row.dataset.rowId = id;
    row.innerHTML = `
      <label class="name-field"><span>Cihaz</span>
        <select class="device-select" aria-label="Cihaz türü">
          ${PRESETS.map(p => `<option value="${p.id}" ${p.id === preset.id ? "selected" : ""}>${p.name}</option>`).join("")}
        </select>
      </label>
      <label><span>Adet</span><input class="qty-input" inputmode="numeric" value="${qty}" min="1" max="1000" step="1" aria-label="Cihaz adedi"></label>
      <label><span>Güç</span><input class="watts-input" inputmode="decimal" value="${wattsOverride ?? preset.watts}" min="0.1" max="1000000" step="0.1" aria-label="Cihaz gücü watt"></label>
      <label><span>Kalkış katı</span><input class="surge-input" inputmode="decimal" value="${preset.surge}" min="1" max="20" step="0.1" aria-label="Kalkış gücü katı"></label>
      <button type="button" class="remove-button" aria-label="Cihazı kaldır">×</button>`;
    row.querySelector(".device-select").addEventListener("change", event => {
      const selected = presetById(event.target.value);
      row.querySelector(".watts-input").value = selected.watts;
      row.querySelector(".surge-input").value = selected.surge;
    });
    row.querySelector(".remove-button").addEventListener("click", () => {
      row.remove();
      if (!loadList.children.length) addLoad("modem");
    });
    loadList.appendChild(row);
    emit("backup_load_added", { preset:preset.id });
  }

  function getLoads() {
    return [...loadList.querySelectorAll(".load-row")].map(row => {
      const preset = presetById(row.querySelector(".device-select").value);
      return {
        preset,
        qty:numberValue(row.querySelector(".qty-input")),
        watts:numberValue(row.querySelector(".watts-input")),
        surge:numberValue(row.querySelector(".surge-input"))
      };
    });
  }

  function batteryFactors() {
    const type = $("batteryType").value;
    if (type === "custom") {
      return {
        label:"Özel batarya",
        dod:clamp(numberValue($("customDod"), 80) / 100, .1, 1),
        aging:clamp(numberValue($("customAging"), 90) / 100, .4, 1)
      };
    }
    return BATTERIES[type];
  }

  function validate(loads) {
    if (!loads.length) return "En az bir cihaz ekleyin.";
    for (const load of loads) {
      if (![load.qty, load.watts, load.surge].every(Number.isFinite)) return "Cihaz alanlarında geçerli sayılar kullanın.";
      if (load.qty < 1 || load.watts <= 0 || load.surge < 1) return "Adet en az 1, güç pozitif ve kalkış katı en az 1 olmalıdır.";
    }
    const efficiency = numberValue($("efficiency"));
    const reserve = numberValue($("reserve"));
    if (!Number.isFinite(efficiency) || efficiency < 50 || efficiency > 99) return "Dönüşüm verimini %50 ile %99 arasında girin.";
    if (!Number.isFinite(reserve) || reserve < 0 || reserve > 80) return "Kapasite rezervini %0 ile %80 arasında girin.";
    if (mode === "need") {
      const hours = numberValue($("targetHours"));
      if (!Number.isFinite(hours) || hours <= 0 || hours > 168) return "Hedef süreyi 0,1 ile 168 saat arasında girin.";
    } else {
      const values = [numberValue($("existingWh")), numberValue($("existingContinuousW")), numberValue($("existingPeakW"))];
      if (values.some(v => !Number.isFinite(v) || v <= 0)) return "Mevcut ürünün Wh, sürekli W ve tepe W değerlerini girin.";
    }
    return "";
  }

  function calculate() {
    const loads = getLoads();
    const error = validate(loads);
    $("validation").textContent = error;
    if (error) return;

    const totalLoad = loads.reduce((sum, item) => sum + item.qty * item.watts, 0);
    const maxExtraSurge = Math.max(0, ...loads.map(item => item.watts * Math.max(0, item.surge - 1)));
    const surgeLoad = totalLoad + maxExtraSurge;
    const factors = batteryFactors();
    const efficiency = numberValue($("efficiency")) / 100;
    const reserve = numberValue($("reserve")) / 100;
    const usableFactor = efficiency * factors.dod * factors.aging;
    const pureSine = loads.some(item => item.preset.pureSine);
    const criticalLoads = loads.filter(item => item.preset.critical);
    const dcFriendly = loads.every(item => item.preset.dcFriendly && item.surge <= 1.2);
    const presetCount = loads.filter(item => item.preset.id !== "custom").length;
    const editedCount = loads.filter(item => Math.abs(item.watts - item.preset.watts) > .01 || Math.abs(item.surge - item.preset.surge) > .01).length;
    let confidence = 88 - Math.max(0, loads.length - presetCount) * 10 - Math.max(0, editedCount) * 2;
    if (criticalLoads.length) confidence -= 8;
    confidence = clamp(confidence, 45, 95);

    const result = {
      mode, loads, totalLoad, surgeLoad, factors, efficiency, reserve, usableFactor,
      pureSine, criticalLoads, dcFriendly, confidence
    };

    if (mode === "need") {
      const hours = numberValue($("targetHours"));
      const rawEnergy = totalLoad * hours;
      const requiredWh = rawEnergy / usableFactor * (1 + reserve);
      const recommendedContinuous = Math.max(totalLoad * 1.25, totalLoad + 30);
      const recommendedPeak = Math.max(surgeLoad * 1.15, recommendedContinuous * 1.5);
      Object.assign(result, { hours, rawEnergy, requiredWh, recommendedContinuous, recommendedPeak });
    } else {
      const existingWh = numberValue($("existingWh"));
      const existingContinuousW = numberValue($("existingContinuousW"));
      const existingPeakW = numberValue($("existingPeakW"));
      const usableWh = existingWh * usableFactor * Math.max(0, 1 - reserve);
      const estimatedHours = usableWh / totalLoad;
      const continuousOk = existingContinuousW >= totalLoad * 1.1;
      const peakOk = existingPeakW >= surgeLoad;
      Object.assign(result, { existingWh, existingContinuousW, existingPeakW, usableWh, estimatedHours, continuousOk, peakOk, rawEnergy:usableWh });
    }

    result.solution = solutionFor(result);
    lastResult = result;
    renderResult(result);
    saveDraft();
    emit("backup_power_calculated", { mode, solution:result.solution.key, total_load_band:band(totalLoad) });
  }

  function band(watts) {
    if (watts <= 100) return "0_100";
    if (watts <= 500) return "101_500";
    if (watts <= 2000) return "501_2000";
    return "2000_plus";
  }

  function solutionFor(result) {
    const wh = result.mode === "need" ? result.requiredWh : result.existingWh;
    if (result.dcFriendly && result.totalLoad <= 80 && wh <= 300 && !result.pureSine) {
      return { key:"mini_ups", label:"DC mini UPS / modem yedeği", href:"https://alo186.com/amazon-elektrik-urunleri?kategori=modem-ups", cta:"Mini UPS rehberini aç" };
    }
    if (result.totalLoad <= 300 && wh <= 700 && result.surgeLoad <= 1000) {
      return { key:"small_station", label:"Küçük taşınabilir güç istasyonu", href:"https://alo186.com/amazon-elektrik-urunleri?kategori=tasinabilir-guc-istasyonu", cta:"Güç istasyonu rehberini aç" };
    }
    if (result.totalLoad <= 1200 && wh <= 2500 && result.surgeLoad <= 3500) {
      return { key:"medium_station", label:"Orta sınıf güç istasyonu / UPS", href:"https://alo186.com/amazon-elektrik-urunleri?kategori=tasinabilir-guc-istasyonu", cta:"Uygun çözüm sınıfını gör" };
    }
    return { key:"professional", label:"Profesyonel UPS / inverter-batarya sistemi", href:"https://alo186.com/iletisim?konu=yedek-guc-projelendirme", cta:"Teknik ön değerlendirme al" };
  }

  function renderResult(r) {
    $("results").classList.remove("hidden");
    $("totalLoad").textContent = format(r.totalLoad, "W", 1);
    $("surgeLoad").textContent = format(r.surgeLoad, "W", 1);
    $("rawEnergy").textContent = r.mode === "need" ? format(r.rawEnergy, "Wh", 0) : format(r.usableWh, "Wh", 0);
    $("waveform").textContent = r.pureSine ? "Saf sinüs önerilir" : "Ürün gereksinimine göre doğrulayın";
    $("solutionClass").textContent = r.solution.label;
    $("confidence").textContent = `%${Math.round(r.confidence)}`;

    const insights = [];
    if (r.mode === "need") {
      $("resultTitle").textContent = "Gerekli yedek güç kapasitesi";
      $("energyMetricLabel").textContent = "Önerilen nominal kapasite";
      $("energyMetric").textContent = format(Math.ceil(r.requiredWh / 10) * 10, "Wh");
      $("energyMetricNote").textContent = `${r.hours.toLocaleString("tr-TR", {maximumFractionDigits:1})} saat hedef ve %${Math.round(r.reserve*100)} rezervle`;
      $("recommendedContinuous").textContent = `en az ${format(Math.ceil(r.recommendedContinuous/10)*10,"W")}`;
      $("recommendedPeak").textContent = `en az ${format(Math.ceil(r.recommendedPeak/10)*10,"W")}`;
      $("statusLabel").textContent = r.solution.key === "professional" ? "Proje gerekli" : "Çözüm sınıfı belirlendi";
      $("statusNote").textContent = r.solution.label;
      insights.push(`Cihazların ${format(r.rawEnergy,"Wh")} ham enerji ihtiyacı, kayıplar ve rezervle yaklaşık ${format(r.requiredWh,"Wh")} nominal kapasiteye yükseliyor.`);
    } else {
      $("resultTitle").textContent = "Mevcut güç kaynağı çalışma süresi";
      $("energyMetricLabel").textContent = "Tahmini çalışma süresi";
      $("energyMetric").textContent = `${r.estimatedHours.toLocaleString("tr-TR", {maximumFractionDigits:2})} saat`;
      $("energyMetricNote").textContent = `Yaklaşık ${Math.round(r.estimatedHours*60).toLocaleString("tr-TR")} dakika`;
      $("recommendedContinuous").textContent = r.continuousOk ? "Sürekli güç uygun görünüyor" : `Yetersiz — yük ${format(r.totalLoad,"W")}`;
      $("recommendedPeak").textContent = r.peakOk ? "Tepe güç uygun görünüyor" : `Yetersiz — ihtiyaç ${format(r.surgeLoad,"W")}`;
      const ok = r.continuousOk && r.peakOk;
      $("statusLabel").textContent = ok ? "Güç uyumu olumlu" : "Güç uyumsuzluğu";
      $("statusNote").textContent = ok ? "Süre tahminini üretici verisiyle doğrulayın" : "Çıkış gücü sınırlarını kontrol edin";
      insights.push(`Nominal ${format(r.existingWh,"Wh")} kapasitenin yaklaşık ${format(r.usableWh,"Wh")} bölümü seçilen verim, deşarj ve rezerv varsayımlarıyla kullanılabilir kabul edildi.`);
    }

    insights.push(`Hesapta ${r.factors.label}; %${Math.round(r.efficiency*100)} dönüşüm verimi, %${Math.round(r.factors.dod*100)} deşarj ve %${Math.round(r.factors.aging*100)} sağlık katsayısı kullanıldı.`);
    if (r.pureSine) insights.push("Motorlu veya hassas yük bulunduğu için saf sinüs çıkış ve üretici uyumluluğu ayrıca kontrol edilmelidir.");
    if (r.criticalLoads.length) insights.push(`${r.criticalLoads.map(item=>item.preset.name).join(", ")} için hazır watt ve kalkış katsayıları yalnız başlangıç varsayımıdır; etiket veya teknik föy değeri girilmelidir.`);
    if (r.loads.length > 1) insights.push("Kalkış hesabı en ağır tek cihazın kalkışını varsayar; eşzamanlı motor kalkışları ayrıca hesaplanmalıdır.");
    $("insightList").innerHTML = insights.map(text => `<li>${escapeHtml(text)}</li>`).join("");

    const professionalReasons = [];
    if (r.solution.key === "professional") professionalReasons.push("yük veya enerji kapasitesi tüketici tipi taşınabilir çözümlerin ötesine geçiyor");
    if (r.totalLoad > 2000) professionalReasons.push("sürekli yük 2 kW üzerinde");
    if (r.surgeLoad > 3500) professionalReasons.push("kalkış gücü 3,5 kW üzerinde");
    if (r.criticalLoads.length > 1) professionalReasons.push("birden fazla motorlu/kritik cihaz bulunuyor");
    const showProfessional = professionalReasons.length > 0;
    $("professionalWarning").classList.toggle("hidden", !showProfessional);
    $("professionalReason").textContent = showProfessional
      ? `Profesyonel kontrol önerilir: ${professionalReasons.join("; ")}. Sabit bina tesisatına doğrudan bağlantı yapılmamalıdır.`
      : "";

    $("nextStepTitle").textContent = r.solution.label;
    $("nextStepText").textContent = r.solution.key === "professional"
      ? "Tek/üç faz, geçiş süresi, koruma, kablo, topraklama ve devreye alma koşullarıyla teknik ön değerlendirme oluşturun."
      : "Sonuçtaki Wh, sürekli W, tepe W ve dalga biçimi şartlarını karşılamayan ürünleri elemeden çıkarın.";
    $("nextStepLink").href = r.solution.href;
    $("nextStepLink").textContent = r.solution.cta;
    $("nextStepLink").onclick = () => emit("backup_solution_clicked", { solution:r.solution.key });
    $("results").scrollIntoView({ behavior:"smooth", block:"start" });
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>'"]/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"}[char]));
  }

  function setMode(nextMode) {
    mode = nextMode;
    document.querySelectorAll(".mode-button").forEach(button => {
      const active = button.dataset.mode === mode;
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", String(active));
    });
    $("runtimeField").classList.toggle("hidden", mode !== "need");
    $("existingProduct").classList.toggle("hidden", mode !== "runtime");
    $("calculateBtn").textContent = mode === "need" ? "Gerekli kapasiteyi hesapla" : "Çalışma süresini hesapla";
    $("results").classList.add("hidden");
    updateAssumptionNote();
  }

  function updateBatteryFields() {
    const custom = $("batteryType").value === "custom";
    $("dodField").classList.toggle("hidden", !custom);
    $("agingField").classList.toggle("hidden", !custom);
    updateAssumptionNote();
  }

  function updateAssumptionNote() {
    const f = batteryFactors();
    $("assumptionNote").textContent = `${f.label}: kullanılabilir deşarj %${Math.round(f.dod*100)}, batarya sağlık katsayısı %${Math.round(f.aging*100)} varsayıldı. Gerçek ürün eğrileri farklı olabilir.`;
  }

  function clearAll() {
    loadList.innerHTML = "";
    addLoad("modem");
    addLoad("ont");
    $("targetHours").value = "4";
    $("batteryType").value = "lifepo4";
    $("efficiency").value = "88";
    $("reserve").value = "20";
    $("existingWh").value = "";
    $("existingContinuousW").value = "";
    $("existingPeakW").value = "";
    $("validation").textContent = "";
    $("results").classList.add("hidden");
    lastResult = null;
    setMode("need");
    updateBatteryFields();
    localStorage.removeItem("alo186_backup_power_draft");
  }

  function fillExample() {
    loadList.innerHTML = "";
    addLoad("modem");
    addLoad("ont");
    addLoad("laptop");
    addLoad("led", 2);
    $("targetHours").value = "5";
    $("batteryType").value = "lifepo4";
    $("efficiency").value = "88";
    $("reserve").value = "20";
    setMode("need");
    updateBatteryFields();
    calculate();
  }

  function saveDraft() {
    const draft = {
      mode,
      targetHours:$("targetHours").value,
      batteryType:$("batteryType").value,
      efficiency:$("efficiency").value,
      reserve:$("reserve").value,
      customDod:$("customDod").value,
      customAging:$("customAging").value,
      existingWh:$("existingWh").value,
      existingContinuousW:$("existingContinuousW").value,
      existingPeakW:$("existingPeakW").value,
      loads:getLoads().map(item => ({ id:item.preset.id, qty:item.qty, watts:item.watts, surge:item.surge }))
    };
    try { localStorage.setItem("alo186_backup_power_draft", JSON.stringify(draft)); } catch (_) {}
  }

  function restoreDraft() {
    let draft;
    try { draft = JSON.parse(localStorage.getItem("alo186_backup_power_draft") || "null"); } catch (_) { return false; }
    if (!draft?.loads?.length) return false;
    loadList.innerHTML = "";
    draft.loads.forEach(item => {
      addLoad(item.id, item.qty, item.watts);
      const row = loadList.lastElementChild;
      row.querySelector(".surge-input").value = item.surge;
    });
    ["targetHours","batteryType","efficiency","reserve","customDod","customAging","existingWh","existingContinuousW","existingPeakW"].forEach(id => {
      if (draft[id] !== undefined && $(id)) $(id).value = draft[id];
    });
    setMode(draft.mode === "runtime" ? "runtime" : "need");
    updateBatteryFields();
    return true;
  }

  function copySummary() {
    if (!lastResult) return;
    const r = lastResult;
    const lines = [
      "ALO186 Yedek Güç Hesaplayıcısı",
      `Sürekli yük: ${format(r.totalLoad,"W",1)}`,
      `Muhtemel kalkış gücü: ${format(r.surgeLoad,"W",1)}`,
      r.mode === "need" ? `Önerilen nominal kapasite: ${format(Math.ceil(r.requiredWh/10)*10,"Wh")}` : `Tahmini çalışma süresi: ${r.estimatedHours.toLocaleString("tr-TR",{maximumFractionDigits:2})} saat`,
      `Çözüm sınıfı: ${r.solution.label}`,
      `Dalga biçimi: ${r.pureSine ? "Saf sinüs önerilir" : "Ürün gereksinimine göre doğrulayın"}`,
      "",
      "Sonuç ön değerlendirmedir; ürün teknik verileri ve tesis koşulları ayrıca doğrulanmalıdır."
    ];
    navigator.clipboard?.writeText(lines.join("\n")).then(() => {
      const button = $("copyBtn");
      const old = button.textContent;
      button.textContent = "Kopyalandı";
      setTimeout(() => button.textContent = old, 1500);
    });
  }

  renderQuickAdd();
  $("quickAdd").addEventListener("click", event => {
    const button = event.target.closest("[data-preset]");
    if (button) addLoad(button.dataset.preset);
  });
  $("addCustomBtn").addEventListener("click", () => addLoad("custom"));
  document.querySelectorAll(".mode-button").forEach(button => button.addEventListener("click", () => setMode(button.dataset.mode)));
  $("batteryType").addEventListener("change", updateBatteryFields);
  $("calculateBtn").addEventListener("click", calculate);
  $("clearBtn").addEventListener("click", clearAll);
  $("exampleBtn").addEventListener("click", fillExample);
  $("copyBtn").addEventListener("click", copySummary);
  $("printBtn").addEventListener("click", () => window.print());

  if (!restoreDraft()) {
    addLoad("modem");
    addLoad("ont");
    setMode("need");
    updateBatteryFields();
  }
})();
