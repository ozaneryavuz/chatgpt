(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const parse = (value) => { const n = Number(String(value).replace(',', '.')); return Number.isFinite(n) && n >= 0 ? n : 0; };
  const formatMoney = (value, currency) => new Intl.NumberFormat('tr-TR', { style: 'currency', currency, maximumFractionDigits: currency === 'TRY' ? 0 : 2 }).format(value);
  const escapeHtml = (value) => String(value).replace(/[&<>'\"]/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','\"':'&quot;'}[c]));

  const labels = {
    revenue: 'Ciro / hizmet kaybı', staff: 'Personel bekleme', spoilage: 'Bozulan ürün / stok',
    generator: 'Jeneratör yakıt ve işletme', restart: 'Yeniden başlatma', damage: 'Cihaz hasarı / servis', other: 'Diğer'
  };

  function init() {
    $('generatorUsed').addEventListener('change', () => $('generatorFields').classList.toggle('hidden', !$('generatorUsed').checked));
    $('calculateBtn').addEventListener('click', calculate);
    $('clearBtn').addEventListener('click', clearAll);
    $('exampleBtn').addEventListener('click', fillExample);
    $('copyBtn').addEventListener('click', copySummary);
    $('printBtn').addEventListener('click', () => window.print());
  }

  function calculate() {
    $('validation').textContent = '';
    const duration = parse($('durationHours').value);
    const events = Math.max(1, Math.round(parse($('eventsPerYear').value)));
    const currency = $('currency').value;
    if (!duration) { $('validation').textContent = 'Kesinti süresini saat olarak girin.'; return; }

    const revenue = parse($('revenuePerHour').value) * duration * (Math.min(100, parse($('lostRevenuePercent').value)) / 100);
    const staff = parse($('idleEmployees').value) * parse($('employeeCostPerHour').value) * duration;
    const spoilage = parse($('spoilageCost').value);
    const restart = parse($('restartCost').value);
    const damage = parse($('damageCost').value);
    const other = parse($('otherCost').value);
    let generator = 0;
    if ($('generatorUsed').checked) {
      const loadKw = parse($('generatorLoadKw').value);
      const specific = parse($('specificFuel').value);
      const fuelPrice = parse($('fuelPrice').value);
      const extra = parse($('generatorExtraPercent').value) / 100;
      generator = loadKw * duration * specific * fuelPrice * (1 + extra);
    }

    const items = { revenue, staff, spoilage, generator, restart, damage, other };
    const eventCost = Object.values(items).reduce((sum, value) => sum + value, 0);
    if (!eventCost) { $('validation').textContent = 'En az bir maliyet kalemi girin.'; return; }
    const annual = eventCost * events;
    const hourly = eventCost / duration;
    const twoYear = annual * 2;

    $('eventCost').textContent = formatMoney(eventCost, currency);
    $('annualCost').textContent = formatMoney(annual, currency);
    $('hourlyCost').textContent = formatMoney(hourly, currency);
    $('twoYearExposure').textContent = formatMoney(twoYear, currency);
    renderBreakdown(items, eventCost, currency);
    renderActions(items, annual, duration, currency);
    $('results').classList.remove('hidden');
    $('results').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function renderBreakdown(items, total, currency) {
    const box = $('breakdown');
    box.innerHTML = '';
    Object.entries(items).filter(([, value]) => value > 0).sort((a,b) => b[1]-a[1]).forEach(([key, value]) => {
      const pct = total ? value / total * 100 : 0;
      const row = document.createElement('div');
      row.className = 'breakdown-row';
      row.innerHTML = `<span>${escapeHtml(labels[key])} · %${pct.toFixed(0)}</span><strong>${escapeHtml(formatMoney(value, currency))}</strong>`;
      box.appendChild(row);
    });
  }

  function renderActions(items, annual, duration, currency) {
    const actions = [];
    const dominant = Object.entries(items).sort((a,b) => b[1]-a[1])[0][0];
    if (dominant === 'revenue') actions.push('En kritik hizmetleri ve yükleri belirleyin; kesinti sırasında hangi faaliyetlerin sürmesi gerektiğini yazılı senaryoya bağlayın.');
    if (dominant === 'staff') actions.push('Personelin kesinti anındaki görev, güvenlik ve kontrollü duruş prosedürünü oluşturun.');
    if (items.spoilage > 0) actions.push('Soğuk zincir ve stok için sıcaklık alarmı, kapı açma kuralı ve yedek güç önceliği belirleyin.');
    if (items.generator > 0) actions.push('Jeneratörün gerçek kW yükünü, yakıt tüketimini, transfer süresini ve haftalık test kayıtlarını izleyin.');
    if (items.damage > 0) actions.push('Gerilim olayı ve cihaz hasarı için tarih-saat, fotoğraf, servis raporu ve dağıtım başvuru numarasını saklayın.');
    if (duration <= 1) actions.push('Kısa kesintilerde kritik elektronik ve kontrol sistemleri için UPS köprüleme süresini doğrulayın.');
    if (duration > 4) actions.push('Uzun kesintiler için yakıt lojistiği, yük atma, haberleşme ve vardiya planı oluşturun.');
    if (annual > 0) actions.push(`Yıllık yaklaşık ${formatMoney(annual, currency)} maruziyeti; bakım, UPS, otomasyon veya jeneratör yatırımının toplam sahip olma maliyetiyle karşılaştırın.`);
    const list = $('actionList');
    list.innerHTML = '';
    actions.slice(0,6).forEach((text) => { const li = document.createElement('li'); li.textContent = text; list.appendChild(li); });

    if (annual >= 100000 || $('facilityType').value === 'hotel' || $('facilityType').value === 'industry') {
      $('nextTitle').textContent = 'Profesyonel süreklilik ve kritik yük analizi önerilir';
      $('nextText').textContent = 'Trafo, jeneratör, UPS, transfer sistemi, kritik yük ve bakım durumunu birlikte değerlendiren bir plan oluşturun.';
    } else {
      $('nextTitle').textContent = 'Kesinti hazırlık planınızı oluşturun';
      $('nextText').textContent = 'Kritik cihazları, hedef çalışma süresini ve gerekli yedek güç sınıfını ayrı hesaplayın.';
    }
  }

  function fillExample() {
    $('facilityType').value = 'hotel'; $('durationHours').value = '3'; $('eventsPerYear').value = '6';
    $('currency').value = 'TRY'; $('revenuePerHour').value = '25000'; $('lostRevenuePercent').value = '40';
    $('idleEmployees').value = '18'; $('employeeCostPerHour').value = '350'; $('spoilageCost').value = '12000';
    $('restartCost').value = '8000'; $('damageCost').value = '0'; $('otherCost').value = '5000';
    $('generatorUsed').checked = true; $('generatorFields').classList.remove('hidden'); $('generatorLoadKw').value = '180';
    $('specificFuel').value = '0.28'; $('fuelPrice').value = '50'; $('generatorExtraPercent').value = '12';
  }

  function clearAll() {
    ['revenuePerHour','idleEmployees','employeeCostPerHour','spoilageCost','restartCost','damageCost','otherCost'].forEach((id) => $(id).value = '0');
    $('durationHours').value = '2'; $('eventsPerYear').value = '4'; $('lostRevenuePercent').value = '100';
    $('generatorUsed').checked = false; $('generatorFields').classList.add('hidden'); $('results').classList.add('hidden'); $('validation').textContent = '';
  }

  async function copySummary() {
    const text = ['ALO186 Kesinti Maliyeti Ön Değerlendirmesi', `Olay başı: ${$('eventCost').textContent}`, `Yıllık: ${$('annualCost').textContent}`, `Saat başı: ${$('hourlyCost').textContent}`, 'Bu sonuç resmî zarar veya tazminat hesabı değildir.'].join('\n');
    try { await navigator.clipboard.writeText(text); $('copyBtn').textContent = 'Kopyalandı'; setTimeout(() => $('copyBtn').textContent = 'Özeti kopyala', 1600); }
    catch (_) { window.prompt('Özeti kopyalayın:', text); }
  }

  document.addEventListener('DOMContentLoaded', init);
})();
