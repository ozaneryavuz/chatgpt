(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.Alo186RoomLighting = api;
  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', () => api.mount(document), { once: true });
    else api.mount(document);
  }
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const ROOM_PROFILES = Object.freeze({
    living: { label: 'Salon / oturma odası', lux: 150, kelvin: 3000, cri: 80 },
    bedroom: { label: 'Yatak odası', lux: 120, kelvin: 2700, cri: 80 },
    kitchen: { label: 'Mutfak', lux: 300, kelvin: 4000, cri: 90 },
    study: { label: 'Çalışma / okuma alanı', lux: 500, kelvin: 4000, cri: 90 },
    corridor: { label: 'Koridor / antre', lux: 100, kelvin: 3000, cri: 80 },
    bathroom: { label: 'Banyo / ayna alanı', lux: 200, kelvin: 4000, cri: 90 },
    outdoor: { label: 'Balkon / açık alan', lux: 75, kelvin: 3000, cri: 80 },
    decorative: { label: 'Dekoratif yardımcı ışık', lux: 50, kelvin: 2700, cri: 80 }
  });

  const SURFACE_FACTORS = Object.freeze({ light: 0.80, medium: 0.70, dark: 0.60 });
  const PRODUCT_LABELS = Object.freeze({
    e27_led: 'E27 LED ampul',
    sensor_bulb: 'Sensörlü E27 LED ampul',
    task_lamp: 'Ayarlanabilir çalışma lambası',
    solar_outdoor: 'Solar dış mekân lambası'
  });

  function number(value, name, min, max) {
    const parsed = Number(value);
    if (!Number.isFinite(parsed) || parsed < min || parsed > max) {
      throw new Error(`${name} ${min}–${max} aralığında olmalıdır.`);
    }
    return parsed;
  }

  function roundUp(value, step) {
    return Math.ceil(value / step) * step;
  }

  function recommendedKelvin(room, use) {
    if (use === 'relax' || use === 'night') return 2700;
    if (use === 'task') return 4000;
    return ROOM_PROFILES[room].kelvin;
  }

  function recommendedLux(room, use) {
    const base = ROOM_PROFILES[room].lux;
    if (use === 'task') return Math.max(base, 500);
    if (use === 'relax') return Math.min(base, 120);
    if (use === 'night') return Math.min(base, 50);
    return base;
  }

  function preferredBulbLumens(deficit) {
    if (deficit <= 1700) return 806;
    if (deficit <= 3600) return 1055;
    return 1521;
  }

  function chooseProduct(input) {
    if (input.use === 'task' && !input.fixedInstallation) return 'task_lamp';
    if (input.room === 'outdoor' && input.solarPossible && !input.fixedInstallation) return 'solar_outdoor';
    if (input.motionSensor && input.socketType === 'e27' && !input.fixedInstallation) return 'sensor_bulb';
    if (input.socketType === 'e27' && !input.fixedInstallation) return 'e27_led';
    return null;
  }

  function evaluate(raw) {
    const room = ROOM_PROFILES[raw.room] ? raw.room : 'living';
    const use = ['general', 'task', 'relax', 'night'].includes(raw.use) ? raw.use : 'general';
    const surface = SURFACE_FACTORS[raw.surface] ? raw.surface : 'medium';
    const areaM2 = number(raw.areaM2, 'Alan', 1, 250);
    const currentLumens = number(raw.currentLumens == null || raw.currentLumens === '' ? 0 : raw.currentLumens, 'Mevcut toplam lümen', 0, 100000);
    const maintenanceFactor = 0.85;
    const targetLux = recommendedLux(room, use);
    const targetKelvin = recommendedKelvin(room, use);
    const targetCri = Math.max(ROOM_PROFILES[room].cri, use === 'task' ? 90 : 80);
    const requiredLumens = roundUp((areaM2 * targetLux) / (SURFACE_FACTORS[surface] * maintenanceFactor), 50);
    const deficitLumens = Math.max(0, requiredLumens - currentLumens);
    const enoughThreshold = requiredLumens * 0.90;
    const bulbLumens = preferredBulbLumens(deficitLumens || requiredLumens);
    const approximateCount = deficitLumens > 0 ? Math.max(1, Math.ceil(deficitLumens / bulbLumens)) : 0;

    const input = {
      room,
      use,
      surface,
      areaM2,
      currentLumens,
      socketType: raw.socketType || 'unknown',
      hasExisting: Boolean(raw.hasExisting),
      existingSafe: Boolean(raw.existingSafe),
      electricalHazard: Boolean(raw.electricalHazard),
      fixedInstallation: Boolean(raw.fixedInstallation),
      dimmerPresent: Boolean(raw.dimmerPresent),
      dimmerCompatible: Boolean(raw.dimmerCompatible),
      enclosedFixture: Boolean(raw.enclosedFixture),
      enclosedRated: Boolean(raw.enclosedRated),
      wetZone: Boolean(raw.wetZone),
      ipRated: Boolean(raw.ipRated),
      motionSensor: Boolean(raw.motionSensor),
      solarPossible: Boolean(raw.solarPossible)
    };

    let state = 'commerce';
    let title = 'Gerçek aydınlatma açığı doğrulandı.';
    let summary = 'Teknik ölçütleri sağlayan düşük riskli taşınabilir veya değiştirilebilir ürün sınıfını karşılaştırabilirsiniz.';

    if (input.electricalHazard) {
      state = 'hazard';
      title = 'Enerjiyi güvenli biçimde kestirin; ürün seçimine devam etmeyin.';
      summary = 'Yanık kokusu, erime, kıvılcım, gevşek duy, açık iletken veya su teması varsa lambayı, anahtarı ya da armatürü kullanmayın. Güvenli alana geçin ve yetkili elektrikçi çağırın; yangın veya elektrik çarpması riski varsa 112’yi arayın.';
    } else if (input.fixedInstallation || (room === 'bathroom' && input.wetZone && !input.ipRated)) {
      state = 'professional';
      title = 'Sabit tesisat veya ıslak hacim için profesyonel seçim gerekir.';
      summary = 'Yeni armatür hattı, sürücü, tavan bağlantısı, ıslak hacim veya dış ortam IP sınıfı yalnız ampul seçimiyle çözülemez. Koruma, kablo, montaj bölgesi ve ürün talimatı birlikte doğrulanmalıdır.';
    } else if (input.socketType === 'unknown' || input.socketType === 'integrated') {
      state = 'evidence';
      title = 'Duy veya armatür tipi doğrulanmadan ürün gösterilmez.';
      summary = 'E27, GU10 veya bütünleşik LED ayrımını; gerilim, azami güç ve armatür etiketini kontrol edin. Bütünleşik LED arızasında yalnız ampul satın almak çözüm olmayabilir.';
    } else if (input.hasExisting && !input.existingSafe) {
      state = 'evidence';
      title = 'Mevcut armatür güvenliği doğrulanmadan yeni ampul önermeyin.';
      summary = 'Gevşeklik, kararma, sık arıza, titreşim veya aşırı ısınma varsa önce duy, anahtar, bağlantı ve besleme koşulları kontrol edilmelidir.';
    } else if (input.dimmerPresent && !input.dimmerCompatible) {
      state = 'evidence';
      title = 'Dimmer ve LED uyumu doğrulanmalı.';
      summary = 'Dimmerli devrede yalnız “dimmable” ifadesi yeterli değildir. Dimmer tipi, asgari yük, sürücü uyumu ve titreme davranışı tam model düzeyinde doğrulanmalıdır.';
    } else if (input.enclosedFixture && !input.enclosedRated) {
      state = 'evidence';
      title = 'Kapalı armatür uygunluğu doğrulanmalı.';
      summary = 'Kapalı armatürde sıcaklık artabilir. Tam LED modelinin kapalı armatür kullanımına izin verdiği üretici belgesinde doğrulanmadan ürün yolu açılmaz.';
    } else if (input.hasExisting && input.existingSafe && currentLumens >= enoughThreshold) {
      state = 'no_buy';
      title = 'Mevcut aydınlatma yeterli: yeni ürün almayın.';
      summary = 'Tahmini ışık düzeyi hedefin yaklaşık yüzde 90’ını karşılıyor ve mevcut sistem güvenli olarak işaretlendi. Önce yerleşim, temizlik, açık renk yüzey ve görev lambası konumunu iyileştirin.';
    }

    let product = null;
    if (state === 'commerce') {
      product = chooseProduct(input);
      if (!product) {
        state = 'evidence';
        title = 'Doğrudan düşük riskli ürün yolu için teknik kanıt eksik.';
        summary = 'Duy tipi, montaj biçimi veya kullanım ortamı doğrudan tüketici ürünü ön elemesine uygun değil. Sabit armatür ve özel duy seçiminde uzman veya üretici belgesiyle ilerleyin.';
      }
    }

    return {
      state,
      title,
      summary,
      roomLabel: ROOM_PROFILES[room].label,
      targetLux,
      targetKelvin,
      targetCri,
      requiredLumens,
      currentLumens,
      deficitLumens,
      bulbLumens,
      approximateCount,
      product,
      productLabel: product ? PRODUCT_LABELS[product] : null,
      noBuy: state === 'no_buy',
      commerceAllowed: state === 'commerce' && Boolean(product),
      assumptions: [
        `Yüzey yansıtma sınıfı: ${surface}`,
        `Bakım katsayısı: ${maintenanceFactor}`,
        'Sonuç fotometrik proje veya ürün onayı değildir.'
      ]
    };
  }

  function amazonQuery(result) {
    const kelvin = `${result.targetKelvin}K`;
    if (result.product === 'task_lamp') return `ayarlanabilir çalışma lambası CRI 90 ${kelvin}`;
    if (result.product === 'sensor_bulb') return `sensörlü E27 LED ampul ${kelvin}`;
    if (result.product === 'solar_outdoor') return 'solar dış mekan lamba IP65';
    return `E27 LED ampul ${result.bulbLumens} lümen ${kelvin} CRI ${result.targetCri}`;
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
    start.setDate(start.getDate() + 180);
    const description = `Oda: ${payload.result.roomLabel}. Hedef: ${payload.result.requiredLumens} lm, ${payload.result.targetKelvin} K, CRI ${payload.result.targetCri}. Titreme, ısınma, arıza, kullanım amacı ve mevcut sistem yeterliliğini yeniden kontrol edin.`;
    return [
      'BEGIN:VCALENDAR',
      'VERSION:2.0',
      'PRODID:-//ALO186//Oda Aydinlatma Kontrolu//TR',
      'BEGIN:VEVENT',
      `UID:alo186-lighting-${Date.now()}@alo186.com`,
      `DTSTART;VALUE=DATE:${dateStamp(start)}`,
      'SUMMARY:ALO186 oda aydınlatması yeniden kontrolü',
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
    const form = doc.getElementById('lightingForm');
    if (!form || form.dataset.mounted === 'true') return;
    form.dataset.mounted = 'true';

    const resultSection = doc.getElementById('result');
    const commerce = doc.getElementById('commerce');
    const affiliateLink = doc.getElementById('affiliateLink');
    const gates = [...doc.querySelectorAll('.commerce-gate')];
    let lastPayload = null;

    function readInput() {
      const checked = (id) => Boolean(doc.getElementById(id).checked);
      const value = (id) => doc.getElementById(id).value;
      return {
        room: value('room'),
        use: value('use'),
        surface: value('surface'),
        areaM2: value('areaM2'),
        currentLumens: value('currentLumens'),
        socketType: value('socketType'),
        hasExisting: checked('hasExisting'),
        existingSafe: checked('existingSafe'),
        electricalHazard: checked('electricalHazard'),
        fixedInstallation: checked('fixedInstallation'),
        dimmerPresent: checked('dimmerPresent'),
        dimmerCompatible: checked('dimmerCompatible'),
        enclosedFixture: checked('enclosedFixture'),
        enclosedRated: checked('enclosedRated'),
        wetZone: checked('wetZone'),
        ipRated: checked('ipRated'),
        motionSensor: checked('motionSensor'),
        solarPossible: checked('solarPossible')
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
      doc.getElementById('state').textContent = ({ hazard: 'Ticari yol kapalı', professional: 'Uzman doğrulaması', evidence: 'Kanıt gerekli', no_buy: 'Satın alma yok', commerce: 'Koşullu ürün yolu' })[result.state];
      doc.getElementById('resultTitle').textContent = result.title;
      doc.getElementById('resultSummary').textContent = result.summary;
      doc.getElementById('luxValue').textContent = `${result.targetLux.toLocaleString('tr-TR')} lx`;
      doc.getElementById('lumenValue').textContent = `${result.requiredLumens.toLocaleString('tr-TR')} lm`;
      doc.getElementById('kelvinValue').textContent = `${result.targetKelvin.toLocaleString('tr-TR')} K`;
      doc.getElementById('criValue').textContent = `CRI ${result.targetCri}+`;
      doc.getElementById('deficitValue').textContent = result.deficitLumens > 0 ? `${result.deficitLumens.toLocaleString('tr-TR')} lm` : 'Açık yok';
      doc.getElementById('countValue').textContent = result.approximateCount > 0 ? `${result.approximateCount} × yaklaşık ${result.bulbLumens} lm` : 'Yeni ampul gerekmiyor';
      doc.getElementById('assumptions').innerHTML = result.assumptions.map((item) => `<li>${item}</li>`).join('');

      commerce.hidden = !result.commerceAllowed;
      if (result.commerceAllowed) {
        doc.getElementById('productClass').textContent = result.productLabel;
        doc.getElementById('productReason').textContent = `${result.deficitLumens.toLocaleString('tr-TR')} lm açık için yaklaşık ${result.approximateCount} adet ${result.bulbLumens} lm sınıfı başlangıç noktasıdır. Yerleşim, kamaşma ve tam ürün etiketi yeniden doğrulanmalıdır.`;
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
        living: { room: 'living', use: 'general', surface: 'medium', areaM2: 22, currentLumens: 2400, socketType: 'e27', hasExisting: true, existingSafe: true },
        study: { room: 'study', use: 'task', surface: 'light', areaM2: 10, currentLumens: 900, socketType: 'e27', hasExisting: true, existingSafe: true },
        corridor: { room: 'corridor', use: 'general', surface: 'medium', areaM2: 7, currentLumens: 0, socketType: 'e27', hasExisting: false, existingSafe: false, motionSensor: true },
        outdoor: { room: 'outdoor', use: 'night', surface: 'dark', areaM2: 12, currentLumens: 0, socketType: 'none', hasExisting: false, existingSafe: false, solarPossible: true }
      };
      const preset = presets[button.dataset.preset];
      if (!preset) return;
      Object.entries(preset).forEach(([key, value]) => {
        const node = doc.getElementById(key);
        if (!node) return;
        if (node.type === 'checkbox') node.checked = Boolean(value);
        else node.value = String(value);
      });
    }));

    doc.getElementById('jsonBtn').addEventListener('click', () => {
      if (!lastPayload) return;
      downloadFile('alo186-oda-aydinlatma-plani.json', `${JSON.stringify(lastPayload, null, 2)}\n`, 'application/json;charset=utf-8');
    });

    doc.getElementById('icsBtn').addEventListener('click', () => {
      if (!lastPayload) return;
      downloadFile('alo186-aydinlatma-yeniden-kontrol.ics', buildIcs(lastPayload), 'text/calendar;charset=utf-8');
    });
  }

  return { ROOM_PROFILES, evaluate, amazonQuery, amazonUrl, buildIcs, mount };
});
