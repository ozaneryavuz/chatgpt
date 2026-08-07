(() => {
  "use strict";

  const core = window.ALO186BackupTCO;
  if (!core) return;

  const STORAGE_KEY = "alo186_backup_tco_v1";
  const STORAGE_TTL_MS = 30 * 24 * 60 * 60 * 1000;
  const form = document.getElementById("tcoForm");
  const validation = document.getElementById("validation");
  const resultsSection = document.getElementById("results");
  const resultsBody = document.getElementById("resultsBody");
  const restoreBtn = document.getElementById("restoreBtn");
  const resetBtn = document.getElementById("resetBtn");
  const printBtn = document.getElementById("printBtn");
  const exportBtn = document.getElementById("exportBtn");
  const affiliateAck = document.getElementById("affiliateAck");
  const productLink = document.getElementById("productLink");
  let latestComparison = null;

  const money = new Intl.NumberFormat("tr-TR", { style: "currency", currency: "TRY", maximumFractionDigits: 0 });
  const decimal = new Intl.NumberFormat("tr-TR", { maximumFractionDigits: 1 });

  function emit(event, parameters = {}) {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ event, ...parameters });
  }

  function numericValue(id) {
    const raw = document.getElementById(id).value.trim();
    return raw === "" ? null : Number(raw);
  }

  function collectAssumptions() {
    return {
      years: numericValue("years"),
      outagesPerYear: numericValue("outagesPerYear"),
      hoursPerOutage: numericValue("hoursPerOutage"),
      impactPerHour: numericValue("impactPerHour"),
      continuousW: numericValue("continuousW"),
      scope: document.getElementById("scope").value,
      phase: document.getElementById("phase").value,
      medical: document.getElementById("medical").checked
    };
  }

  function collectSolutions() {
    return Array.from(document.querySelectorAll("#solutionRows tr[data-solution]")).map((row) => ({
      id: row.dataset.solution,
      enabled: row.querySelector(".enabled").checked,
      purchase: Number(row.querySelector(".purchase").value || 0),
      installation: Number(row.querySelector(".installation").value || 0),
      annualMaintenance: Number(row.querySelector(".maintenance").value || 0),
      annualOperating: Number(row.querySelector(".operating").value || 0),
      replacementYears: Number(row.querySelector(".replacementYears").value || 0),
      replacementCost: Number(row.querySelector(".replacementCost").value || 0),
      coveragePercent: Number(row.querySelector(".coverage").value || 0)
    }));
  }

  function setValue(id, value) {
    const element = document.getElementById(id);
    if (element) element.value = value ?? "";
  }

  function applySolutions(solutions) {
    const byId = new Map((solutions || []).map((item) => [item.id, item]));
    document.querySelectorAll("#solutionRows tr[data-solution]").forEach((row) => {
      const item = byId.get(row.dataset.solution);
      if (!item) return;
      row.querySelector(".enabled").checked = Boolean(item.enabled);
      row.querySelector(".purchase").value = item.purchase || "";
      row.querySelector(".installation").value = item.installation || 0;
      row.querySelector(".maintenance").value = item.annualMaintenance || 0;
      row.querySelector(".operating").value = item.annualOperating || 0;
      row.querySelector(".replacementYears").value = item.replacementYears || "";
      row.querySelector(".replacementCost").value = item.replacementCost || 0;
      row.querySelector(".coverage").value = item.coveragePercent || "";
    });
  }

  function saveLocal(assumptions, solutions) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(core.sanitizeForStorage(assumptions, solutions)));
      restoreBtn.hidden = false;
    } catch (_) {
      // Private browsing or storage restrictions must not block the calculator.
    }
  }

  function readLocal() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      const savedAt = Date.parse(parsed.savedAt || "");
      if (!Number.isFinite(savedAt) || Date.now() - savedAt > STORAGE_TTL_MS) {
        localStorage.removeItem(STORAGE_KEY);
        return null;
      }
      return parsed;
    } catch (_) {
      return null;
    }
  }

  function restoreLocal() {
    const saved = readLocal();
    if (!saved) {
      restoreBtn.hidden = true;
      return;
    }
    const assumptions = saved.assumptions || {};
    ["years", "outagesPerYear", "hoursPerOutage", "impactPerHour", "continuousW"].forEach((id) => setValue(id, assumptions[id]));
    if (assumptions.scope) document.getElementById("scope").value = assumptions.scope;
    if (assumptions.phase) document.getElementById("phase").value = assumptions.phase;
    document.getElementById("medical").checked = false;
    applySolutions(saved.solutions);
    emit("backup_tco_restored");
  }

  function clearLocal() {
    try { localStorage.removeItem(STORAGE_KEY); } catch (_) {}
    restoreBtn.hidden = true;
  }

  function showErrors(errors) {
    validation.innerHTML = errors.map((message) => `<div>${escapeHtml(message)}</div>`).join("");
    validation.focus();
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>'"]/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[character]));
  }

  function formatPayback(value, horizon) {
    if (value == null || !Number.isFinite(value)) return "Hesaplanamadı";
    if (value > horizon) return `${decimal.format(value)} yıl (dönem dışı)`;
    return `${decimal.format(value)} yıl`;
  }

  function renderTable(comparison) {
    resultsBody.innerHTML = comparison.results.map((item, index) => {
      const netClass = item.netBenefit >= 0 ? "positive" : "negative";
      return `<tr class="${index === 0 ? "rank-first" : ""}"><td><strong>${escapeHtml(item.label)}</strong>${index === 0 ? "<small>En yüksek net fark</small>" : ""}</td><td>${money.format(item.tco)}</td><td>${money.format(item.avoidedImpact)}</td><td class="${netClass}">${money.format(item.netBenefit)}</td><td>${formatPayback(item.paybackYears, comparison.assumptions.years)}</td><td>${item.costPerProtectedHour == null ? "—" : `${money.format(item.costPerProtectedHour)}/saat`}</td></tr>`;
    }).join("");
  }

  function renderDecision(comparison) {
    const best = comparison.best;
    const status = document.getElementById("resultStatus");
    const bestLabel = document.getElementById("bestLabel");
    const bestNote = document.getElementById("bestNote");
    const decisionMetric = document.getElementById("decisionMetric");
    const decisionText = document.getElementById("decisionText");
    const decisionList = document.getElementById("decisionList");
    const professionalPanel = document.getElementById("professionalPanel");
    const affiliatePanel = document.getElementById("affiliatePanel");

    document.getElementById("outageHoursMetric").textContent = `${decimal.format(comparison.annualOutageHours)} saat`;
    document.getElementById("impactMetric").textContent = money.format(comparison.annualGrossImpact);
    document.getElementById("lowestTcoMetric").textContent = money.format(Math.min(...comparison.results.map((item) => item.tco)));

    if (comparison.noBuy) {
      status.className = "status warn";
      status.textContent = "Satın alma ekonomik olarak doğrulanmadı";
      bestLabel.textContent = "Önce satın almayı erteleyin";
      bestNote.textContent = "Girilen varsayımlarda hiçbir çözüm toplam maliyetini karşılamıyor.";
      decisionMetric.textContent = "Önce kayıt / azaltma";
      decisionText.innerHTML = "<p><strong>“Bir ürün seçmek” bu karşılaştırmanın zorunlu sonucu değildir.</strong> Kesinti etkisini yeniden doğrulayın, kritik yükü küçültün ve daha düşük kapasiteli senaryoyu tekrar çalıştırın.</p>";
      decisionList.innerHTML = "<li>Kesinti Günlüğü ile gerçek süre ve sıklığı doğrulayın.</li><li>Yalnız kritik cihazları ayırarak gerekli W ve Wh değerini azaltın.</li><li>Satın alma kararını düşük, orta ve yüksek kesinti etkisi senaryolarıyla test edin.</li>";
      affiliatePanel.classList.add("hidden");
      professionalPanel.classList.toggle("hidden", !comparison.professional);
      emit("backup_tco_no_buy_shown");
      return;
    }

    status.className = comparison.professional ? "status warn" : "status ok";
    status.textContent = comparison.professional ? "Teknik proje doğrulaması gerekli" : "Ekonomik öncelik bulundu";
    bestLabel.textContent = best.label;
    bestNote.textContent = `${comparison.assumptions.years} yılda yaklaşık ${money.format(best.netBenefit)} net fark; yalnız girilen varsayımlara göre.`;
    decisionMetric.textContent = comparison.professional ? "Uzman doğrulaması" : best.label;
    decisionText.innerHTML = `<p><strong>${escapeHtml(best.label)}</strong>, girilen maliyet ve etki varsayımlarında en yüksek net farkı veriyor. Bu sonuç marka, kapasite veya kurulum onayı değildir.</p>`;
    decisionList.innerHTML = `<li>Toplam maliyet: ${money.format(best.tco)}</li><li>Karşılanacağı varsayılan etki: %${decimal.format(best.coveragePercent)}</li><li>Dönem içi yenileme sayısı: ${best.replacements}</li><li>Yaklaşık geri ödeme: ${formatPayback(best.paybackYears, comparison.assumptions.years)}</li>`;

    professionalPanel.classList.toggle("hidden", !comparison.professional);
    affiliatePanel.classList.toggle("hidden", !comparison.affiliateEligible || comparison.professional);
    affiliateAck.checked = false;
    updateAffiliateLink();
    emit("backup_tco_solution_ranked", { solution: best.id, professional: comparison.professional });
  }

  function renderBrief(comparison) {
    const list = document.getElementById("briefList");
    const assumptions = comparison.assumptions;
    list.innerHTML = `<li>Kritik sürekli yük: ${decimal.format(assumptions.continuousW)} W</li><li>Hedeflenen kayıt dönemi: ${assumptions.years} yıl</li><li>Kesinti varsayımı: yılda ${decimal.format(assumptions.outagesPerYear)} olay × ${decimal.format(assumptions.hoursPerOutage)} saat</li><li>Kapsam: ${assumptions.scope === "fixed" ? "sabit tesisat / bina devresi" : "yalnız fişli cihazlar"}</li><li>Faz: ${assumptions.phase === "single" ? "monofaze" : assumptions.phase === "three" ? "trifaze" : "bilinmiyor"}</li><li>Teklifte istenecek ortak kalemler: cihaz, kurulum, yıllık bakım/işletme, yenileme, garanti kapsamı ve teknik güvenlik doğrulaması</li>`;
  }

  function render(comparison) {
    latestComparison = comparison;
    renderTable(comparison);
    renderDecision(comparison);
    renderBrief(comparison);
    resultsSection.classList.remove("hidden");
    resultsSection.focus();
  }

  function updateAffiliateLink() {
    const enabled = affiliateAck.checked;
    productLink.classList.toggle("disabled", !enabled);
    productLink.setAttribute("aria-disabled", String(!enabled));
    productLink.tabIndex = enabled ? 0 : -1;
  }

  function exportSummary() {
    if (!latestComparison) return;
    const exportObject = {
      generatedAt: new Date().toISOString(),
      disclaimer: "ALO186 fiyat, ürün veya proje onayı değildir. Değerler kullanıcı varsayımıdır.",
      assumptions: { ...latestComparison.assumptions, medical: undefined },
      results: latestComparison.results.map(({ id, label, tco, avoidedImpact, netBenefit, paybackYears, coveragePercent, replacements }) => ({ id, label, tco, avoidedImpact, netBenefit, paybackYears, coveragePercent, replacements })),
      decision: latestComparison.noBuy ? "Satın alma ekonomik olarak doğrulanmadı" : latestComparison.best.label
    };
    const blob = new Blob([JSON.stringify(exportObject, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "alo186-yedek-guc-maliyet-karsilastirmasi.json";
    anchor.click();
    URL.revokeObjectURL(url);
    emit("backup_tco_exported");
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    validation.textContent = "";
    const assumptions = collectAssumptions();
    const solutions = collectSolutions();
    const comparison = core.compare(assumptions, solutions);
    if (!comparison.ok) {
      showErrors(comparison.errors);
      resultsSection.classList.add("hidden");
      return;
    }
    saveLocal(assumptions, solutions);
    render(comparison);
    emit("backup_tco_calculated", { solutions: comparison.results.length, no_buy: comparison.noBuy });
  });

  restoreBtn.addEventListener("click", restoreLocal);
  resetBtn.addEventListener("click", () => {
    form.reset();
    clearLocal();
    resultsSection.classList.add("hidden");
    validation.textContent = "";
    document.getElementById("medical").checked = false;
    latestComparison = null;
    emit("backup_tco_cleared");
  });
  printBtn.addEventListener("click", () => { window.print(); emit("backup_tco_printed"); });
  exportBtn.addEventListener("click", exportSummary);
  affiliateAck.addEventListener("change", updateAffiliateLink);
  productLink.addEventListener("click", (event) => {
    if (productLink.getAttribute("aria-disabled") === "true") event.preventDefault();
    else emit("backup_tco_product_center_opened", { solution: latestComparison?.best?.id || "unknown" });
  });

  const saved = readLocal();
  restoreBtn.hidden = !saved;
})();