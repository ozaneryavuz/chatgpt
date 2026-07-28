(() => {
  "use strict";

  const core = window.AloContinuityPassport;
  if (!core) return;

  const STORAGE_KEY = "alo186.continuityPassport.v1";
  const MATURITY_HANDOFF_KEY = "alo186.continuityMaturityHandoff.v1";
  const PASSPORT_HANDOFF_KEY = "alo186.continuityPassportHandoff.v1";
  const HANDOFF_TTL_MS = 7 * 24 * 60 * 60 * 1000;

  const form = document.getElementById("passportForm");
  const facilityType = document.getElementById("facilityType");
  const criticalLoads = document.getElementById("criticalLoads");
  const backupSources = document.getElementById("backupSources");
  const evidenceList = document.getElementById("evidenceList");
  const immediateDanger = document.getElementById("immediateDanger");
  const lifeSupport = document.getElementById("lifeSupport");
  const storageOptIn = document.getElementById("storageOptIn");
  const validation = document.getElementById("validation");
  const emergencyNotice = document.getElementById("emergencyNotice");
  const results = document.getElementById("results");
  const restoreBtn = document.getElementById("restoreBtn");
  const resetBtn = document.getElementById("resetBtn");
  const importMaturityBtn = document.getElementById("importMaturityBtn");
  const maturityImportState = document.getElementById("maturityImportState");
  const progressBar = document.getElementById("progressBar");
  const progressText = document.getElementById("progressText");
  const scoreValue = document.getElementById("scoreValue");
  const bandValue = document.getElementById("bandValue");
  const scoreSummary = document.getElementById("scoreSummary");
  const p0Value = document.getElementById("p0Value");
  const p1Value = document.getElementById("p1Value");
  const reviewValue = document.getElementById("reviewValue");
  const maturityResult = document.getElementById("maturityResult");
  const professionalNotice = document.getElementById("professionalNotice");
  const evidenceMatrix = document.getElementById("evidenceMatrix");
  const priorityP0 = document.getElementById("priorityP0");
  const priorityP1 = document.getElementById("priorityP1");
  const priorityP2 = document.getElementById("priorityP2");
  const exportBtn = document.getElementById("exportBtn");
  const printBtn = document.getElementById("printBtn");
  const panelLink = document.getElementById("panelLink");
  const businessCta = document.getElementById("businessCta");

  let lastResult = null;
  let importedMaturity = null;
  let startedTracked = false;

  function track(event, params) {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ event, ...(params || {}) });
  }

  function renderChoices(target, catalogue, groupName) {
    const fragment = document.createDocumentFragment();
    catalogue.forEach((item) => {
      const label = document.createElement("label");
      label.className = "choice-item";
      label.innerHTML = `<input type="checkbox" name="${groupName}" value="${item.id}"><span>${item.label}</span>`;
      fragment.appendChild(label);
    });
    target.replaceChildren(fragment);
  }

  function renderEvidence() {
    const fragment = document.createDocumentFragment();
    core.EVIDENCE_FIELDS.forEach((field, index) => {
      const fieldset = document.createElement("fieldset");
      fieldset.className = "evidence-row";
      fieldset.dataset.evidence = field.id;
      const legend = document.createElement("legend");
      legend.innerHTML = `<span class="evidence-number">${index + 1}</span><span><strong>${field.title}</strong><small>Ağırlık: ${field.weight}/100 · önerilen yenileme: ${field.reviewDays} gün</small></span>`;
      fieldset.appendChild(legend);
      const options = document.createElement("div");
      options.className = "status-options";
      [
        ["current", "Güncel", "Tarih, kapsam ve sonuç kullanılabilir"],
        ["due", "Yenileme zamanı", "Var fakat süresi veya kapsamı zayıf"],
        ["planned", "Planlandı", "Sorumlu veya tarih var, kanıt henüz yok"],
        ["missing", "Yok", "Kayıt bulunmuyor veya bilinmiyor"]
      ].forEach(([value, title, detail]) => {
        const option = document.createElement("label");
        option.className = "status-option";
        option.innerHTML = `<input type="radio" name="evidence_${field.id}" value="${value}"><span><strong>${title}</strong><small>${detail}</small></span>`;
        options.appendChild(option);
      });
      fieldset.appendChild(options);
      fragment.appendChild(fieldset);
    });
    evidenceList.replaceChildren(fragment);
  }

  function selectedValues(name) {
    return [...form.querySelectorAll(`input[name="${name}"]:checked`)].map((item) => item.value);
  }

  function readEvidence() {
    const evidence = {};
    core.EVIDENCE_FIELDS.forEach((field) => {
      const selected = form.querySelector(`input[name="evidence_${field.id}"]:checked`);
      if (selected) evidence[field.id] = selected.value;
    });
    return evidence;
  }

  function readInput() {
    return {
      facilityType: facilityType.value,
      criticalLoads: selectedValues("critical_load"),
      backupSources: selectedValues("backup_source"),
      evidence: readEvidence(),
      immediateDanger: immediateDanger.checked,
      lifeSupport: lifeSupport.checked
    };
  }

  function updateProgress() {
    const criticalDone = selectedValues("critical_load").length > 0 ? 1 : 0;
    const backupDone = selectedValues("backup_source").length > 0 ? 1 : 0;
    const evidenceDone = Object.keys(readEvidence()).length;
    const completed = criticalDone + backupDone + evidenceDone;
    const total = core.EVIDENCE_FIELDS.length + 2;
    const percent = Math.round((completed / total) * 100);
    progressBar.style.width = `${percent}%`;
    progressBar.parentElement.setAttribute("aria-valuenow", String(percent));
    progressText.textContent = `${completed} / ${total} alan tamamlandı`;
    if (!startedTracked && completed > 0) {
      startedTracked = true;
      track("continuity_passport_started", {
        facility_type: facilityType.value,
        maturity_imported: Boolean(importedMaturity)
      });
    }
  }

  function showValidation(message, target) {
    validation.textContent = message || "";
    validation.hidden = !message;
    if (!message) return;
    validation.focus();
    if (target) target.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  function normalizeBackupNone() {
    const boxes = [...form.querySelectorAll('input[name="backup_source"]')];
    const none = boxes.find((item) => item.value === "none");
    if (!none) return;
    if (none.checked) boxes.filter((item) => item !== none).forEach((item) => { item.checked = false; });
    else if (boxes.some((item) => item.value !== "none" && item.checked)) none.checked = false;
  }

  function saveIfAllowed() {
    if (!storageOptIn.checked) {
      try { localStorage.removeItem(STORAGE_KEY); } catch (_error) {}
      return;
    }
    try {
      const payload = core.sanitizeStorage(readInput());
      localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
      restoreBtn.hidden = false;
      track("continuity_passport_storage_enabled", { ttl_days: 30 });
    } catch (_error) {
      showValidation("Tarayıcı yerel saklamaya izin vermedi. Pasaport yine de hesaplanabilir ve indirilebilir.");
    }
  }

  function storedPayload() {
    try {
      const payload = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
      if (!core.isStoredPayloadFresh(payload)) {
        localStorage.removeItem(STORAGE_KEY);
        return null;
      }
      return payload;
    } catch (_error) {
      return null;
    }
  }

  function applyChecks(name, values) {
    const selected = new Set(values || []);
    form.querySelectorAll(`input[name="${name}"]`).forEach((item) => { item.checked = selected.has(item.value); });
  }

  function restoreDraft() {
    const payload = storedPayload();
    if (!payload) {
      showValidation("Geçerli 30 günlük yerel kayıt bulunamadı.");
      return;
    }
    facilityType.value = payload.facilityType;
    applyChecks("critical_load", payload.criticalLoads);
    applyChecks("backup_source", payload.backupSources);
    Object.entries(payload.evidence || {}).forEach(([id, value]) => {
      const input = form.querySelector(`input[name="evidence_${id}"][value="${value}"]`);
      if (input) input.checked = true;
    });
    storageOptIn.checked = true;
    immediateDanger.checked = false;
    lifeSupport.checked = false;
    updateProgress();
    showValidation("Kapalı uçlu teknik seçimler yüklendi. Acil tehlike ve yaşam destek seçimi güvenlik nedeniyle kaydedilmedi.");
    track("continuity_passport_restored", { facility_type: facilityType.value });
  }

  function maturityHandoff() {
    try {
      const payload = JSON.parse(localStorage.getItem(MATURITY_HANDOFF_KEY) || "null");
      if (!payload || !payload.expiresAt || new Date(payload.expiresAt).getTime() <= Date.now()) return null;
      return core.sanitizeMaturityHandoff(payload);
    } catch (_error) {
      return null;
    }
  }

  function importMaturity() {
    const payload = maturityHandoff();
    if (!payload) {
      maturityImportState.textContent = "Geçerli olgunluk handoff kaydı bulunamadı. Önce olgunluk skorunu oluşturup panel aktarımına dokunun.";
      track("continuity_passport_maturity_import_failed", { reason: "not_found_or_expired" });
      return;
    }
    importedMaturity = payload;
    facilityType.value = payload.facilityType;
    maturityImportState.textContent = `İçe aktarıldı: ${payload.score}/100 · ${payload.band || "olgunluk sonucu"}. Kişisel veri içermez.`;
    updateProgress();
    track("continuity_passport_maturity_imported", {
      facility_type: payload.facilityType,
      score_bucket: Math.floor(payload.score / 10) * 10
    });
  }

  function formatDate(value) {
    try {
      return new Intl.DateTimeFormat("tr-TR", { day: "2-digit", month: "long", year: "numeric" }).format(new Date(value));
    } catch (_error) {
      return String(value || "—");
    }
  }

  function renderPriorityList(target, items) {
    target.replaceChildren();
    if (!items.length) {
      const li = document.createElement("li");
      li.textContent = "Bu öncelikte açık boşluk yok. Güncellik tarihlerini izleyin.";
      target.appendChild(li);
      return;
    }
    items.forEach((item) => {
      const li = document.createElement("li");
      li.innerHTML = `<strong>${item.title}</strong><span>${item.action}</span>`;
      target.appendChild(li);
    });
  }

  function renderResult(result) {
    scoreValue.textContent = `${result.score}/100`;
    bandValue.textContent = result.classification.label;
    bandValue.className = `status ${result.classification.tone}`;
    scoreSummary.textContent = result.classification.summary;
    p0Value.textContent = String(result.priorities.P0.length);
    p1Value.textContent = String(result.priorities.P1.length);
    reviewValue.textContent = formatDate(result.nextReviewAt);
    maturityResult.textContent = importedMaturity
      ? `Olgunluk handoff karşılaştırması: ${importedMaturity.score}/100 · ${importedMaturity.band || "sonuç"}. Pasaport skoru yalnız kanıt setini ölçer.`
      : "Olgunluk skoru içe aktarılmadı; pasaport skoru yalnız kanıt setini ölçer.";

    evidenceMatrix.replaceChildren();
    core.EVIDENCE_FIELDS.forEach((field) => {
      const status = result.evidence[field.id];
      const article = document.createElement("article");
      article.className = `evidence-card ${status}`;
      article.innerHTML = `<div><strong>${field.title}</strong><span class="status ${status === "current" ? "good" : status === "due" ? "warn" : "danger"}">${core.STATUS_LABELS[status]}</span></div><small>Ağırlık ${field.weight}/100 · yenileme hedefi ${field.reviewDays} gün</small>`;
      evidenceMatrix.appendChild(article);
    });

    renderPriorityList(priorityP0, result.priorities.P0);
    renderPriorityList(priorityP1, result.priorities.P1);
    renderPriorityList(priorityP2, result.priorities.P2);

    professionalNotice.hidden = !result.professionalPlanRequired;
    if (lifeSupport.checked) {
      professionalNotice.innerHTML = "<strong>Profesyonel plan zorunlu.</strong> Tıbbi veya yaşam destek yükü için bu pasaport yeterli değildir; üretici onaylı, test edilmiş ve yetkili uzman tarafından doğrulanmış süreklilik planı kullanın. Bu seçim saklanmadı ve dışa aktarılmayacak.";
    } else if (result.professionalPlanRequired) {
      professionalNotice.innerHTML = "<strong>Profesyonel saha doğrulaması önerilir.</strong> Kritik yük–yedek kaynak ilişkisi veya temel kanıt skoru P0 seviyesinde boşluk içeriyor. Önce ölçüm, kapasite ve geçiş koşulunu doğrulayın.";
    }

    businessCta.hidden = !result.revenueAllowed;
    results.hidden = false;
    results.scrollIntoView({ behavior: "smooth", block: "start" });
    results.focus();
  }

  function evaluate(event) {
    event.preventDefault();
    emergencyNotice.hidden = true;
    const result = core.evaluatePassport(readInput());
    if (result.emergency) {
      lastResult = null;
      results.hidden = true;
      businessCta.hidden = true;
      emergencyNotice.hidden = false;
      emergencyNotice.focus();
      track("continuity_passport_emergency_route_shown", {});
      return;
    }
    if (!result.valid) {
      showValidation(result.errors.join(" "), result.errors[0] && selectedValues("critical_load").length === 0 ? criticalLoads : backupSources);
      return;
    }
    showValidation("");
    lastResult = result;
    saveIfAllowed();
    renderResult(result);
    track("continuity_passport_completed", {
      facility_type: result.facilityType,
      score_band: result.classification.id,
      score_bucket: Math.floor(result.score / 10) * 10,
      p0_count: result.priorities.P0.length,
      p1_count: result.priorities.P1.length,
      p2_count: result.priorities.P2.length,
      backup_present: !result.backupSources.includes("none"),
      panel_recommended: result.panelRecommended
    });
  }

  function exportPassport() {
    if (!lastResult) return;
    const payload = core.createExport(lastResult, { importedMaturity });
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `alo186-elektrik-surekliligi-pasaportu-${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    track("continuity_passport_exported", {
      facility_type: lastResult.facilityType,
      score_band: lastResult.classification.id,
      p0_count: lastResult.priorities.P0.length,
      maturity_imported: Boolean(importedMaturity)
    });
  }

  function createPanelHandoff() {
    if (!lastResult) return null;
    const generatedAt = new Date();
    return {
      version: 1,
      importId: `passport-${generatedAt.getTime()}-${lastResult.score}-${lastResult.facilityType}`,
      generatedAt: generatedAt.toISOString(),
      expiresAt: new Date(generatedAt.getTime() + HANDOFF_TTL_MS).toISOString(),
      facilityType: lastResult.facilityType,
      score: lastResult.score,
      band: lastResult.classification.label,
      criticalLoadCategories: [...lastResult.criticalLoads],
      backupSourceClasses: [...lastResult.backupSources],
      evidence: core.EVIDENCE_FIELDS.map((field) => ({ id: field.id, status: lastResult.evidence[field.id], weight: field.weight })),
      priorityGaps: lastResult.gaps.slice(0, 20).map((item) => ({ id: item.id, priority: item.priority, action: item.action })),
      nextReviewAt: lastResult.nextReviewAt,
      privacy: { containsPersonalData: false, lifeSupportFlagIncluded: false, immediateDangerFlagIncluded: false }
    };
  }

  function preparePanelHandoff() {
    const payload = createPanelHandoff();
    if (!payload) return;
    try {
      localStorage.setItem(PASSPORT_HANDOFF_KEY, JSON.stringify(payload));
      track("continuity_passport_panel_handoff_created", {
        facility_type: payload.facilityType,
        score_band: lastResult.classification.id,
        p0_count: lastResult.priorities.P0.length,
        gap_count: payload.priorityGaps.length,
        ttl_days: 7
      });
    } catch (_error) {
      track("continuity_passport_panel_handoff_failed", { reason: "local_storage_unavailable" });
    }
  }

  function clearAll() {
    form.reset();
    importedMaturity = null;
    lastResult = null;
    startedTracked = false;
    results.hidden = true;
    emergencyNotice.hidden = true;
    validation.hidden = true;
    maturityImportState.textContent = "İçe aktarma bulunamadı veya seçilmedi.";
    try {
      localStorage.removeItem(STORAGE_KEY);
      localStorage.removeItem(PASSPORT_HANDOFF_KEY);
    } catch (_error) {}
    restoreBtn.hidden = true;
    updateProgress();
    track("continuity_passport_reset", {});
  }

  renderChoices(criticalLoads, core.CRITICAL_LOADS, "critical_load");
  renderChoices(backupSources, core.BACKUP_SOURCES, "backup_source");
  renderEvidence();
  restoreBtn.hidden = !storedPayload();
  updateProgress();

  form.addEventListener("change", (event) => {
    if (event.target && event.target.name === "backup_source") normalizeBackupNone();
    updateProgress();
  });
  form.addEventListener("submit", evaluate);
  restoreBtn.addEventListener("click", restoreDraft);
  resetBtn.addEventListener("click", clearAll);
  importMaturityBtn.addEventListener("click", importMaturity);
  exportBtn.addEventListener("click", exportPassport);
  printBtn.addEventListener("click", () => {
    if (!lastResult) return;
    track("continuity_passport_printed", { facility_type: lastResult.facilityType, score_band: lastResult.classification.id });
    window.print();
  });
  panelLink.addEventListener("click", preparePanelHandoff);
})();
