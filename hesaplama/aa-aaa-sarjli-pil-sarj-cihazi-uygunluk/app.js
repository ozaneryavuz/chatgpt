(() => {
  'use strict';

  const truthy = (value) => Boolean(value === true || value === 'on' || value === 'true');
  const unique = (items) => [...new Set(items.filter(Boolean))];

  function evaluate(raw) {
    const data = { ...raw };
    const stops = [];
    const professional = [];
    const evidence = [];
    const actions = [];
    const strengths = [];

    if (truthy(data.damage)) {
      stops.push('Sızıntılı, şişmiş, paslanmış, aşırı ısınan veya yanık kokusu olan pil ya da şarj cihazını kullanmayın ve şarj etmeyin. Üretici ve yerel atık kurallarına göre güvenli biçimde ayırın.');
    }
    if (['smoke', 'co', 'medical', 'safety'].includes(data.deviceClass)) {
      professional.push('Duman/CO alarmı, tıbbi veya can güvenliği cihazında pil kimyası yalnız tam model üretici kılavuzuyla doğrulanmalıdır. Genel NiMH önerisi verilmez.');
    }
    if (data.manual === 'no') {
      professional.push('Cihaz kılavuzu NiMH şarjlı pili kabul etmiyor. 1,2 V NiMH ürüne geçmeyin.');
    }
    if (data.currentChemistry === 'alkaline' && data.chargePlan === 'charge') {
      stops.push('Alkalin veya başka bir birincil pili şarj etmeyin. Yalnız açıkça şarj edilebilir olarak işaretlenmiş ve şarj cihazıyla uyumlu hücreler şarj edilir.');
    }
    if (['lithium-primary', 'liion'].includes(data.currentChemistry) && data.chargerType.startsWith('nimh')) {
      stops.push('NiMH şarj cihazında lityum birincil veya lityum iyon hücre şarj etmeyin. Kimya ve şarj cihazı eşleşmesi zorunludur.');
    }
    if (data.mix === 'mixed') {
      stops.push('Aynı cihazda farklı kimya, yaş, kapasite veya dolulukta hücreleri karıştırmayın.');
    }

    if (data.size === 'unknown') evidence.push('Cihazın AA veya AAA pil boyutu doğrulanmadı. Pil yuvası ve tam model kılavuzu kontrol edilmelidir.');
    if (data.manual === 'unknown') evidence.push('Cihazın 1,2 V NiMH şarjlı pil kullanımına izin verip vermediği bilinmiyor.');
    if (data.voltage === 'unknown') evidence.push('Cihazın beklediği pil gerilimi ve düşük pil davranışı doğrulanmadı.');
    if (data.condition === 'unknown') evidence.push('Mevcut pillerin sızıntı, ısınma, korozyon ve eş set durumu kontrol edilmedi.');
    if (data.chargerType === 'unknown') evidence.push('Şarj cihazının yalnız NiMH/NiCd veya farklı kimya için olup olmadığı ve kanal düzeni bilinmiyor.');
    if (data.chargerCondition === 'unknown') evidence.push('Şarj cihazının kablo, gövde, LED ve otomatik kesme davranışı doğrulanmadı.');
    if (data.mix === 'unknown') evidence.push('Birlikte kullanılan hücrelerin aynı kimya, yaş ve kapasite sınıfında olup olmadığı bilinmiyor.');

    if (data.voltage === '1.5-only') actions.push('Cihaz yalnız 1,5 V birincil pil istiyorsa 1,2 V NiMH hücreyi uygun kabul etmeyin.');
    if (data.chargerCondition === 'fault') actions.push('Arıza, aşırı ısınma, kesme sorunu veya hasarlı kablo bulunan şarj cihazını kullanmayın.');
    if (data.chargerType === 'nimh-pair' && Number(data.deviceCells || 1) % 2 === 1) actions.push('Çift kanal/pair şarj cihazında tek hücreli cihaz için yedek eş hücre planı gerekir; tek hücreyi ayrı şarj edebilen model olmadığı varsayılmamalıdır.');

    if (data.manual === 'yes') strengths.push('Cihaz kılavuzu NiMH şarjlı pil kullanımına izin veriyor.');
    if (['AA', 'AAA'].includes(data.size)) strengths.push(`${data.size} pil boyutu doğrulandı.`);
    if (data.voltage === '1.2-ok') strengths.push('Cihazın 1,2 V NiMH gerilim davranışı doğrulandı.');
    if (data.currentChemistry === 'nimh' && data.condition === 'good') strengths.push('Mevcut NiMH hücreler fiziksel olarak sağlam görünüyor.');
    if (['nimh-individual', 'nimh-pair'].includes(data.chargerType) && data.chargerCondition === 'good') strengths.push('Mevcut şarj cihazı NiMH için uyumlu ve fiziksel kontrolü geçti.');

    const compatibleDevice = data.manual === 'yes' && data.voltage === '1.2-ok' && ['AA', 'AAA'].includes(data.size);
    const healthyCells = data.currentChemistry === 'nimh' && data.condition === 'good' && data.mix === 'same';
    const healthyCharger = ['nimh-individual', 'nimh-pair'].includes(data.chargerType) && data.chargerCondition === 'good';
    const existingPass = compatibleDevice && healthyCells && healthyCharger;

    let status = 'recommend';
    let headline = 'NiMH pil ve şarj cihazı sınıfı için ön seçim hazır';
    if (stops.length) {
      status = 'stop';
      headline = 'Şarj ve ürün seçimini durdurun';
    } else if (professional.length) {
      status = 'professional';
      headline = 'Tam model üretici talimatı gerekli';
    } else if (existingPass) {
      status = 'no-buy';
      headline = 'Mevcut pil ve şarj cihazı yeterli — yeni ürün almayın';
    } else if (evidence.length) {
      status = 'evidence';
      headline = 'Satın almadan önce eksik uyum kanıtlarını tamamlayın';
    }

    const categories = [];
    if (compatibleDevice && !healthyCells) categories.push('rechargeable_nimh_battery');
    if (compatibleDevice && !healthyCharger) categories.push('nimh_battery_charger');
    const confirmations = truthy(data.confirmNeed) && truthy(data.confirmSpecs) && truthy(data.confirmAffiliate);
    const affiliateAllowed = status === 'recommend' && categories.length > 0 && confirmations;

    return {
      ok: true,
      status,
      headline,
      stops: unique(stops),
      professional: unique(professional),
      evidence: unique(evidence),
      actions: unique(actions),
      strengths: unique(strengths),
      categories,
      affiliateAllowed,
      confirmations,
      existingPass,
      privacy: 'Hesap cihazınızda yapılır; ad, adres, konum, seri numarası veya hesap kaydı kullanılmaz.'
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
    const error = document.querySelector('#error');
    if (!result.ok) {
      error.textContent = result.error || 'Sonuç üretilemedi.';
      error.hidden = false;
      output.hidden = true;
      return;
    }
    error.hidden = true;
    output.hidden = false;
    output.dataset.status = result.status;
    const affiliate = result.affiliateAllowed
      ? `<div class="affiliate"><strong>Şeffaf satış ortaklığı ürün sınıfı</strong><p>Sonraki sayfada doğrulanmış Amazon satış ortaklığı bağlantıları bulunabilir. ALO186 fiyat, stok, puan, satıcı, teslimat veya garanti yayımlamaz. Pil boyutu, NiMH kimyası, 1,2 V uyumu ve şarj kanal düzenini mağazada yeniden doğrulayın.</p>${result.categories.map((id) => `<a href="/akilli-urun-secimi/?niyet=reusable-battery-continuity&sinif=${id}" rel="sponsored nofollow noopener">${categoryLabel(id)} sınıfını karşılaştır</a>`).join(' ')}</div>`
      : `<div class="affiliate"><strong>Ürün bağlantısı kapalı</strong><p>Tehlike, özel cihaz, eksik teknik kanıt veya yeterli mevcut ekipman varken satın alma önerilmez.</p></div>`;
    output.innerHTML = `<h2>${result.headline}</h2><div class="summary-grid"><div class="metric"><span>Sonuç</span><strong>${result.status}</strong></div><div class="metric"><span>Ürün sınıfı</span><strong>${result.categories.length ? result.categories.map(categoryLabel).join(' + ') : 'Yok'}</strong></div><div class="metric"><span>Affiliate</span><strong>${result.affiliateAllowed ? 'Açık ve etiketli' : 'Kapalı'}</strong></div></div>${list('Durdurma', result.stops)}${list('Özel kapsam', result.professional)}${list('Eksik kanıt', result.evidence)}${list('Yapılacaklar', result.actions)}${list('Korunan mevcut kanıtlar', result.strengths)}${affiliate}<p class="hint">${result.privacy}</p><div class="actions"><button type="button" id="printResult">Yazdır / PDF</button><button type="button" class="ghost" id="downloadResult">JSON sonucu indir</button></div>`;
    output.querySelector('#printResult').addEventListener('click', () => window.print());
    output.querySelector('#downloadResult').addEventListener('click', () => {
      const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = 'alo186-aa-aaa-pil-uygunluk-sonucu.json';
      link.click();
      URL.revokeObjectURL(link.href);
    });
    output.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
  }

  if (typeof module !== 'undefined' && module.exports) module.exports = { evaluate };
  if (typeof document !== 'undefined') {
    const form = document.querySelector('#batteryForm');
    if (form) {
      form.addEventListener('submit', (event) => { event.preventDefault(); render(evaluate(fromForm(form))); });
      form.addEventListener('reset', () => setTimeout(() => { document.querySelector('#result').hidden = true; document.querySelector('#error').hidden = true; }, 0));
    }
  }
})();