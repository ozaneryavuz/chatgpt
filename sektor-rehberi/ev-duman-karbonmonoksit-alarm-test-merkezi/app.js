(() => {
  'use strict';

  const truthy = (value) => Boolean(value === true || value === 'on' || value === 'true');
  const unique = (items) => [...new Set(items.filter(Boolean))];

  function buildPlan(raw) {
    const data = { ...raw };
    const p0 = [];
    const p1 = [];
    const p2 = [];

    if (truthy(data.emergency)) {
      p0.push('Duman, alev, yoğun ısı, CO alarmı/belirtisi veya gaz kokusunda binayı güvenli biçimde terk edin; 112’yi, gaz kokusunda güvenli alandan 187’yi arayın.');
      return { status: 'stop', headline: 'Takvim değil, acil çıkış ve resmî yardım', p0, p1, p2, interval: Number(data.interval) || 30 };
    }

    if (!truthy(data.manufacturer)) p1.push('Tam model test, temizlik, pil ve değiştirme talimatını bulun; genel internet önerisini ürün kılavuzu yerine kullanmayın.');
    if (!truthy(data.noCommerce)) p1.push('Mevcut çalışan alarmın test, pil, yerleşim ve ömür kanıtını tamamlamadan yeni ürün karşılaştırmasına geçmeyin.');

    if (data.alarms === 'none') {
      p1.push('Önce duman/ısı ve CO alarmı uygunluk araçlarıyla evde hangi tehlikenin ve alanın kapsanmadığını belirleyin.');
    }
    if (['both', 'smoke'].includes(data.alarms)) {
      p1.push('Duman/ısı alarmında test düğmesini, pil veya arıza sinyalini, üretim/değiştirme tarihini ve uyku rotası kapsamını kontrol edin.');
    }
    if (['both', 'co'].includes(data.alarms)) {
      p1.push('CO alarmında test düğmesini, EN 50291 belgesini, ömür sonu sinyalini, kat/uyku alanı kapsamını ve sinyal açıklamasını kontrol edin.');
    }
    if (data.fuel === 'yes') {
      p1.push('Yakıtlı cihaz, baca, menfez ve havalandırma bakımını yetkili servis/uzmanla doğrulayın; CO alarmını bakımın yerine kullanmayın.');
    } else if (data.fuel === 'unknown') {
      p1.push('Kombi, soba, şofben, şömine, kapalı garaj, jeneratör veya komşu CO kaynağı riskini belirleyin.');
    }

    if (data.reason === 'signal') {
      p1.push('Düşük pil, arıza ve ömür sonu sinyalini tam model kılavuzundan ayırın; yalnız sesi susturmayın.');
    }
    if (data.reason === 'incident') {
      p1.push('Yanlış alarmın mutfak/buhar/konum/kirlenme kaynağını ve gerçek olay ihtimalini belgeleyin; alarmı devre dışı bırakmayın.');
    }
    if (data.reason === 'move') {
      p1.push('Yeni evde kat, yatak odası, uyku alanı dışı koridor, mutfak, garaj ve yakıtlı cihaz konumlarını yeniden haritalayın.');
    }
    if (data.reason === 'heating') {
      p1.push('Isıtma sezonu başlamadan önce CO alarmı, baca/menfez, kombi-soba-şofben bakımı ve hane halkının 112/187 planını birlikte doğrulayın.');
    }

    p2.push('Alarm seslerini hane halkıyla gözden geçirin; CO, duman, düşük pil, arıza ve ömür sonu sinyallerinin farklı olabileceğini anlatın.');
    p2.push('Alarmın önünü kapatmayın; boya, bant, dolap, perde, hava menfezi, yoğun buhar veya toz etkisini kontrol edin.');
    p2.push(`${Number(data.interval) === 90 ? '90 günlük kapsam ve bakım' : '30 günlük işlev testi'} hatırlatmasını takvime ekleyin.`);

    return {
      status: 'plan',
      headline: 'Kişisel verisiz alarm test planı hazır',
      p0: unique(p0),
      p1: unique(p1),
      p2: unique(p2),
      interval: Number(data.interval) === 90 ? 90 : 30,
      reason: data.reason,
      alarms: data.alarms,
      directAffiliate: false,
      privacy: 'Plan tarayıcıda oluşturulur; ad, adres, konum veya hesap kaydı kullanılmaz.'
    };
  }

  function dateStamp(date) {
    return date.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}Z$/, 'Z');
  }

  function makeIcs(plan) {
    const now = new Date();
    const due = new Date(now.getTime() + plan.interval * 86400000);
    const description = [...plan.p1, ...plan.p2].join(' ').replace(/[;,\\]/g, ' ');
    return [
      'BEGIN:VCALENDAR',
      'VERSION:2.0',
      'PRODID:-//ALO186//Ev Alarm Test Merkezi//TR',
      'BEGIN:VEVENT',
      `UID:alo186-alarm-test-${now.getTime()}@alo186.com`,
      `DTSTAMP:${dateStamp(now)}`,
      `DTSTART:${dateStamp(due)}`,
      `SUMMARY:ALO186 ev duman ve CO alarmı tekrar testi`,
      `DESCRIPTION:${description}`,
      'END:VEVENT',
      'END:VCALENDAR'
    ].join('\r\n');
  }

  function download(name, content, type) {
    const blob = new Blob([content], { type });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = name;
    link.click();
    URL.revokeObjectURL(link.href);
  }

  const list = (title, items) => items.length ? `<section><h3>${title}</h3><ul>${items.map((item) => `<li>${item}</li>`).join('')}</ul></section>` : '';

  function render(plan) {
    const output = document.querySelector('#result');
    const error = document.querySelector('#error');
    error.hidden = true;
    output.hidden = false;
    output.dataset.status = plan.status;
    const tools = plan.status === 'stop'
      ? '<p><a class="button" href="/acil-numaralar/">112 / 187 acil numaralarını aç</a></p>'
      : `<div class="actions"><button type="button" id="downloadJson">JSON planı indir</button><button type="button" class="ghost" id="downloadIcs">${plan.interval} günlük .ics takvimi indir</button><button type="button" class="ghost" id="printPlan">Yazdır / PDF</button></div>`;
    output.innerHTML = `<h2>${plan.headline}</h2>${list('P0 — hemen', plan.p0)}${list('P1 — bugün / bu hafta', plan.p1)}${list('P2 — periyodik kontrol', plan.p2)}${tools}${plan.privacy ? `<p class="hint">${plan.privacy} Merkez doğrudan affiliate bağlantısı göstermez.</p>` : ''}`;
    if (plan.status !== 'stop') {
      output.querySelector('#downloadJson').addEventListener('click', () => download('alo186-ev-alarm-test-plani.json', JSON.stringify(plan, null, 2), 'application/json'));
      output.querySelector('#downloadIcs').addEventListener('click', () => download('alo186-ev-alarm-tekrar-testi.ics', makeIcs(plan), 'text/calendar'));
      output.querySelector('#printPlan').addEventListener('click', () => window.print());
    }
    output.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
  }

  if (typeof module !== 'undefined' && module.exports) module.exports = { buildPlan, makeIcs };
  if (typeof document !== 'undefined') {
    const form = document.querySelector('#planForm');
    if (form) {
      form.addEventListener('submit', (event) => {
        event.preventDefault();
        const data = Object.fromEntries(new FormData(form).entries());
        for (const name of ['emergency', 'manufacturer', 'noCommerce']) data[name] = Boolean(form.elements[name]?.checked);
        render(buildPlan(data));
      });
      form.addEventListener('reset', () => setTimeout(() => { document.querySelector('#result').hidden = true; document.querySelector('#error').hidden = true; }, 0));
    }
  }
})();