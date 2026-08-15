(() => {
  'use strict';

  const ROUTE = '/hesaplama/priz-kac-watt-ayni-devre-yuk-uygunluk/';
  const PRODUCT_ROUTES = {
    meter: '/akilli-urun-secimi?intent=priz-tipi-enerji-olcer',
    strip: '/amazon-elektrik-urunleri/akim-korumali-grup-priz-secimi',
    tester: '/amazon-elektrik-urunleri/priz-rcd-test-cihazi-secimi'
  };

  const number = (value) => Number.isFinite(Number(value)) ? Math.max(0, Number(value)) : 0;
  const round = (value, digits = 0) => {
    const factor = 10 ** digits;
    return Math.round(value * factor) / factor;
  };
  const loadKeys = ['kettleW', 'airfryerW', 'microwaveW', 'coffeeW', 'heaterW', 'laundryW', 'electronicsW', 'otherW'];

  function calculate(input) {
    const voltage = Math.min(250, Math.max(200, number(input.voltage) || 230));
    const loads = Object.fromEntries(loadKeys.map((key) => [key, number(input[key])]));
    const totalW = Object.values(loads).reduce((sum, value) => sum + value, 0);
    const currentA = totalW / voltage;
    const candidates = [number(input.breakerA), number(input.socketA)];
    if (input.connection === 'single_strip' || input.connection === 'daisy' || input.connection === 'adapter' || input.connection === 'wound_reel') {
      candidates.push(number(input.stripA));
    }
    const knownLimits = candidates.filter((value) => value > 0);
    const limitA = knownLimits.length ? Math.min(...knownLimits) : 0;
    const planningFactor = input.duration === 'long' ? 0.8 : 0.9;
    const planningA = limitA * planningFactor;
    const planningW = planningA * voltage;
    const remainingW = limitA ? Math.max(0, planningW - totalW) : 0;
    const highPowerCount = Object.values(loads).filter((value) => value >= 1200).length;
    const largestLoadW = Math.max(0, ...Object.values(loads));
    return {
      totalW: round(totalW),
      currentA: round(currentA, 2),
      limitA: round(limitA, 1),
      planningA: round(planningA, 1),
      planningW: round(planningW),
      remainingW: round(remainingW),
      highPowerCount,
      largestLoadW: round(largestLoadW),
      voltage,
      planningFactor
    };
  }

  function decision(code, title, summary, tone = 'warn', affiliate = null, actions = []) {
    return { code, title, summary, tone, affiliate, actions };
  }

  function decide(input) {
    const metrics = calculate(input);
    const physicalHazard = ['hot', 'discolored', 'loose', 'wet', 'cracked'].includes(input.physicalCondition);
    const prohibitedContext = ['medical', 'ev', 'fixed'].includes(input.usageContext);
    const stripConnection = ['single_strip', 'daisy', 'adapter', 'wound_reel'].includes(input.connection);
    const highPowerProfile = ['kitchen', 'heating', 'laundry', 'mixed'].includes(input.usageContext) || metrics.largestLoadW >= 1200;

    if (input.emergency) {
      return { ...decision('emergency', 'Enerjiyi zorlamayın; önce can güvenliği', 'Duman, aktif kıvılcım, elektrik çarpması, erime veya yangın riski varsa prize ve cihaza dokunmayın. Güvenli mesafeye geçin; yangın veya yaralanmada 112 önceliklidir.', 'stop', null, ['Ürünü yeniden çalıştırmayın', 'Güvenli mesafeden 112 veya yetkili elektrikçi rotasına ilerleyin']), metrics };
    }
    if (physicalHazard) {
      return { ...decision('physical_hazard', 'Priz veya bağlantı fiziksel olarak güvenli değil', 'Isınma, renk değişimi, gevşeklik, su veya çatlak varken watt hesabı uygunluk kanıtı değildir. Kullanımı durdurun ve bağlantıyı ölçümle kontrol ettirin.', 'stop', null, ['Fişi çekmek güvenliyse yükü kullanım dışı bırakın', 'Priz, klemens, iletken ve koruma düzenini yetkili elektrikçiye kontrol ettirin']), metrics };
    }
    if (prohibitedContext) {
      const label = input.usageContext === 'medical' ? 'tıbbi/yaşam destek yükü' : input.usageContext === 'ev' ? 'elektrikli araç şarjı' : 'sabit tesisat veya sabit bağlı cihaz';
      return { ...decision('specialist', 'Bu kullanım tüketici tipi priz ürünüyle çözülemez', `${label} için genel çoklayıcı, adaptör veya priz tipi ürün önerisi yapılmaz. Üretici talimatı, devre projesi ve yetkili uzman değerlendirmesi gerekir.`, 'stop', null, ['Genel ürün yönlendirmesini kullanmayın', 'İlgili özel ALO186 aracına veya yetkili uzmana ilerleyin']), metrics };
    }
    if (input.connection === 'daisy') {
      return { ...decision('daisy_chain', 'Çoklayıcıları art arda bağlamayın', 'Birden fazla grup priz veya uzatmayı zincirlemek temas noktalarını artırır, etiket sınırlarını belirsizleştirir ve ısınma riskini büyütür. Ticari yönlendirme kapatıldı.', 'stop', null, ['Zinciri kaldırın', 'Yükleri doğrudan ve ayrı uygun prizlere dağıtın']), metrics };
    }
    if (input.connection === 'adapter') {
      return { ...decision('adapter_chain', 'Yüksek akımı adaptör zincirinden geçirmeyin', 'Fiş dönüştürücü, üçlü adaptör veya gevşek ara bağlantı üzerinden yüksek güçlü cihaz kullanımı uygun kabul edilmez.', 'stop', null, ['Adaptörü kaldırın', 'Doğrudan, topraklı ve etiketi doğrulanmış bağlantı kullanın']), metrics };
    }
    if (input.connection === 'wound_reel' && metrics.totalW > 500) {
      return { ...decision('wound_reel', 'Kablo makarasını sarılı durumda kullanmayın', 'Sarılı makara ısıyı hapseder. Ürün etiketindeki sarılı/açılmış güç sınırları doğrulanmadan bu yük çalıştırılmamalıdır.', 'stop', null, ['Makarayı tamamen açın', 'Uzatma kablosu uygunluk testine geçin']), metrics };
    }
    if (metrics.totalW <= 0) {
      return { ...decision('missing_load', 'Önce çalışan cihazların watt değerlerini girin', 'Toplam yük olmadan priz, sigorta veya grup priz uygunluğu hesaplanamaz.', 'warn', null, ['Cihaz etiketindeki INPUT veya power consumption değerini bulun']), metrics };
    }
    if (input.evidence === 'estimated') {
      const eligible = !stripConnection && metrics.totalW <= 2300 && !highPowerProfile;
      return { ...decision('measure_first', 'Tahmini wattla ürün seçmeyin', 'Gerçek eşzamanlı yükü cihaz etiketinden veya uygun bir priz tipi enerji ölçerle doğrulayın. PSU kapasitesi, pişirme gücü veya pazaryeri başlığı gerçek giriş tüketimi olmayabilir.', 'warn', eligible ? 'meter' : null, ['Gerçek W değerini ölçün veya teknik föyden doğrulayın', 'Ölçüm tamamlanınca testi yeniden çalıştırın']), metrics };
    }
    if (!metrics.limitA || number(input.breakerA) <= 0 || number(input.socketA) <= 0 || (stripConnection && number(input.stripA) <= 0)) {
      return { ...decision('label_needed', 'Devre ve ürün etiketleri eksik', 'Sigorta amperi, priz/çoklayıcı etiket akımı ve kullanılan bağlantı bilinmeden güvenli sınır üretilemez.', 'warn', null, ['Panoyu açmadan sigorta kolundaki amper değerini okuyun', 'Priz veya grup priz etiketini doğrulayın', 'Bilinmiyorsa yetkili elektrikçiden devre kontrolü isteyin']), metrics };
    }
    if (input.earthStatus === 'failed') {
      return { ...decision('earth_failed', 'Koruma iletkeni doğrulanmadı', 'Topraklama gerektiren cihazlarda koruma iletkeni hatası varken ürünü çalıştırmayın. Priz test cihazı tek başına tesisat uygunluk belgesi değildir.', 'stop', null, ['Kullanımı durdurun', 'PE sürekliliği ve hata korumasını ölçtürün']), metrics };
    }
    if (input.rcdStatus === 'failed') {
      return { ...decision('rcd_failed', 'Kaçak akım koruması testten geçmedi', 'Test düğmesi veya ölçümlü RCD testi başarısızsa yük paylaşımı hesabı yeterli değildir. Koruma düzeni doğrulanmadan kullanımı sürdürmeyin.', 'stop', null, ['RCD’yi köprülemeyin', 'Yetkili elektrikçiyle açma süresi ve devre kontrolü yaptırın']), metrics };
    }
    if (input.earthStatus === 'unknown' && highPowerProfile) {
      return { ...decision('earth_unknown', 'Topraklama ve priz durumu önce doğrulanmalı', 'Yüksek güçlü veya metal gövdeli cihazlarda yalnız watt hesabı yeterli değildir. Koruma iletkeni, priz sıkılığı ve RCD düzeni kontrol edilmelidir.', 'warn', null, ['Doğrudan ve topraklı priz kullanın', 'Bilinmeyen tesisatta uzman kontrolü alın']), metrics };
    }
    if (metrics.currentA > metrics.limitA) {
      return { ...decision('overload', 'Hesaplanan akım etiket sınırını aşıyor', `Toplam yaklaşık ${metrics.currentA} A, en düşük doğrulanmış ${metrics.limitA} A sınırının üzerindedir. Daha büyük çoklayıcı takmak devreyi büyütmez.`, 'stop', null, ['Cihazları aynı anda çalıştırmayın', 'Yükleri farklı doğrulanmış devrelere dağıtın', 'Gerekirse devre kapasitesini projeyle değerlendirin']), metrics };
    }
    if (metrics.highPowerCount >= 2) {
      return { ...decision('stagger', 'İki yüksek güçlü cihazı aynı anda çalıştırmayın', 'Toplam akım sınır altında görünse bile birden fazla rezistanslı veya motorlu cihazın eşzamanlı çalışması priz, temas ve devre üzerinde gereksiz ısıl yük oluşturur.', 'warn', null, ['Kettle, airfryer, ütü, ısıtıcı ve benzeri cihazları sırayla kullanın', 'Her cihazı doğrudan uygun prize bağlayın']), metrics };
    }
    if (metrics.currentA > metrics.planningA) {
      return { ...decision('near_limit', 'Yük muhafazakâr planlama bandının üzerinde', `Etiket sınırı aşılmasa da ${input.duration === 'long' ? 'uzun süreli' : 'kısa süreli'} kullanım için kullanılan yüzde ${Math.round(metrics.planningFactor * 100)} planlama bandı geçiliyor. Bu oran bir standart hükmü değil, ısınma ve belirsizlik için ALO186 ön değerlendirme payıdır.`, 'warn', null, ['Yükleri sırayla çalıştırın', 'Priz ve fişte ısınma olup olmadığını izleyin', 'Sürekli kullanım için devreyi ölçtürün']), metrics };
    }
    if (input.evaluationMode === 'existing') {
      return { ...decision('no_buy', 'Mevcut düzen ön kontrolde yeterli — yeni ürün almayın', 'Doğrulanmış etiketler, bağlantı biçimi, fiziksel durum ve hesaplanan akım seçilen planlama bandını karşılıyor. Bu sonuç tesisat uygunluk belgesi değildir; gevşek temas ve gerçek sıcaklık ayrıca izlenmelidir.', 'good', null, ['Cihazları yalnız değerlendirilen biçimde kullanın', 'Fiş ve prizde ısınma, ses veya renk değişimi oluşursa kullanımı durdurun']), metrics };
    }
    if (input.usageContext === 'electronics' && input.needMoreOutlets === 'yes' && metrics.totalW <= Math.min(2300, metrics.planningW) && !highPowerProfile) {
      return { ...decision('electronics_strip', 'Düşük güçlü elektronikler için tek grup priz sınıfı değerlendirilebilir', 'Yalnız TV, modem, bilgisayar çevre birimi gibi düşük güçlü elektroniklerde; tek, topraklı, etiketi doğrulanmış ve zincirlenmeyen grup priz teknik aday olabilir. Isıtıcı, kettle, airfryer, ütü veya beyaz eşya bağlamayın.', 'good', 'strip', ['Toplam W ve etiket A değerini yeniden doğrulayın', 'Tek grup priz kullanın; başka çoklayıcı bağlamayın']), metrics };
    }
    return { ...decision('direct_only', 'Yük kapasite içinde; doğrudan uygun priz kullanın', 'Yüksek güçlü cihaz için yeni çoklayıcı veya adaptör önermek yerine doğrudan, topraklı ve etiketi doğrulanmış priz kullanımı tercih edilmelidir.', 'good', null, ['Cihazı doğrudan uygun prize bağlayın', 'Eşzamanlı cihazları ve kullanım süresini değiştirmeden önce hesabı yenileyin']), metrics };
  }

  function readForm(form) {
    const value = (id) => form.querySelector(`#${id}`)?.value ?? '';
    const checked = (id) => Boolean(form.querySelector(`#${id}`)?.checked);
    return {
      emergency: checked('emergency'),
      evaluationMode: value('evaluationMode'),
      usageContext: value('usageContext'),
      connection: value('connection'),
      duration: value('duration'),
      evidence: value('evidence'),
      voltage: value('voltage'),
      breakerA: value('breakerA'),
      socketA: value('socketA'),
      stripA: value('stripA'),
      physicalCondition: value('physicalCondition'),
      earthStatus: value('earthStatus'),
      rcdStatus: value('rcdStatus'),
      needMoreOutlets: value('needMoreOutlets'),
      kettleW: value('kettleW'),
      airfryerW: value('airfryerW'),
      microwaveW: value('microwaveW'),
      coffeeW: value('coffeeW'),
      heaterW: value('heaterW'),
      laundryW: value('laundryW'),
      electronicsW: value('electronicsW'),
      otherW: value('otherW')
    };
  }

  function render(result, root) {
    const resultBox = root.querySelector('#result');
    resultBox.hidden = false;
    resultBox.className = `result panel ${result.tone}`;
    resultBox.tabIndex = -1;
    resultBox.innerHTML = `
      <span class="status">${result.code.replaceAll('_', ' ')}</span>
      <h2>${result.title}</h2>
      <p>${result.summary}</p>
      <div class="metrics" aria-label="Hesap sonucu">
        <div><span>Toplam yük</span><strong>${result.metrics.totalW} W</strong></div>
        <div><span>Yaklaşık akım</span><strong>${result.metrics.currentA} A</strong></div>
        <div><span>Planlama bandı</span><strong>${result.metrics.planningW || '—'} W</strong></div>
        <div><span>Kalan pay</span><strong>${result.metrics.limitA ? `${result.metrics.remainingW} W` : '—'}</strong></div>
      </div>
      <h3>Güvenli sonraki adımlar</h3>
      <ol>${result.actions.map((item) => `<li>${item}</li>`).join('')}</ol>`;

    const affiliate = root.querySelector('#affiliate');
    const affiliateLink = root.querySelector('#affiliateLink');
    root.querySelectorAll('.affiliate-check').forEach((input) => { input.checked = false; });
    affiliate.hidden = !result.affiliate;
    affiliate.dataset.product = result.affiliate || '';
    affiliateLink.href = result.affiliate ? PRODUCT_ROUTES[result.affiliate] : '#';
    affiliateLink.setAttribute('aria-disabled', 'true');
    affiliateLink.tabIndex = -1;
    affiliateLink.textContent = result.affiliate === 'meter' ? 'Enerji ölçer teknik sınıfını aç' : 'Grup priz teknik sınıfını aç';
    resultBox.focus();
  }

  function updateAffiliate(root) {
    const affiliate = root.querySelector('#affiliate');
    const link = root.querySelector('#affiliateLink');
    if (affiliate.hidden) return;
    const ready = [...root.querySelectorAll('.affiliate-check')].every((input) => input.checked);
    link.setAttribute('aria-disabled', ready ? 'false' : 'true');
    link.tabIndex = ready ? 0 : -1;
  }

  function downloadJson(input, result) {
    const payload = {
      schema: 'alo186-priz-yuk-uygunluk-v127',
      generatedAt: new Date().toISOString(),
      personalDataIncluded: false,
      input,
      result
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'alo186-priz-yuk-uygunluk.json';
    link.click();
    URL.revokeObjectURL(link.href);
  }

  function init(root = document) {
    const form = root.querySelector('#loadForm');
    if (!form) return;
    let lastInput = null;
    let lastResult = null;

    root.querySelectorAll('[data-preset]').forEach((button) => {
      button.addEventListener('click', () => {
        const presets = {
          kitchen: { usageContext: 'kitchen', connection: 'direct', kettleW: 1800, airfryerW: 0, microwaveW: 0, coffeeW: 900, electronicsW: 0, duration: 'short' },
          electronics: { usageContext: 'electronics', connection: 'single_strip', kettleW: 0, airfryerW: 0, microwaveW: 0, coffeeW: 0, electronicsW: 650, duration: 'long' },
          risky: { usageContext: 'mixed', connection: 'daisy', kettleW: 1800, airfryerW: 1700, microwaveW: 0, coffeeW: 0, electronicsW: 150, duration: 'long' }
        };
        const preset = presets[button.dataset.preset];
        Object.entries(preset).forEach(([key, value]) => {
          const field = root.querySelector(`#${key}`);
          if (field) field.value = String(value);
        });
      });
    });

    form.addEventListener('submit', (event) => {
      event.preventDefault();
      lastInput = readForm(form);
      lastResult = decide(lastInput);
      render(lastResult, root);
    });
    root.querySelectorAll('.affiliate-check').forEach((input) => input.addEventListener('change', () => updateAffiliate(root)));
    root.querySelector('#downloadJson')?.addEventListener('click', () => {
      if (lastInput && lastResult) downloadJson(lastInput, lastResult);
    });
    root.querySelector('#printResult')?.addEventListener('click', () => window.print());
  }

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ROUTE, PRODUCT_ROUTES, calculate, decide };
  } else if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', () => init(document));
  }
})();
