(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.Alo186AquariumBackup = api;
  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', () => api.mount(document), { once: true });
    else api.mount(document);
  }
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const EFFICIENCY = 0.85;
  const USABLE_FRACTION = 0.80;
  const OUTPUT_HEADROOM = 1.25;

  const TANK_LABELS = Object.freeze({
    coldwater: 'Soğuk su akvaryumu',
    tropical: 'Tropikal tatlı su akvaryumu',
    marine: 'Deniz akvaryumu',
    reef: 'Resif akvaryumu',
    pond: 'Süs havuzu / koi sistemi'
  });

  const PRODUCT_LABELS = Object.freeze({
    battery_air_pump: 'Pilli veya USB yedek hava motoru',
    small_power_station: 'Küçük saf sinüs power station',
    power_station: 'Saf sinüs power station'
  });

  function number(value, name, min, max) {
    const parsed = Number(value);
    if (!Number.isFinite(parsed) || parsed < min || parsed > max) {
      throw new Error(`${name} ${min}–${max} aralığında olmalıdır.`);
    }
    return parsed;
  }

  function optionalNumber(value, name, min, max, fallback) {
    if (value == null || value === '') return fallback;
    return number(value, name, min, max);
  }

  function roundUp(value, step) {
    return Math.ceil(value / step) * step;
  }

  function evaluate(raw) {
    const tankType = TANK_LABELS[raw.tankType] ? raw.tankType : 'tropical';
    const volumeL = number(raw.volumeL, 'Akvaryum hacmi', 5, 5000);
    const outageHours = number(raw.outageHours, 'Hedef kesinti süresi', 0.5, 72);
    const waterTempC = optionalNumber(raw.waterTempC, 'Su sıcaklığı', 0, 40, 25);
    const filterW = optionalNumber(raw.filterW, 'Filtre gücü', 0, 800, 0);
    const airPumpW = optionalNumber(raw.airPumpW, 'Hava motoru gücü', 0, 150, 0);
    const returnPumpW = optionalNumber(raw.returnPumpW, 'Dönüş/sirkülasyon pompası gücü', 0, 1200, 0);
    const heaterW = optionalNumber(raw.heaterW, 'Isıtıcı gücü', 0, 3000, 0);
    const heaterDutyPct = optionalNumber(raw.heaterDutyPct, 'Isıtıcı çalışma oranı', 0, 100, 35);
    const otherW = optionalNumber(raw.otherW, 'Diğer kritik yük', 0, 1000, 0);
    const lightingW = optionalNumber(raw.lightingW, 'Aydınlatma gücü', 0, 1500, 0);

    const heaterAverageW = heaterW * (heaterDutyPct / 100);
    const lifeSupportW = airPumpW + filterW + returnPumpW + heaterAverageW + otherW;
    const lifeSupportPeakW = airPumpW + filterW + returnPumpW + heaterW + otherW;
    const fullSystemW = lifeSupportW + lightingW;
    const requiredContinuousW = roundUp(Math.max(lifeSupportPeakW, 1) * OUTPUT_HEADROOM, 10);
    const requiredNominalWh = roundUp((lifeSupportW * outageHours) / EFFICIENCY / USABLE_FRACTION, 10);
    const fullSystemWh = roundUp((fullSystemW * outageHours) / EFFICIENCY / USABLE_FRACTION, 10);

    const input = {
      tankType,
      volumeL,
      outageHours,
      waterTempC,
      filterW,
      airPumpW,
      returnPumpW,
      heaterW,
      heaterDutyPct,
      otherW,
      lightingW,
      activeOutage: Boolean(raw.activeOutage),
      electricalHazard: Boolean(raw.electricalHazard),
      wetPlugOrCable: Boolean(raw.wetPlugOrCable),
      fixedInstallation: Boolean(raw.fixedInstallation),
      commercialSystem: Boolean(raw.commercialSystem),
      centralSump: Boolean(raw.centralSump),
      highValueLivestock: Boolean(raw.highValueLivestock),
      rcdVerified: Boolean(raw.rcdVerified),
      dripLoopVerified: Boolean(raw.dripLoopVerified),
      speciesPlanVerified: Boolean(raw.speciesPlanVerified),
      thermometerAvailable: Boolean(raw.thermometerAvailable),
      hasExistingSource: Boolean(raw.hasExistingSource),
      existingContinuousW: optionalNumber(raw.existingContinuousW, 'Mevcut kaynak sürekli gücü', 0, 10000, 0),
      existingWh: optionalNumber(raw.existingWh, 'Mevcut kaynak kapasitesi', 0, 50000, 0),
      existingPureSine: Boolean(raw.existingPureSine),
      realOutageTestPassed: Boolean(raw.realOutageTestPassed)
    };

    let state = 'commerce';
    let title = 'Akvaryum yaşam desteği için yedek güç açığı doğrulandı.';
    let summary = 'Yalnız kritik hava, filtre, sirkülasyon ve gerekli ısıtma yükünü karşılayan düşük riskli yedek güç sınıfını karşılaştırın.';

    if (input.electricalHazard || input.wetPlugOrCable) {
      state = 'hazard';
      title = 'Su ve elektrik riski var: ekipmana dokunmayın.';
      summary = 'Islak priz, fiş, uzatma, açık iletken, kıvılcım, yanık kokusu veya elektrik çarpması riski varsa enerjiyi güvenli biçimde kestirin. Suya veya ıslak ekipmana yaklaşmayın; gerektiğinde 112 ve yetkili elektrikçi desteği alın.';
    } else if (input.activeOutage) {
      state = 'active_event';
      title = 'Aktif kesintide önce oksijen, sıcaklık ve su kalitesini koruyun.';
      summary = 'Ürün teslimatını anlık çözüm saymayın. Mevcut pilli hava motorunu veya doğrulanmış yedek kaynağı devreye alın, yemlemeyi azaltın, su sıcaklığını ve balık davranışını izleyin; türünüze özel acil bakım planını uygulayın.';
    } else if (input.fixedInstallation || input.commercialSystem || input.centralSump || input.highValueLivestock || volumeL > 500 || requiredContinuousW > 800 || outageHours > 24) {
      state = 'professional';
      title = 'Bu sistem için profesyonel süreklilik tasarımı gerekir.';
      summary = 'Merkezi sump, ticari sistem, yüksek değerli canlı yükü, büyük hacim, yüksek güç veya 24 saati aşan hedef; N+1 hava/sirkülasyon, otomatik transfer, alarm, batarya ve jeneratör planıyla ele alınmalıdır.';
    } else if (!input.rcdVerified || !input.dripLoopVerified) {
      state = 'evidence';
      title = 'Elektrik güvenliği doğrulanmadan ürün yolu açılmaz.';
      summary = 'Akvaryum prizi için kaçak akım korumasını, kuru bağlantıyı ve kablolarda damlama halkasını doğrulayın. Çoklayıcıyı yerde veya su hattının altında kullanmayın.';
    } else if (!input.speciesPlanVerified || !input.thermometerAvailable) {
      state = 'evidence';
      title = 'Canlı türü ve sıcaklık planı doğrulanmalı.';
      summary = 'Oksijen, sıcaklık ve akış gereksinimi tür, stok yoğunluğu, salinite ve su sıcaklığına göre değişir. Türünüze özel plan ve çalışan termometre olmadan evrensel “kaç saat dayanır” sonucu verilmez.';
    } else if (lifeSupportW <= 0) {
      state = 'evidence';
      title = 'En az bir yaşam destek yükü girin.';
      summary = 'Hava motoru, filtre, dönüş pompası, ısıtıcı veya diğer kritik yüklerin etiket watt değerlerinden en az birini girin.';
    } else if (waterTempC >= 28 && airPumpW <= 0 && returnPumpW <= 0) {
      state = 'evidence';
      title = 'Yüksek sıcaklıkta yedek havalandırma kanıtı eksik.';
      summary = 'Yüksek su sıcaklığında tür ve stok yoğunluğuna bağlı olarak ek havalandırma gerekebilir. En az bir doğrulanmış hava veya sirkülasyon yükünü plana ekleyin.';
    } else if ((tankType === 'marine' || tankType === 'reef') && returnPumpW <= 0 && airPumpW <= 0) {
      state = 'evidence';
      title = 'Deniz/resif sistemi için gaz değişimi ve sirkülasyon yükü eksik.';
      summary = 'Dönüş pompası, dalga motoru veya hava desteğinin kritik watt değerini ekleyin; yalnız aydınlatma ya da ısıtıcıyla süreklilik hesabı yapılmaz.';
    }

    const existingEnough = input.hasExistingSource &&
      input.existingContinuousW >= requiredContinuousW &&
      input.existingWh >= requiredNominalWh &&
      input.existingPureSine &&
      input.realOutageTestPassed;

    if (state === 'commerce' && existingEnough) {
      state = 'no_buy';
      title = 'Mevcut yedek kaynak yeterli: yeni ürün almayın.';
      summary = 'Mevcut kaynak sürekli güç ve nominal enerji eşiklerini karşılıyor; saf sinüs ve gerçek kesinti testi de doğrulandı. Yalnız periyodik test ve batarya sağlığı takibi yapın.';
    }

    let product = null;
    if (state === 'commerce') {
      if (airPumpW > 0 && filterW === 0 && returnPumpW === 0 && heaterW === 0 && otherW === 0 && requiredNominalWh <= 100 && requiredContinuousW <= 30) {
        product = 'battery_air_pump';
      } else if (requiredContinuousW <= 200 && requiredNominalWh <= 600) {
        product = 'small_power_station';
      } else {
        product = 'power_station';
      }
    }

    const existingGaps = [];
    if (input.hasExistingSource && !existingEnough) {
      if (input.existingContinuousW < requiredContinuousW) existingGaps.push(`sürekli güç ${requiredContinuousW - input.existingContinuousW} W eksik`);
      if (input.existingWh < requiredNominalWh) existingGaps.push(`nominal enerji ${requiredNominalWh - input.existingWh} Wh eksik`);
      if (!input.existingPureSine) existingGaps.push('saf sinüs kanıtı yok');
      if (!input.realOutageTestPassed) existingGaps.push('gerçek kesinti testi geçilmedi');
    }

    return {
      state,
      title,
      summary,
      tankLabel: TANK_LABELS[tankType],
      heaterAverageW: Math.round(heaterAverageW),
      lifeSupportW: Math.round(lifeSupportW),
      lifeSupportPeakW: Math.round(lifeSupportPeakW),
      fullSystemW: Math.round(fullSystemW),
      requiredContinuousW,
      requiredNominalWh,
      fullSystemWh,
      product,
      productLabel: product ? PRODUCT_LABELS[product] : null,
      existingEnough,
      existingGaps,
      noBuy: state === 'no_buy',
      commerceAllowed: state === 'commerce' && Boolean(product),
      assumptions: [
        `AC dönüşüm verimi: ${Math.round(EFFICIENCY * 100)}%`,
        `Kullanılabilir enerji oranı: ${Math.round(USABLE_FRACTION * 100)}%`,
        `Sürekli çıkış payı: ${Math.round((OUTPUT_HEADROOM - 1) * 100)}%`,
        'Sürekli W hesabında ısıtıcı etiket gücü tam yük; Wh hesabında çalışma oranına göre ortalama yük olarak kullanılır.',
        'Aydınlatma yaşam destek hesabına dahil edilmez; tam sistem hesabında ayrı gösterilir.',
        'Sonuç veterinerlik, akvaryum uzmanlığı veya sabit tesisat projesi değildir.'
      ]
    };
  }

  function amazonQuery(result) {
    if (result.product === 'battery_air_pump') return 'akvaryum pilli hava motoru USB yedek oksijen';
    const wh = roundUp(result.requiredNominalWh, 50);
    const watts = roundUp(result.requiredContinuousW, 50);
    return `saf sinüs taşınabilir güç istasyonu ${watts}W ${wh}Wh`;
  }

  function amazonUrl(result) {
    return `https://www.amazon.com.tr/s?k=${encodeURIComponent(amazonQuery(result))}&tag=alo186rehber-21`;
  }

  function escapeIcs(value) {
    return String(value).replace(/\\/g, '\\\\').replace(/;/g, '\\;').replace(/,/g, '\\,').replace(/\n/g, '\\n');
  }

  function dateStamp(date) {
    return [date.getFullYear(), String(date.getMonth() + 1).padStart(2, '0'), String(date.getDate()).padStart(2, '0')].join('');
  }

  function buildIcs(payload, now) {
    const start = new Date(now || Date.now());
    start.setDate(start.getDate() + 90);
    const description = `${payload.result.tankLabel}; kritik yük ${payload.result.lifeSupportW} W; gereken kaynak ${payload.result.requiredContinuousW} W / ${payload.result.requiredNominalWh} Wh. RCD, damlama halkası, hava motoru, filtre, sıcaklık ve gerçek kesinti testini yeniden kontrol edin.`;
    return [
      'BEGIN:VCALENDAR',
      'VERSION:2.0',
      'PRODID:-//ALO186//Akvaryum Yedek Guc Kontrolu//TR',
      'BEGIN:VEVENT',
      `UID:alo186-aquarium-${Date.now()}@alo186.com`,
      `DTSTART;VALUE=DATE:${dateStamp(start)}`,
      'SUMMARY:ALO186 akvaryum yedek güç yeniden testi',
      `DESCRIPTION:${escapeIcs(description)}`,
      'END:VEVENT',
      'END:VCALENDAR',
      ''
    ].join('\r\n');
  }

  function downloadFile(filename, content, type) {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  function mount(doc) {
    const form = doc.getElementById('aquariumForm');
    if (!form || form.dataset.mounted === 'true') return;
    form.dataset.mounted = 'true';

    const resultSection = doc.getElementById('result');
    const commerce = doc.getElementById('commerce');
    const affiliateLink = doc.getElementById('affiliateLink');
    const gates = [...doc.querySelectorAll('.commerce-gate')];
    let lastPayload = null;

    function checked(id) { return Boolean(doc.getElementById(id).checked); }
    function value(id) { return doc.getElementById(id).value; }

    function readInput() {
      return {
        tankType: value('tankType'),
        volumeL: value('volumeL'),
        outageHours: value('outageHours'),
        waterTempC: value('waterTempC'),
        filterW: value('filterW'),
        airPumpW: value('airPumpW'),
        returnPumpW: value('returnPumpW'),
        heaterW: value('heaterW'),
        heaterDutyPct: value('heaterDutyPct'),
        otherW: value('otherW'),
        lightingW: value('lightingW'),
        activeOutage: checked('activeOutage'),
        electricalHazard: checked('electricalHazard'),
        wetPlugOrCable: checked('wetPlugOrCable'),
        fixedInstallation: checked('fixedInstallation'),
        commercialSystem: checked('commercialSystem'),
        centralSump: checked('centralSump'),
        highValueLivestock: checked('highValueLivestock'),
        rcdVerified: checked('rcdVerified'),
        dripLoopVerified: checked('dripLoopVerified'),
        speciesPlanVerified: checked('speciesPlanVerified'),
        thermometerAvailable: checked('thermometerAvailable'),
        hasExistingSource: checked('hasExistingSource'),
        existingContinuousW: value('existingContinuousW'),
        existingWh: value('existingWh'),
        existingPureSine: checked('existingPureSine'),
        realOutageTestPassed: checked('realOutageTestPassed')
      };
    }

    function updateCommerceGate() {
      const enabled = lastPayload && lastPayload.result.commerceAllowed && gates.every((gate) => gate.checked);
      affiliateLink.setAttribute('aria-disabled', enabled ? 'false' : 'true');
      affiliateLink.tabIndex = enabled ? 0 : -1;
    }

    function render(payload) {
      const result = payload.result;
      resultSection.hidden = false;
      resultSection.dataset.state = result.state;
      const labels = {
        hazard: 'Ticari yol kapalı',
        active_event: 'Aktif kesinti',
        professional: 'Uzman tasarımı',
        evidence: 'Kanıt gerekli',
        no_buy: 'Satın alma yok',
        commerce: 'Koşullu ürün yolu'
      };
      doc.getElementById('state').textContent = labels[result.state];
      doc.getElementById('resultTitle').textContent = result.title;
      doc.getElementById('resultSummary').textContent = result.summary;
      doc.getElementById('lifeSupportValue').textContent = `${result.lifeSupportW.toLocaleString('tr-TR')} W`;
      doc.getElementById('continuousValue').textContent = `${result.requiredContinuousW.toLocaleString('tr-TR')} W`;
      doc.getElementById('energyValue').textContent = `${result.requiredNominalWh.toLocaleString('tr-TR')} Wh`;
      doc.getElementById('fullValue').textContent = `${result.fullSystemW.toLocaleString('tr-TR')} W / ${result.fullSystemWh.toLocaleString('tr-TR')} Wh`;
      doc.getElementById('heaterValue').textContent = `${result.heaterAverageW.toLocaleString('tr-TR')} W ortalama`;
      doc.getElementById('gapValue').textContent = result.existingGaps.length ? result.existingGaps.join(' · ') : (result.existingEnough ? 'Açık yok' : 'Mevcut kaynak girilmedi');
      doc.getElementById('assumptions').innerHTML = result.assumptions.map((item) => `<li>${item}</li>`).join('');

      commerce.hidden = !result.commerceAllowed;
      if (result.commerceAllowed) {
        doc.getElementById('productClass').textContent = result.productLabel;
        doc.getElementById('productReason').textContent = result.product === 'battery_air_pump'
          ? `Yalnız ${result.lifeSupportW} W hava yükü ve ${result.requiredNominalWh} Wh hedef için pilli/USB yedek hava sınıfı önceliklidir.`
          : `${result.requiredContinuousW} W sürekli çıkış ve ${result.requiredNominalWh} Wh nominal enerji alt sınırını karşılayan saf sinüs sınıfı gerekir.`;
        affiliateLink.href = amazonUrl(result);
        gates.forEach((gate) => { gate.checked = false; });
        updateCommerceGate();
      } else {
        affiliateLink.removeAttribute('href');
        affiliateLink.setAttribute('aria-disabled', 'true');
      }
      resultSection.focus();
    }

    form.addEventListener('submit', (event) => {
      event.preventDefault();
      const validation = doc.getElementById('validation');
      validation.textContent = '';
      try {
        const input = readInput();
        const result = evaluate(input);
        lastPayload = { schemaVersion: 1, generatedAt: new Date().toISOString(), personalData: false, input, result };
        render(lastPayload);
      } catch (error) {
        validation.textContent = error.message;
        validation.focus();
      }
    });

    form.addEventListener('reset', () => {
      setTimeout(() => {
        lastPayload = null;
        resultSection.hidden = true;
        commerce.hidden = true;
        affiliateLink.removeAttribute('href');
        affiliateLink.setAttribute('aria-disabled', 'true');
        gates.forEach((gate) => { gate.checked = false; });
      }, 0);
    });

    gates.forEach((gate) => gate.addEventListener('change', updateCommerceGate));
    affiliateLink.addEventListener('click', (event) => {
      if (affiliateLink.getAttribute('aria-disabled') !== 'false') event.preventDefault();
    });

    doc.querySelectorAll('[data-preset]').forEach((button) => button.addEventListener('click', () => {
      const presets = {
        nano: { tankType: 'tropical', volumeL: 40, outageHours: 8, waterTempC: 25, filterW: 0, airPumpW: 5, returnPumpW: 0, heaterW: 0, heaterDutyPct: 0, otherW: 0, lightingW: 12 },
        tropical: { tankType: 'tropical', volumeL: 120, outageHours: 8, waterTempC: 26, filterW: 18, airPumpW: 5, returnPumpW: 0, heaterW: 100, heaterDutyPct: 30, otherW: 0, lightingW: 35 },
        marine: { tankType: 'marine', volumeL: 250, outageHours: 6, waterTempC: 25, filterW: 25, airPumpW: 0, returnPumpW: 45, heaterW: 200, heaterDutyPct: 25, otherW: 20, lightingW: 120 },
        existing: { tankType: 'tropical', volumeL: 100, outageHours: 4, waterTempC: 25, filterW: 15, airPumpW: 5, returnPumpW: 0, heaterW: 50, heaterDutyPct: 20, otherW: 0, lightingW: 25, hasExistingSource: true, existingContinuousW: 100, existingWh: 300, existingPureSine: true, realOutageTestPassed: true }
      };
      const preset = presets[button.dataset.preset];
      if (!preset) return;
      Object.entries(preset).forEach(([key, val]) => {
        const node = doc.getElementById(key);
        if (!node) return;
        if (node.type === 'checkbox') node.checked = Boolean(val);
        else node.value = String(val);
      });
    }));

    doc.getElementById('jsonBtn').addEventListener('click', () => {
      if (!lastPayload) return;
      downloadFile('alo186-akvaryum-yedek-guc-plani.json', `${JSON.stringify(lastPayload, null, 2)}\n`, 'application/json;charset=utf-8');
    });

    doc.getElementById('icsBtn').addEventListener('click', () => {
      if (!lastPayload) return;
      downloadFile('alo186-akvaryum-yedek-guc-yeniden-test.ics', buildIcs(lastPayload), 'text/calendar;charset=utf-8');
    });
  }

  return { EFFICIENCY, USABLE_FRACTION, OUTPUT_HEADROOM, TANK_LABELS, evaluate, amazonQuery, amazonUrl, buildIcs, mount };
});
