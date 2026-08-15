'use strict';
(function(root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) {
    root.Alo186AirConditionerSizing = api;
    if (root.document) api.mount(root.document);
  }
})(typeof globalThis !== 'undefined' ? globalThis : this, function() {
  const ROUTE = '/hesaplama/klima-btu-elektrik-altyapi-uygunluk/';
  const AREA_TABLE = [
    [13.94, 5000], [23.23, 6000], [27.87, 7000], [32.52, 8000],
    [37.16, 9000], [41.81, 10000], [51.10, 12000], [65.03, 14000],
    [92.90, 18000], [111.48, 21000], [130.06, 23000], [139.35, 24000],
    [185.81, 30000], [232.26, 34000]
  ];
  const STANDARD_CLASSES = [7000, 9000, 10000, 12000, 14000, 18000, 21000, 24000, 30000, 36000];
  const num = value => Number(value);
  const finite = value => Number.isFinite(num(value));
  const round = (value, digits = 0) => Number(num(value).toFixed(digits));
  const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

  function baseCapacity(areaM2) {
    const area = num(areaM2);
    if (!Number.isFinite(area) || area <= 0) return NaN;
    const match = AREA_TABLE.find(([limit]) => area <= limit);
    return match ? match[1] : NaN;
  }

  function standardClass(btu) {
    if (!Number.isFinite(btu) || btu <= 0) return NaN;
    return STANDARD_CLASSES.find(value => value >= btu) || NaN;
  }

  function calculate(data) {
    const areaM2 = num(data.areaM2);
    const ceilingM = num(data.ceilingM);
    const people = Math.max(0, Math.round(num(data.people) || 0));
    const electronicsW = Math.max(0, num(data.electronicsW) || 0);
    const baseBtu = baseCapacity(areaM2);
    if (!Number.isFinite(baseBtu) || !Number.isFinite(ceilingM) || ceilingM <= 0) {
      return { valid: false };
    }

    const ceilingFactor = clamp(ceilingM / 2.44, 0.9, 1.6);
    const sunFactor = data.sun === 'shaded' ? 0.9 : data.sun === 'sunny' ? 1.1 : 1;
    const climateFactor = data.climate === 'mild' ? 0.95 : data.climate === 'very_hot' ? 1.1 : 1;
    const insulationFactor = data.insulation === 'good' ? 0.95 : data.insulation === 'poor' ? 1.1 : 1;
    const occupancyExtraBtu = Math.max(0, people - 2) * 600;
    const kitchenExtraBtu = data.kitchen === 'yes' ? 4000 : 0;
    const electronicsExtraBtu = electronicsW * 3.412;
    const adjustedBtu = Math.ceil(
      baseBtu * ceilingFactor * sunFactor * climateFactor * insulationFactor
      + occupancyExtraBtu + kitchenExtraBtu + electronicsExtraBtu
    );
    const recommendedBtu = standardClass(adjustedBtu);
    const planningLowBtu = Math.round(adjustedBtu * 0.9 / 100) * 100;
    const planningHighBtu = Math.round(adjustedBtu * 1.2 / 100) * 100;

    const voltage = finite(data.voltage) && num(data.voltage) > 0 ? num(data.voltage) : 230;
    const inputW = Math.max(0, num(data.candidateInputW) || 0);
    const ratedA = Math.max(0, num(data.candidateRatedA) || 0);
    const calculatedA = inputW > 0 ? inputW / voltage : 0;
    const workingA = Math.max(calculatedA, ratedA);
    const candidateBtu = Math.max(0, num(data.candidateBtu) || 0);
    const candidateRatio = candidateBtu > 0 ? candidateBtu / adjustedBtu : 0;
    const requiredBreakerA = Math.max(0, num(data.requiredBreakerA) || 0);
    const circuitBreakerA = Math.max(0, num(data.circuitBreakerA) || 0);

    return {
      valid: true,
      areaM2: round(areaM2, 1),
      baseBtu,
      ceilingFactor: round(ceilingFactor, 2),
      occupancyExtraBtu,
      kitchenExtraBtu,
      electronicsExtraBtu: round(electronicsExtraBtu),
      adjustedBtu,
      planningLowBtu,
      planningHighBtu,
      recommendedBtu,
      candidateBtu,
      candidateRatio: round(candidateRatio, 2),
      workingA: round(workingA, 2),
      requiredBreakerA,
      circuitBreakerA,
      electricalHeadroomA: circuitBreakerA > 0 ? round(circuitBreakerA - workingA, 2) : NaN
    };
  }

  function decide(data) {
    const metrics = calculate(data);
    const confirmations = Boolean(data.confirmNeed && data.confirmEvidence && data.confirmAffiliate);
    const dangerousPhysical = ['hot', 'burned', 'loose', 'wet', 'damaged'].includes(data.physicalCondition);
    if (data.emergency === 'yes' || dangerousPhysical || data.symptom === 'shock_smoke') {
      return result('danger', 'Önce can ve yangın güvenliği', 'Duman, erime, su, elektrik çarpması, yanık kokusu veya aşırı ısınmada cihazı çalıştırmayın. Yangın ve yaralanmada 112; güvenli enerji kesme ve ölçüm için yetkili elektrikçi gerekir.', false, metrics);
    }
    if (data.symptom === 'bright_dim' || data.scope === 'building_area') {
      return result('grid_risk', 'Klima seçmeden önce şebeke veya nötr riskini ayırın', 'Birden fazla odada parlaklık değişimi veya bina/sokak etkisi ürün seçimiyle çözülmez. 186, ilgili EDAŞ ve yetkili elektrikçi rotasına ilerleyin.', false, metrics);
    }
    if (data.mode === 'active_outage') {
      return result('active_outage', 'Yeni ürün aktif kesintinin anlık çözümü değildir', 'Önce güvenli serinleme, mevcut ekipmanın kontrollü kullanımı ve resmî kesinti bilgisini doğrulayın. Teslim edilmemiş klima veya elektrik ürünü anlık çözüm sayılmaz.', false, metrics);
    }
    if (!metrics.valid) {
      return result('sizing_input_missing', 'Alan ve tavan yüksekliğini doğrulayın', 'Odanın net alanı ve tavan yüksekliği olmadan BTU ön seçimi yapılmaz.', false, metrics);
    }
    if (['commercial', 'multi_room', 'medical_server'].includes(data.useCase) || !Number.isFinite(metrics.recommendedBtu)) {
      return result('professional', 'Profesyonel ısı kazancı ve elektrik projesi gerekir', 'Çok odalı, ticari, server/medikal veya 36.000 BTU üzeri ihtiyaçlar tüketici tipi ürün karşılaştırmasına dönüştürülmez.', false, metrics);
    }
    if (['extension', 'power_strip', 'adapter_chain'].includes(data.connection)) {
      return result('unsafe_connection', 'Uzatma ve çoklayıcı kullanmayın', 'Klima doğrudan üretici talimatına uygun, topraklı ve yeterli devreye bağlanmalıdır. Uzatma, çoklayıcı veya adaptör zinciri kapasiteyi güvenli hâle getirmez.', false, metrics);
    }
    if (data.earthStatus !== 'verified' || data.rcdStatus !== 'tested') {
      return result('electrical_evidence_missing', 'Topraklama ve kaçak akım korumasını doğrulayın', 'Ürün karşılaştırmasından önce topraklama, RCD ve devre koşulları yetkili ölçüm veya kayıtla doğrulanmalıdır.', false, metrics);
    }
    if (data.unitType === 'split' && data.dedicatedCircuit !== 'yes') {
      return result('dedicated_circuit_missing', 'Split klima için ayrı devreyi doğrulayın', 'Sabit split klima; üretici kılavuzu, ayrı devre, koruma elemanları, kablo kesiti ve yetkili montajla değerlendirilmelidir.', false, metrics);
    }
    if (data.unitType === 'portable' && data.connection !== 'direct') {
      return result('unsafe_connection', 'Portatif klimayı doğrudan uygun prize bağlayın', 'Üretici izin vermedikçe uzatma veya grup priz kullanmayın.', false, metrics);
    }

    const hasCandidate = metrics.candidateBtu > 0;
    if (hasCandidate && data.manualEvidence !== 'verified') {
      return result('manual_missing', 'Tam model teknik belgeyi bulun', 'BTU, gerçek giriş W/A, gerekli sigorta/devre ve montaj şartları tam model üretici belgesinden doğrulanmalıdır.', false, metrics);
    }
    if (hasCandidate && (metrics.requiredBreakerA <= 0 || metrics.circuitBreakerA <= 0)) {
      return result('electrical_spec_missing', 'Gerekli sigorta ve mevcut devre akımı eksik', 'Soğutma kapasitesi ile elektrik giriş gücü aynı değildir. Tam model gerekli sigorta/devre bilgisi ve mevcut devre değeri olmadan elektrik uygunluğu onaylanmaz.', false, metrics);
    }
    if (hasCandidate && metrics.requiredBreakerA > metrics.circuitBreakerA) {
      return result('circuit_mismatch', 'Mevcut devre aday klimanın şartını karşılamıyor', 'Daha büyük sigorta takmak çözüm değildir. Kablo, devre, koruma ve üretici şartları yetkili elektrikçi tarafından birlikte değerlendirilmelidir.', false, metrics);
    }
    if (hasCandidate && metrics.candidateRatio < 0.9) {
      return result('undersized', 'Aday kapasite düşük görünüyor', 'Aday cihaz ön planlama yükünün altında. Daha büyük etikete geçmeden önce gerçek ısı kazancı ve montaj koşullarını doğrulayın.', false, metrics);
    }
    if (hasCandidate && metrics.candidateRatio > 1.35) {
      return result('oversized', 'Aday kapasite gereğinden büyük görünüyor', 'Büyük klima her zaman daha iyi değildir; kısa çevrim, nem alma zayıflığı ve gereksiz yatırım riski oluşabilir.', false, metrics);
    }
    if (data.existingUnit === 'yes') {
      if (data.realPerformanceTest === 'passed' && data.comfortResult === 'good' && hasCandidate && metrics.candidateRatio >= 0.9 && metrics.candidateRatio <= 1.25) {
        return result('no_buy', 'Mevcut klima hedefi karşılıyor — yeni ürün almayın', 'Kapasite, elektrik altyapısı, gerçek sıcaklık/nem konforu ve çalışma testi yeterliyse yalnız daha yüksek BTU veya yeni model etiketi için değişim gerekmiyor.', false, metrics);
      }
      if (data.realPerformanceTest === 'failed' || data.comfortResult === 'poor') {
        return result('service_first', 'Önce bakım ve montaj performansını doğrulayın', 'Filtre, hava akışı, dış ünite, soğutucu akışkan, izolasyon ve montaj sorunu çözülmeden daha büyük klima seçmek doğru sonuç vermeyebilir.', false, metrics);
      }
    }

    return result(
      'eligible_compare',
      hasCandidate ? 'Aday kapasite ön seçim bandında' : 'Ön seçim sınıfı oluşturuldu',
      'Bu sonuç kesin proje veya ürün onayı değildir. Tam model kapasite, gerçek giriş W/A, üretici devre şartı, montaj ve gerçek performans testi birlikte doğrulanmalıdır.',
      confirmations,
      metrics
    );
  }

  function result(code, title, summary, commerce, metrics) {
    return { code, title, summary, commerce: Boolean(commerce), metrics };
  }

  function formData(form) {
    const raw = Object.fromEntries(new FormData(form).entries());
    form.querySelectorAll('input[type="checkbox"]').forEach(input => {
      raw[input.name] = input.checked ? input.value || 'yes' : '';
    });
    return raw;
  }

  function metricCards(metrics) {
    if (!metrics || !metrics.valid) return '';
    const recommended = Number.isFinite(metrics.recommendedBtu) ? `${metrics.recommendedBtu.toLocaleString('tr-TR')} BTU/h` : 'Profesyonel hesap';
    return `<div class="metrics">
      <div><span>Ön yük</span><strong>${metrics.adjustedBtu.toLocaleString('tr-TR')} BTU/h</strong></div>
      <div><span>Planlama bandı</span><strong>${metrics.planningLowBtu.toLocaleString('tr-TR')}–${metrics.planningHighBtu.toLocaleString('tr-TR')}</strong></div>
      <div><span>Yakın sınıf</span><strong>${recommended}</strong></div>
      <div><span>Aday çalışma akımı</span><strong>${metrics.workingA > 0 ? `${metrics.workingA.toLocaleString('tr-TR')} A` : 'Etiketten doğrulayın'}</strong></div>
    </div>`;
  }

  function render(doc, decision) {
    const box = doc.getElementById('result');
    const link = doc.getElementById('productLink');
    const metrics = decision.metrics || {};
    box.hidden = false;
    box.className = `result ${['danger', 'grid_risk', 'unsafe_connection', 'circuit_mismatch'].includes(decision.code) ? 'danger-result' : ''}`;
    box.innerHTML = `<span class="result-code">${decision.code.replaceAll('_', ' ')}</span><h2 tabindex="-1">${decision.title}</h2><p>${decision.summary}</p>${metricCards(metrics)}`;
    box.querySelector('h2').focus();

    const canCompare = decision.code === 'eligible_compare';
    const btu = metrics.recommendedBtu || metrics.adjustedBtu || '';
    link.dataset.href = `/akilli-urun-secimi?category=klima&capacity_btu=${encodeURIComponent(btu)}`;
    link.hidden = !canCompare;
    if (canCompare && decision.commerce) {
      link.href = link.dataset.href;
      link.removeAttribute('aria-disabled');
      link.textContent = 'Şeffaf klima ürün sınıfını karşılaştır →';
    } else if (canCompare) {
      link.removeAttribute('href');
      link.setAttribute('aria-disabled', 'true');
      link.textContent = 'Üç teknik ve satış ortaklığı onayını tamamlayın';
    } else {
      link.removeAttribute('href');
      link.setAttribute('aria-disabled', 'true');
    }
    return decision;
  }

  function exportJson(doc, data, decision) {
    const payload = {
      schema: 'alo186-klima-btu-elektrik-altyapi-v1',
      generatedAt: new Date().toISOString(),
      route: ROUTE,
      personalDataIncluded: false,
      input: data,
      result: decision
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const anchor = doc.createElement('a');
    anchor.href = url;
    anchor.download = 'alo186-klima-btu-elektrik-uygunluk.json';
    anchor.click();
    URL.revokeObjectURL(url);
  }

  function mount(doc) {
    const form = doc.getElementById('airForm');
    if (!form || form.dataset.mounted === 'yes') return;
    form.dataset.mounted = 'yes';
    let latest = null;
    form.addEventListener('submit', event => {
      event.preventDefault();
      const data = formData(form);
      latest = { data, decision: decide(data) };
      render(doc, latest.decision);
    });
    form.addEventListener('change', () => {
      if (latest) {
        const data = formData(form);
        latest = { data, decision: decide(data) };
        render(doc, latest.decision);
      }
    });
    doc.getElementById('printResult')?.addEventListener('click', () => doc.defaultView?.print());
    doc.getElementById('exportResult')?.addEventListener('click', () => {
      if (!latest) form.requestSubmit();
      if (latest) exportJson(doc, latest.data, latest.decision);
    });
  }

  return { ROUTE, AREA_TABLE, STANDARD_CLASSES, baseCapacity, standardClass, calculate, decide, mount };
});
