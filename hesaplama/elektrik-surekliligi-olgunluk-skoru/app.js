(() => {
  "use strict";

  const core = window.AloContinuityMaturity;
  if (!core) return;

  const STORAGE_KEY = "alo186.continuityMaturity.v1";
  const HANDOFF_KEY = "alo186.continuityMaturityHandoff.v1";
  const HANDOFF_TTL_MS = 7 * 24 * 60 * 60 * 1000;
  const form = document.getElementById("maturityForm");
  const questionnaire = document.getElementById("questionnaire");
  const validation = document.getElementById("validation");
  const results = document.getElementById("results");
  const scoreValue = document.getElementById("scoreValue");
  const bandValue = document.getElementById("bandValue");
  const criticalValue = document.getElementById("criticalValue");
  const weakestValue = document.getElementById("weakestValue");
  const scoreSummary = document.getElementById("scoreSummary");
  const dimensionList = document.getElementById("dimensionList");
  const plan30 = document.getElementById("plan30");
  const plan60 = document.getElementById("plan60");
  const plan90 = document.getElementById("plan90");
  const professionalNotice = document.getElementById("professionalNotice");
  const emergencyNotice = document.getElementById("emergencyNotice");
  const facilityType = document.getElementById("facilityType");
  const medical = document.getElementById("medical");
  const immediateDanger = document.getElementById("immediateDanger");
  const progressBar = document.getElementById("progressBar");
  const progressText = document.getElementById("progressText");
  const restoreBtn = document.getElementById("restoreBtn");
  const resetBtn = document.getElementById("resetBtn");
  const exportBtn = document.getElementById("exportBtn");
  const printBtn = document.getElementById("printBtn");
  const panelLink = document.getElementById("panelLink");

  let lastResult = null;

  function track(event, params) {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ event, ...(params || {}) });
  }

  function renderQuestions() {
    const fragment = document.createDocumentFragment();
    core.DIMENSIONS.forEach((dimension, dimensionIndex) => {
      const section = document.createElement("section");
      section.className = "dimension panel";
      section.dataset.dimension = dimension.id;
      const heading = document.createElement("div");
      heading.className = "section-title";
      heading.innerHTML = `<div><span class="step">${dimensionIndex + 1}</span><h2>${dimension.title}</h2></div>`;
      section.appendChild(heading);
      const questions = document.createElement("div");
      questions.className = "question-list";
      core.QUESTIONS.filter((item) => item.dimension === dimension.id).forEach((question, questionIndex) => {
        const fieldset = document.createElement("fieldset");
        fieldset.className = "question";
        fieldset.dataset.question = question.id;
        const legend = document.createElement("legend");
        legend.textContent = `${dimensionIndex + 1}.${questionIndex + 1} ${question.text}`;
        fieldset.appendChild(legend);
        const options = document.createElement("div");
        options.className = "answer-options";
        [["yes", "Evet", "Tam ve güncel"],["partial", "Kısmen", "Var, fakat eksik veya doğrulanmamış"],["no", "Hayır", "Yok veya bilinmiyor"]].forEach(([value, label, detail]) => {
          const option = document.createElement("label");
          option.className = "answer-option";
          option.innerHTML = `<input type="radio" name="${question.id}" value="${value}"><span><strong>${label}</strong><small>${detail}</small></span>`;
          options.appendChild(option);
        });
        fieldset.appendChild(options);
        questions.appendChild(fieldset);
      });
      section.appendChild(questions);
      fragment.appendChild(section);
    });
    questionnaire.replaceChildren(fragment);
  }

  function readAnswers() {
    const answers = {};
    core.QUESTIONS.forEach((question) => {
      const selected = form.querySelector(`input[name="${question.id}"]:checked`);
      if (selected) answers[question.id] = selected.value;
    });
    return answers;
  }

  function updateProgress() {
    const completed = Object.keys(readAnswers()).length;
    const percent = Math.round((completed / core.QUESTIONS.length) * 100);
    progressBar.style.width = `${percent}%`;
    progressBar.parentElement.setAttribute("aria-valuenow", String(percent));
    progressText.textContent = `${completed} / ${core.QUESTIONS.length} yanıtlandı`;
  }

  function showValidation(message, questionId) {
    validation.textContent = message;
    validation.hidden = !message;
    if (message) {
      validation.focus();
      if (questionId) {
        const target = questionnaire.querySelector(`[data-question="${questionId}"]`);
        if (target) target.scrollIntoView({ behavior: "smooth", block: "center" });
      }
    }
  }

  function saveDraft() {
    try {
      const payload = core.sanitizeStorage({ facilityType: facilityType.value, answers: readAnswers(), medical: medical.checked, immediateDanger: immediateDanger.checked });
      localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
      restoreBtn.hidden = false;
    } catch (_error) {
      // Araç localStorage olmadan da tam çalışır.
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

  function restoreDraft() {
    const payload = storedPayload();
    if (!payload) return;
    facilityType.value = payload.facilityType;
    Object.entries(payload.answers || {}).forEach(([id, value]) => {
      const input = form.querySelector(`input[name="${id}"][value="${value}"]`);
      if (input) input.checked = true;
    });
    medical.checked = false;
    immediateDanger.checked = false;
    updateProgress();
    showValidation("Son teknik yanıtlar yüklendi. Hassas yük ve acil tehlike seçimleri güvenlik nedeniyle kaydedilmedi.");
    track("continuity_maturity_draft_restored", { facility_type: facilityType.value });
  }

  function clearAll() {
    form.reset();
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(HANDOFF_KEY);
    lastResult = null;
    results.hidden = true;
    emergencyNotice.hidden = true;
    validation.hidden = true;
    restoreBtn.hidden = true;
    updateProgress();
    track("continuity_maturity_reset", {});
  }

  function planList(target, items) {
    target.replaceChildren();
    items.forEach((item) => {
      const li = document.createElement("li");
      const dimension = core.DIMENSIONS.find((entry) => entry.id === item.dimension);
      li.innerHTML = `<strong>${dimension ? dimension.short : "İyileştirme"}:</strong> ${item.action}`;
      target.appendChild(li);
    });
    if (!items.length) {
      const li = document.createElement("li");
      li.textContent = "Bu aşama için ek öncelik oluşmadı; önceki aksiyonların kapanışını doğrulayın.";
      target.appendChild(li);
    }
  }

  function renderResult(result) {
    scoreValue.textContent = `${result.score}/100`;
    bandValue.textContent = result.classification.label;
    bandValue.className = `status ${result.classification.tone}`;
    criticalValue.textContent = String(result.criticalGaps.length);
    weakestValue.textContent = result.weakestDimensions.map((item) => item.short).join(" · ");
    scoreSummary.textContent = result.classification.summary;
    dimensionList.replaceChildren();
    result.dimensions.forEach((dimension) => {
      const item = document.createElement("div");
      item.className = "dimension-score";
      item.innerHTML = `<div><strong>${dimension.title}</strong><span>${dimension.score}/100</span></div><div class="progress" role="progressbar" aria-label="${dimension.title}" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${dimension.score}"><i style="width:${dimension.score}%"></i></div>`;
      dimensionList.appendChild(item);
    });
    planList(plan30, result.plan.day30);
    planList(plan60, result.plan.day60);
    planList(plan90, result.plan.day90);
    professionalNotice.hidden = !(result.professionalReviewRecommended || medical.checked);
    if (medical.checked) professionalNotice.innerHTML = "<strong>Hassas yük doğrulaması gerekli.</strong> Tıbbi veya yaşam destek yükleri için bu skor yeterli değildir; üretici onaylı, test edilmiş ve profesyonel süreklilik planı kullanın. Bu seçim yerel kayda, panel aktarımına ve JSON özetine yazılmaz.";
    else if (result.professionalReviewRecommended) professionalNotice.innerHTML = "<strong>Profesyonel öncelik önerilir.</strong> Temel kritik boşluklardan biri düşük. Sabit tesisat, transfer, jeneratör, UPS ve koruma sistemlerinde yetkili uzmanla saha doğrulaması yapın.";
    panelLink.textContent = "90 günlük planı panelde takip et";
    panelLink.href = "https://alo186.com/isletme-surekliligi?maturity=1";
    results.hidden = false;
    results.scrollIntoView({ behavior: "smooth", block: "start" });
    results.focus();
  }

  function evaluate(event) {
    event.preventDefault();
    emergencyNotice.hidden = true;
    if (immediateDanger.checked) {
      results.hidden = true;
      emergencyNotice.hidden = false;
      emergencyNotice.focus();
      track("continuity_maturity_emergency_route_shown", {});
      return;
    }
    const answers = readAnswers();
    const result = core.evaluateAssessment(answers, { planLimit: 6 });
    if (!result.valid) {
      const firstMissing = result.validation.missing[0] || result.validation.invalid[0];
      showValidation(`Değerlendirmeyi tamamlamak için ${result.validation.missing.length} soruyu daha yanıtlayın.`, firstMissing);
      return;
    }
    showValidation("");
    lastResult = result;
    saveDraft();
    renderResult(result);
    track("continuity_maturity_assessment_completed", { facility_type: facilityType.value, score_band: result.classification.id, score_bucket: Math.floor(result.score / 10) * 10, critical_gap_count: result.criticalGaps.length, weakest_dimension: result.weakestDimensions[0] ? result.weakestDimensions[0].id : "none", panel_recommended: result.panelRecommended });
  }

  function exportResult() {
    if (!lastResult) return;
    const payload = core.createExport(lastResult, facilityType.value);
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `alo186-elektrik-surekliligi-ozeti-${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    track("continuity_maturity_exported", { facility_type: facilityType.value, score_band: lastResult.classification.id });
  }

  function createPanelHandoff(result) {
    const generatedAt = new Date();
    const safeFacility = ["hotel", "site", "business", "other"].includes(facilityType.value) ? facilityType.value : "other";
    const safePlan = {};
    ["day30", "day60", "day90"].forEach((phase) => {
      safePlan[phase] = (result.plan[phase] || []).slice(0, 9).map((item) => ({
        questionId: String(item.questionId || "").slice(0, 80),
        dimension: String(item.dimension || "").slice(0, 40),
        action: String(item.action || "").replace(/[<>]/g, "").replace(/\s+/g, " ").trim().slice(0, 240),
        priority: Math.max(0, Math.min(9, Number(item.priority) || 0))
      })).filter((item) => item.questionId && item.dimension && item.action);
    });
    return {
      version: 1,
      importId: `maturity-${generatedAt.getTime()}-${result.score}-${safeFacility}`,
      generatedAt: generatedAt.toISOString(),
      expiresAt: new Date(generatedAt.getTime() + HANDOFF_TTL_MS).toISOString(),
      facilityType: safeFacility,
      score: result.score,
      band: result.classification.label,
      dimensions: result.dimensions.map((item) => ({ id: item.id, title: item.title, score: item.score })),
      criticalGapIds: result.criticalGaps.slice(0, 5),
      plan: safePlan,
      privacy: { containsPersonalData: false, medicalOrLifeSupportFlagIncluded: false, immediateDangerFlagIncluded: false }
    };
  }

  function preparePanelHandoff() {
    if (!lastResult) return;
    const payload = createPanelHandoff(lastResult);
    try {
      localStorage.setItem(HANDOFF_KEY, JSON.stringify(payload));
      const actionCount = Object.values(payload.plan).reduce((sum, items) => sum + items.length, 0);
      track("continuity_maturity_handoff_created", { facility_type: payload.facilityType, score_band: lastResult.classification.id, score_bucket: Math.floor(payload.score / 10) * 10, action_count: actionCount, ttl_days: 7 });
    } catch (_error) {
      track("continuity_maturity_handoff_failed", { reason: "local_storage_unavailable" });
    }
  }

  renderQuestions();
  restoreBtn.hidden = !storedPayload();
  updateProgress();
  questionnaire.addEventListener("change", updateProgress);
  form.addEventListener("submit", evaluate);
  restoreBtn.addEventListener("click", restoreDraft);
  resetBtn.addEventListener("click", clearAll);
  exportBtn.addEventListener("click", exportResult);
  printBtn.addEventListener("click", () => { if (lastResult) { track("continuity_maturity_printed", { score_band: lastResult.classification.id }); window.print(); } });
  panelLink.addEventListener("click", () => {
    preparePanelHandoff();
    track("continuity_maturity_panel_opened", { facility_type: facilityType.value, score_band: lastResult ? lastResult.classification.id : "not_scored", handoff_available: Boolean(lastResult) });
  });
})();
