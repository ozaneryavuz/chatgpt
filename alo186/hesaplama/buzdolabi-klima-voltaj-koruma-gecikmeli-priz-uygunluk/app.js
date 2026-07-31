(() => {
  'use strict';

  const STANDARD_AMPS = [6, 10, 13, 16, 20, 25, 32];
  const PLUGGABLE = new Set(['fridge', 'freezer', 'wine_cooler', 'portable_ac', 'dehumidifier']);
  const FIXED = new Set(['split_ac', 'heat_pump', 'cold_room', 'fixed_other']);
  const number = (value) => Number.isFinite(Number(value)) ? Number(value) : 0;
  const round = (value, digits = 2) => Number(number(value).toFixed(digits));

  function calculate(input) {
    const voltage = number(input.voltage) || 230;
    const watts = number(input.deviceW);
    const nameplateA = number(input.deviceA);
    const calculatedA = watts > 0 ? watts / voltage : 0;
    const workingA = Math.max(nameplateA, calculatedA);
    const requiredA = workingA * 1.25;
    const standardA = STANDARD_AMPS.find((item) => item >= requiredA) || null;
    const requiredDelay = number(input.manualDelayMinutes);
    const existingDelay = number(input.existingDelayMinutes);
    const existingRatedA = number(input.existingRatedA);
    const measuredMin = number(input.measuredMinV);
    const measuredMax = number(input.measuredMaxV);
    const lowThreshold = number(input.lowThresholdV);
    const highThreshold = number(input.highThresholdV);
    return {
      voltage,
      watts: round(watts, 0),
      nameplateA: round(nameplateA),
      calculatedA: round(calculatedA),
      workingA: round(workingA),
      requiredA: round(requiredA),
      standardA,
      requiredDelay,
      existingDelay,
      existingRatedA,
      currentMarginA: round(existingRatedA - requiredA),
      delayGapMinutes: round(Math.max(0, requiredDelay - existingDelay), 1),
      lowEventDetected: Boolean(measuredMin && lowThreshold && measuredMin < lowThreshold),
      highEventDetected: Boolean(measuredMax && highThreshold && measuredMax > highThreshold)
    };
  }

  const outcome = (code, title, tone, actions, commercial = false) => ({
    code, title, tone, actions, commercial,
    productClass: commercial ? 'plug_voltage_protector' : ''
  });

  function decide(input) {
    const m = calculate(input);
    const badPhysical = ['hot', 'burned', 'loose', 'wet', 'damaged'].includes(input.physicalCondition);
    const neutralRisk = input.symptom === 'bright_dim' || input.scope === 'building_area';
    const unsafeConnection = ['extension', 'power_strip', 'adapter_chain'].includes(input.connection);
    const fixedLoad = FIXED.has(input.applianceType) || input.connection === 'fixed';
    const manualKnown = input.manualEvidence === 'verified' && m.requiredDelay > 0;
    const existing = input.existingType && input.existingType !== 'none';
    const evidenceOkay = input.existingEvidence === 'verified';
    const functionsOkay = input.existingFunctions === 'under_over_delay';
    const currentOkay = m.existingRatedA > 0 && m.existingRatedA >= m.requiredA;
    const delayOkay = manualKnown && m.existingDelay >= m.requiredDelay;
    const testOkay = input.existingTest === 'passed';
    const connectionOkay = input.connection === 'direct' && input.earthStatus === 'verified' && input.rcdStatus === 'tested';

    if (input.emergency === 'yes' || badPhysical) return outcome('emergency', 'Enerjiyi zorlamayın; güvenlik kontrolü önce gelir.', 'danger', [
      'Duman, erime, yanık kokusu, su veya elektrik çarpması varsa cihazı yeniden çalıştırmayın.',
      'Yangın veya yaralanmada 112; priz, kablo ve sabit tesisat için yetkili elektrikçi kullanın.'
    ]);
    if (neutralRisk) return outcome('neutral_grid_risk', 'Ürün seçmeyin; nötr veya şebeke olayı dışlanmalıdır.', 'danger', [
      'Birden fazla odada lambalar farklı parlaklıktaysa cihaz koruyucuyla deneme yapmayın.',
      '186/ilgili EDAŞ ve yetkili elektrikçi üzerinden olay kaydı ve gerilim-nötr ölçümü isteyin.'
    ]);
    if (input.applianceType === 'medical') return outcome('medical_professional', 'Tıbbi yük tüketici tipi koruyucuya dönüştürülemez.', 'danger', [
      'Cihaz üreticisi, sağlık profesyoneli ve uygun yedek güç planı esas alınmalıdır.'
    ]);
    if (fixedLoad) return outcome('fixed_professional', 'Sabit veya yüksek güçlü cihaz için pano tipi profesyonel çözüm gerekir.', 'warn', [
      'Split klima, ısı pompası ve soğuk oda için fiş tipi ürün kullanmayın.',
      'Gerilim izleme rölesi, kontaktör ve yeniden başlatma şartını yetkili elektrikçi doğrulamalıdır.'
    ]);
    if (unsafeConnection) return outcome('unsafe_connection', 'Uzatma veya çoklayıcı zinciri çözülmeden ürün seçmeyin.', 'danger', [
      'Kompresörlü cihazı doğrudan, sağlam ve topraklı duvar prizine bağlayın.'
    ]);
    if (input.earthStatus === 'failed' || input.rcdStatus === 'failed') return outcome('earth_rcd_failed', 'Topraklama veya kaçak akım koruması doğrulanmalıdır.', 'danger', [
      'Gerilim koruyucu, topraklama veya RCD eksikliğini gidermez.'
    ]);
    if (input.mode === 'active_outage') return outcome('active_outage', 'Aktif kesintide yeni ürün anlık çözüm değildir.', 'warn', [
      'Enerji geri geldiğinde tam model kılavuzundaki yeniden başlatma süresini uygulayın.',
      'Ürün seçimini şebeke kararlı hâle geldikten sonra yapın.'
    ]);
    if (!PLUGGABLE.has(input.applianceType)) return outcome('unsupported_appliance', 'Bu cihaz için genel fiş tipi koruyucu doğrulanamaz.', 'warn', [
      'Tam model üretici kılavuzu ve bağlantı biçimi esas alınmalıdır.'
    ]);
    if (input.measurementEvidence === 'unsafe_handheld') return outcome('unsafe_measurement', 'Canlı prizde kullanıcı ölçümü yapmayın.', 'danger', [
      'Priz içine prob sokmayın; kayıt cihazı, EDAŞ ölçümü veya yetkili elektrikçi raporu kullanın.'
    ]);
    if (!m.workingA || !m.standardA) return outcome('load_evidence_missing', 'Cihazın gerçek giriş W veya A bilgisi eksik.', 'warn', [
      'BTU veya soğutma kapasitesi yerine INPUT / rated current / power consumption etiketini bulun.'
    ]);
    if (!manualKnown) return outcome('manual_delay_missing', 'Yeniden başlatma gecikmesi tam model kılavuzundan doğrulanmalı.', 'warn', [
      'Evrensel bir dakika değeri varsaymayın; üretici talimatını bulun.'
    ]);
    if (m.requiredA > 16 || m.workingA > 10) return outcome('high_current_professional', 'Fiş tipi tüketici koruyucusu için akım yüksektir.', 'warn', [
      `Çalışma akımı yaklaşık ${m.workingA} A, planlama alt sınırı ${m.requiredA} A.`,
      'Pano tipi röle/kontaktör çözümünü yetkili elektrikçi değerlendirmelidir.'
    ]);
    if (input.existingType === 'surge_only') return outcome('surge_not_voltage', 'Akım korumalı priz, düşük/yüksek gerilim ve gecikme koruması değildir.', 'warn', [
      'Ani darbe koruması ile sürekli gerilim izleme işlevini ayırın.',
      'Düşük + yüksek gerilim + yeniden bağlama gecikmesi tam modelde birlikte doğrulanmalıdır.'
    ], true);
    if (existing && evidenceOkay && functionsOkay && currentOkay && delayOkay && testOkay && connectionOkay) return outcome('no_buy', 'Mevcut koruma kanıtları yeterli — yeni ürün almayın.', 'ok', [
      `Mevcut ${m.existingRatedA} A koruma, yaklaşık ${m.requiredA} A planlama alt sınırını karşılıyor.`,
      `Mevcut ${m.existingDelay} dakikalık gecikme, kılavuzdaki ${m.requiredDelay} dakikayı karşılıyor.`,
      'Gerçek kesinti-sonrası testi dönemsel olarak tekrarlayın.'
    ]);
    if (existing && !evidenceOkay) return outcome('protector_evidence_missing', 'Mevcut ürünün tam model teknik kanıtı eksik.', 'warn', [
      'İşlev, anma akımı, gecikme ve uygunluk belgesini tam modelde doğrulayın.'
    ]);
    if (existing && !functionsOkay) return outcome('functions_missing', 'Mevcut ürün gerekli üç işlevi birlikte kanıtlamıyor.', 'warn', [
      'Düşük gerilim, yüksek gerilim ve yeniden bağlama gecikmesi birlikte bulunmalıdır.'
    ], true);
    if (existing && !currentOkay) return outcome('current_shortfall', 'Mevcut koruyucunun akım kapasitesi yetersiz.', 'warn', [
      `Planlama alt sınırı ${m.requiredA} A; mevcut ürün ${m.existingRatedA || 0} A.`
    ], true);
    if (existing && !delayOkay) return outcome('delay_shortfall', 'Mevcut yeniden bağlama gecikmesi yetersiz.', 'warn', [
      `Kılavuz şartı ${m.requiredDelay} dakika; mevcut gecikme ${m.existingDelay || 0} dakika.`
    ], true);
    if (existing && !testOkay) return outcome('test_missing', 'Gerçek kesinti-sonrası işlev testi eksik.', 'warn', [
      'Hızlı aç-kapa yapmayın; üretici talimatını izleyerek kontrollü test yapın.'
    ]);
    if (input.symptom === 'single_appliance_only' && input.measurementEvidence === 'verified_normal') return outcome('appliance_service', 'Şebeke kanıtı normalken belirti tek cihazdaysa servis incelemesi gerekir.', 'warn', [
      'Koruyucu satın almak cihaz içi arızayı çözmeyebilir.'
    ]);
    return outcome('eligible_compare', 'Fiş tipi düşük/yüksek gerilim ve gecikme koruyucusu karşılaştırılabilir.', 'ok', [
      `Çalışma akımı yaklaşık ${m.workingA} A; planlama alt sınırı ${m.requiredA} A ve ilk standart sınıf ${m.standardA} A.`,
      `Yeniden bağlama gecikmesi en az tam model kılavuzundaki ${m.requiredDelay} dakikayı karşılamalıdır.`,
      'Ürün; düşük/yüksek gerilim izleme, gerçek anma akımı, doğrudan topraklı bağlantı ve tam model belgeyle doğrulanmalıdır.'
    ], true);
  }

  function summaryPayload(input, result) {
    return {
      schemaVersion: 1,
      generatedAt: new Date().toISOString(),
      privacy: 'Kişisel veri içermez; tarayıcıda oluşturulur.',
      applianceType: input.applianceType,
      metrics: calculate(input),
      decision: { code: result.code, title: result.title, productClass: result.productClass || null }
    };
  }

  function boot() {
    if (typeof document === 'undefined') return;
    const form = document.getElementById('voltageForm');
    if (!form) return;
    const result = document.getElementById('result');
    const affiliate = document.getElementById('affiliateBox');
    const affiliateLink = document.getElementById('affiliateLink');
    let latestInput = null;
    let latestDecision = null;
    const read = () => Object.fromEntries(new FormData(form).entries());
    const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
    const syncAffiliate = () => {
      const checks = [...document.querySelectorAll('[data-affiliate-check]')];
      const enabled = Boolean(latestDecision?.commercial && checks.every((check) => check.checked));
      affiliateLink.setAttribute('aria-disabled', String(!enabled));
      affiliateLink.tabIndex = enabled ? 0 : -1;
      affiliateLink.classList.toggle('disabled', !enabled);
    };
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      latestInput = read();
      latestDecision = decide(latestInput);
      const m = calculate(latestInput);
      result.hidden = false;
      result.className = `result ${latestDecision.tone}`;
      result.innerHTML = `<span class="status">${escapeHtml(latestDecision.code)}</span><h2>${escapeHtml(latestDecision.title)}</h2><div class="metrics"><div><b>${m.workingA || '—'} A</b><span>Çalışma akımı</span></div><div><b>${m.requiredA || '—'} A</b><span>%25 planlama payı</span></div><div><b>${m.standardA ? `${m.standardA} A` : '—'}</b><span>İlk standart sınıf</span></div><div><b>${m.requiredDelay || '—'} dk</b><span>Kılavuz gecikmesi</span></div></div><ol>${latestDecision.actions.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ol><p class="notice">Bu sonuç uygunluk belgesi, servis teşhisi veya tesisat projesi değildir.</p>`;
      result.focus();
      affiliate.hidden = !latestDecision.commercial;
      document.querySelectorAll('[data-affiliate-check]').forEach((check) => { check.checked = false; });
      syncAffiliate();
    });
    document.querySelectorAll('[data-affiliate-check]').forEach((check) => check.addEventListener('change', syncAffiliate));
    affiliateLink.addEventListener('click', (event) => {
      if (affiliateLink.getAttribute('aria-disabled') === 'true') event.preventDefault();
    });
    document.getElementById('printButton').addEventListener('click', () => window.print());
    document.getElementById('jsonButton').addEventListener('click', () => {
      if (!latestInput || !latestDecision) return;
      const blob = new Blob([JSON.stringify(summaryPayload(latestInput, latestDecision), null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'alo186-voltaj-koruma-sonucu.json';
      link.click();
      URL.revokeObjectURL(url);
    });
  }

  globalThis.Alo186VoltageProtection = { calculate, decide, summaryPayload };
  if (typeof document !== 'undefined') document.addEventListener('DOMContentLoaded', boot);
})();
