(() => {
  'use strict';

  const truthy = (value) => Boolean(value === true || value === 'on' || value === 'true');
  const unique = (items) => [...new Set(items.filter(Boolean))];

  function buildPlan(raw) {
    const data = { ...raw };
    const p0 = [];
    const p1 = [];
    const p2 = [];
    const links = [];

    if (truthy(data.emergency)) {
      p0.push('Aktif su basması, elektrik çarpması, duman/yangın, CO alarmı/belirtisi veya gaz kokusunda güvenli biçimde dışarı çıkın; can güvenliği için 112’yi, gaz kokusunda güvenli alandan 187’yi arayın.');
      p0.push('Islak zeminde elektrik anahtarı, priz, pano veya cihaz kullanmayın.');
      return { status: 'stop', headline: 'Takvim değil, acil çıkış ve resmî yardım', p0, p1, p2, links, interval: Number(data.interval) || 30, directAffiliate: false };
    }

    if (['common', 'commercial'].includes(data.property)) {
      p1.push('Apartman ortak alanı, otel veya işyeri tüketici tipi ev planıyla kapatılamaz. Yangın algılama, pompalar, acil aydınlatma, BMS, su ve elektrik tesisatı profesyonel görev planı gerektirir.');
    }
    if (!truthy(data.manufacturer)) p1.push('Açık kalacak her cihazın tam model kapatma, yeniden başlatma, bakım ve uzun süre bekleme talimatını bulun.');
    if (!truthy(data.official)) p1.push('Kesinti, su, gaz, yangın veya tesisat olayı için ilgili resmî/profesyonel kanalı önceden belirleyin.');
    if (!truthy(data.noCommerce)) p1.push('Mevcut ekipmanın gerçek testini tamamlamadan ürün karşılaştırmasına geçmeyin.');

    if (data.cold === 'on_unknown') {
      p1.push('Buzdolabı veya dondurucunun bağımsız sıcaklık ölçümünü, kesinti sonrası kayıt davranışını ve alarm ihtiyacını doğrulayın.');
      links.push('/hesaplama/buzdolabi-dondurucu-sicaklik-alarmi-uygunluk/');
    } else if (data.cold === 'on_verified') {
      p2.push('Buzdolabı/dondurucu sıcaklık termometresi, alarm, pil ve min/max hafızasını tekrar test edin.');
    } else if (data.cold === 'off') {
      p1.push('Cihazı üretici talimatına göre boşaltın, temizleyin, kurutun ve koku/küf riskine karşı kapı konumunu doğrulayın.');
    }

    if (data.water === 'on_unknown') {
      p1.push('Suyun açık kalacağı risk noktalarında sensör yerleşimi, pil, yerel alarm, uzaktan bildirim ve gerçek su testini tamamlayın.');
      links.push('/hesaplama/su-kacagi-sensoru-otomatik-vana-uygunluk/');
    } else if (data.water === 'on_sensor') {
      p2.push('Su kaçağı sensörü veya akış izleme cihazında pil, bildirim, vana ve manuel yeniden açma testini tekrarlayın.');
    } else if (data.water === 'off_verified') {
      p1.push('Ana vana kapatma ve dönüşte kontrollü yeniden açma adımını tesisatçı/üretici talimatına göre yazılı görev olarak bırakın.');
    } else if (data.water === 'special') {
      p1.push('Isıtma, yangın sistemi, sulama, havuz veya özel tesisat nedeniyle su kapatma kararını profesyonel tesisat planına bırakın.');
    }

    if (data.alarms === 'none' || data.alarms === 'partial') {
      p1.push('Duman/ısı ve karbonmonoksit alarmında kapsam, test, pil, ömür ve yerleşim kanıtlarını tamamlayın.');
      links.push('/hesaplama/duman-alarmi-isi-alarmi-uygunluk/');
      links.push('/hesaplama/karbonmonoksit-alarmi-uygunluk/');
    } else if (data.alarms === 'verified') {
      p2.push('Duman/CO alarmında üretici testini, düşük pil/ömür sonu sinyalini ve tahliye planını yeniden kontrol edin.');
    } else if (data.alarms === 'system') {
      p1.push('Bina yangın alarm sistemi bakım ve izleme görevini yetkili kuruluşla doğrulayın; bağımsız ev alarmı ile ikame etmeyin.');
    }

    if (data.electrical === 'fault') {
      p1.push('Sürekli açma, ısınma, cihaz reseti veya gerilim olayı varsa evi boş bırakmadan önce yetkili elektrikçi ve gerekiyorsa EDAŞ kanıtını tamamlayın.');
      links.push('/edas-bul/');
    } else if (data.electrical === 'unknown') {
      p1.push('RCD TEST düğmesi, priz/fiş ısınması, kablo hasarı, pano görünür durumu ve açık kalacak devreleri doğrulayın.');
      links.push('/hesaplama/kacak-akim-rolesi-tipi-uygunluk/');
    } else {
      p2.push('Açık kalacak devrelerde priz, kablo, adaptör ve koruma cihazlarının görünür durumunu yeniden kontrol edin.');
    }

    if (data.remote === 'unknown') p1.push('Modem, güvenlik cihazı ve akıllı sensörlerde elektrik, internet, pil, bulut ve bağlantı kaybı davranışını test edin.');
    if (data.remote === 'verified') p2.push('Uzaktan bildirim test mesajını, modem yeniden başlatmasını ve bağlantı kaybı uyarısını tekrar doğrulayın.');
    if (data.visit === 'none' && ['month', 'season'].includes(data.absence)) p1.push('Uzun süre boş kalacak ev için güvenilir kişi veya yetkili servis fiziksel kontrol planı oluşturun; yalnız bulut bildirimine güvenmeyin.');
    if (data.reason === 'reopen') p1.push('Enerji ve suyu kademeli açın; priz, pano, kablo, pompa, vana ve cihazlarda nem, korozyon, koku, böcek/kemirgen hasarı ve ısınma kontrolü yapın.');
    if (data.reason === 'incident') p1.push('Olayın başlangıç/bitiş zamanını, hangi sistemin etkilendiğini ve uygulanan çözümü kişisel veri olmadan JSON görev dosyasına kaydedin.');

    const interval = [7, 30, 90].includes(Number(data.interval)) ? Number(data.interval) : 30;
    p2.push(`${interval === 7 ? '7 günlük olay sonrası' : interval === 90 ? '90 günlük rutin bakım' : '30 günlük hazırlık'} hatırlatmasını takvime ekleyin.`);
    p2.push('Evde açık kalan görev, cihaz veya tesisat değiştiğinde planı baştan değerlendirin.');
    p2.push('Her dönüşte sensör, alarm ve sıcaklık kaydını gerçek görev sonucu ile karşılaştırın.');

    const professional = ['common', 'commercial'].includes(data.property);
    return {
      status: professional ? 'professional' : 'plan',
      headline: professional ? 'Profesyonel bina görev planı gerekli' : 'Kişisel verisiz tatil / yazlık güvenlik planı hazır',
      p0: unique(p0),
      p1: unique(p1),
      p2: unique(p2),
      links: unique(links),
      interval,
      reason: data.reason,
      property: data.property,
      directAffiliate: false,
      privacy: 'Plan tarayıcıda oluşturulur; ad, adres, konum, seyahat tarihi veya hesap kaydı kullanılmaz.'
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
      'BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//ALO186//Tatil Yazlik Ev Guvenlik Merkezi//TR',
      'BEGIN:VEVENT', `UID:alo186-away-home-${now.getTime()}@alo186.com`, `DTSTAMP:${dateStamp(now)}`,
      `DTSTART:${dateStamp(due)}`, 'SUMMARY:ALO186 tatil ve yazlik ev tekrar kontrolu',
      `DESCRIPTION:${description}`, 'END:VEVENT', 'END:VCALENDAR'
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
    const linkNames = {
      '/hesaplama/buzdolabi-dondurucu-sicaklik-alarmi-uygunluk/': 'Sıcaklık alarmı aracını aç',
      '/hesaplama/su-kacagi-sensoru-otomatik-vana-uygunluk/': 'Su kaçağı sensörü aracını aç',
      '/hesaplama/duman-alarmi-isi-alarmi-uygunluk/': 'Duman/ısı alarmı aracını aç',
      '/hesaplama/karbonmonoksit-alarmi-uygunluk/': 'CO alarmı aracını aç',
      '/hesaplama/kacak-akim-rolesi-tipi-uygunluk/': 'RCD uygunluk aracını aç',
      '/edas-bul/': 'Yetkili EDAŞ kanalını bul'
    };
    const links = plan.links.length
      ? `<section><h3>İlgili ücretsiz araçlar</h3><div class="cards">${plan.links.map((href) => `<a class="card" href="${href}"><strong>${linkNames[href] || 'İlgili aracı aç'}</strong><span>Önce ücretsiz teknik kanıtı tamamlayın.</span></a>`).join('')}</div></section>`
      : '';
    const tools = plan.status === 'stop'
      ? '<p><a class="button" href="/acil-numaralar/">112 / 187 acil numaralarını aç</a></p>'
      : `<div class="actions"><button type="button" id="downloadJson">JSON planı indir</button><button type="button" class="ghost" id="downloadIcs">${plan.interval} günlük .ics takvimi indir</button><button type="button" class="ghost" id="printPlan">Yazdır / PDF</button></div>`;
    output.innerHTML = `<h2>${plan.headline}</h2>${list('P0 — hemen', plan.p0)}${list('P1 — çıkmadan önce / dönüşte', plan.p1)}${list('P2 — periyodik kontrol', plan.p2)}${links}${tools}${plan.privacy ? `<p class="hint">${plan.privacy} Merkez doğrudan affiliate bağlantısı göstermez.</p>` : ''}`;
    if (plan.status !== 'stop') {
      output.querySelector('#downloadJson').addEventListener('click', () => download('alo186-tatil-yazlik-ev-plani.json', JSON.stringify(plan, null, 2), 'application/json'));
      output.querySelector('#downloadIcs').addEventListener('click', () => download('alo186-tatil-yazlik-ev-tekrar-kontrol.ics', makeIcs(plan), 'text/calendar'));
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
        for (const name of ['emergency', 'manufacturer', 'official', 'noCommerce']) data[name] = Boolean(form.elements[name]?.checked);
        render(buildPlan(data));
      });
      form.addEventListener('reset', () => setTimeout(() => { document.querySelector('#result').hidden = true; document.querySelector('#error').hidden = true; }, 0));
    }
  }
})();