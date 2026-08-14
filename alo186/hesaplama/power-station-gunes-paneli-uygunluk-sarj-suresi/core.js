(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.PowerStationSolarCore = api;
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  const round = (value, digits = 2) => {
    const factor = 10 ** digits;
    return Math.round((Number(value) + Number.EPSILON) * factor) / factor;
  };
  const num = (value) => {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : NaN;
  };
  const bool = (value) => value === true;

  function calculate(input) {
    const stationMinV = num(input.stationMinV);
    const stationMaxV = num(input.stationMaxV);
    const stationMaxCurrentA = num(input.stationMaxCurrentA);
    const stationMaxIscA = input.stationMaxIscA === '' || input.stationMaxIscA == null ? NaN : num(input.stationMaxIscA);
    const stationMaxPowerW = num(input.stationMaxPowerW);
    const batteryWh = num(input.batteryWh);
    const currentSoc = num(input.currentSoc);
    const targetSoc = num(input.targetSoc);
    const solarPlanningPct = num(input.solarPlanningPct);

    const panelPmaxW = num(input.panelPmaxW);
    const panelVocV = num(input.panelVocV);
    const panelVmpV = num(input.panelVmpV);
    const panelIscA = num(input.panelIscA);
    const panelImpA = num(input.panelImpA);
    const tempCoeffVocPct = num(input.tempCoeffVocPct);
    const minTempC = num(input.minTempC);
    const seriesCount = Math.max(1, Math.trunc(num(input.seriesCount)) || 1);
    const parallelCount = Math.max(1, Math.trunc(num(input.parallelCount)) || 1);

    const coldDeltaC = Math.max(0, 25 - minTempC);
    const coldVocMultiplier = 1 + (Math.abs(tempCoeffVocPct) / 100) * coldDeltaC;
    const panelColdVocV = panelVocV * coldVocMultiplier;
    const arrayVocStcV = panelVocV * seriesCount;
    const arrayColdVocV = panelColdVocV * seriesCount;
    const arrayVmpV = panelVmpV * seriesCount;
    const arrayIscA = panelIscA * parallelCount;
    const arrayImpA = panelImpA * parallelCount;
    const arrayPmaxW = panelPmaxW * seriesCount * parallelCount;
    const currentLimitedPowerW = arrayVmpV * stationMaxCurrentA;
    const screenedInputCeilingW = Math.min(arrayPmaxW, stationMaxPowerW, currentLimitedPowerW);
    const planningInputW = screenedInputCeilingW * (solarPlanningPct / 100);
    const energyNeedWh = batteryWh * Math.max(0, targetSoc - currentSoc) / 100;
    const estimatedSolarHours = planningInputW > 0 ? energyNeedWh / planningInputW : NaN;

    return {
      stationMinV, stationMaxV, stationMaxCurrentA, stationMaxIscA, stationMaxPowerW,
      batteryWh, currentSoc, targetSoc, solarPlanningPct,
      panelPmaxW, panelVocV, panelVmpV, panelIscA, panelImpA, tempCoeffVocPct, minTempC,
      seriesCount, parallelCount, coldDeltaC: round(coldDeltaC, 1), coldVocMultiplier: round(coldVocMultiplier, 4),
      panelColdVocV: round(panelColdVocV, 2), arrayVocStcV: round(arrayVocStcV, 2),
      arrayColdVocV: round(arrayColdVocV, 2), arrayVmpV: round(arrayVmpV, 2),
      arrayIscA: round(arrayIscA, 2), arrayImpA: round(arrayImpA, 2), arrayPmaxW: round(arrayPmaxW, 1),
      currentLimitedPowerW: round(currentLimitedPowerW, 1), screenedInputCeilingW: round(screenedInputCeilingW, 1),
      planningInputW: round(planningInputW, 1), energyNeedWh: round(energyNeedWh, 1),
      estimatedSolarHours: round(estimatedSolarHours, 2)
    };
  }

  function validate(c) {
    const errors = [];
    const positive = [
      ['stationMinV', c.stationMinV], ['stationMaxV', c.stationMaxV], ['stationMaxCurrentA', c.stationMaxCurrentA],
      ['stationMaxPowerW', c.stationMaxPowerW], ['batteryWh', c.batteryWh], ['panelPmaxW', c.panelPmaxW],
      ['panelVocV', c.panelVocV], ['panelVmpV', c.panelVmpV], ['panelIscA', c.panelIscA], ['panelImpA', c.panelImpA]
    ];
    for (const [key, value] of positive) if (!(value > 0)) errors.push(key);
    if (!(c.stationMaxV > c.stationMinV)) errors.push('stationVoltageRange');
    if (!(c.panelVocV > c.panelVmpV)) errors.push('panelVocVmp');
    if (!(c.panelIscA >= c.panelImpA)) errors.push('panelIscImp');
    if (!(c.tempCoeffVocPct > -2 && c.tempCoeffVocPct < 0)) errors.push('tempCoeffVocPct');
    if (!(c.minTempC >= -50 && c.minTempC <= 25)) errors.push('minTempC');
    if (!(c.currentSoc >= 0 && c.currentSoc < 100)) errors.push('currentSoc');
    if (!(c.targetSoc > c.currentSoc && c.targetSoc <= 100)) errors.push('targetSoc');
    if (!(c.solarPlanningPct >= 30 && c.solarPlanningPct <= 100)) errors.push('solarPlanningPct');
    if (!(c.seriesCount >= 1 && c.seriesCount <= 12)) errors.push('seriesCount');
    if (!(c.parallelCount >= 1 && c.parallelCount <= 12)) errors.push('parallelCount');
    if (Number.isFinite(c.stationMaxIscA) && !(c.stationMaxIscA > 0)) errors.push('stationMaxIscA');
    return errors;
  }

  function evaluate(input) {
    const c = calculate(input);
    const errors = validate(c);
    if (errors.length) return { status: 'invalid', affiliateEligible: false, errors, calc: c };

    const stopReasons = [];
    if (!bool(input.noDamageDry)) stopReasons.push('damage_or_wet');
    if (!bool(input.noLiveWork)) stopReasons.push('live_rewiring');
    if (bool(input.activeStorm)) stopReasons.push('active_storm');
    if (stopReasons.length) return { status: 'stop', affiliateEligible: false, reasons: stopReasons, calc: c };

    if (input.installationType !== 'portable') {
      return { status: 'professional', affiliateEligible: false, reasons: ['fixed_rooftop_or_grid_tied_pv'], calc: c };
    }

    const evidence = [];
    if (!bool(input.stationDocsVerified)) evidence.push('station_docs');
    if (!bool(input.panelDocsVerified)) evidence.push('panel_docs');
    if (!bool(input.connectorPolarityVerified)) evidence.push('connector_polarity');
    if (!bool(input.cableVerified)) evidence.push('manufacturer_cable');
    if (!bool(input.tempDataVerified)) evidence.push('voc_temperature_data');
    if (evidence.length) return { status: 'evidence', affiliateEligible: false, reasons: evidence, calc: c };

    const hard = [];
    if (c.arrayColdVocV >= c.stationMaxV) hard.push('cold_voc_at_or_above_max');
    if (c.arrayVmpV < c.stationMinV) hard.push('vmp_below_mppt_min');
    if (c.arrayVmpV >= c.stationMaxV) hard.push('vmp_at_or_above_input_max');
    if (Number.isFinite(c.stationMaxIscA) && c.arrayIscA > c.stationMaxIscA) hard.push('isc_above_documented_max');
    if (hard.length) return { status: 'incompatible', affiliateEligible: false, reasons: hard, calc: c };

    const conditional = [];
    if (!Number.isFinite(c.stationMaxIscA) && c.arrayImpA > c.stationMaxCurrentA) conditional.push('no_documented_isc_limit_for_overcurrent');
    if (c.arrayImpA > c.stationMaxCurrentA && !bool(input.currentClippingVerified)) conditional.push('input_current_clipping_not_verified');
    if (c.arrayPmaxW > c.stationMaxPowerW && !bool(input.overpanelVerified)) conditional.push('overpanel_power_not_verified');
    if (conditional.length) return { status: 'conditional', affiliateEligible: false, reasons: conditional, calc: c };

    if (input.ownership === 'owned') {
      if (!bool(input.realSolarTestPassed)) {
        return { status: 'conditional', affiliateEligible: false, reasons: ['real_solar_test_missing'], calc: c };
      }
      return { status: 'no_buy', affiliateEligible: false, reasons: ['existing_compatible_panel'], calc: c };
    }

    return { status: 'compatible_candidate', affiliateEligible: true, reasons: ['screening_passed'], calc: c };
  }

  return { calculate, evaluate, round };
});
