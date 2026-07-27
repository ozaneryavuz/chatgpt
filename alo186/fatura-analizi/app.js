(() => {
  "use strict";

  const MONTHS = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"];
  const SHORT_MONTHS = ["Oca","Şub","Mar","Nis","May","Haz","Tem","Ağu","Eyl","Eki","Kas","Ara"];
  const LIMITS = {
    residential: { label: "Mesken", limit: 4000 },
    service: { label: "Kamu ve özel hizmetler sektörü / diğer", limit: 15000 },
    industry: { label: "Sanayi", limit: 15000 },
    lighting: { label: "Aydınlatma", limit: 15000 },
    agriculture: { label: "Tarımsal faaliyetler", limit: 150000000 }
  };
  const FREE_CONSUMER_LIMIT = 500;
  const EXAMPLE = [245,228,214,205,236,322,418];

  const $ = (id) => document.getElementById(id);
  const monthGrid = $("monthGrid");
  let lastResult = null;

  function createMonthInputs() {
    MONTHS.forEach((month, index) => {
      const wrapper = document.createElement("div");
      wrapper.className = "month-field";
      wrapper.innerHTML = `
        <label for="month-${index}">${month}</label>
        <input id="month-${index}" inputmode="decimal" autocomplete="off"
          aria-label="${month} tüketimi kWh" placeholder="—" min="0" step="0.01">
        <b>kWh</b>`;
      monthGrid.appendChild(wrapper);
    });
  }

  function parseValue(input) {
    const raw = String(input.value || "").trim().replace(/\s/g, "").replace(",", ".");
    if (!raw) return null;
    const value = Number(raw);
    return Number.isFinite(value) && value >= 0 ? value : NaN;
  }

  function getValues() {
    return MONTHS.map((_, i) => parseValue($(`month-${i}`)));
  }

  function validate(values) {
    if (values.some(Number.isNaN)) return "Tüketim alanlarında yalnız sıfır veya pozitif sayı kullanın.";
    const nonEmpty = values.filter(v => v !== null);
    if (nonEmpty.length < 2) return "Anlamlı bir eğilim için en az iki aylık kWh tüketimi girin.";
    const firstEmpty = values.findIndex(v => v === null);
    if (firstEmpty !== -1 && values.slice(firstEmpty + 1).some(v => v !== null)) {
      return "Ayları Ocak'tan itibaren sıralı doldurun; arada boş ay bırakmayın.";
    }
    if (nonEmpty.some(v => v > 100000000)) return "Girilen aylık tüketim olağan sınırların dışında görünüyor.";
    return "";
  }

  function weightedAverage(values) {
    let numerator = 0, denominator = 0;
    values.forEach((v, i) => {
      const w = i + 1;
      numerator += v * w;
      denominator += w;
    });
    return denominator ? numerator / denominator : 0;
  }

  function formatKwh(value, maxDigits = 0) {
    return `${value.toLocaleString("tr-TR", { minimumFractionDigits: 0, maximumFractionDigits: maxDigits })} kWh`;
  }

  function calculate(values, groupKey) {
    const actual = values.filter(v => v !== null);
    const n = actual.length;
    const total = actual.reduce((a, b) => a + b, 0);
    const avg = total / n;
    const weighted = weightedAverage(actual);
    const remainingMonths = 12 - n;
    const simpleForecast = total + avg * remainingMonths;
    const trendForecast = total + weighted * remainingMonths;
    const lowForecast = Math.min(simpleForecast, trendForecast);
    const highForecast = Math.max(simpleForecast, trendForecast);
    const midpoint = (lowForecast + highForecast) / 2;
    const limit = LIMITS[groupKey].limit;
    const riskRatio = highForecast / limit;

    let risk = "Düşük";
    let riskClass = "low";
    if (riskRatio >= 1.05) { risk = "Sınır aşımı olası"; riskClass = "very-high"; }
    else if (riskRatio >= .95) { risk = "Yüksek"; riskClass = "high"; }
    else if (riskRatio >= .80) { risk = "İzleme gerekli"; riskClass = "medium"; }

    let crossingIndex = null;
    let cumulative = 0;
    actual.forEach((v, i) => {
      cumulative += v;
      if (crossingIndex === null && cumulative >= limit) crossingIndex = i;
    });
    if (crossingIndex === null && weighted > 0) {
      let projected = cumulative;
      for (let i = n; i < 12; i++) {
        projected += weighted;
        if (projected >= limit) { crossingIndex = i; break; }
      }
    }

    const anomalies = [];
    actual.forEach((v, i) => {
      const deviation = avg ? (v - avg) / avg : 0;
      if (deviation >= .25) anomalies.push({ month: MONTHS[i], type: "high", deviation, value: v });
      else if (deviation <= -.25) anomalies.push({ month: MONTHS[i], type: "low", deviation, value: v });
    });
    anomalies.sort((a,b) => Math.abs(b.deviation) - Math.abs(a.deviation));

    const crossingMonth = crossingIndex !== null ? MONTHS[crossingIndex] : null;
    let applicationDate = null;
    if (crossingIndex !== null) {
      const d = new Date(2026, crossingIndex + 3, 1);
      applicationDate = d.toLocaleDateString("tr-TR", { day:"numeric", month:"long", year:"numeric" });
    }

    return {
      actual, n, total, avg, weighted, lowForecast, highForecast, midpoint,
      limit, risk, riskClass, riskRatio, crossingIndex, crossingMonth, applicationDate,
      remaining: Math.max(0, limit - total), anomalies,
      freeConsumerActual: total >= FREE_CONSUMER_LIMIT,
      freeConsumerForecast: midpoint >= FREE_CONSUMER_LIMIT
    };
  }

  function riskExplanation(result) {
    if (result.riskClass === "very-high") return "Üst tahmin yıllık limitin üzerinde.";
    if (result.riskClass === "high") return "Tahmin limit çevresinde; aylık takip önemli.";
    if (result.riskClass === "medium") return "Limitin %80'inden fazlasına ulaşma ihtimali var.";
    return "Mevcut eğilim limitin belirgin biçimde altında.";
  }

  function buildActions(result, groupKey) {
    const actions = [];
    if (result.riskClass === "very-high" || result.riskClass === "high") {
      actions.push("Son 12 faturadaki dönem tüketimlerini doğrulayın; tahmini yalnız TL tutarıyla değil kWh ile takip edin.");
      actions.push("EPDK'nın resmî fatura hesaplama modülü üzerinden güncel tarife ve abone grubunu kontrol edin.");
      actions.push("Klima, elektrikli su ısıtma, EV şarjı ve yeni eklenen yüksek güçlü cihazları ayrı ayrı gözden geçirin.");
    } else if (result.riskClass === "medium") {
      actions.push("Aylık kWh tüketimini kaydetmeye devam edin ve son üç aylık eğilimi izleyin.");
      actions.push("Yüksek tüketimli cihazların çalışma saatlerini ölçerek yıllık projeksiyonu güncelleyin.");
    } else {
      actions.push("Tüketim düşük riskli görünse de aylık kWh değerlerini düzenli kaydedin.");
      actions.push("Beklenmedik artışta önce sayaç dönemi, cihaz kullanımı ve mevsim etkisini karşılaştırın.");
    }
    if (groupKey !== "residential") {
      actions.push("İşletmelerde yalnız toplam kWh değil; maksimum talep, reaktif değerler ve faaliyet birimi başına tüketim birlikte değerlendirilmelidir.");
    }
    if (result.freeConsumerActual) {
      actions.push("Girilen takvim yılı toplamınız 500 kWh serbest tüketici limitini aşmış görünüyor; tedarikçi seçme hakkının koşullarını EPDK sayfasından inceleyin.");
    } else if (result.freeConsumerForecast) {
      actions.push("Yıl sonu tahmini 500 kWh serbest tüketici limitini aşıyor; hak kazanma durumu için gerçekleşen takvim yılı toplamını izleyin.");
    }
    return actions;
  }

  function renderAnomalies(result) {
    const list = $("anomalyList");
    list.innerHTML = "";
    if (!result.anomalies.length) {
      list.innerHTML = "<li>Girilen dönemlerde ortalamadan ±%25 sapma gösteren belirgin bir ay bulunmadı.</li>";
      return;
    }
    result.anomalies.slice(0, 4).forEach(item => {
      const li = document.createElement("li");
      const pct = Math.abs(item.deviation * 100).toFixed(0);
      li.textContent = `${item.month}: ${formatKwh(item.value, 1)} — dönem ortalamasının %${pct} ${item.type === "high" ? "üzerinde" : "altında"}.`;
      list.appendChild(li);
    });
  }

  function renderActions(result, groupKey) {
    const list = $("actionList");
    list.innerHTML = "";
    buildActions(result, groupKey).forEach(text => {
      const li = document.createElement("li");
      li.textContent = text;
      list.appendChild(li);
    });
  }

  function drawChart(result) {
    const canvas = $("usageChart");
    const rect = canvas.getBoundingClientRect();
    const ratio = Math.max(1, window.devicePixelRatio || 1);
    canvas.width = Math.round(rect.width * ratio);
    canvas.height = Math.round(rect.height * ratio);
    const ctx = canvas.getContext("2d");
    ctx.scale(ratio, ratio);

    const w = rect.width, h = rect.height;
    const pad = { top: 24, right: 18, bottom: 46, left: 54 };
    const cw = w - pad.left - pad.right;
    const ch = h - pad.top - pad.bottom;
    const monthlyLimit = result.limit / 12;
    const maxVal = Math.max(...result.actual, monthlyLimit, 1) * 1.18;

    ctx.clearRect(0,0,w,h);
    ctx.font = "12px system-ui";
    ctx.textAlign = "right";
    ctx.textBaseline = "middle";

    for (let i=0;i<=4;i++) {
      const value = maxVal * (1 - i/4);
      const y = pad.top + ch * i/4;
      ctx.strokeStyle = "#e8edf5";
      ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(pad.left,y); ctx.lineTo(w-pad.right,y); ctx.stroke();
      ctx.fillStyle = "#7b879a";
      ctx.fillText(Math.round(value).toLocaleString("tr-TR"), pad.left-8, y);
    }

    const xStep = cw / 12;
    result.actual.forEach((v,i) => {
      const barW = Math.max(8, xStep * .58);
      const x = pad.left + i*xStep + (xStep-barW)/2;
      const barH = ch * v/maxVal;
      const y = pad.top + ch - barH;
      const grad = ctx.createLinearGradient(0,y,0,pad.top+ch);
      grad.addColorStop(0,"#1e5eff");
      grad.addColorStop(1,"#2eb8d6");
      ctx.fillStyle = grad;
      ctx.beginPath();
      if (ctx.roundRect) ctx.roundRect(x,y,barW,barH,[7,7,2,2]);
      else ctx.rect(x,y,barW,barH);
      ctx.fill();
    });

    const limitY = pad.top + ch - ch * monthlyLimit/maxVal;
    ctx.setLineDash([6,5]);
    ctx.strokeStyle = "#e98819";
    ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(pad.left,limitY); ctx.lineTo(w-pad.right,limitY); ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = "#b46510";
    ctx.textAlign = "left";
    ctx.fillText("Aylık aritmetik limit karşılığı", pad.left+5, Math.max(10,limitY-11));

    ctx.fillStyle = "#6e798d";
    ctx.textAlign = "center";
    ctx.textBaseline = "top";
    SHORT_MONTHS.forEach((m,i) => {
      const x = pad.left + i*xStep + xStep/2;
      ctx.fillText(m, x, pad.top+ch+12);
    });
  }

  function render(result, groupKey) {
    lastResult = { ...result, groupKey };
    $("results").classList.remove("hidden");
    $("actualTotal").textContent = formatKwh(result.total, 1);
    $("monthsEntered").textContent = `${result.n} aylık gerçek veri`;
    $("monthlyAverage").textContent = formatKwh(result.avg, 1);
    $("forecastRange").textContent = `${Math.round(result.lowForecast).toLocaleString("tr-TR")}–${Math.round(result.highForecast).toLocaleString("tr-TR")} kWh`;
    $("riskLabel").textContent = result.risk;
    $("riskExplanation").textContent = riskExplanation(result);
    $("annualLimit").textContent = formatKwh(result.limit);
    $("remainingToLimit").textContent = result.remaining > 0 ? formatKwh(result.remaining, 1) : "Limit mevcut veride aşılmış";
    $("crossingMonth").textContent = result.crossingMonth || "Tahmin aralığında görünmüyor";
    $("applicationDate").textContent = result.applicationDate || "Öngörülmüyor";
    $("eligibleFreeConsumer").textContent = result.freeConsumerActual
      ? "Girilen toplam 500 kWh eşiğini aştı"
      : result.freeConsumerForecast
        ? "Yıl sonu tahmini 500 kWh eşiğini aşıyor"
        : "Girilen toplam ve tahmin 500 kWh altında";
    renderAnomalies(result);
    renderActions(result, groupKey);
    requestAnimationFrame(() => drawChart(result));
    $("results").scrollIntoView({ behavior:"smooth", block:"start" });
  }

  function analyze() {
    const values = getValues();
    const error = validate(values);
    $("validation").textContent = error;
    if (error) return;
    const groupKey = $("subscriberGroup").value;
    render(calculate(values, groupKey), groupKey);
  }

  function clearAll() {
    MONTHS.forEach((_,i) => $(`month-${i}`).value = "");
    $("validation").textContent = "";
    $("results").classList.add("hidden");
    lastResult = null;
  }

  function fillExample() {
    clearAll();
    EXAMPLE.forEach((v,i) => $(`month-${i}`).value = v);
    analyze();
  }

  function copySummary() {
    if (!lastResult) return;
    const r = lastResult;
    const text = [
      "ALO186 Elektrik Faturası Zekâ Merkezi",
      `Abone grubu: ${LIMITS[r.groupKey].label}`,
      `Girilen toplam: ${formatKwh(r.total,1)}`,
      `Aylık ortalama: ${formatKwh(r.avg,1)}`,
      `Yıl sonu tahmini: ${Math.round(r.lowForecast).toLocaleString("tr-TR")}–${Math.round(r.highForecast).toLocaleString("tr-TR")} kWh`,
      `2026 yıllık limit: ${formatKwh(r.limit)}`,
      `Risk: ${r.risk}`,
      `Tahmini aşım ayı: ${r.crossingMonth || "öngörülmüyor"}`,
      "",
      "Bu sonuç yön göstericidir; kesin fatura veya resmî tarife kararı değildir."
    ].join("\n");
    navigator.clipboard?.writeText(text).then(() => {
      const btn = $("copyBtn");
      const old = btn.textContent;
      btn.textContent = "Kopyalandı";
      setTimeout(() => btn.textContent = old, 1600);
    });
  }

  function updateLimitNote() {
    const key = $("subscriberGroup").value;
    const item = LIMITS[key];
    $("limitNote").textContent = `${item.label} için 2026 son kaynak limiti ${item.limit.toLocaleString("tr-TR")} kWh/yıldır.`;
  }

  createMonthInputs();
  updateLimitNote();
  $("subscriberGroup").addEventListener("change", updateLimitNote);
  $("analyzeBtn").addEventListener("click", analyze);
  $("clearBtn").addEventListener("click", clearAll);
  $("exampleBtn").addEventListener("click", fillExample);
  $("copyBtn").addEventListener("click", copySummary);
  $("printBtn").addEventListener("click", () => window.print());
  window.addEventListener("resize", () => { if (lastResult) drawChart(lastResult); });
})();
