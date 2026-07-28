(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  root.ALO186BackupTCO = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const SOLUTION_LABELS = Object.freeze({
    ups: "UPS",
    powerStation: "Taşınabilir power station",
    inverterBattery: "İnverter + batarya sistemi",
    generator: "Jeneratör"
  });

  function finiteNumber(value, fallback) {
    if (value === null || value === undefined || value === "") return fallback;
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : fallback;
  }

  function clamp(value, min, max) {
    return Math.min(max, Math.max(min, value));
  }

  function normalizedReplacementInterval(value) {
    const interval = finiteNumber(value, 0);
    return interval > 0 ? clamp(interval, 0.5, 50) : 0;
  }

  function replacementCount(years, intervalYears) {
    const horizon = Math.max(0, finiteNumber(years, 0));
    const interval = normalizedReplacementInterval(intervalYears);
    if (interval <= 0 || horizon <= interval) return 0;
    return Math.floor((horizon - 0.000001) / interval);
  }

  function calculatePaybackYears({
    horizonYears,
    upfront,
    annualAvoidedImpact,
    annualRecurring,
    replacementYears,
    replacementCost
  }) {
    const horizon = Math.max(0, finiteNumber(horizonYears, 0));
    const initialCost = Math.max(0, finiteNumber(upfront, 0));
    const annualNetCashFlow = finiteNumber(annualAvoidedImpact, 0) - finiteNumber(annualRecurring, 0);
    const interval = normalizedReplacementInterval(replacementYears);
    const replacementOutlay = Math.max(0, finiteNumber(replacementCost, 0));

    if (horizon <= 0 || annualNetCashFlow <= 0) return null;
    if (initialCost <= 0) return 0;

    let elapsed = 0;
    let cumulative = -initialCost;

    if (interval > 0 && replacementOutlay > 0) {
      for (let eventTime = interval; eventTime < horizon - 1e-9; eventTime += interval) {
        const candidate = elapsed + (-cumulative / annualNetCashFlow);
        if (candidate >= elapsed && candidate < eventTime - 1e-9) return candidate;

        cumulative += annualNetCashFlow * (eventTime - elapsed);
        cumulative -= replacementOutlay;
        elapsed = eventTime;
        if (cumulative >= 0) return elapsed;
      }
    }

    const finalCandidate = elapsed + (-cumulative / annualNetCashFlow);
    return finalCandidate >= elapsed && finalCandidate <= horizon + 1e-9 ? finalCandidate : null;
  }

  function normalizeAssumptions(input) {
    const hasImpact = input.impactPerHour !== null && input.impactPerHour !== undefined && input.impactPerHour !== "";
    return {
      years: clamp(finiteNumber(input.years, 0), 1, 20),
      outagesPerYear: clamp(finiteNumber(input.outagesPerYear, 0), 0, 1000),
      hoursPerOutage: clamp(finiteNumber(input.hoursPerOutage, 0), 0, 720),
      impactPerHour: hasImpact ? clamp(finiteNumber(input.impactPerHour, 0), 0, 100000000) : null,
      continuousW: clamp(finiteNumber(input.continuousW, 0), 0, 1000000),
      scope: input.scope === "fixed" ? "fixed" : "plug",
      phase: ["single", "three", "unknown"].includes(input.phase) ? input.phase : "unknown",
      medical: Boolean(input.medical)
    };
  }

  function normalizeSolution(solution) {
    return {
      id: String(solution.id || ""),
      enabled: Boolean(solution.enabled),
      purchase: clamp(finiteNumber(solution.purchase, 0), 0, 1000000000),
      installation: clamp(finiteNumber(solution.installation, 0), 0, 1000000000),
      annualMaintenance: clamp(finiteNumber(solution.annualMaintenance, 0), 0, 1000000000),
      annualOperating: clamp(finiteNumber(solution.annualOperating, 0), 0, 1000000000),
      replacementYears: normalizedReplacementInterval(solution.replacementYears),
      replacementCost: clamp(finiteNumber(solution.replacementCost, 0), 0, 1000000000),
      coveragePercent: clamp(finiteNumber(solution.coveragePercent, 0), 0, 100)
    };
  }

  function calculateSolution(assumptions, rawSolution) {
    const solution = normalizeSolution(rawSolution);
    const annualOutageHours = assumptions.outagesPerYear * assumptions.hoursPerOutage;
    const annualGrossImpact = annualOutageHours * assumptions.impactPerHour;
    const annualAvoidedImpact = annualGrossImpact * (solution.coveragePercent / 100);
    const replacements = replacementCount(assumptions.years, solution.replacementYears);
    const upfront = solution.purchase + solution.installation;
    const annualRecurring = solution.annualMaintenance + solution.annualOperating;
    const tco = upfront + (annualRecurring * assumptions.years) + (replacements * solution.replacementCost);
    const avoidedImpact = annualAvoidedImpact * assumptions.years;
    const netBenefit = avoidedImpact - tco;
    const paybackYears = calculatePaybackYears({
      horizonYears: assumptions.years,
      upfront,
      annualAvoidedImpact,
      annualRecurring,
      replacementYears: solution.replacementYears,
      replacementCost: solution.replacementCost
    });
    const protectedHours = annualOutageHours * assumptions.years * (solution.coveragePercent / 100);
    const costPerProtectedHour = protectedHours > 0 ? tco / protectedHours : null;

    return {
      ...solution,
      label: SOLUTION_LABELS[solution.id] || solution.id,
      annualOutageHours,
      annualGrossImpact,
      annualAvoidedImpact,
      replacements,
      upfront,
      annualRecurring,
      tco,
      avoidedImpact,
      netBenefit,
      paybackYears,
      protectedHours,
      costPerProtectedHour
    };
  }

  function affiliateEligibility(assumptions, result) {
    const portableType = result.id === "ups" || result.id === "powerStation";
    const technicalLowRisk = assumptions.scope === "plug" && assumptions.phase === "single" && assumptions.continuousW > 0 && assumptions.continuousW <= 1200;
    return portableType && technicalLowRisk && !assumptions.medical && result.netBenefit > 0;
  }

  function compare(rawAssumptions, rawSolutions) {
    const assumptions = normalizeAssumptions(rawAssumptions || {});
    const enabledSolutions = (rawSolutions || []).map(normalizeSolution).filter((item) => item.enabled);
    const errors = [];

    if (enabledSolutions.length < 2) errors.push("Karşılaştırma için en az iki çözüm seçin.");
    if (assumptions.years < 1) errors.push("Analiz süresi en az bir yıl olmalıdır.");
    if (assumptions.continuousW <= 0) errors.push("Sürekli yük gücünü girin.");
    if (assumptions.outagesPerYear <= 0 || assumptions.hoursPerOutage <= 0) errors.push("Kesinti sıklığı ve süresi sıfırdan büyük olmalıdır.");
    if (assumptions.impactPerHour === null) errors.push("Kesintinin saatlik tahmini etkisini girin; etkiniz yoksa 0 yazın.");

    enabledSolutions.forEach((solution) => {
      const hasCurrentCostBasis = solution.purchase + solution.installation + solution.annualMaintenance + solution.annualOperating > 0;
      if (!hasCurrentCostBasis) errors.push(`${SOLUTION_LABELS[solution.id] || solution.id} için satın alma, kurulum veya dönem içi işletme maliyetinizden en az birini girin.`);
      if (solution.coveragePercent <= 0) errors.push(`${SOLUTION_LABELS[solution.id] || solution.id} için karşılama oranını girin.`);
      if (solution.replacementCost > 0 && solution.replacementYears <= 0) errors.push(`${SOLUTION_LABELS[solution.id] || solution.id} yenileme bedeli girildiyse yenileme aralığını da girin.`);
    });

    if (errors.length) return { ok: false, errors, assumptions, results: [] };

    const results = enabledSolutions
      .map((solution) => calculateSolution(assumptions, solution))
      .sort((a, b) => (b.netBenefit - a.netBenefit) || (a.tco - b.tco));

    const best = results[0] || null;
    const noBuy = !best || best.netBenefit <= 0;
    const professional = assumptions.medical || assumptions.scope === "fixed" || assumptions.phase !== "single" || assumptions.continuousW > 1200 || (best && ["generator", "inverterBattery"].includes(best.id));

    return {
      ok: true,
      errors: [],
      assumptions,
      annualOutageHours: assumptions.outagesPerYear * assumptions.hoursPerOutage,
      annualGrossImpact: assumptions.outagesPerYear * assumptions.hoursPerOutage * assumptions.impactPerHour,
      results,
      best,
      noBuy,
      professional,
      affiliateEligible: best ? affiliateEligibility(assumptions, best) : false
    };
  }

  function sanitizeForStorage(rawAssumptions, rawSolutions, savedAt) {
    const assumptions = normalizeAssumptions(rawAssumptions || {});
    delete assumptions.medical;
    return {
      version: 1,
      savedAt: savedAt || new Date().toISOString(),
      assumptions,
      solutions: (rawSolutions || []).map(normalizeSolution)
    };
  }

  return {
    SOLUTION_LABELS,
    normalizedReplacementInterval,
    replacementCount,
    calculatePaybackYears,
    normalizeAssumptions,
    normalizeSolution,
    calculateSolution,
    affiliateEligibility,
    compare,
    sanitizeForStorage
  };
});