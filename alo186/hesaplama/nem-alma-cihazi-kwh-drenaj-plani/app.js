(() => {
  'use strict';
  const truthy = (value) => Boolean(value === true || value === 'on' || value === 'true');
  const unique = (items) => [...new Set(items.filter(Boolean))];
  const n = (value, fallback = 0) => Number.isFinite(Number(value)) ? Number(value) : fallback;
  function calculate(raw) {
    const watts = Math.max(0, Math.min(2500, n(raw.watts)));
    const hours = Math.max(0, Math.min(24, n(raw.hours)));
    const days = Math.max(0, Math.min(31, n(raw.days, 30)));
    const liters = Math.max(0, Math.min(100, n(raw.liters)));
    const tank = Math.max(0, Math.min(20, n(raw.tank)));
    return { watts, hours, days, liters, tank, kwhDay: watts * hours / 1000, kwhPeriod: watts * hours * days / 1000, tankCycles: tank > 0 && liters > 0 ? liters / tank : 0 };
  }
  function evaluate(raw) {
    const data = { ...raw }, metrics = calculate(data), stops = [], professional = [], evidence = [], actions = [], strengths = [];
    if (truthy(data.electricalWaterRisk)) stops.push('Islak priz, su birikintisi, elektrikli cihazla su teması veya elektrik çarpması riski varsa cihazı bağlamayın; güvenli alandan acil yardım ve yetkili uzman rotasına geçin.');
    if (data.scope === 'whole-home' || data.scope === 'commercial') professional.push('Tüm konut, ticari alan veya kanal bağlantılı sistem için oda tipi taşınabilir cihaz hesabı yeterli değildir; HVAC, drenaj ve elektrik altyapısı birlikte projelendirilmelidir.');
    if (data.drain === 'hose' && data.drainSafe !== 'yes') professional.push('Sürekli hortum drenajında geri akış, eğim, taşma ve gider bağlantısı doğrulanmadan gözetimsiz çalıştırmayın.');
    if (data.outletSafe !== 'yes') stops.push('Doğrudan topraklı priz, RCD ve üretici bağlantı sınırı doğrulanmadı. Uzatma kablosu veya grup priz üzerinden nem alma cihazı çalıştırmayın.');
    if (data.sourceFixed !== 'yes') evidence.push('Nem kaynağının giderildiği doğrulanmadı. Cihaz, sızıntı veya yapı kaynaklı nemin onarımının yerine geçmez.');
    if (data.rhLog !== 'yes') evidence.push('En az 7 günlük bağıl nem kaydı yok. Tek gün veya tek ölçüm kapasite ve çalışma süresi seçimi için yeterli değildir.');
    if (!metrics.watts) evidence.push('Cihaz etiketindeki gerçek giriş gücü W değeri girilmedi; kWh hesabı üretilemez.');
    if (data.drain === 'tank' && !metrics.tank) evidence.push('Tank hacmi doğrulanmadı; boşaltma sıklığı planlanamaz.');
    if (data.existingDevice === 'yes' && data.targetMet === 'yes' && data.drainSafe === 'yes') strengths.push('Mevcut cihaz hedef nemi ve drenaj görevini karşılıyor.');
    if (metrics.watts && metrics.hours) strengths.push('Enerji hesabı kullanıcı tarafından girilen etiket W ve çalışma saatiyle yapıldı; TL veya tarife tahmini kullanılmadı.');
    const existingPass = data.existingDevice === 'yes' && data.targetMet === 'yes' && data.drainSafe === 'yes' && data.outletSafe === 'yes';
    let status = 'evidence', headline = 'Önce nem kaydı, kaynak ve drenaj kanıtını tamamlayın';
    if (stops.length) { status = 'stop'; headline = 'Çalıştırmayı ve ürün seçimini durdurun'; }
    else if (professional.length) { status = 'professional'; headline = 'Oda tipi cihaz yerine profesyonel kapsam gerekli'; }
    else if (existingPass) { status = 'no-buy'; headline = 'Mevcut nem alma cihazı yeterli — yeni ürün almayın'; }
    else if (!evidence.length && data.needConfirmed === 'yes') { status = 'recommend'; headline = 'Etiket gücü, çalışma ve drenaj planıyla ürün sınıfı değerlendirilebilir'; }
    if (data.drain === 'tank' && metrics.tankCycles > 0) actions.push(`Girilen su toplama ve tank değerine göre günde yaklaşık ${metrics.tankCycles.toFixed(1)} tank boşaltma gerekir; gerçek sonuç ortam ve test koşullarına göre değişir.`);
    if (data.drain === 'hose') actions.push('Hortum çapı, azami uzunluk/eğim, gider kotu ve geri akış sınırını yalnız tam model üretici belgesinden doğrulayın.');
    actions.push('Kapasiteyi yalnız oda m² değerine göre seçmeyin; başlangıç RH, sıcaklık, nem kaynağı, kapı/pencere kullanımı ve üretici test koşulları birlikte değerlendirilmelidir.');
    actions.push('Filtre, hava girişi/çıkışı, tank şamandırası ve drenajı üretici bakım talimatına göre tekrar test edin.');
    const confirmations = truthy(data.confirmNeed) && truthy(data.confirmSpecs) && truthy(data.confirmAffiliate);
    const affiliateAllowed = status === 'recommend' && confirmations;
    return { ok: true, status, headline, metrics, stops: unique(stops), professional: unique(professional), evidence: unique(evidence), actions: unique(actions), strengths: unique(strengths), categories: status === 'recommend' ? ['portable_dehumidifier'] : [], confirmations, affiliateAllowed, existingPass, privacy: 'Hesap cihazınızda yapılır; adres, konum, fotoğraf, marka veya seri numarası istenmez.' };
  }
  function fromForm(form) { const data = Object.fromEntries(new FormData(form).entries()); for (const name of ['electricalWaterRisk','confirmNeed','confirmSpecs','confirmAffiliate']) data[name] = Boolean(form.elements[name]?.checked); return data; }
  const list = (title, items) => items.length ? `<section><h3>${title}</h3><ul>${items.map((item) => `<li>${item}</li>`).join('')}</ul></section>` : '';
  function render(result) {
    const output = document.querySelector('#result'); output.hidden = false; output.dataset.status = result.status; const m = result.metrics;
    const affiliate = result.affiliateAllowed ? `<div class="affiliate"><strong>Şeffaf satış ortaklığı ürün sınıfı</strong><p>Sonraki ürün merkezinde Amazon satış ortaklığı bağlantıları bulunabilir. ALO186 fiyat, stok, puan, satıcı, teslimat veya garanti yayımlamaz. Kapasite, W, drenaj, ses, sıcaklık aralığı ve elektrik bağlantısını tam model belgesinde yeniden doğrulayın.</p><a href="/amazon-elektrik-urunleri/" rel="sponsored nofollow noopener">Oda tipi nem alma cihazı sınıfını karşılaştır</a></div>` : `<div class="affiliate"><strong>Ürün bağlantısı kapalı</strong><p>Tehlike, eksik nem kaydı, çözülmemiş kaynak, profesyonel kapsam veya yeterli mevcut cihaz varken satın alma önerilmez.</p></div>`;
    output.innerHTML = `<h2>${result.headline}</h2><div class="summary-grid"><div class="metric"><span>Enerji</span><strong>${m.kwhDay.toFixed(2)} kWh/gün</strong></div><div class="metric"><span>${m.days} günlük enerji</span><strong>${m.kwhPeriod.toFixed(1)} kWh</strong></div><div class="metric"><span>Tank çevrimi</span><strong>${m.tankCycles ? `${m.tankCycles.toFixed(1)} / gün` : 'Veri yok'}</strong></div></div>${list('Durdurma', result.stops)}${list('Profesyonel kapsam', result.professional)}${list('Eksik kanıt', result.evidence)}${list('Plan', result.actions)}${list('Korunan mevcut kanıtlar', result.strengths)}${affiliate}<p class="hint">${result.privacy}</p><div class="actions"><button type="button" id="printResult">Yazdır / PDF</button><button type="button" class="ghost" id="downloadResult">JSON sonucu indir</button></div>`;
    output.querySelector('#printResult').addEventListener('click', () => window.print()); output.querySelector('#downloadResult').addEventListener('click', () => { const link=document.createElement('a'); link.href=URL.createObjectURL(new Blob([JSON.stringify(result,null,2)],{type:'application/json'})); link.download='alo186-nem-alma-kwh-drenaj-plani.json'; link.click(); URL.revokeObjectURL(link.href); }); output.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});
  }
  if (typeof module !== 'undefined' && module.exports) module.exports = { calculate, evaluate };
  if (typeof document !== 'undefined') { const form=document.querySelector('#dehumidifierForm'); if(form) form.addEventListener('submit',(event)=>{event.preventDefault();render(evaluate(fromForm(form)));}); }
})();
