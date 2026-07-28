(() => {
  "use strict";

  const core = window.AloContinuityPassport;
  if (!core) return;

  const STORAGE_KEY = "alo186.continuityPassport.v1";
  const HANDOFF_KEY = "alo186.continuityPassportHandoff.v1";
  const HANDOFF_TTL_MS = 7 * 24 * 60 * 60 * 1000;
  const form = document.getElementById("passportForm");
  const facilityType = document.getElementById("facilityType");
  const immediateDanger = document.getElementById("immediateDanger");
  const lifeSupportPresent = document.getElementById("lifeSupportPresent");
  const criticalLoads = document.getElementById("criticalLoads");
  const backupSources = document.getElementById("backupSources");
  const evidenceList = document.getElementById("evidenceList");
  const maturityFile = document.getElementById("maturityFile");
  const importStatus = document.getElementById("importStatus");
  const storageOptIn = document.getElementById("storageOptIn");
  const restoreBtn = document.getElementById("restoreBtn");
  const clearBtn = document.getElementById("clearBtn");
  const validation = document.getElementById("validation");
  const emergencyNotice = document.getElementById("emergencyNotice");
  const results = document.getElementById("results");
  const scoreValue = document.getElementById("scoreValue");
  const bandValue = document.getElementById("bandValue");
  const scoreSummary = document.getElementById("scoreSummary");
  const p0Count = document.getElementById("p0Count");
  const gapCount = document.getElementById("gapCount");
  const reviewDate = document.getElementById("reviewDate");
  const maturityReferenceResult = document.getElementById("maturityReferenceResult");
  const professionalNotice = document.getElementById("professionalNotice");
  const evidenceResults = document.getElementById("evidenceResults");
  const gapP0 = document.getElementById("gapP0");
  const gapP1 = document.getElementById("gapP1");
  const gapP2 = document.getElementById("gapP2");
  const managerTitle = document.getElementById("managerTitle");
  const managerSummary = document.getElementById("managerSummary");
  const exportBtn = document.getElementById("exportBtn");
  const printBtn = document.getElementById("printBtn");
  const handoffBtn = document.getElementById("handoffBtn");
  const panelLink = document.getElementById("panelLink");
  const businessCta = document.getElementById("businessCta");

  let lastResult = null;
  let maturityReference = null;

  function track(event, params) {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ event, ...(params || {}) });
  }

  function renderChoice(container, name, item) {
    const label = document.createElement("label");
    label.className = "choice-card";
    label.innerHTML = `<input type="checkbox" name="${name}" value="${item.id}"><span>${item.label}</span>`;
    container.appendChild(label);
  }

  function renderInputs() {
    core.CRITICAL_LOAD_CATEGORIES.forEach((item) => renderChoice(criticalLoads, "criticalLoad", item));
    core.BACKUP_SOURCE_CLASSES.forEach((item) => renderChoice(backupSources, "backupSource", item));
    core.EVIDENCE.forEach((item) => {
      const row = document.createElement("div");
      row.className = "evidence-row";
      row.dataset.evidence = item.id;
      row.innerHTML = `<div class="evidence-copy"><strong><span class="priority-tag ${item.priority}">${item.priority}</span>${item.label}</strong><p>${item.description}</p></div><label><span class="sr-only">${item.label} durumu</span><select name="evidence-${item.id}" aria-label="${item.label} durumu"><option value="current">Güncel ve doğrulanabilir</option><option value="due">Var, yenileme zamanı</option><option value="planned">Planlandı, kanıt oluşmadı</option><option value="missing" selected>Yok veya bilinmiyor</option></select></label>`;
      evidenceList.appendChild(row);
    });
  }

  function selectedValues(name) {
    return Array.from(form.querySelectorAll(`input[name="${name}"]:checked`)).map((input) => input.value);
  }

  function readEvidenceStatuses() {
    const statuses = {};
    core.EVIDENCE.forEach((item) => {
      const select = form.elements[`evidence-${item.id}`];
      statuses[item.id] = select ? select.value : "missing";
    });
    return statuses;
  }

  function readInput() {
    return {
      facilityType: facilityType.value,
      criticalLoadCategories: selectedValues("criticalLoad"),
      backupSourceClasses: selectedValues("backupSource"),
      evidenceStatuses: readEvidenceStatuses(),
      immediateDanger: immediateDanger.checked,
      lifeSupportPresent: lifeSupportPresent.checked,
      maturityReference
    };
  }

  function setChecked(name, values) {
    const selected = new Set(Array.isArray(values) ? values : []);
    form.querySelectorAll(`input[name="${name}"]`).forEach((input) => { input.checked = selected.has(input.value); });
  }

  function showValidation(message) {
    validation.textContent = message || "";
    validation.hidden = !message;
    if (message) validation.focus();
  }

  function savedPayload() {
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

  function saveDraft() {
    if (!storageOptIn.checked) {
      try { localStorage.removeItem(STORAGE_KEY); } catch (_error) { /* localStorage isteğe bağlı */ }
      return;
    }
    try {
      const payload = core.sanitizeStorage(readInput());
      localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
      restoreBtn.hidden = false;
      track("continuity_passport_storage_opted_in", { ttl_days: 30, facility_type: payload.facilityType });
    } catch (_error) {
      showValidation("Bu tarayıcı yerel kayda izin vermedi. Pasaport yine çalışır; JSON indirerek saklayabilirsiniz.");
    }
  }

  function restoreDraft() {
    const payload = savedPayload();
    if (!payload) return;
    facilityType.value = payload.facilityType;
    setChecked("criticalLoad", payload.criticalLoadCategories);
    setChecked("backupSource", payload.backupSourceClasses);
    core.EVIDENCE.forEach((item) => {
      const select = form.elements[`evidence-${item.id}`];
      if (select) select.value = payload.evidenceStatuses[item.id] || "missing";
    });
    maturityReference = payload.maturityReference || null;
    immediateDanger.checked = false;
    lifeSupportPresent.checked = false;
    storageOptIn.checked = true;
    importStatus.className = maturityReference ? "info success" : "info";
    importStatus.textContent = maturityReference ? `Olgunluk referansı yüklendi: ${maturityReference.score}/100 ${maturityReference.band || ""}` : "Kayıtlı teknik seçimler yüklendi.";
    showValidation("Son pasaport taslağı yüklendi. Acil tehlike ve yaşam destek seçimleri güvenlik nedeniyle saklanmadı.");
    track("continuity_passport_draft_restored", { facility_type: payload.facilityType });
  }

  function clearAll() {
    form.reset();
    core.EVIDENCE.forEach((item) => {
      const select = form.elements[`evidence-${item.id}`];
      if (select) select.value = "missing";
    });
    try {
      localStorage.removeItem(STORAGE_KEY);
      localStorage.removeItem(HANDOFF_KEY);
    } catch (_error) { /* araç depolama olmadan çalışır */ }
    maturityReference = null;
    lastResult = null;
    results.hidden = true;
    emergencyNotice.hidden = true;
    restoreBtn.hidden = true;
    importStatus.className = "info";
    importStatus.textContent = "İçe aktarma isteğe bağlıdır.";
    maturityFile.value = "";
    showValidation("");
    track("continuity_passport_reset", {});
  }

  function gapList(target, items) {
    target.replaceChildren();
    if (!items.length) {
      const li = document.createElement("li");
      li.textContent = "Bu öncelikte açık boşluk yok.";
      target.appendChild(li);
      return;
    }
    items.forEach((item) => {
      const li = document.createElement("li");
      li.innerHTML = `<strong>${item.label}</strong><br>${item.action}<br><small>Hedef: ${item.targetDate}</small>`;
      target.appendChild(li);
    });
  }

  function statusLabel(status) {
    return { current: "Güncel", due: "Yenileme zamanı", planned: "Planlandı", missing: "Yok" }[status] || status;
  }

  function renderResult(result) {
    scoreValue.textContent = `${result.score}/100`;
    bandValue.textContent = result.classification.label;
    bandValue.className = `status ${result.classification.tone}`;
    scoreSummary.textContent = result.classification.summary;
    p0Count.textContent = String(result.gaps.P0.length);
    gapCount.textContent = String(result.totalGapCount);
    reviewDate.textContent = result.nextReviewDate;

    if (maturityReference) {
      maturityReferenceResult.hidden = false;
      maturityReferenceResult.querySelector("span").textContent = `${maturityReference.score}/100 ${maturityReference.band || ""}`;
    } else maturityReferenceResult.hidden = true;

    evidenceResults.replaceChildren();
    result.evidence.forEach((item) => {
      const card = document.createElement("article");
      card.className = "evidence-result";
      card.innerHTML = `<header><h3><span class="priority-tag ${item.priority}">${item.priority}</span>${item.label}</h3><span class="evidence-status ${item.status}">${statusLabel(item.status)}</span></header><p>${item.description}</p><p><strong>Sonraki kontrol:</strong> ${item.nextReviewDate}</p>`;
      evidenceResults.appendChild(card);
    });

    gapList(gapP0, result.gaps.P0);
    gapList(gapP1, result.gaps.P1);
    gapList(gapP2, result.gaps.P2);

    professionalNotice.hidden = !result.professionalReviewRequired;
    if (result.lifeSupportPresentAtRuntime) {
      professionalNotice.innerHTML = "<strong>Yaşam destek yükü için profesyonel plan zorunlu.</strong> Bu pasaport tek başına yeterli değildir. Üretici onaylı, test edilmiş, alternatif kaynak ve alarm zinciri içeren profesyonel süreklilik planı oluşturun. Bu hassas seçim JSON ve yerel kayda eklenmedi.";
    } else if (result.gaps.P0.length) {
      professionalNotice.innerHTML = "<strong>P0 teknik boşluk var.</strong> Kritik yük, kapasite, yedek kaynak veya gerçek çalışma testi alanlarından en az biri yetersiz. Sabit tesisat ve yedek güç kararlarını yetkili uzmanla sahada doğrulayın.";
    } else {
      professionalNotice.innerHTML = "<strong>Profesyonel gözden geçirme önerilir.</strong> Kanıt skoru henüz güçlü bantta değil; ölçüm, test ve saha kayıtlarını yetkili uzmanla doğrulayın.";
    }

    const typeLabels = { hotel: "otel/konaklama", site: "site/apartman", business: "işletme", other: "teknik tesis" };
    managerTitle.textContent = `${typeLabels[result.facilityType] || "tesis"} elektrik sürekliliği yönetici özeti`;
    managerSummary.textContent = `Pasaport skoru ${result.score}/100 ve kanıt seviyesi “${result.classification.label}” olarak hesaplandı. ${result.gaps.P0.length} P0, ${result.gaps.P1.length} P1 ve ${result.gaps.P2.length} P2 aksiyon bulunuyor. En yakın gözden geçirme tarihi ${result.nextReviewDate}. Sonuç sertifika değildir; yönetim kararı gerçek test, ölçüm ve saha kanıtıyla doğrulanmalıdır.`;

    businessCta.hidden = !result.revenueAllowed;
    results.hidden = false;
    results.scrollIntoView({ behavior: "smooth", block: "start" });
    results.focus();
  }

  function evaluate(event) {
    event.preventDefault();
    emergencyNotice.hidden = true;
    const input = readInput();
    const result = core.evaluatePassport(input);
    if (result.emergency) {
      lastResult = null;
      results.hidden = true;
      businessCta.hidden = true;
      emergencyNotice.hidden = false;
      emergencyNotice.focus();
      track("continuity_passport_emergency_route_shown", { revenue_allowed: false });
      return;
    }
    lastResult = result;
    showValidation("");
    saveDraft();
    renderResult(result);
    track("continuity_passport_completed", {
      facility_type: result.facilityType,
      score_band: result.classification.id,
      score_bucket: Math.floor(result.score / 10) * 10,
      p0_count: result.gaps.P0.length,
      p1_count: result.gaps.P1.length,
      p2_count: result.gaps.P2.length,
      maturity_reference_present: Boolean(maturityReference),
      life_support_runtime: result.lifeSupportPresentAtRuntime
    });
  }

  function downloadJson(payload, filename) {
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  function exportPassport() {
    if (!lastResult) return;
    const payload = core.createPassportExport(lastResult, { maturityReference });
    downloadJson(payload, `alo186-elektrik-surekliligi-pasaportu-${new Date().toISOString().slice(0, 10)}.json`);
    track("continuity_passport_exported", { score_band: lastResult.classification.id, action_count: payload.handoff.actions.length, contains_personal_data: false });
  }

  function createHandoff() {
    if (!lastResult) return;
    const passport = core.createPassportExport(lastResult, { maturityReference });
    const createdAt = new Date();
    const handoff = {
      version: 1,
      importId: `passport-${createdAt.getTime()}-${lastResult.score}`,
      generatedAt: createdAt.toISOString(),
      expiresAt: new Date(createdAt.getTime() + HANDOFF_TTL_MS).toISOString(),
      source: "alo186-electric-continuity-passport",
      facilityType: passport.facilityType,
      score: passport.score,
      band: passport.maturityBandLabel,
      criticalLoadCategories: passport.criticalLoadCategories,
      backupSourceClasses: passport.backupSourceClasses,
      evidence: passport.evidence,
      actions: passport.handoff.actions,
      privacy: passport.privacy
    };
    try {
      localStorage.setItem(HANDOFF_KEY, JSON.stringify(handoff));
      handoffBtn.textContent = "Panel handoff’u hazırlandı";
      panelLink.href = "https://www.alo186.com/isletme-surekliligi?passport=1&handoff=1";
      track("continuity_passport_handoff_created", { action_count: handoff.actions.length, ttl_days: 7, contains_personal_data: false });
    } catch (_error) {
      downloadJson(handoff, `alo186-panel-handoff-${new Date().toISOString().slice(0, 10)}.json`);
      showValidation("Yerel handoff kaydı oluşturulamadı; bunun yerine handoff JSON dosyası indirildi.");
    }
  }

  function importMaturity(file) {
    if (!file) return;
    if (file.size > 1024 * 1024) {
      importStatus.className = "info error";
      importStatus.textContent = "JSON dosyası 1 MB sınırını aşıyor.";
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const payload = JSON.parse(String(reader.result || ""));
        const parsed = core.parseMaturityImport(payload);
        if (!parsed.valid) throw new Error(parsed.reason);
        facilityType.value = parsed.facilityType;
        maturityReference = parsed.maturityReference;
        importStatus.className = "info success";
        importStatus.textContent = `Olgunluk referansı bağlandı: ${maturityReference.score}/100 ${maturityReference.band || ""}. Kanıt statülerini gerçek belgelerle seçin.`;
        track("continuity_passport_maturity_imported", { source_type: parsed.sourceType, score_bucket: Math.floor(maturityReference.score / 10) * 10, contains_personal_data: false });
      } catch (_error) {
        maturityReference = null;
        importStatus.className = "info error";
        importStatus.textContent = "Dosya desteklenen ALO186 olgunluk özeti/handoff biçiminde değil veya kişisel veri içerdiği işaretlenmiş.";
      }
    };
    reader.onerror = () => {
      importStatus.className = "info error";
      importStatus.textContent = "JSON dosyası okunamadı.";
    };
    reader.readAsText(file);
  }

  renderInputs();
  restoreBtn.hidden = !savedPayload();
  track("continuity_passport_started", { local_storage_default_enabled: false, evidence_count: core.EVIDENCE.length });
  form.addEventListener("submit", evaluate);
  restoreBtn.addEventListener("click", restoreDraft);
  clearBtn.addEventListener("click", clearAll);
  maturityFile.addEventListener("change", () => importMaturity(maturityFile.files && maturityFile.files[0]));
  exportBtn.addEventListener("click", exportPassport);
  printBtn.addEventListener("click", () => { if (lastResult) { track("continuity_passport_printed", { score_band: lastResult.classification.id }); window.print(); } });
  handoffBtn.addEventListener("click", createHandoff);
  panelLink.addEventListener("click", () => track("continuity_passport_panel_clicked", { score_band: lastResult ? lastResult.classification.id : "unknown", handoff_ready: panelLink.href.includes("handoff=1") }));
})();
