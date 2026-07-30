(() => {
  'use strict';

  const configs = {
    combi: {
      label: 'Kombi için saf sinüs UPS / yedek güç araması',
      url: 'https://www.amazon.com.tr/s?k=kombi+saf+sin%C3%BCs+ups&tag=alo186rehber-21',
      reminder: 'Kombi yedek güç kontrolü: tam model elektrik W, kalkış W, saf sinüs, topraklama, transfer davranışı, batarya durumu ve uyanıkken kontrollü testi yeniden doğrula.'
    },
    cold_chain: {
      label: 'Buzdolabı ve dondurucu için power station araması',
      url: 'https://www.amazon.com.tr/s?k=LiFePO4+power+station+saf+sin%C3%BCs&tag=alo186rehber-21',
      reminder: 'Soğuk zincir yedek güç kontrolü: kompresör sürekli ve kalkış W, hedef Wh, saf sinüs, batarya durumu, şarj seviyesi ve uyanıkken kontrollü başlatma testini yeniden doğrula.'
    }
  };

  const $ = (id) => document.getElementById(id);
  const body = document.body;
  const config = configs[body.dataset.applianceGuide];
  if (!config) return;

  const scenario = $('scenario');
  const checks = ['actualNeed', 'technicalCheck', 'affiliateCheck'].map($).filter(Boolean);
  const link = $('affiliateLink');
  const status = $('gateStatus');

  function gateReady() {
    return scenario && scenario.value === 'planning' && checks.length === 3 && checks.every((item) => item.checked);
  }

  function syncGate() {
    const activeOutage = scenario && scenario.value === 'active';
    const ready = gateReady();
    if (link) {
      link.textContent = config.label;
      link.classList.toggle('disabled', !ready);
      link.setAttribute('aria-disabled', String(!ready));
      if (ready) {
        link.href = config.url;
        link.target = '_blank';
        link.rel = 'sponsored nofollow noopener';
      } else {
        link.removeAttribute('href');
        link.removeAttribute('target');
      }
    }
    if (status) {
      if (activeOutage) {
        status.textContent = 'Aktif kesintide ürün teslimatı anlık çözüm değildir. Önce güvenlik, gıda/ısıtma sürekliliği ve daha önce test edilmiş mevcut kaynak planını uygulayın.';
      } else if (ready) {
        status.textContent = 'Teknik gereksinimi yeniden doğrulama sorumluluğuyla satış ortaklığı araması açıldı. Arama sonucu uygunluk onayı değildir.';
      } else {
        status.textContent = 'Satış ortaklığı araması kapalı. Önce ücretsiz hesabı ve üç doğrulama adımını tamamlayın.';
      }
    }
  }

  function createIcs(now = new Date()) {
    const start = new Date(now.getTime() + 90 * 86400000);
    const stamp = (date) => date.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}Z$/, 'Z');
    const day = start.toISOString().slice(0, 10).replace(/-/g, '');
    return [
      'BEGIN:VCALENDAR',
      'VERSION:2.0',
      'PRODID:-//ALO186//Appliance Backup Review//TR',
      'CALSCALE:GREGORIAN',
      'BEGIN:VEVENT',
      `UID:alo186-appliance-${body.dataset.applianceGuide}-${stamp(now)}@alo186.com`,
      `DTSTAMP:${stamp(now)}`,
      `DTSTART;VALUE=DATE:${day}`,
      'SUMMARY:ALO186 yedek güç 90 günlük kontrolü',
      `DESCRIPTION:${config.reminder}`,
      'END:VEVENT',
      'END:VCALENDAR'
    ].join('\r\n');
  }

  function downloadCalendar() {
    const blob = new Blob([createIcs()], { type: 'text/calendar;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `alo186-${body.dataset.applianceGuide}-90-gun-kontrol.ics`;
    anchor.click();
    setTimeout(() => URL.revokeObjectURL(url), 500);
  }

  if (scenario) scenario.addEventListener('change', syncGate);
  checks.forEach((item) => item.addEventListener('change', syncGate));
  const calendar = $('downloadIcs');
  if (calendar) calendar.addEventListener('click', downloadCalendar);
  const printButton = $('printGuide');
  if (printButton) printButton.addEventListener('click', () => window.print());
  syncGate();

  if (typeof module === 'object' && module.exports) module.exports = { createIcs };
})();
