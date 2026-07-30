(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const roundUp = (value, step) => Math.ceil(value / step) * step;
  const amazonSearch = (query) => `https://www.amazon.com.tr/s?k=${encodeURIComponent(query)}&tag=alo186rehber-21`;

  function inferredPf(selected, wave) {
    if (selected !== 'auto') return Number(selected);
    if (wave === 'active') return 0.85;
    if (wave === 'simple') return 0.75;
    if (wave === 'transformer') return 0.65;
    return 0.65;
  }

  function commerceAllowed(result) {
    return !result.hazard && !result.professional && result.runtime <= 30 && result.watts <= 1500 && ['standby', 'line'].includes(result.topologyKey);
  }

  function topologyFor(input) {
    if (input.use === 'medical') return { key: 'professional', label: 'Profesyonel kritik güç sistemi', reason: 'Sağlık, yangın veya can güvenliği yükünde tek cihaz önerisi ve affiliate yönlendirmesi uygun değildir.' };
    if (input.use === 'motor' || input.wave === 'transformer') return { key: 'professional', label: 'İnverter / jeneratör / özel UPS incelemesi', reason: 'Motor, kompresör ve trafo yüklerinde kalkış akımı ile dalga biçimi üretici tarafından doğrulanmalıdır.' };
    if (input.sensitivity === 'zero' || input.use === 'server' || input.environment === 'rack') return { key: 'online', label: 'Online çift dönüşümlü UPS', reason: 'Sıfıra yakın transfer, gerilim dönüşümü ve profesyonel izleme ihtiyacı öne çıkıyor.' };
    if (input.use === 'network' && input.watts <= 120 && input.runtime <= 30) return { key: 'mini', label: 'DC mini UPS veya saf sinüs line-interactive', reason: 'Modem/ONT gibi DC yüklerde önce voltaj, polarite, jak ve toplam watt doğrulanmalıdır.' };
    if (input.sensitivity === 'reboot' && input.wave === 'simple' && input.runtime <= 10 && input.watts <= 500) return { key: 'standby', label: 'Standby / offline UPS', reason: 'Düşük hassasiyetli ve kısa süreli düşük yükte temel UPS sınıfı yeterli olabilir.' };
    return { key: 'line', label: 'Saf sinüs line-interactive UPS', reason: 'Aktif PFC elektronik ve kısa/orta kesinti için gerilim düzenleme ile kısa transfer dengeli bir başlangıç noktasıdır.' };
  }

  function resultFromForm() {
    const input = {
      use: $('use').value,
      watts: Number($('watts').value),
      peak: Number($('peak').value || 0),
      pfSelected: $('pf').value,
      runtime: Number($('runtime').value),
      sensitivity: $('sensitivity').value,
      wave: $('wave').value,
      environment: $('environment').value,
      hazard: $('smoke').checked || $('battery').checked || $('water').checked
    };
    if (!(input.watts >= 10 && input.watts <= 5000)) throw new Error('Sürekli yük 10–5000 W arasında olmalıdır.');
    if (!(input.peak >= 0 && input.peak <= 12000)) throw new Error('Tepe yükü 0–12000 W arasında olmalıdır.');
    const pf = inferredPf(input.pfSelected, input.wave);
    const designW = roundUp(Math.max(input.watts * 1.25, input.peak > 0 ? input.peak * 1.10 : 0), 50);
    const designVA = roundUp(Math.max(input.watts * 1.25 / pf, input.peak > 0 ? input.peak * 1.10 / pf : 0), 50);
    const energyWh = roundUp((input.watts * (input.runtime / 60)) / (0.85 * 0.80), 10);
    const topology = topologyFor(input);
    const professional = topology.key === 'professional' || topology.key === 'online' || input.runtime > 30 || input.watts > 1500;
    return { ...input, pf, designW, designVA, energyWh, topologyKey: topology.key, topologyLabel: topology.label, topologyReason: topology.reason, professional };
  }

  function setGate(link, gate) {
    const checked = [...gate.querySelectorAll('.confirm')].every((item) => item.checked);
    link.setAttribute('aria-disabled', checked ? 'false' : 'true');
    link.tabIndex = checked ? 0 : -1;
  }

  function render(result) {
    const hazard = result.hazard;
    $('result').classList.remove('hidden');
    $('commerce').classList.add('hidden');
    $('professional').classList.add('hidden');
    $('state').className = `pill ${hazard ? 'bad' : result.professional ? 'warn' : 'good'}`;

    if (hazard) {
      $('state').textContent = 'Kullanmayı durdurun';
      $('title').textContent = 'Fiziksel veya elektriksel güvenlik riski seçildi.';
      $('summary').textContent = "UPS'i veya aküyü açmayın, şarj etmeyin ve teste devam etmeyin. Enerjiyi güvenli biçimde kestirin; duman veya yangın riski varsa güvenli alana geçerek 112’yi arayın.";
      $('va').textContent = 'Hesap yok';
      $('watt').textContent = 'Hesap yok';
      $('wh').textContent = 'Hesap yok';
      $('topology').textContent = 'Ticari rota kapalı';
      $('steps').innerHTML = '<li>Cihazı yanıcı malzemelerden uzak ve enerjisiz bırakın.</li><li>Şişmiş veya sızdıran aküye temas etmeyin.</li><li>Yetkili servis veya elektrik uzmanı incelemesi olmadan tekrar enerjilendirmeyin.</li>';
      $('professionalText').textContent = 'Acil ve hasarlı cihaz durumunda ürün veya hizmet satışı yerine güvenli uzaklaşma ve resmî acil yardım önceliklidir.';
      $('professional').classList.remove('hidden');
      $('professional').querySelector('a').classList.add('hidden');
      $('result').focus();
      return;
    }

    $('professional').querySelector('a').classList.remove('hidden');
    $('state').textContent = result.professional ? 'Profesyonel doğrulama' : 'Ürün sınıfı belirlenebilir';
    $('title').textContent = result.topologyLabel;
    $('summary').textContent = `${result.topologyReason} Hesap, ${result.pf.toLocaleString('tr-TR',{maximumFractionDigits:2})} güç faktörü ve %25 sürekli güç payıyla yaklaşık alt sınır üretir.`;
    $('va').textContent = `${result.designVA.toLocaleString('tr-TR')} VA`;
    $('watt').textContent = `${result.designW.toLocaleString('tr-TR')} W`;
    $('wh').textContent = `${result.energyWh.toLocaleString('tr-TR')} Wh`;
    $('topology').textContent = result.topologyLabel;

    const steps = [
      `UPS teknik sayfasında en az ${result.designVA.toLocaleString('tr-TR')} VA ve ${result.designW.toLocaleString('tr-TR')} W değerlerinin birlikte sağlandığını kontrol edin.`,
      'Üreticinin gerçek yükte runtime tablosunu ve akü kartuşu kodunu doğrulayın.',
      result.wave === 'active' || result.use === 'gaming' ? 'Aktif PFC güç kaynağı için saf sinüs çıkış ve üretici uyumluluğunu doğrulayın.' : 'Çıkış dalga biçimi ve bağlı cihaz üretici uyumluluğunu doğrulayın.',
      'Priz tipi, USB/ağ yönetimi, ses seviyesi, bypass ve değiştirilebilir akü ihtiyacını kullanım yerine göre kontrol edin.'
    ];
    if (result.runtime > 30) steps.push('30 dakikayı aşan hedeflerde yalnız VA büyütmek yerine haricî akü, power station, inverter-batarya veya jeneratör seçeneğini karşılaştırın.');
    if (result.use === 'network') steps.push('DC mini UPS düşünülüyorsa çıkış voltajı, polarite, jak ölçüsü ve modem+ONT toplam akımını ayrı doğrulayın.');
    if (result.peak > 0) steps.push(`Girilen ${result.peak.toLocaleString('tr-TR')} W tepe değeri için üreticinin kısa süreli aşırı yük süresini kontrol edin.`);
    $('steps').innerHTML = steps.map((item) => `<li>${item}</li>`).join('');

    if (commerceAllowed(result)) {
      const query = result.topologyKey === 'standby'
        ? `UPS ${result.designVA} VA ${result.designW} W`
        : `saf sinüs line interactive UPS ${result.designVA} VA ${result.designW} W`;
      $('affiliate').href = amazonSearch(query);
      $('commerce').classList.remove('hidden');
      const gate = $('commerce').querySelector('.gate');
      gate.querySelectorAll('.confirm').forEach((item) => { item.checked = false; });
      setGate($('affiliate'), gate);
    } else {
      $('professionalText').textContent = result.topologyKey === 'mini'
        ? "DC mini UPS veya ağ UPS'i seçmeden önce voltaj, polarite, jak ve toplam watt hesabını tamamlayın. Genel mağaza araması bu aşamada açılmaz."
        : 'Kritik, uzun süreli, rack, online UPS veya yüksek güçlü yükte tek ürün bağlantısı yerine proje, seçicilik, akü ve kabul koşulları birlikte doğrulanmalıdır.';
      $('professional').classList.remove('hidden');
    }
    $('result').focus();
  }

  $('test').addEventListener('submit', (event) => {
    event.preventDefault();
    try { render(resultFromForm()); }
    catch (error) { alert(error.message); }
  });
  $('commerce').addEventListener('change', () => setGate($('affiliate'), $('commerce').querySelector('.gate')));
  $('affiliate').addEventListener('click', (event) => {
    if ($('affiliate').getAttribute('aria-disabled') !== 'false') event.preventDefault();
  });
  $('print').addEventListener('click', () => window.print());
})();
