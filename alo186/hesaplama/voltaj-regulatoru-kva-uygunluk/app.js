(() => {
  'use strict';

  const $ = (id) => document.getElementById(id);
  const standardKva = [0.5, 1, 1.5, 2, 3, 5, 7.5, 10, 15, 20, 30, 40, 50, 75, 100, 125, 160, 200, 250, 315, 400, 500, 630];
  const amazonSearch = (query) => `https://www.amazon.com.tr/s?k=${encodeURIComponent(query)}&tag=alo186rehber-21`;

  function nextStandard(value) {
    return standardKva.find((item) => item >= value) || Math.ceil(value / 100) * 100;
  }

  function inferredPf(selected, use) {
    if (selected !== 'auto') return Number(selected);
    if (use === 'electronics' || use === 'critical') return 0.9;
    if (use === 'motor') return 0.75;
    return 0.8;
  }

  function track(event, data = {}) {
    if (typeof window.Alo186Track !== 'function') return;
    window.Alo186Track(event, data);
  }

  function resultFromForm() {
    const input = {
      phase: $('phase').value,
      vmin: Number($('vmin').value),
      vmax: Number($('vmax').value),
      frequency: $('frequency').value,
      use: $('use').value,
      loadKw: Number($('loadKw').value),
      pfSelected: $('pf').value,
      motorKw: Number($('motorKw').value || 0),
      startFactor: Number($('startFactor').value),
      installation: $('installation').value,
      continuity: $('continuity').value,
      problem: $('problem').value,
      hazard: $('neutral').checked || $('smoke').checked || $('water').checked
    };

    const nominal = input.phase === 'mono' ? 230 : 400;
    if (input.hazard) {
      return {
        ...input,
        nominal,
        pf: null,
        runningKva: 0,
        startKva: 0,
        derating: 1,
        rawKva: 0,
        selectedKva: 0,
        designKw: 0,
        lowDeviation: 0,
        highDeviation: 0,
        deviation: 0,
        solutionKey: 'hazard',
        solutionLabel: 'Ticari rota kapalı',
        reason: 'Nötr, yanık bağlantı, su veya elektrik çarpması şüphesinde regülatör seçimi yapılmaz.',
        professional: true
      };
    }

    const maxVoltage = input.phase === 'mono' ? 320 : 520;
    if (!(input.vmin >= 80 && input.vmin <= maxVoltage)) throw new Error('En düşük gerilim değeri geçerli aralıkta olmalıdır.');
    if (!(input.vmax >= 80 && input.vmax <= maxVoltage)) throw new Error('En yüksek gerilim değeri geçerli aralıkta olmalıdır.');
    if (input.vmax < input.vmin) throw new Error('En yüksek gerilim, en düşük gerilimden küçük olamaz.');
    if (!(input.loadKw >= 0.05 && input.loadKw <= 500)) throw new Error('Toplam eşzamanlı güç 0,05–500 kW arasında olmalıdır.');
    if (!(input.motorKw >= 0 && input.motorKw <= input.loadKw)) throw new Error('Motor gücü toplam eşzamanlı gücü aşamaz.');

    const pf = inferredPf(input.pfSelected, input.use);
    const runningKva = (input.loadKw / pf) * 1.25;
    const startLoadKw = input.motorKw > 0
      ? Math.max(input.loadKw, (input.loadKw - input.motorKw) + input.motorKw * input.startFactor)
      : input.loadKw;
    const startKva = (startLoadKw / pf) * (input.motorKw > 0 ? 1.1 : 1);
    const lowRatio = input.vmin / nominal;
    const highRatio = input.vmax / nominal;
    const derating = lowRatio < 0.7 ? 1.5 : lowRatio < 0.8 ? 1.35 : lowRatio < 0.9 ? 1.2 : highRatio > 1.15 ? 1.15 : 1;
    const rawKva = Math.max(runningKva, startKva) * derating;
    const selectedKva = nextStandard(rawKva);
    const designKw = Math.max(input.loadKw * 1.25, startLoadKw * (input.motorKw > 0 ? 1.1 : 1));
    const lowDeviation = Math.max(0, ((nominal - input.vmin) / nominal) * 100);
    const highDeviation = Math.max(0, ((input.vmax - nominal) / nominal) * 100);
    const deviation = Math.max(lowDeviation, highDeviation);
    const extreme = input.phase === 'mono'
      ? input.vmin < 150 || input.vmax > 280
      : input.vmin < 270 || input.vmax > 470;
    const nearNominal = input.vmin >= nominal * 0.95 && input.vmax <= nominal * 1.05;

    let solutionKey = 'professional';
    let solutionLabel = 'Profesyonel servo/statik regülatör incelemesi';
    let reason = 'Pano, trifaze, motorlu veya yüksek güçlü yükte kısa devre dayanımı, bypass, faz dengesizliği ve koruma koordinasyonu birlikte projelendirilmelidir.';

    if (input.problem === 'spike') {
      solutionKey = 'spd';
      solutionLabel = 'Regülatör değil, SPD/parafudr değerlendirmesi';
      reason = 'Ani darbe ve yıldırım endişesi sürekli gerilim regülasyonundan farklıdır; uygun SPD koordinasyonu değerlendirilmelidir.';
    } else if (input.continuity === 'zero' || input.use === 'critical') {
      solutionKey = 'ups';
      solutionLabel = 'UPS / kritik güç topolojisi';
      reason = 'Regülatör enerji kesildiğinde yükü beslemez. Sıfıra yakın transfer veya kritik yük için UPS ve yedek enerji birlikte değerlendirilmelidir.';
    } else if (nearNominal && input.frequency === 'rare') {
      solutionKey = 'no_buy';
      solutionLabel = 'Şimdilik regülatör satın almayın';
      reason = 'Girilen gerilim aralığı nominal değere yakın ve olay nadir. Önce farklı zamanlarda ölçüm, olay kaydı ve kök neden kontrolü yapın.';
    } else if (extreme || input.frequency === 'continuous') {
      solutionKey = 'root_cause';
      solutionLabel = 'Önce şebeke / tesisat kök neden incelemesi';
      reason = 'Aşırı geniş veya uzun süreli gerilim sapması yalnız regülatörle örtülmemeli; nötr, bağlantı, kablo, trafo kademesi ve dağıtım şebekesi değerlendirilmelidir.';
    } else if (input.phase === 'mono' && input.installation === 'plug' && input.motorKw === 0 && input.loadKw <= 1.5 && ['electronics', 'mixed'].includes(input.use) && selectedKva <= 3) {
      solutionKey = 'plug_avr';
      solutionLabel = 'Prize takılan AVR / regülatör sınıfı';
      reason = 'Düşük güçlü, monofaze ve motorsuz yükte ürün sınıfı teknik ölçüm ve giriş aralığı doğrulandıktan sonra karşılaştırılabilir.';
    }

    const professional = ['professional', 'root_cause', 'ups'].includes(solutionKey);
    return {
      ...input,
      nominal,
      pf,
      runningKva,
      startKva,
      derating,
      rawKva,
      selectedKva,
      designKw,
      lowDeviation,
      highDeviation,
      deviation,
      solutionKey,
      solutionLabel,
      reason,
      professional
    };
  }

  function setGate() {
    const gate = $('commerce').querySelector('.gate');
    const checked = [...gate.querySelectorAll('.confirm')].every((item) => item.checked);
    $('affiliate').setAttribute('aria-disabled', checked ? 'false' : 'true');
    $('affiliate').tabIndex = checked ? 0 : -1;
  }

  function setList(items) {
    $('steps').replaceChildren(...items.map((text) => {
      const li = document.createElement('li');
      li.textContent = text;
      return li;
    }));
  }

  function render(result) {
    $('result').classList.remove('hidden');
    $('commerce').classList.add('hidden');
    $('professional').classList.add('hidden');
    $('professional').querySelector('a').classList.remove('hidden');

    if (result.solutionKey === 'hazard') {
      $('state').className = 'pill bad';
      $('state').textContent = 'Kullanmayı durdurun';
      $('title').textContent = 'Önce fiziksel ve elektriksel güvenlik';
      $('summary').textContent = 'Regülatör veya UPS bağlamayın. Enerjiyi güvenli biçimde kestirin; duman veya yangın riski varsa güvenli alana geçip 112’yi arayın. Nötr ve bağlantı arızası uzman tarafından ölçülmeden tekrar enerjilendirmeyin.';
      $('designKw').textContent = 'Hesap yok';
      $('designKva').textContent = 'Hesap yok';
      $('deviation').textContent = 'Ölçümle işlem yok';
      $('solution').textContent = 'Ticari rota kapalı';
      setList(['Cihazları ve regülatörü enerjisiz bırakın.', 'Yanık veya gevşek bağlantıya dokunmayın.', 'Nötr, faz gerilimleri ve bağlantılar yetkili uzman tarafından kontrol edilmeden ürüne yönelmeyin.']);
      $('professionalText').textContent = 'Acil ve tehlikeli durumda ürün veya hizmet satışı yerine güvenli uzaklaşma ve resmî acil yardım önceliklidir.';
      $('professional').classList.remove('hidden');
      $('professional').querySelector('a').classList.add('hidden');
      $('result').focus();
      track('voltage_regulator_result', { result: 'hazard' });
      return;
    }

    const stateClass = ['plug_avr', 'no_buy'].includes(result.solutionKey) ? 'good' : 'warn';
    $('state').className = `pill ${stateClass}`;
    $('state').textContent = result.solutionKey === 'plug_avr' ? 'Ürün sınıfı belirlenebilir' : result.solutionKey === 'no_buy' ? 'Satın alma gerekmeyebilir' : 'Teknik doğrulama gerekli';
    $('title').textContent = result.solutionLabel;
    $('summary').textContent = `${result.reason} Hesapta ${result.pf.toLocaleString('tr-TR', { maximumFractionDigits: 2 })} güç faktörü, %25 sürekli çalışma payı ve ${result.derating.toLocaleString('tr-TR', { maximumFractionDigits: 2 })} giriş gerilimi payı kullanıldı.`;
    $('designKw').textContent = `${result.designKw.toLocaleString('tr-TR', { maximumFractionDigits: 2 })} kW`;
    $('designKva').textContent = `${result.selectedKva.toLocaleString('tr-TR', { maximumFractionDigits: 1 })} kVA`;
    $('deviation').textContent = `-%${result.lowDeviation.toLocaleString('tr-TR', { maximumFractionDigits: 1 })} / +%${result.highDeviation.toLocaleString('tr-TR', { maximumFractionDigits: 1 })}`;
    $('solution').textContent = result.solutionLabel;

    const steps = [
      `Ürün veya teklif teknik sayfasında en az ${result.selectedKva.toLocaleString('tr-TR', { maximumFractionDigits: 1 })} kVA sürekli sınıfı ve ${result.designKw.toLocaleString('tr-TR', { maximumFractionDigits: 2 })} kW yük kapasitesini birlikte doğrulayın.`,
      `Giriş gerilim aralığının ölçülen ${result.vmin.toLocaleString('tr-TR')}–${result.vmax.toLocaleString('tr-TR')} V değerlerini derating olmadan kapsayıp kapsamadığını kontrol edin.`,
      'Bypass, kısa devre dayanımı, aşırı yük süresi, çıkış hassasiyeti, tepki süresi, fan sesi ve servis koşullarını karşılaştırın.',
      'Regülatör öncesi/sonrası sigorta, RCD, SPD, topraklama ve kablo kesitinin proje ile uyumunu doğrulayın.'
    ];
    if (result.motorKw > 0) steps.push(`En büyük ${result.motorKw.toLocaleString('tr-TR')} kW motor için ${result.startFactor}× kalkış varsayımını ve regülatörün kısa süreli aşırı yük eğrisini üreticiyle doğrulayın.`);
    if (result.phase === 'three') steps.push('Üç fazın ayrı gerilimlerini, faz dengesizliğini, nötr yapısını ve tek-faz yük dağılımını ölçün.');
    if (result.solutionKey === 'no_buy') steps.push('En az birkaç farklı saat ve yük durumunda ölçüm yapın; sorun tekrarlamıyorsa yeni ürün almayın.');
    if (result.solutionKey === 'spd') steps.push('Ani darbe için Tip 1/2/3 SPD koordinasyonunu ve pano yerleşimini ayrı değerlendirin.');
    if (result.solutionKey === 'ups') steps.push('UPS seçiminde VA yanında gerçek W, transfer süresi, saf sinüs ve runtime tablosunu doğrulayın.');
    setList(steps);

    if (result.solutionKey === 'plug_avr') {
      $('affiliate').href = amazonSearch(`otomatik voltaj regülatörü AVR ${result.selectedKva} kVA 230V`);
      $('commerce').querySelectorAll('.confirm').forEach((item) => { item.checked = false; });
      $('commerce').classList.remove('hidden');
      setGate();
    } else {
      const messages = {
        no_buy: 'Ölçümler nominale yakın ve olay nadir. Yeni ürün yerine ölçüm kaydı ve mevcut tesisatın korunması önerilir.',
        spd: 'Ani darbe/yıldırım senaryosunda regülatör araması açılmaz; SPD seçimi pano ve tesisat koordinasyonu gerektirir.',
        ups: 'Kesintisiz çalışma beklentisinde regülatör tek başına çözüm değildir. UPS topolojisi, akü enerjisi ve transfer süresi birlikte doğrulanmalıdır.',
        root_cause: 'Uzun süreli veya aşırı gerilim sapmasında önce dağıtım şebekesi ve tesisat kök nedeni ölçülmelidir.',
        professional: 'Trifaze, motorlu, pano tipi veya yüksek güçlü regülatörde tek mağaza bağlantısı yerine proje, üretici seçimi ve teknik kabul gerekir.'
      };
      $('professionalText').textContent = messages[result.solutionKey] || messages.professional;
      $('professional').classList.remove('hidden');
    }

    $('result').focus();
    track('voltage_regulator_result', { result: result.solutionKey, phase: result.phase, kva: String(result.selectedKva) });
  }

  $('phase').addEventListener('change', () => {
    if ($('phase').value === 'three') {
      $('vmin').value = '330';
      $('vmax').value = '430';
    } else {
      $('vmin').value = '185';
      $('vmax').value = '250';
    }
  });

  $('test').addEventListener('submit', (event) => {
    event.preventDefault();
    try { render(resultFromForm()); }
    catch (error) { window.alert(error.message); }
  });
  $('commerce').addEventListener('change', setGate);
  $('affiliate').addEventListener('click', (event) => {
    if ($('affiliate').getAttribute('aria-disabled') !== 'false') event.preventDefault();
    else track('voltage_regulator_affiliate_opened', { destination: 'amazon_search' });
  });
  $('print').addEventListener('click', () => window.print());
})();
