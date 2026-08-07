(() => {
  'use strict';

  const unique = (items) => [...new Set(items.filter(Boolean))];
  const escapeIcs = (value) => String(value).replace(/\\/g, '\\\\').replace(/,/g, '\\,').replace(/;/g, '\\;').replace(/\n/g, '\\n');
  const dateStamp = (date) => date.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}Z$/, 'Z');

  function buildPlan(raw) {
    const data = { ...raw };
    const immediate = [];
    const next = [];
    const repeat = [];
    let cadence = 90;
    let priority = 'P2';

    if (data.scenario === 'damage') {
      priority = 'P0';
      cadence = 7;
      immediate.push('Sızıntılı, şişmiş, korozyonlu veya aşırı ısınan pili ve şarj cihazını kullanmayın; çocuklardan ve metal nesnelerden uzak, üretici/yerel atık talimatına uygun biçimde ayırın.');
      immediate.push('Hasarlı hücreyi yeniden şarj etmeyin ve sağlam hücrelerle aynı kutuda taşımayın.');
    } else if (data.scenario === 'new-device') {
      priority = 'P1';
      cadence = 30;
      immediate.push('Yeni cihazın tam model kılavuzunda AA/AAA boyutunu, kabul edilen pil kimyasını ve 1,2 V NiMH davranışını doğrulayın.');
      next.push('Mevcut sağlam pil ve şarj cihazını uyumluluk testinden geçirin; yalnız gerçek eksikte ürün sınıfına ilerleyin.');
    } else if (data.scenario === 'slow-charge') {
      priority = 'P1';
      cadence = 30;
      immediate.push('Şarj süresini aynı hücre seti, aynı ortam ve aynı şarj cihazıyla yeniden ölçün; aşırı ısınma veya kesme hatası varsa kullanımı durdurun.');
      next.push('Hücre yaşını, kapasite dengesini, şarj kanal düzenini ve güç girişini ayrı ayrı kontrol edin.');
    } else if (data.scenario === 'travel') {
      priority = 'P1';
      cadence = 30;
      immediate.push('Seyahat öncesi cihaz sayısını, aktif hücreleri, yedek seti, şarj girişini ve adaptör uyumunu yeniden doğrulayın.');
      next.push('Hasarlı veya gevşek hücreleri seyahat setine eklemeyin; pilleri metal temasından koruyan kutuda taşıyın.');
    } else if (data.scenario === 'inventory') {
      priority = 'P2';
      cadence = 90;
      immediate.push('AA ve AAA hücreleri kimya, kapasite sınıfı, yaş ve kullanım grubuna göre ayırın; karışık setleri cihazlarda birlikte kullanmayın.');
      next.push('Döngü planlayıcıyla fazla ve eksik yedek sayısını hesaplayın.');
    } else {
      priority = 'P2';
      cadence = 90;
      immediate.push('Pil yuvası, hücre yüzeyi, şarj cihazı gövdesi, kablo ve LED/kesme davranışını gözle kontrol edin.');
      next.push('En çok kullanılan cihaz için gerçek çalışma süresini ve bir tam şarj süresini kaydedin.');
    }

    if (data.deviceClass === 'safety') {
      priority = 'P0';
      cadence = 7;
      immediate.push('Duman/CO alarmı, tıbbi veya can güvenliği cihazında genel NiMH planı kullanmayın; tam model üretici talimatını ve zorunlu test programını izleyin.');
    }
    if (data.currentIssue === 'leak') immediate.push('Pil yuvasında korozyon veya sızıntı varsa cihazı enerjisiz bırakın; üretici temizleme ve servis talimatı olmadan tekrar pil takmayın.');
    if (data.currentIssue === 'heat') immediate.push('Şarj sırasında aşırı ısınma varsa fişi güvenli biçimde çekin ve tekrar kullanmayın.');
    if (data.currentIssue === 'short-runtime') next.push('Kısa çalışma süresinin cihaz yükü, temas/korozyon, hücre dengesizliği veya yaşlanmadan kaynaklanıp kaynaklanmadığını ayırın.');

    repeat.push(`${cadence} gün sonra aynı cihaz ve hücre setinde fiziksel durum, gerçek çalışma süresi ve şarj süresini yeniden kontrol edin.`);
    repeat.push('Yeni cihaz, farklı pil boyutu, yeni şarj cihazı veya mevsimsel uzun kullanımda planı yeniden oluşturun.');
    repeat.push('Mevcut sistem testi geçiyorsa yeni pil veya şarj cihazı almayın.');

    return {
      ok: true,
      priority,
      cadence,
      immediate: unique(immediate),
      next: unique(next),
      repeat: unique(repeat),
      privacy: 'Plan cihazınızda oluşturulur; ad, e-posta, adres, konum, marka veya seri numarası istenmez.'
    };
  }

  function download(name, content, type) {
    const blob = new Blob([content], { type });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = name;
    link.click();
    URL.revokeObjectURL(link.href);
  }

  function render(plan) {
    const result = document.querySelector('#result');
    result.hidden = false;
    result.dataset.status = plan.priority === 'P0' ? 'stop' : plan.priority === 'P1' ? 'evidence' : 'no-buy';
    const list = (title, items) => `<section><h3>${title}</h3><ul>${items.map((item) => `<li>${item}</li>`).join('')}</ul></section>`;
    result.innerHTML = `<h2>${plan.priority} pil süreklilik planı</h2><div class="summary-grid"><div class="metric"><span>Öncelik</span><strong>${plan.priority}</strong></div><div class="metric"><span>Tekrar kontrol</span><strong>${plan.cadence} gün</strong></div><div class="metric"><span>Doğrudan affiliate</span><strong>Yok</strong></div></div>${list('Şimdi', plan.immediate)}${list('Sonraki doğrulama', plan.next)}${list('Tekrar ziyaret nedeni', plan.repeat)}<p class="hint">${plan.privacy}</p><div class="actions"><button type="button" id="downloadJson">JSON planını indir</button><button type="button" class="ghost" id="downloadIcs">Takvime ekle (.ics)</button></div>`;
    result.querySelector('#downloadJson').addEventListener('click', () => download('alo186-aa-aaa-pil-sureklilik-plani.json', JSON.stringify(plan, null, 2), 'application/json'));
    result.querySelector('#downloadIcs').addEventListener('click', () => {
      const start = new Date(Date.now() + plan.cadence * 86400000);
      start.setUTCHours(9, 0, 0, 0);
      const end = new Date(start.getTime() + 30 * 60000);
      const description = [...plan.immediate, ...plan.next, ...plan.repeat].join('\n');
      const ics = `BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//ALO186//Pil Sureklilik//TR\r\nBEGIN:VEVENT\r\nUID:alo186-battery-${Date.now()}@alo186.com\r\nDTSTAMP:${dateStamp(new Date())}\r\nDTSTART:${dateStamp(start)}\r\nDTEND:${dateStamp(end)}\r\nSUMMARY:${escapeIcs('AA/AAA pil ve şarj cihazı tekrar testi')}\r\nDESCRIPTION:${escapeIcs(description)}\r\nURL:https://alo186.com/sektor-rehberi/aa-aaa-pil-sureklilik-test-merkezi/\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n`;
      download('alo186-aa-aaa-pil-tekrar-testi.ics', ics, 'text/calendar');
    });
    result.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
  }

  if (typeof module !== 'undefined' && module.exports) module.exports = { buildPlan };
  if (typeof document !== 'undefined') {
    const form = document.querySelector('#planForm');
    if (form) form.addEventListener('submit', (event) => {
      event.preventDefault();
      render(buildPlan(Object.fromEntries(new FormData(form).entries())));
    });
  }
})();