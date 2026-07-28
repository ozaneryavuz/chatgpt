(() => {
  'use strict';

  const labels = {
    facility: {
      hotel: 'Otel / tatil tesisi',
      site: 'Site / apartman / villa projesi',
      restaurant: 'Restoran / mağaza / soğuk zincir',
      office: 'Ofis / küçük işletme',
      industrial: 'Atölye / üretim tesisi'
    },
    problem: {
      outage: 'Tekrarlayan elektrik kesintisi',
      voltage: 'Düşük/yüksek gerilim ve cihaz riski',
      backup: 'UPS/jeneratör kapasitesi belirsiz',
      energy: 'GES, batarya veya enerji maliyeti',
      ev: 'EV şarj ve güç kapasitesi',
      audit: 'Genel elektrik sürekliliği ve risk incelemesi'
    },
    backup: {
      none: 'Yok / bilinmiyor',
      ups: 'UPS',
      generator: 'Jeneratör',
      both: 'UPS + jeneratör',
      solar_storage: 'GES / batarya / hibrit sistem'
    },
    scope: {
      remote: 'Uzaktan doküman ön incelemesi',
      comparison: 'Yedek güç ve maliyet karşılaştırması',
      site: 'Yerinde keşif ve teknik rapor',
      roadmap: '90 günlük süreklilik yol haritası'
    }
  };

  const byId = (id) => document.getElementById(id);
  const safeChoice = (group, id) => {
    const value = String(byId(id).value || '');
    return Object.prototype.hasOwnProperty.call(labels[group], value) ? value : Object.keys(labels[group])[0];
  };

  function track(name, data = {}) {
    const allowed = {};
    for (const key of ['facility', 'problem', 'backup', 'scope']) {
      if (typeof data[key] === 'string' && data[key].length < 60) allowed[key] = data[key];
    }
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ event: name, ...allowed });
  }

  document.addEventListener('DOMContentLoaded', () => {
    const form = byId('serviceForm');
    const link = byId('mailLink');

    form.addEventListener('submit', (event) => {
      event.preventDefault();
      const selection = {
        facility: safeChoice('facility', 'facility'),
        problem: safeChoice('problem', 'problem'),
        backup: safeChoice('backup', 'backup'),
        scope: safeChoice('scope', 'scope')
      };
      const readable = {
        facility: labels.facility[selection.facility],
        problem: labels.problem[selection.problem],
        backup: labels.backup[selection.backup],
        scope: labels.scope[selection.scope]
      };

      byId('resultTitle').textContent = `${readable.facility} için ücretli ön değerlendirme talebi hazır.`;
      byId('resultText').textContent = 'Aşağıdaki kapsam e-posta taslağına eklenecek. İletişim bilgisi veya dosya eklemek sizin tercihinizdir.';
      byId('summary').innerHTML = [
        ['Tesis türü', readable.facility],
        ['Ana problem', readable.problem],
        ['Mevcut yedek kaynak', readable.backup],
        ['İstenen kapsam', readable.scope]
      ].map(([title, value]) => `<div><strong>${title}</strong>${value}</div>`).join('');

      const subject = `ALO186 ücretli teknik ön değerlendirme talebi — ${readable.facility}`;
      const body = [
        'Merhaba,',
        '',
        'ALO186 Kurumsal Elektrik Sürekliliği Ön Değerlirmesi için bilgi rica ediyorum.',
        '',
        `Tesis türü: ${readable.facility}`,
        `Ana problem: ${readable.problem}`,
        `Mevcut yedek kaynak: ${readable.backup}`,
        `İstenen kapsam: ${readable.scope}`,
        '',
        'Çalışmaya başlamadan önce kapsam, ücret, teslim biçimi ve gerekiyorsa saha koşullarının yazılı olarak teyit edilmesini rica ederim.',
        '',
        'Not: Bu e-posta resmî arıza/şikâyet kaydı değildir.'
      ].join('\n');

      link.href = `mailto:bilgi@alo186.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
      link.classList.remove('disabled');
      link.setAttribute('aria-disabled', 'false');
      link.tabIndex = 0;
      track('paid_assessment_request_prepared', selection);
    });

    link.addEventListener('click', (event) => {
      if (link.getAttribute('aria-disabled') === 'true') {
        event.preventDefault();
        return;
      }
      track('paid_assessment_email_opened', {
        facility: safeChoice('facility', 'facility'),
        problem: safeChoice('problem', 'problem'),
        backup: safeChoice('backup', 'backup'),
        scope: safeChoice('scope', 'scope')
      });
    });
  });
})();
