(() => {
  'use strict';

  const truthy = (value) => Boolean(value === true || value === 'on' || value === 'true');
  const number = (value, fallback = 0) => Number.isFinite(Number(value)) ? Number(value) : fallback;
  const unique = (items) => [...new Set(items.filter(Boolean))];
  const roundPair = (value, mode) => mode === 'pair' && value % 2 ? value + 1 : value;

  function evaluate(raw) {
    const data = { ...raw };
    const stops = [];
    const professional = [];
    const evidence = [];
    const actions = [];
    const strengths = [];

    const deviceCount = Math.max(1, Math.min(20, number(data.deviceCount, 1)));
    const cellsPerDevice = Math.max(1, Math.min(8, number(data.cellsPerDevice, 2)));
    const activeCells = deviceCount * cellsPerDevice;
    const slots = Math.max(1, Math.min(16, number(data.slots, 4)));
    const chargeHours = Math.max(0.5, Math.min(48, number(data.chargeHours, 8)));
    const serviceDays = Math.max(0.25, Math.min(365, number(data.serviceDays, 7)));
    const existingSpare = Math.max(0, Math.min(100, number(data.existingSpare, 0)));

    if (truthy(data.damage)) stops.push('Sızıntılı, şişmiş, korozyonlu veya aşırı ısınan hücreleri döngü planına dahil etmeyin ve şarj etmeyin.');
    if (['smoke', 'co', 'medical', 'safety'].includes(data.deviceClass)) professional.push('Alarm, tıbbi veya can güvenliği cihazında pil kimyası ve yedek adedi tam model üretici kılavuzuyla belirlenmelidir; genel NiMH döngü hesabı kullanılmaz.');
    if (data.manual === 'no') professional.push('Cihaz NiMH şarjlı pili kabul etmiyor; döngü planı oluşturmayın.');
    if (data.manual === 'unknown') evidence.push('Cihazın 1,2 V NiMH kullanımına izin verip vermediği doğrulanmadı.');
    if (!['AA', 'AAA'].includes(data.size)) evidence.push('AA veya AAA pil boyutu doğrulanmadı.');
    if (data.chargerMode === 'unknown') evidence.push('Şarj cihazının bağımsız kanal mı, çift kanal mı olduğu bilinmiyor.');
    if (data.chargerStatus === 'unknown') evidence.push('Şarj cihazının gerçek şarj, kesme ve ısınma testi tamamlanmadı.');
    if (data.currentSet === 'unknown') evidence.push('Çalışan pil setinin aynı kimya, yaş ve kapasite sınıfında olduğu doğrulanmadı.');

    const fullContinuity = data.downtime === 'no';
    const rawBackup = fullContinuity ? activeCells : cellsPerDevice;
    const targetBackup = roundPair(rawBackup, data.chargerMode);
    const targetTotal = activeCells + targetBackup;
    const requiredAdditional = Math.max(0, targetBackup - existingSpare);
    const chargeBatches = Math.max(1, Math.ceil(targetBackup / slots));
    const totalChargeHours = chargeBatches * chargeHours;
    const availableWindowHours = serviceDays * 24;
    const chargerCapacityPass = totalChargeHours <= availableWindowHours;

    if (data.chargerMode === 'pair' && targetBackup !== rawBackup) actions.push('Çift kanal/pair şarj cihazı nedeniyle yedek hücre sayısı bir üst çift sayıya yuvarlandı.');
    if (!chargerCapacityPass) actions.push('Mevcut şarj cihazı, gözlenen pil değiştirme süresi içinde hedef yedek seti tamamlayamıyor. Daha fazla hücre almak yerine önce kanal ve şarj süresi darboğazını çözün.');
    if (existingSpare > targetBackup * 2) actions.push('Mevcut yedek sayısı hedefin iki katından fazla. Yeni pil almadan önce hücreleri etiketleyip gerçek kapasite ve kullanım sırasını test edin.');
    if (data.currentSet === 'mixed') stops.push('Farklı kimya, yaş, kapasite veya dolulukta hücreleri aynı cihaz setinde kullanmayın.');
    if (data.chargerStatus === 'fault') stops.push('Aşırı ısınan, hasarlı veya kesme davranışı arızalı şarj cihazını kullanmayın.');

    if (data.manual === 'yes') strengths.push('Cihaz kılavuzu 1,2 V NiMH kullanımına izin veriyor.');
    if (data.currentSet === 'healthy') strengths.push('Çalışan set aynı kimya, yaş ve kapasite sınıfında.');
    if (data.chargerStatus === 'good') strengths.push('Şarj cihazı gerçek şarj ve kesme testini geçti.');
    if (existingSpare >= targetBackup) strengths.push('Mevcut yedek hücre sayısı hedef döngüyü karşılıyor.');
    if (chargerCapacityPass) strengths.push('Şarj kapasitesi gözlenen değiştirme süresi içinde yedek seti tamamlayabiliyor.');

    const compatible = data.manual === 'yes' && ['AA', 'AAA'].includes(data.size);
    const existingPass = compatible
      && data.currentSet === 'healthy'
      && data.chargerStatus === 'good'
      && data.chargerMode !== 'unknown'
      && existingSpare >= targetBackup
      && chargerCapacityPass;

    let status = 'recommend';
    let headline = 'Gereken en küçük pil döngüsü hazır';
    if (stops.length) {
      status = 'stop';
      headline = 'Pil döngüsünü durdurun ve hasarlı ekipmanı ayırın';
    } else if (professional.length) {
      status = 'professional';
      headline = 'Tam model üretici pil planı gerekli';
    } else if (existingPass) {
      status = 'no-buy';
      headline = 'Mevcut pil döngüsü yeterli — yeni ürün almayın';
    } else if (evidence.length) {
      status = 'evidence';
      headline = 'Adet hesaplamadan önce eksik uyum kanıtlarını tamamlayın';
    }

    const categories = [];
    if (compatible && requiredAdditional > 0) categories.push('rechargeable_nimh_battery');
    if (compatible && (data.chargerStatus !== 'good' || data.chargerMode === 'unknown' || !chargerCapacityPass)) categories.push('nimh_battery_charger');
    const confirmations = truthy(data.confirmNeed) && truthy(data.confirmSpecs) && truthy(data.confirmAffiliate);
    const affiliateAllowed = status === 'recommend' && categories.length > 0 && confirmations;

    return {
      ok: true,
      status,
      headline,
      activeCells,
      targetBackup,
      targetTotal,
      requiredAdditional,
      chargeBatches,
      totalChargeHours: Number(totalChargeHours.toFixed(1)),
      availableWindowHours: Number(availableWindowHours.toFixed(1)),
      chargerCapacityPass,
      stops: unique(stops),
      professional: unique(professional),
      evidence: unique(evidence),
      actions: unique(actions),
      strengths: unique(strengths),
      categories,
      affiliateAllowed,
      privacy: 'Plan tarayıcıda hesaplanır; cihaz markası, seri numarası, adres veya kullanıcı hesabı istenmez.'
    };
  }

  function fromForm(form) {
    const data = Object.fromEntries(new FormData(form).entries());
    for (const name of ['damage', 'confirmNeed', 'confirmSpecs', 'confirmAffiliate']) data[name] = Boolean(form.elements[name]?.checked);
    return data;
  }

  const list = (title, items) => items.length ? `<section><h3>${title}</h3><ul>${items.map((item) => `<li>${item}</li>`).join('')}</ul></section>` : '';
  const categoryLabel = (id) => id === 'nimh_battery_charger' ? 'AA/AAA NiMH şarj cihazı' : 'AA/AAA NiMH şarj edilebilir pil';

  function render(result) {
    const output = document.querySelector('#result');
    output.hidden = false;
    output.dataset.status = result.status;
    const affiliate = result.affiliateAllowed
      ? `<div class="affiliate"><strong>Şeffaf satış ortaklığı ürün sınıfı</strong><p>Sonraki sayfa Amazon satış ortaklığı bağlantıları içerebilir. ALO186 fiyat, stok, puan veya garanti yayımlamaz. Hesaplanan adet üst sınır değil, kullanıcı verisine göre en küçük döngü planıdır.</p>${result.categories.map((id) => `<a href="/akilli-urun-secimi/?niyet=reusable-battery-continuity&sinif=${id}" rel="sponsored nofollow noopener">${categoryLabel(id)} sınıfını karşılaştır</a>`).join(' ')}</div>`
      : `<div class="affiliate"><strong>Ürün bağlantısı kapalı</strong><p>Mevcut döngü yeterliyse, teknik kanıt eksikse veya güvenlik sınırı varsa yeni pil ya da şarj cihazı önerilmez.</p></div>`;
    output.innerHTML = `<h2>${result.headline}</h2><div class="summary-grid"><div class="metric"><span>Aktif hücre</span><strong>${result.activeCells}</strong></div><div class="metric"><span>Hedef yedek</span><strong>${result.targetBackup}</strong></div><div class="metric"><span>Toplam hedef</span><strong>${result.targetTotal}</strong></div><div class="metric"><span>Eksik hücre</span><strong>${result.requiredAdditional}</strong></div><div class="metric"><span>Şarj partisi</span><strong>${result.chargeBatches}</strong></div><div class="metric"><span>Toplam şarj süresi</span><strong>${result.totalChargeHours} saat</strong></div></div>${list('Durdurma', result.stops)}${list('Özel kapsam', result.professional)}${list('Eksik kanıt', result.evidence)}${list('Yapılacaklar', result.actions)}${list('Korunan mevcut kanıtlar', result.strengths)}${affiliate}<p class="hint">${result.privacy}</p><div class="actions"><button type="button" id="printResult">Yazdır / PDF</button><button type="button" class="ghost" id="downloadResult">JSON planını indir</button></div>`;
    output.querySelector('#printResult').addEventListener('click', () => window.print());
    output.querySelector('#downloadResult').addEventListener('click', () => {
      const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = 'alo186-sarjli-pil-dongu-plani.json';
      link.click();
      URL.revokeObjectURL(link.href);
    });
    output.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
  }

  if (typeof module !== 'undefined' && module.exports) module.exports = { evaluate };
  if (typeof document !== 'undefined') {
    const form = document.querySelector('#rotationForm');
    if (form) {
      form.addEventListener('submit', (event) => { event.preventDefault(); render(evaluate(fromForm(form))); });
      form.addEventListener('reset', () => setTimeout(() => { document.querySelector('#result').hidden = true; }, 0));
    }
  }
})();