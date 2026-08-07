(function () {
  "use strict";

  const core = window.AloOutageDrill;
  if (!core) return;

  const form = document.getElementById("drillForm");
  const scenarioSelect = document.getElementById("scenarioId");
  const criticalLoads = document.getElementById("criticalLoads");
  const backupSources = document.getElementById("backupSources");
  const taskList = document.getElementById("taskList");
  const validation = document.getElementById("validation");
  const emergency = document.getElementById("emergencyNotice");
  const results = document.getElementById("results");
  const statusSummary = document.getElementById("statusSummary");
  const scoreValue = document.getElementById("scoreValue");
  const bandValue = document.getElementById("bandValue");
  const scoreSummary = document.getElementById("scoreSummary");
  const p0Value = document.getElementById("p0Value");
  const p1Value = document.getElementById("p1Value");
  const nextDrillValue = document.getElementById("nextDrillValue");
  const managerSummary = document.getElementById("managerSummary");
  const timeline = document.getElementById("timeline");
  const gapList = document.getElementById("gapList");
  const passportSuggestions = document.getElementById("passportSuggestions");
  const exportBtn = document.getElementById("exportBtn");
  const printBtn = document.getElementById("printBtn");
  const panelBtn = document.getElementById("panelBtn");
  const resetBtn = document.getElementById("resetBtn");
  let latestResult = null;

  function emit(name, params) {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ event: name, ...(params || {}) });
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char]));
  }

  function renderChoices(target, catalogue, name) {
    target.innerHTML = catalogue.map((item) => `
      <label class="choice-card"><input type="checkbox" name="${name}" value="${item.id}"><span>${escapeHtml(item.label)}</span></label>
    `).join("");
  }

  function enforceExclusiveNone(target, name) {
    target.addEventListener("change", (event) => {
      const changed = event.target;
      if (!(changed instanceof HTMLInputElement) || changed.name !== name || !changed.checked) return;
      const options = [...target.querySelectorAll(`input[name="${name}"]`)];
      if (changed.value === "none") options.forEach((item) => { if (item !== changed) item.checked = false; });
      else options.forEach((item) => { if (item.value === "none") item.checked = false; });
    });
  }

  function renderTasks() {
    const tasks = core.activeTasks(scenarioSelect.value);
    taskList.innerHTML = ["5", "15", "60"].map((windowValue) => {
      const group = tasks.filter((task) => task.window === windowValue);
      return `<section class="time-window"><header><span>İlk ${windowValue} dakika</span><strong>${group.length} görev</strong></header>${group.map((task) => `
        <label class="task-row">
          <span><strong>${escapeHtml(task.title)}</strong><small>${escapeHtml(task.action)}</small></span>
          <select name="task-${task.id}" aria-label="${escapeHtml(task.title)} durumu">
            <option value="missing">Eksik</option>
            <option value="partial">Kısmen hazır</option>
            <option value="ready">Hazır</option>
          </select>
        </label>
      `).join("")}</section>`;
    }).join("");
  }

  function selected(name) {
    return [...form.querySelectorAll(`input[name="${name}"]:checked`)].map((item) => item.value);
  }

  function collect() {
    const statuses = {};
    core.activeTasks(scenarioSelect.value).forEach((task) => {
      const field = form.elements[`task-${task.id}`];
      statuses[task.id] = field ? field.value : "missing";
    });
    return {
      facilityType: form.elements.facilityType.value,
      scenarioId: scenarioSelect.value,
      immediateDanger: form.elements.immediateDanger.checked,
      lifeSupport: form.elements.lifeSupport.checked,
      confirmTabletop: form.elements.confirmTabletop.checked,
      rolesAssigned: form.elements.rolesAssigned.checked,
      offlineContacts: form.elements.offlineContacts.checked,
      recordTemplate: form.elements.recordTemplate.checked,
      criticalLoads: selected("criticalLoad"),
      backupSources: selected("backupSource"),
      taskStatuses: statuses
    };
  }

  function showValidation(errors) {
    validation.hidden = false;
    validation.innerHTML = `<strong>Eksik alanlar</strong><ul>${errors.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
    validation.focus();
  }

  function hideValidation() {
    validation.hidden = true;
    validation.innerHTML = "";
  }

  function invalidateResult() {
    if (!latestResult && results.hidden) return;
    results.hidden = true;
    latestResult = null;
    panelBtn.textContent = "7 günlük panel aktarımını hazırla";
    delete panelBtn.dataset.handoffReady;
  }

  function formatDate(date) {
    return new Intl.DateTimeFormat("tr-TR", { day: "2-digit", month: "long", year: "numeric" }).format(date);
  }

  function renderResult(result) {
    latestResult = result;
    panelBtn.textContent = "7 günlük panel aktarımını hazırla";
    delete panelBtn.dataset.handoffReady;
    scoreValue.textContent = `${result.score}/100`;
    bandValue.textContent = result.classification.label;
    bandValue.className = `status ${result.classification.tone}`;
    scoreSummary.textContent = result.classification.summary;
    p0Value.textContent = String(result.p0Count);
    p1Value.textContent = String(result.p1Count);
    nextDrillValue.textContent = formatDate(result.nextDrillDate);
    managerSummary.textContent = result.managerSummary;
    statusSummary.textContent = `${result.scenario.label} · ${result.classification.label}`;

    timeline.innerHTML = result.timeline.map((group) => `
      <article class="timeline-card"><span class="time-badge">${group.window} dk</span><ul>${group.tasks.map((task) => `<li class="${task.status}"><strong>${escapeHtml(task.title)}</strong><span>${escapeHtml(task.statusLabel)}</span></li>`).join("")}</ul></article>
    `).join("");

    gapList.innerHTML = result.gaps.length ? result.gaps.map((gap) => `
      <article class="gap-card ${gap.priority.toLowerCase()}"><div><span>${gap.priority} · ${gap.window} dk</span><h3>${escapeHtml(gap.title)}</h3><p>${escapeHtml(gap.action)}</p></div><b>${escapeHtml(gap.statusLabel)}</b></article>
    `).join("") : `<div class="empty-state"><strong>Kritik boşluk görünmüyor.</strong><p>Tatbikatı kanıtla kapatın, sonuçları pasaporta ve panele aktarın.</p></div>`;

    const labels = {
      recovery_drill: "Kurtarma tatbikatı",
      emergency_contacts: "Acil iletişim ve görev listesi",
      outage_log: "Kesinti ve olay günlüğü",
      generator_ups_test: "Yedek kaynak test kaydı",
      transfer_test: "Transfer ve geri dönüş testi"
    };
    const stateLabels = { current: "Güncel önerisi", planned: "Planlandı önerisi", due: "Yenileme zamanı önerisi" };
    passportSuggestions.innerHTML = Object.entries(result.passportEvidenceSuggestions).map(([key, value]) => `<li><strong>${escapeHtml(labels[key] || key)}</strong><span>${escapeHtml(stateLabels[value] || value)}</span></li>`).join("");

    results.hidden = false;
    results.focus();
    emit("continuity_drill_completed", {
      scenario_id: result.scenario.id,
      facility_type: result.facilityType,
      score_band: result.classification.id,
      p0_count: result.p0Count,
      p1_count: result.p1Count
    });
  }

  function downloadJson() {
    if (!latestResult) return;
    const payload = core.exportPayload(latestResult);
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `alo186-elektrik-kesintisi-tatbikati-${new Date().toISOString().slice(0, 10)}.json`;
    anchor.click();
    URL.revokeObjectURL(url);
    emit("continuity_drill_exported", { format: "json", score_band: latestResult.classification.id });
  }

  function saveHandoff() {
    if (!latestResult) return;
    try {
      localStorage.setItem("alo186.continuity-drill-handoff.v1", JSON.stringify(latestResult.handoff));
      if (panelBtn.dataset.handoffReady === "true") {
        emit("continuity_drill_handoff_refreshed", { score_band: latestResult.classification.id, p0_count: latestResult.p0Count });
        window.location.href = "https://alo186.com/isletme-surekliligi";
        return;
      }
      panelBtn.dataset.handoffReady = "true";
      panelBtn.textContent = "Panele git ve bulguları içe aktar";
      emit("continuity_drill_handoff_saved", { score_band: latestResult.classification.id, p0_count: latestResult.p0Count });
    } catch (_error) {
      panelBtn.textContent = "Tarayıcı aktarımı kaydedemedi";
    }
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    hideValidation();
    const result = core.evaluate(collect());
    if (result.emergency) {
      results.hidden = true;
      latestResult = null;
      emergency.hidden = false;
      emergency.focus();
      emit("continuity_drill_emergency_stopped", { route: "112" });
      return;
    }
    emergency.hidden = true;
    if (!result.valid) {
      results.hidden = true;
      latestResult = null;
      showValidation(result.errors);
      return;
    }
    renderResult(result);
  });

  form.addEventListener("change", (event) => {
    if (event.target === scenarioSelect) renderTasks();
    invalidateResult();
  });

  exportBtn.addEventListener("click", downloadJson);
  printBtn.addEventListener("click", () => { if (latestResult) { emit("continuity_drill_exported", { format: "print", score_band: latestResult.classification.id }); window.print(); } });
  panelBtn.addEventListener("click", saveHandoff);
  resetBtn.addEventListener("click", () => {
    form.reset();
    renderTasks();
    hideValidation();
    emergency.hidden = true;
    results.hidden = true;
    latestResult = null;
    panelBtn.textContent = "7 günlük panel aktarımını hazırla";
    delete panelBtn.dataset.handoffReady;
    window.scrollTo({ top: 0, behavior: "smooth" });
  });

  renderChoices(criticalLoads, core.CRITICAL_LOADS, "criticalLoad");
  renderChoices(backupSources, core.BACKUP_SOURCES, "backupSource");
  enforceExclusiveNone(criticalLoads, "criticalLoad");
  enforceExclusiveNone(backupSources, "backupSource");
  renderTasks();
})();
